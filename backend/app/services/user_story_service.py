import logging

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.gemini_provider import GeminiProvider
from app.prompts.user_story_prompt import (
    SYSTEM_INSTRUCTION,
    build_user_story_prompt,
)
from app.schemas.user_story import (
    UserStoryGenerationRequest,
    UserStoryGenerationResponse,
)


logger = logging.getLogger(__name__)


class UserStoryGenerationError(Exception):
    """Raised when user-story generation cannot be completed."""


class UserStoryService:
    def __init__(self) -> None:
        try:
            self.provider = GeminiProvider()
        except LlmConfigurationError as exc:
            raise UserStoryGenerationError(str(exc)) from exc

    async def generate(
        self,
        request: UserStoryGenerationRequest,
    ) -> UserStoryGenerationResponse:
        prompt = build_user_story_prompt(request)
        logger.info(
            "Starting user-story generation with model=%s",
            self.provider.model,
        )

        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=UserStoryGenerationResponse,
            )
        except LlmTemporaryError as exc:
            logger.warning(
                "User-story generation failed status=temporary_failure"
            )
            raise UserStoryGenerationError(
                "Gemini is temporarily unavailable. "
                "Please retry after a short time."
            ) from exc
        except LlmRequestError as exc:
            logger.error(
                "User-story generation failed status=request_error"
            )
            raise UserStoryGenerationError(
                "Gemini rejected the user-story request. "
                "Check the model, API quota, and request configuration."
            ) from exc
        except LlmResponseValidationError as exc:
            logger.error(
                "User-story generation failed "
                "status=response_validation_error"
            )
            raise UserStoryGenerationError(
                "Gemini returned an invalid structured user-story response."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()
