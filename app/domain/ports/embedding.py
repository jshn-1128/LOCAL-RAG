"""
Embedding port.

Defines the contract for text embedding providers.
Implementations: SentenceTransformers, ONNX, OpenAI-compatible (future).
Future milestone: Milestone 8 — Embeddings.
"""

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]: ...

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def dimensions(self) -> int: ...
