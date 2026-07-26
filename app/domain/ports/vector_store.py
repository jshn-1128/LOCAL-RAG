"""
Vector store port.

Defines the contract for vector storage and similarity search.
Implementations: ChromaDB, FAISS, PGVector (future).
Future milestone: Milestone 9 — Vector Store.
"""

from abc import ABC, abstractmethod

from app.domain.models.chunk import Chunk
from app.domain.models.query import Query
from app.domain.models.result import RetrievalResult


class VectorStorePort(ABC):
    @abstractmethod
    async def add_chunks(
        self, chunks: list[Chunk], embeddings: list[list[float]]
    ) -> None: ...

    @abstractmethod
    async def search(self, query: Query, embedding: list[float]) -> RetrievalResult: ...

    @abstractmethod
    async def delete(self, chunk_ids: list[str]) -> None: ...

    @abstractmethod
    async def count(self) -> int: ...
