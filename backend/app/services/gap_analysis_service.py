import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.gap_analysis_prompt import (
    GAP_ANALYSIS_SYSTEM_INSTRUCTION,
    build_gap_analysis_prompt,
)
from app.schemas.gap_analysis import (
    GapAnalysisRequest,
    GapAnalysisResponse,
)


logger = logging.getLogger(__name__)


class GapAnalysisError(Exception):
    """Raised when requirement gap analysis cannot be completed."""


class GapAnalysisService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: GapAnalysisRequest,
    ) -> GapAnalysisResponse:
        logger.info(
            "Starting requirement gap analysis requirement_id=%s",
            request.requirement_id,
        )

        try:
            result = await self.provider.generate_structured(
                prompt=build_gap_analysis_prompt(request),
                system_instruction=GAP_ANALYSIS_SYSTEM_INSTRUCTION,
                response_schema=GapAnalysisResponse,
                temperature=0.1,
            )
            logger.info(
                "Requirement gap analysis completed requirement_id=%s",
                request.requirement_id,
            )
            return result
        except LlmError as exc:
            logger.warning(
                "Requirement gap analysis failed requirement_id=%s: %s",
                request.requirement_id,
                type(exc).__name__,
            )
            raise GapAnalysisError(
                "Unable to complete requirement gap analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()
