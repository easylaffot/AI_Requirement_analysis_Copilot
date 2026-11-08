import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.requirement_risk_prompt import (
    REQUIREMENT_RISK_SYSTEM_INSTRUCTION,
    build_requirement_risk_prompt,
)
from app.schemas.requirement_risk import (
    RequirementRiskRequest,
    RequirementRiskResponse,
)


logger = logging.getLogger(__name__)


class RequirementRiskAnalysisError(Exception):
    """Raised when requirement risk analysis fails."""


class RequirementRiskService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: RequirementRiskRequest,
    ) -> RequirementRiskResponse:
        logger.info(
            "Starting risk analysis title=%s count=%s",
            request.analysis_title,
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_requirement_risk_prompt(request),
                system_instruction=(
                    REQUIREMENT_RISK_SYSTEM_INSTRUCTION
                ),
                response_schema=RequirementRiskResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Requirement risk analysis failed error=%s",
                type(exc).__name__,
            )

            raise RequirementRiskAnalysisError(
                "Unable to complete requirement risk analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()