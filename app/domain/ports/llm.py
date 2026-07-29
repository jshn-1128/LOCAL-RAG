"""
LLM port.

Defines the contract for large language model providers.
Implementations: Ollama, llama.cpp, OpenAI-compatible (future).
Future milestone: Milestone 10 — LLM Integration.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMPort(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs: object) -> str: ...

    @abstractmethod
    async def generate_stream(
        self, prompt: str, **kwargs: object
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def generate_chat(
        self, messages: list[dict[str, str]], **kwargs: object
    ) -> str: ...

    @abstractmethod
    async def generate_chat_stream(
        self, messages: list[dict[str, str]], **kwargs: object
    ) -> AsyncIterator[str]: ...
