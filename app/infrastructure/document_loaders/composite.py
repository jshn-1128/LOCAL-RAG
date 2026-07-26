"""
Composite document loader.

Implements DocumentLoaderPort by delegating to format-specific loaders
based on file extension.  This allows the IngestionService to use a
single loader port instance while supporting multiple document formats.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.domain.exceptions import UnsupportedDocumentError
from app.domain.models.document import Document
from app.domain.ports.document_loader import DocumentLoaderPort

logger = logging.getLogger(__name__)


class CompositeDocumentLoader(DocumentLoaderPort):
    """Delegates loading to the appropriate format-specific loader.

    Loaders are indexed by their supported_extensions property.
    """

    def __init__(self, loaders: list[DocumentLoaderPort]) -> None:
        self._extension_map: dict[str, DocumentLoaderPort] = {}
        for loader in loaders:
            for ext in loader.supported_extensions:
                if ext in self._extension_map:
                    logger.warning(
                        "Duplicate loader registration for extension %s: %s overrides %s",
                        ext,
                        type(loader).__name__,
                        type(self._extension_map[ext]).__name__,
                    )
                self._extension_map[ext] = loader

        self._loaders = loaders

    async def load(self, source: Path) -> Document:
        loader = self._resolve_loader(source)
        logger.debug("Loading %s via %s", source.name, type(loader).__name__)
        return await loader.load(source)

    async def load_many(self, sources: list[Path]) -> list[Document]:
        return [await self.load(s) for s in sources]

    @property
    def supported_extensions(self) -> set[str]:
        return set(self._extension_map.keys())

    def _resolve_loader(self, source: Path) -> DocumentLoaderPort:
        extension = source.suffix.lower()
        loader = self._extension_map.get(extension)
        if loader is None:
            raise UnsupportedDocumentError(
                f"No loader registered for extension '{extension}'. "
                f"Supported: {', '.join(sorted(self._extension_map.keys()))}"
            )
        return loader
