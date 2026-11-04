import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.prompts.user_story_prompt import (
    SYSTEM_INSTRUCTION,
    build_user_story_prompt,
)
from app.schemas.user_story import (
    UserStoryGenerationRequest,
    UserStoryGenerationResponse,
)


load_dotenv()

logger = logging.getLogger(__name__)


class UserStoryGenerationError(Exception):
    """Raised when user-story generation cannot be completed."""


class UserStoryService:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing from backend/.env"
            )

        if not model:
            raise RuntimeError(
                "GEMINI_MODEL is missing from backend/.env"
            )

        self.model = model
        self.client = genai.Client(api_key=api_key)

    async def generate(
        self,
        request: UserStoryGenerationRequest,
    ) -> UserStoryGenerationResponse:
        prompt = build_user_story_prompt(request)

        logger.info(
            "Starting user-story generation with model=%s "
            "requirement_title=%s",
            self.model,
            request.requirement_title,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=UserStoryGenerationResponse,
                ),
            )

            return self._validate_response(response)

        except errors.ServerError as exc:
            logger.warning(
                "Gemini service error during user-story "
                "generation: %s",
                exc,
            )

            raise UserStoryGenerationError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc

        except errors.ClientError as exc:
            logger.exception(
                "Gemini rejected the user-story request."
            )

            raise UserStoryGenerationError(
                "Gemini rejected the user-story request. "
                "Check the model, API quota, and request "
                "configuration."
            ) from exc

        except ValidationError as exc:
            logger.exception(
                "Gemini output did not match the user-story schema."
            )

            raise UserStoryGenerationError(
                "Gemini returned an invalid structured "
                "user-story response."
            ) from exc

        except ValueError as exc:
            logger.exception(
                "The user-story response could not be parsed."
            )

            raise UserStoryGenerationError(
                "The generated user-story response could not "
                "be parsed."
            ) from exc

    @staticmethod
    def _validate_response(
        response: object,
    ) -> UserStoryGenerationResponse:
        parsed = getattr(response, "parsed", None)

        if parsed is not None:
            return UserStoryGenerationResponse.model_validate(
                parsed
            )

        response_text = getattr(response, "text", None)

        if not response_text:
            raise UserStoryGenerationError(
                "Gemini returned an empty user-story response."
            )

        return UserStoryGenerationResponse.model_validate_json(
            response_text
        )

    async def close(self) -> None:
        await self.client.aio.aclose()