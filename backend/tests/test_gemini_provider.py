from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from google.genai import errors
from pydantic import BaseModel

from app.llm.exceptions import (
    LlmConfigurationError,
    LlmRequestError,
    LlmResponseValidationError,
    LlmTemporaryError,
)
from app.llm.gemini_provider import GeminiProvider


class SampleResponse(BaseModel):
    message: str


def _client(response: object | None = None) -> SimpleNamespace:
    models = SimpleNamespace(
        generate_content=AsyncMock(return_value=response),
    )
    aio = SimpleNamespace(
        models=models,
        aclose=AsyncMock(),
    )
    return SimpleNamespace(aio=aio)


def _configure_provider(
    monkeypatch: pytest.MonkeyPatch,
    client: SimpleNamespace,
) -> None:
    monkeypatch.setattr(
        "app.llm.gemini_provider.load_dotenv",
        lambda: None,
    )
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    monkeypatch.setattr(
        "app.llm.gemini_provider.genai.Client",
        Mock(return_value=client),
    )


def test_missing_api_key_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    _configure_provider(monkeypatch, client)
    monkeypatch.delenv("GEMINI_API_KEY")

    with pytest.raises(LlmConfigurationError, match="GEMINI_API_KEY"):
        GeminiProvider()


def test_missing_model_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    _configure_provider(monkeypatch, client)
    monkeypatch.delenv("GEMINI_MODEL")

    with pytest.raises(LlmConfigurationError, match="GEMINI_MODEL"):
        GeminiProvider()


@pytest.mark.asyncio
async def test_parsed_pydantic_response_is_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = SampleResponse(message="parsed")
    client = _client(SimpleNamespace(parsed=expected, text=None))
    _configure_provider(monkeypatch, client)
    provider = GeminiProvider()

    result = await provider.generate_structured(
        "prompt",
        "instruction",
        SampleResponse,
    )

    assert result == expected


@pytest.mark.asyncio
async def test_json_text_fallback_is_validated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(
        SimpleNamespace(parsed=None, text='{"message":"from json"}')
    )
    _configure_provider(monkeypatch, client)
    provider = GeminiProvider()

    result = await provider.generate_structured(
        "prompt",
        "instruction",
        SampleResponse,
    )

    assert result == SampleResponse(message="from json")


@pytest.mark.asyncio
async def test_empty_response_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(SimpleNamespace(parsed=None, text=None))
    _configure_provider(monkeypatch, client)
    provider = GeminiProvider()

    with pytest.raises(LlmResponseValidationError, match="empty"):
        await provider.generate_structured(
            "prompt",
            "instruction",
            SampleResponse,
        )


@pytest.mark.asyncio
async def test_invalid_json_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(SimpleNamespace(parsed=None, text="{invalid"))
    _configure_provider(monkeypatch, client)
    provider = GeminiProvider()

    with pytest.raises(LlmResponseValidationError, match="invalid JSON"):
        await provider.generate_structured(
            "prompt",
            "instruction",
            SampleResponse,
        )


@pytest.mark.asyncio
async def test_client_error_becomes_request_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    client.aio.models.generate_content.side_effect = errors.ClientError(
        400,
        {"error": {"message": "invalid request"}},
    )
    _configure_provider(monkeypatch, client)
    provider = GeminiProvider()

    with pytest.raises(LlmRequestError) as raised:
        await provider.generate_structured(
            "prompt",
            "instruction",
            SampleResponse,
        )

    assert isinstance(raised.value.__cause__, errors.ClientError)
    assert client.aio.models.generate_content.await_count == 1


@pytest.mark.asyncio
async def test_server_error_retries_then_raises_temporary_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    client.aio.models.generate_content.side_effect = errors.ServerError(
        503,
        {"error": {"message": "unavailable"}},
    )
    _configure_provider(monkeypatch, client)
    sleep = AsyncMock()
    monkeypatch.setattr("app.llm.gemini_provider.asyncio.sleep", sleep)
    provider = GeminiProvider()

    with pytest.raises(LlmTemporaryError) as raised:
        await provider.generate_structured(
            "prompt",
            "instruction",
            SampleResponse,
        )

    assert isinstance(raised.value.__cause__, errors.ServerError)
    assert client.aio.models.generate_content.await_count == 2
    sleep.assert_awaited_once()


@pytest.mark.asyncio
async def test_successful_second_attempt_is_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = SampleResponse(message="recovered")
    client = _client()
    client.aio.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"message": "unavailable"}}),
        SimpleNamespace(parsed=expected, text=None),
    ]
    _configure_provider(monkeypatch, client)
    sleep = AsyncMock()
    monkeypatch.setattr("app.llm.gemini_provider.asyncio.sleep", sleep)
    provider = GeminiProvider()

    result = await provider.generate_structured(
        "prompt",
        "instruction",
        SampleResponse,
    )

    assert result == expected
    assert client.aio.models.generate_content.await_count == 2
    sleep.assert_awaited_once()


@pytest.mark.asyncio
async def test_incident_fallback_model_is_used_on_second_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = SampleResponse(message="fallback")
    client = _client()
    client.aio.models.generate_content.side_effect = [
        errors.ServerError(503, {"error": {"message": "unavailable"}}),
        SimpleNamespace(parsed=expected, text=None),
    ]
    _configure_provider(monkeypatch, client)
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "fallback-model")
    monkeypatch.setattr(
        "app.llm.gemini_provider.asyncio.sleep",
        AsyncMock(),
    )
    provider = GeminiProvider(use_fallback_model=True)

    result = await provider.generate_structured(
        "prompt",
        "instruction",
        SampleResponse,
    )

    assert result == expected
    assert [
        call.kwargs["model"]
        for call in client.aio.models.generate_content.await_args_list
    ] == ["test-model", "fallback-model"]


@pytest.mark.asyncio
async def test_close_invokes_async_client_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client()
    _configure_provider(monkeypatch, client)
    provider = GeminiProvider()

    await provider.close()

    client.aio.aclose.assert_awaited_once()
