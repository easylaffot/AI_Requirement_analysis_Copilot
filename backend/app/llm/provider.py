from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class LlmProvider(ABC):
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: type[T],
        temperature: float = 0.2,
    ) -> T:
        """Generate and validate structured output."""

    @abstractmethod
    async def close(self) -> None:
        """Close provider resources."""
