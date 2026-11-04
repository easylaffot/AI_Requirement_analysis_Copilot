import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.prompts.acceptance_criteria_prompt import (
    SYSTEM_INSTRUCTION,
    build_acceptance_criteria_prompt,
)
from app.schemas.acceptance_criteria import (
    AcceptanceCriteriaRequest,
    AcceptanceCriteriaResponse,
)


load_dotenv()

logger = logging.getLogger(__name__)


class AcceptanceCriteriaGenerationError(Exception):
    """Raised when acceptance-criteria generation fails."""


class AcceptanceCriteriaService:
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
        request: AcceptanceCriteriaRequest,
    ) -> AcceptanceCriteriaResponse:
        prompt = build_acceptance_criteria_prompt(request)

        logger.info(
            "Starting acceptance-criteria generation "
            "with model=%s story_id=%s",
            self.model,
            request.story_id,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=AcceptanceCriteriaResponse,
                ),
            )

            return self._validate_response(response)

        except errors.ServerError as exc:
            logger.warning(
                "Gemini service error during acceptance-criteria "
                "generation: %s",
                exc,
            )

            raise AcceptanceCriteriaGenerationError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc

        except errors.ClientError as exc:
            logger.exception(
                "Gemini rejected the acceptance-criteria request."
            )

            raise AcceptanceCriteriaGenerationError(
                "Gemini rejected the acceptance-criteria request. "
                "Check the model, quota, and request configuration."
            ) from exc

        except ValidationError as exc:
            logger.exception(
                "Gemini output did not match the "
                "acceptance-criteria schema."
            )

            raise AcceptanceCriteriaGenerationError(
                "Gemini returned an invalid structured "
                "acceptance-criteria response."
            ) from exc

        except ValueError as exc:
            logger.exception(
                "The acceptance-criteria response could not "
                "be parsed."
            )

            raise AcceptanceCriteriaGenerationError(
                "The generated acceptance-criteria response "
                "could not be parsed."
            ) from exc

    @staticmethod
    def _validate_response(
        response: object,
    ) -> AcceptanceCriteriaResponse:
        parsed = getattr(response, "parsed", None)

        if parsed is not None:
            return AcceptanceCriteriaResponse.model_validate(
                parsed
            )

        response_text = getattr(response, "text", None)

        if not response_text:
            raise AcceptanceCriteriaGenerationError(
                "Gemini returned an empty acceptance-criteria "
                "response."
            )

        return AcceptanceCriteriaResponse.model_validate_json(
            response_text
        )

    async def close(self) -> None:
        await self.client.aio.aclose()