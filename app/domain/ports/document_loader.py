"""
Document loader port.

Defines the contract for loading documents from various sources.
Implementations: PDF loader, Markdown loader, plain text loader, directory watcher.

Each implementation handles a specific source type and returns
a domain Document ready for chunking and indexing.

Future milestone: Milestone 7 — Document Ingestion.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.models.document import Document


class DocumentLoaderPort(ABC):
    @abstractmethod
    async def load(self, source: Path) -> Document: ...

    @abstractmethod
    async def load_many(self, sources: list[Path]) -> list[Document]: ...

    @property
    @abstractmethod
    def supported_extensions(self) -> set[str]: ...
