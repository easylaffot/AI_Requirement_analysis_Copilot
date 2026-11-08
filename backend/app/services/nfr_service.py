import logging

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.gemini_provider import GeminiProvider
from app.prompts.nfr_prompt import (
    SYSTEM_INSTRUCTION,
    build_nfr_prompt,
)
from app.schemas.nfr import (
    NfrRecommendationRequest,
    NfrRecommendationResponse,
)


logger = logging.getLogger(__name__)


class NfrRecommendationError(Exception):
    """Raised when NFR recommendation cannot be completed."""


class NfrService:
    def __init__(self) -> None:
        try:
            self.provider = GeminiProvider()
        except LlmConfigurationError as exc:
            raise NfrRecommendationError(str(exc)) from exc

    async def recommend(
        self,
        request: NfrRecommendationRequest,
    ) -> NfrRecommendationResponse:
        prompt = build_nfr_prompt(request)
        logger.info(
            "Starting NFR recommendation with model=%s",
            self.provider.model,
        )

        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=NfrRecommendationResponse,
            )
        except LlmTemporaryError as exc:
            logger.warning("NFR recommendation failed status=temporary_failure")
            raise NfrRecommendationError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc
        except LlmRequestError as exc:
            logger.error("NFR recommendation failed status=request_error")
            raise NfrRecommendationError(
                "Gemini rejected the NFR request. Check the model, API quota, "
                "and request configuration."
            ) from exc
        except LlmResponseValidationError as exc:
            logger.error(
                "NFR recommendation failed status=response_validation_error"
            )
            raise NfrRecommendationError(
                "Gemini returned an invalid structured NFR response."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()
