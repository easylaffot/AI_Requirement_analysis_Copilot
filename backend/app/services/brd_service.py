import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.prompts.brd_prompt import (
    SYSTEM_INSTRUCTION,
    build_brd_prompt,
)
from app.schemas.brd import (
    BrdAnalysisRequest,
    BrdAnalysisResponse,
)


load_dotenv()

logger = logging.getLogger(__name__)


class BrdAnalysisError(Exception):
    """Raised when BRD analysis cannot be completed."""


class BrdService:
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

    async def analyze(
        self,
        request: BrdAnalysisRequest,
    ) -> BrdAnalysisResponse:
        prompt = build_brd_prompt(request)

        logger.info(
            "Starting BRD analysis with model=%s project=%s",
            self.model,
            request.project_name,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=BrdAnalysisResponse,
                ),
            )

            return self._validate_response(response)

        except errors.ServerError as exc:
            logger.warning(
                "Gemini service error during BRD analysis: %s",
                exc,
            )

            raise BrdAnalysisError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc

        except errors.ClientError as exc:
            logger.exception(
                "Gemini rejected the BRD analysis request."
            )

            raise BrdAnalysisError(
                "Gemini rejected the BRD request. Check the "
                "model, API quota and request configuration."
            ) from exc

        except ValidationError as exc:
            logger.exception(
                "Gemini returned BRD output that did not match "
                "the required schema."
            )

            raise BrdAnalysisError(
                "Gemini returned an invalid structured BRD response."
            ) from exc

        except ValueError as exc:
            logger.exception(
                "The BRD response could not be parsed."
            )

            raise BrdAnalysisError(
                "The generated BRD analysis could not be parsed."
            ) from exc

    @staticmethod
    def _validate_response(
        response: object,
    ) -> BrdAnalysisResponse:
        parsed = getattr(response, "parsed", None)

        if parsed is not None:
            return BrdAnalysisResponse.model_validate(parsed)

        response_text = getattr(response, "text", None)

        if not response_text:
            raise BrdAnalysisError(
                "Gemini returned an empty BRD analysis."
            )

        return BrdAnalysisResponse.model_validate_json(
            response_text
        )

    async def close(self) -> None:
        await self.client.aio.aclose()