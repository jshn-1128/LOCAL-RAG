"""
Text file loader (.txt).

Handles plain text files with encoding detection,
metadata extraction, and checksum generation.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from app.domain.models.document import Document
from app.domain.ports.document_loader import DocumentLoaderPort
from app.infrastructure.document_loaders.checksum_generator import generate_checksum
from app.infrastructure.document_loaders.encoding_detector import decode_content
from app.infrastructure.document_loaders.metadata_extractor import extract_content_stats
from app.infrastructure.document_loaders.mime_type_detector import detect_mime_type

logger = logging.getLogger(__name__)


class TextLoader(DocumentLoaderPort):
    async def load(self, source: Path) -> Document:
        return self._load_file(source)

    async def load_many(self, sources: list[Path]) -> list[Document]:
        return [self._load_file(s) for s in sources]

    @property
    def supported_extensions(self) -> set[str]:
        return {".txt"}

    def _load_file(self, path: Path) -> Document:
        raw = path.read_bytes()
        text, encoding = decode_content(raw)
        mime_type = detect_mime_type(".txt")
        checksum = generate_checksum(text)
        metadata = extract_content_stats(text)
        stat = os.stat(str(path))

        return Document(
            content=text,
            source_path=path.resolve(),
            filename=path.name,
            title=path.stem,
            checksum=checksum,
            file_type=".txt",
            mime_type=mime_type,
            encoding=encoding,
            created_at=(
                datetime.fromtimestamp(stat.st_birthtime)
                if hasattr(stat, "st_birthtime")
                else None
            ),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            metadata=metadata,
        )
