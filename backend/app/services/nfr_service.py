import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.prompts.nfr_prompt import (
    SYSTEM_INSTRUCTION,
    build_nfr_prompt,
)
from app.schemas.nfr import (
    NfrRecommendationRequest,
    NfrRecommendationResponse,
)


load_dotenv()

logger = logging.getLogger(__name__)


class NfrRecommendationError(Exception):
    """Raised when NFR recommendation cannot be completed."""


class NfrService:
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

    async def recommend(
        self,
        request: NfrRecommendationRequest,
    ) -> NfrRecommendationResponse:
        prompt = build_nfr_prompt(request)

        logger.info(
            "Starting NFR recommendation with model=%s "
            "requirement_id=%s",
            self.model,
            request.requirement_id,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=NfrRecommendationResponse,
                ),
            )

            return self._validate_response(response)

        except errors.ServerError as exc:
            logger.warning(
                "Gemini service error during NFR recommendation: %s",
                exc,
            )

            raise NfrRecommendationError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc

        except errors.ClientError as exc:
            logger.exception(
                "Gemini rejected the NFR recommendation request."
            )

            raise NfrRecommendationError(
                "Gemini rejected the NFR request. "
                "Check the model, API quota, and request "
                "configuration."
            ) from exc

        except ValidationError as exc:
            logger.exception(
                "Gemini output did not match the NFR schema."
            )

            raise NfrRecommendationError(
                "Gemini returned an invalid structured "
                "NFR response."
            ) from exc

        except ValueError as exc:
            logger.exception(
                "The NFR response could not be parsed."
            )

            raise NfrRecommendationError(
                "The generated NFR response could not be parsed."
            ) from exc

    @staticmethod
    def _validate_response(
        response: object,
    ) -> NfrRecommendationResponse:
        parsed = getattr(response, "parsed", None)

        if parsed is not None:
            return NfrRecommendationResponse.model_validate(
                parsed
            )

        response_text = getattr(response, "text", None)

        if not response_text:
            raise NfrRecommendationError(
                "Gemini returned an empty NFR response."
            )

        return NfrRecommendationResponse.model_validate_json(
            response_text
        )

    async def close(self) -> None:
        await self.client.aio.aclose()