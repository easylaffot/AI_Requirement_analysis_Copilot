import logging

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.gemini_provider import GeminiProvider
from app.prompts.incident_prompt import (
    SYSTEM_INSTRUCTION,
    build_incident_prompt,
)
from app.schemas.analysis import IncidentAnalysisResponse
from app.schemas.incident import IncidentRequest


logger = logging.getLogger(__name__)


class IncidentAnalysisError(Exception):
    """Raised when incident analysis cannot be completed."""


class IncidentService:
    def __init__(self) -> None:
        try:
            self.provider = GeminiProvider(use_fallback_model=True)
        except LlmConfigurationError as exc:
            raise IncidentAnalysisError(str(exc)) from exc

    async def analyze(
        self,
        incident: IncidentRequest,
    ) -> IncidentAnalysisResponse:
        prompt = build_incident_prompt(incident)
        logger.info(
            "Starting incident analysis with model=%s",
            self.provider.model,
        )

        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                system_instruction=SYSTEM_INSTRUCTION,
                response_schema=IncidentAnalysisResponse,
            )
        except LlmTemporaryError as exc:
            logger.warning("Incident analysis failed status=temporary_failure")
            raise IncidentAnalysisError(
                "All configured Gemini models are temporarily "
                "unavailable. Please retry after a short time."
            ) from exc
        except LlmRequestError as exc:
            logger.error("Incident analysis failed status=request_error")
            raise IncidentAnalysisError(
                "Gemini rejected the request. Check the API key, model ID, "
                "quota and structured output configuration."
            ) from exc
        except LlmResponseValidationError as exc:
            logger.error(
                "Incident analysis failed status=response_validation_error"
            )
            raise IncidentAnalysisError(
                "Gemini returned an invalid structured response."
            ) from exc

    async def close(self) -> None:
        await self.provider.close()
