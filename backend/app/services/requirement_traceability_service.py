import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.requirement_traceability_prompt import (
    REQUIREMENT_TRACEABILITY_SYSTEM_INSTRUCTION,
    build_requirement_traceability_prompt,
)
from app.schemas.requirement_traceability import (
    RequirementTraceabilityRequest,
    RequirementTraceabilityResponse,
)


logger = logging.getLogger(__name__)


class RequirementTraceabilityAnalysisError(Exception):
    """Raised when traceability analysis fails."""


class RequirementTraceabilityService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: RequirementTraceabilityRequest,
    ) -> RequirementTraceabilityResponse:
        logger.info(
            "Starting traceability analysis title=%s "
            "requirements=%s stories=%s criteria=%s tests=%s",
            request.analysis_title,
            len(request.requirements),
            len(request.user_stories),
            len(request.acceptance_criteria),
            len(request.test_cases),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_requirement_traceability_prompt(request),
                system_instruction=(
                    REQUIREMENT_TRACEABILITY_SYSTEM_INSTRUCTION
                ),
                response_schema=RequirementTraceabilityResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Traceability analysis failed error=%s",
                type(exc).__name__,
            )

            raise RequirementTraceabilityAnalysisError(
                "Unable to complete requirement traceability "
                "analysis. Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()