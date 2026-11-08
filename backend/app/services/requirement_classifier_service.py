import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.requirement_classifier_prompt import (
    REQUIREMENT_CLASSIFIER_SYSTEM_INSTRUCTION,
    build_requirement_classifier_prompt,
)
from app.schemas.requirement_classifier import (
    RequirementClassificationRequest,
    RequirementClassificationResponse,
)


logger = logging.getLogger(__name__)


class RequirementClassificationError(Exception):
    """Raised when requirement classification cannot be completed."""


class RequirementClassifierService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def classify(
        self,
        request: RequirementClassificationRequest,
    ) -> RequirementClassificationResponse:
        logger.info(
            "Starting requirement classification title=%s count=%s",
            request.analysis_title,
            len(request.requirements),
        )

        try:
            return await self.provider.generate_structured(
                prompt=build_requirement_classifier_prompt(request),
                system_instruction=(
                    REQUIREMENT_CLASSIFIER_SYSTEM_INSTRUCTION
                ),
                response_schema=RequirementClassificationResponse,
                temperature=0.1,
            )

        except LlmError as exc:
            logger.warning(
                "Requirement classification failed error=%s",
                type(exc).__name__,
            )

            raise RequirementClassificationError(
                "Unable to classify requirements. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()