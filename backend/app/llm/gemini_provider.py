import asyncio
import logging
import os
import random
from typing import TypeVar

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.provider import LlmProvider


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LlmProvider):
    MAX_ATTEMPTS = 2
    BASE_RETRY_DELAY_SECONDS = 0.1

    def __init__(self, *, use_fallback_model: bool = False) -> None:
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL")
        fallback_model = (
            os.getenv("GEMINI_FALLBACK_MODEL")
            if use_fallback_model
            else None
        )

        if not api_key:
            raise LlmConfigurationError(
                "GEMINI_API_KEY is missing from backend/.env"
            )
        if not model:
            raise LlmConfigurationError(
                "GEMINI_MODEL is missing from backend/.env"
            )

        self.model = model
        self.retry_model = (
            fallback_model
            if fallback_model and fallback_model != model
            else model
        )
        self.client = genai.Client(api_key=api_key)

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: type[T],
        temperature: float = 0.2,
    ) -> T:
        schema_name = getattr(response_schema, "__name__", str(response_schema))
        if not isinstance(response_schema, type) or not issubclass(
            response_schema, BaseModel
        ):
            error = LlmResponseValidationError(
                "The requested response schema must be a Pydantic model."
            )
            logger.error(
                "Gemini generation failed model=%s schema=%s status=invalid_schema",
                self.model,
                schema_name,
            )
            raise error

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=response_schema,
            )
        except (TypeError, ValueError) as exc:
            logger.error(
                "Gemini generation failed model=%s schema=%s status=invalid_schema",
                self.model,
                schema_name,
            )
            raise LlmResponseValidationError(
                "The requested response schema is invalid."
            ) from exc

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            attempt_model = (
                self.model if attempt == 1 else self.retry_model
            )
            try:
                logger.info(
                    "Gemini generation started model=%s schema=%s attempt=%s",
                    attempt_model,
                    schema_name,
                    attempt,
                )
                response = await self.client.aio.models.generate_content(
                    model=attempt_model,
                    contents=prompt,
                    config=config,
                )
                result = self._validate_response(response, response_schema)
                logger.info(
                    "Gemini generation succeeded model=%s schema=%s",
                    self.model,
                    schema_name,
                )
                return result
            except errors.ClientError as exc:
                logger.error(
                    "Gemini generation failed model=%s schema=%s status=request_error",
                    self.model,
                    schema_name,
                )
                raise LlmRequestError(
                    "Gemini rejected the structured generation request."
                ) from exc
            except (
                errors.ServerError,
                httpx.TransportError,
                TimeoutError,
                ConnectionError,
                OSError,
            ) as exc:
                if attempt < self.MAX_ATTEMPTS:
                    delay = (
                        self.BASE_RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                        + random.uniform(0.0, self.BASE_RETRY_DELAY_SECONDS)
                    )
                    logger.warning(
                        "Gemini generation retry model=%s schema=%s "
                        "attempt=%s max_attempts=%s",
                        self.retry_model,
                        schema_name,
                        attempt + 1,
                        self.MAX_ATTEMPTS,
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(
                    "Gemini generation failed model=%s schema=%s "
                    "status=temporary_failure attempts=%s",
                    attempt_model,
                    schema_name,
                    attempt,
                )
                raise LlmTemporaryError(
                    "Gemini is temporarily unavailable after retrying."
                ) from exc
            except LlmResponseValidationError:
                logger.error(
                    "Gemini generation failed model=%s schema=%s "
                    "status=response_validation_error",
                    self.model,
                    schema_name,
                )
                raise

        raise LlmTemporaryError(
            "Gemini is temporarily unavailable after retrying."
        )

    @staticmethod
    def _validate_response(
        response: object,
        response_schema: type[T],
    ) -> T:
        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            try:
                return response_schema.model_validate(parsed)
            except ValidationError as exc:
                raise LlmResponseValidationError(
                    "Gemini returned output that did not match the response schema."
                ) from exc

        response_text = getattr(response, "text", None)
        if not response_text:
            raise LlmResponseValidationError(
                "Gemini returned an empty structured response."
            )

        try:
            return response_schema.model_validate_json(response_text)
        except (ValidationError, ValueError) as exc:
            raise LlmResponseValidationError(
                "Gemini returned invalid JSON or output that did not match "
                "the response schema."
            ) from exc

    async def close(self) -> None:
        await self.client.aio.aclose()
