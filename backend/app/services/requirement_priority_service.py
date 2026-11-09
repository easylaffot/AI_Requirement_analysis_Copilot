import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.requirement_priority_prompt import (
    REQUIREMENT_PRIORITY_SYSTEM_INSTRUCTION,
    build_requirement_priority_prompt,
)
from app.schemas.requirement_priority import (
    RequirementPriorityRequest,
    RequirementPriorityResponse,
)


logger = logging.getLogger(__name__)


class RequirementPriorityAnalysisError(Exception):
    """Raised when requirement prioritization fails."""


class RequirementPriorityService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def prioritize(
        self,
        request: RequirementPriorityRequest,
    ) -> RequirementPriorityResponse:
        logger.info(
            "Starting prioritization title=%s count=%s",
            request.analysis_title,
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_requirement_priority_prompt(request),
                system_instruction=(
                    REQUIREMENT_PRIORITY_SYSTEM_INSTRUCTION
                ),
                response_schema=RequirementPriorityResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Requirement prioritization failed error=%s",
                type(exc).__name__,
            )

            raise RequirementPriorityAnalysisError(
                "Unable to prioritize requirements. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()