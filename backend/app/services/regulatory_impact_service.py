import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.regulatory_impact_prompt import (
    REGULATORY_IMPACT_SYSTEM_INSTRUCTION,
    build_regulatory_impact_prompt,
)
from app.schemas.regulatory_impact import (
    RegulatoryImpactRequest,
    RegulatoryImpactResponse,
)


logger = logging.getLogger(__name__)


class RegulatoryImpactAnalysisError(Exception):
    """Raised when regulatory impact analysis fails."""


class RegulatoryImpactService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: RegulatoryImpactRequest,
    ) -> RegulatoryImpactResponse:
        logger.info(
            "Starting regulatory impact analysis title=%s "
            "obligations=%s requirements=%s",
            request.analysis_title,
            len(request.obligations),
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_regulatory_impact_prompt(request),
                system_instruction=(
                    REGULATORY_IMPACT_SYSTEM_INSTRUCTION
                ),
                response_schema=RegulatoryImpactResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Regulatory impact analysis failed error=%s",
                type(exc).__name__,
            )

            raise RegulatoryImpactAnalysisError(
                "Unable to complete regulatory impact analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()