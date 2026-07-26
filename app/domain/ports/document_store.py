"""
Document store port.

Defines the contract for persistent document storage.
Implementations: Filesystem, S3-compatible (future).
Future milestone: Milestone 7 — Document Ingestion.
"""

from abc import ABC, abstractmethod

from app.domain.models.document import Document


class DocumentStorePort(ABC):
    @abstractmethod
    async def save(self, document: Document) -> None: ...

    @abstractmethod
    async def get(self, document_id: str) -> Document | None: ...

    @abstractmethod
    async def delete(self, document_id: str) -> None: ...

    @abstractmethod
    async def list_documents(self) -> list[Document]: ...
