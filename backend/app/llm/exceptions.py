class LlmError(Exception):
    """Base exception for language-model provider failures."""


class LlmConfigurationError(LlmError):
    """Raised when the provider is not configured correctly."""


class LlmTemporaryError(LlmError):
    """Raised when a transient provider failure persists after retries."""


class LlmRequestError(LlmError):
    """Raised when the provider rejects a generation request."""


class LlmResponseValidationError(LlmError):
    """Raised when generated output does not match the requested schema."""
