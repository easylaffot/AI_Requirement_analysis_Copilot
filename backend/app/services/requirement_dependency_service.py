import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.requirement_dependency_prompt import (
    REQUIREMENT_DEPENDENCY_SYSTEM_INSTRUCTION,
    build_requirement_dependency_prompt,
)
from app.schemas.requirement_dependency import (
    RequirementDependencyRequest,
    RequirementDependencyResponse,
)


logger = logging.getLogger(__name__)


class RequirementDependencyAnalysisError(Exception):
    """Raised when dependency analysis cannot be completed."""


class RequirementDependencyService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: RequirementDependencyRequest,
    ) -> RequirementDependencyResponse:
        logger.info(
            "Starting dependency analysis title=%s count=%s",
            request.analysis_title,
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_requirement_dependency_prompt(request),
                system_instruction=(
                    REQUIREMENT_DEPENDENCY_SYSTEM_INSTRUCTION
                ),
                response_schema=RequirementDependencyResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Requirement dependency analysis failed error=%s",
                type(exc).__name__,
            )

            raise RequirementDependencyAnalysisError(
                "Unable to complete requirement dependency analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()