import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.duplicate_requirement_prompt import (
    DUPLICATE_REQUIREMENT_SYSTEM_INSTRUCTION,
    build_duplicate_requirement_prompt,
)
from app.schemas.duplicate_requirement import (
    DuplicateAnalysisRequest,
    DuplicateAnalysisResponse,
)


logger = logging.getLogger(__name__)


class DuplicateRequirementAnalysisError(Exception):
    """Raised when duplicate analysis cannot be completed."""


class DuplicateRequirementService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: DuplicateAnalysisRequest,
    ) -> DuplicateAnalysisResponse:
        logger.info(
            "Starting duplicate analysis title=%s requirements=%s",
            request.analysis_title,
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_duplicate_requirement_prompt(request),
                system_instruction=(
                    DUPLICATE_REQUIREMENT_SYSTEM_INSTRUCTION
                ),
                response_schema=DuplicateAnalysisResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Duplicate analysis failed error=%s",
                type(exc).__name__,
            )

            raise DuplicateRequirementAnalysisError(
                "Unable to complete duplicate requirement analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()