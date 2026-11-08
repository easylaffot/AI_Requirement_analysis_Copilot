import logging

from app.llm.exceptions import LlmError
from app.llm.gemini_provider import GeminiProvider
from app.prompts.ambiguity_prompt import (
    SYSTEM_INSTRUCTION,
    build_ambiguity_prompt,
)
from app.schemas.ambiguity import (
    AmbiguityAnalysisRequest,
    AmbiguityAnalysisResponse,
)


logger = logging.getLogger(__name__)


class AmbiguityAnalysisError(Exception):
    """Raised when ambiguity analysis cannot be completed."""


class AmbiguityService:
    def __init__(self) -> None:
        self.provider = GeminiProvider()

    async def analyze(
        self,
        request: AmbiguityAnalysisRequest,
    ) -> AmbiguityAnalysisResponse:
        logger.info(
            "Starting ambiguity analysis requirement_id=%s",
            request.requirement_id,
        )

        try:
            result = await self.provider.generate_structured(
                prompt=build_ambiguity_prompt(request),
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=AmbiguityAnalysisResponse,
                temperature=0.1,
            )

            logger.info(
                "Ambiguity analysis completed requirement_id=%s",
                request.requirement_id,
            )

            return result

        except LlmError as exc:
            logger.warning(
                "Ambiguity analysis failed requirement_id=%s: %s",
                request.requirement_id,
                type(exc).__name__,
            )

            raise AmbiguityAnalysisError(
                "Unable to complete ambiguity analysis. "
                "Please retry after a short time."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()