import asyncio
import logging
import os
import random

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.prompts.incident_prompt import (
    SYSTEM_INSTRUCTION,
    build_incident_prompt,
)
from app.schemas.analysis import IncidentAnalysisResponse
from app.schemas.incident import IncidentRequest


load_dotenv()

logger = logging.getLogger(__name__)


class IncidentAnalysisError(Exception):
    """Raised when incident analysis cannot be completed."""


class IncidentService:
    MAX_ATTEMPTS_PER_MODEL = 2

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        primary_model = os.getenv("GEMINI_MODEL")
        fallback_model = os.getenv("GEMINI_FALLBACK_MODEL")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing from backend/.env"
            )

        if not primary_model:
            raise RuntimeError(
                "GEMINI_MODEL is missing from backend/.env"
            )

        self.models = [primary_model]

        if (
            fallback_model
            and fallback_model != primary_model
        ):
            self.models.append(fallback_model)

        self.client = genai.Client(api_key=api_key)

    async def analyze(
        self,
        incident: IncidentRequest,
    ) -> IncidentAnalysisResponse:
        prompt = build_incident_prompt(incident)
        last_error: Exception | None = None

        for model in self.models:
            for attempt in range(1, self.MAX_ATTEMPTS_PER_MODEL + 1):
                try:
                    logger.info(
                        "Analyzing incident with model=%s attempt=%s",
                        model,
                        attempt,
                    )

                    response = (
                        await self.client.aio.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_INSTRUCTION,
                                temperature=0.2,
                                response_mime_type="application/json",
                                response_schema=IncidentAnalysisResponse,
                            ),
                        )
                    )

                    return self._validate_response(response)

                except errors.ServerError as exc:
                    last_error = exc

                    logger.warning(
                        "Temporary Gemini failure for model=%s "
                        "attempt=%s: %s",
                        model,
                        attempt,
                        exc,
                    )

                    if attempt < self.MAX_ATTEMPTS_PER_MODEL:
                        delay = (2 ** (attempt - 1)) + random.uniform(
                            0.0,
                            1.0,
                        )
                        await asyncio.sleep(delay)

                except errors.ClientError as exc:
                    logger.exception(
                        "Gemini rejected the request for model=%s",
                        model,
                    )

                    raise IncidentAnalysisError(
                        "Gemini rejected the request. Check the "
                        "API key, model ID, quota and structured "
                        "output configuration."
                    ) from exc

                except ValidationError as exc:
                    logger.exception(
                        "Gemini returned output that did not match "
                        "the incident analysis schema."
                    )

                    raise IncidentAnalysisError(
                        "Gemini returned an invalid structured response."
                    ) from exc

        raise IncidentAnalysisError(
            "All configured Gemini models are temporarily "
            "unavailable. Please retry after a short time."
        ) from last_error

    @staticmethod
    def _validate_response(
        response: object,
    ) -> IncidentAnalysisResponse:
        parsed = getattr(response, "parsed", None)

        if parsed is not None:
            return IncidentAnalysisResponse.model_validate(parsed)

        response_text = getattr(response, "text", None)

        if not response_text:
            raise IncidentAnalysisError(
                "Gemini returned an empty response."
            )

        return IncidentAnalysisResponse.model_validate_json(
            response_text
        )

    async def close(self) -> None:
        await self.client.aio.aclose()