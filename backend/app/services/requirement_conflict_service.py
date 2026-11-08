import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.requirement_conflict_prompt import (
    REQUIREMENT_CONFLICT_SYSTEM_INSTRUCTION,
    build_requirement_conflict_prompt,
)
from app.schemas.requirement_conflict import (
    ConflictAnalysisRequest,
    ConflictAnalysisResponse,
)


logger = logging.getLogger(__name__)


class RequirementConflictAnalysisError(Exception):
    """Raised when conflict analysis cannot be completed."""


class RequirementConflictService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: ConflictAnalysisRequest,
    ) -> ConflictAnalysisResponse:
        logger.info(
            "Starting conflict analysis title=%s requirements=%s",
            request.analysis_title,
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_requirement_conflict_prompt(request),
                system_instruction=(
                    REQUIREMENT_CONFLICT_SYSTEM_INSTRUCTION
                ),
                response_schema=ConflictAnalysisResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Conflict analysis failed error=%s",
                type(exc).__name__,
            )

            raise RequirementConflictAnalysisError(
                "Unable to complete requirement conflict analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()