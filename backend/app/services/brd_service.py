import logging

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.gemini_provider import GeminiProvider
from app.prompts.brd_prompt import (
    SYSTEM_INSTRUCTION,
    build_brd_prompt,
)
from app.schemas.brd import (
    BrdAnalysisRequest,
    BrdAnalysisResponse,
)


logger = logging.getLogger(__name__)


class BrdAnalysisError(Exception):
    """Raised when BRD analysis cannot be completed."""


class BrdService:
    def __init__(self) -> None:
        try:
            self.provider = GeminiProvider()
        except LlmConfigurationError as exc:
            raise BrdAnalysisError(str(exc)) from exc

    async def analyze(
        self,
        request: BrdAnalysisRequest,
    ) -> BrdAnalysisResponse:
        prompt = build_brd_prompt(request)
        logger.info(
            "Starting BRD analysis with model=%s",
            self.provider.model,
        )

        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=BrdAnalysisResponse,
            )
        except LlmTemporaryError as exc:
            logger.warning("BRD analysis failed status=temporary_failure")
            raise BrdAnalysisError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc
        except LlmRequestError as exc:
            logger.error("BRD analysis failed status=request_error")
            raise BrdAnalysisError(
                "Gemini rejected the BRD request. Check the "
                "model, API quota and request configuration."
            ) from exc
        except LlmResponseValidationError as exc:
            logger.error(
                "BRD analysis failed status=response_validation_error"
            )
            raise BrdAnalysisError(
                "Gemini returned an invalid structured BRD response."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()
