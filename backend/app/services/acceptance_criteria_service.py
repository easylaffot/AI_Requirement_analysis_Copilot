import logging

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.gemini_provider import GeminiProvider
from app.prompts.acceptance_criteria_prompt import (
    SYSTEM_INSTRUCTION,
    build_acceptance_criteria_prompt,
)
from app.schemas.acceptance_criteria import (
    AcceptanceCriteriaRequest,
    AcceptanceCriteriaResponse,
)


logger = logging.getLogger(__name__)


class AcceptanceCriteriaGenerationError(Exception):
    """Raised when acceptance-criteria generation fails."""


class AcceptanceCriteriaService:
    def __init__(self) -> None:
        try:
            self.provider = GeminiProvider()
        except LlmConfigurationError as exc:
            raise AcceptanceCriteriaGenerationError(str(exc)) from exc

    async def generate(
        self,
        request: AcceptanceCriteriaRequest,
    ) -> AcceptanceCriteriaResponse:
        prompt = build_acceptance_criteria_prompt(request)
        logger.info(
            "Starting acceptance-criteria generation with model=%s",
            self.provider.model,
        )

        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=AcceptanceCriteriaResponse,
            )
        except LlmTemporaryError as exc:
            logger.warning(
                "Acceptance-criteria generation failed "
                "status=temporary_failure"
            )
            raise AcceptanceCriteriaGenerationError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc
        except LlmRequestError as exc:
            logger.error(
                "Acceptance-criteria generation failed status=request_error"
            )
            raise AcceptanceCriteriaGenerationError(
                "Gemini rejected the acceptance-criteria request. "
                "Check the model, quota, and request configuration."
            ) from exc
        except LlmResponseValidationError as exc:
            logger.error(
                "Acceptance-criteria generation failed "
                "status=response_validation_error"
            )
            raise AcceptanceCriteriaGenerationError(
                "Gemini returned an invalid structured "
                "acceptance-criteria response."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()
