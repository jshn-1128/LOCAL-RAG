"""
Markdown file loader (.md).

Handles Markdown files with front matter extraction,
encoding detection, metadata extraction, and checksum generation.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from app.domain.models.document import Document, DocumentMetadata
from app.domain.ports.document_loader import DocumentLoaderPort
from app.infrastructure.document_loaders.checksum_generator import generate_checksum
from app.infrastructure.document_loaders.encoding_detector import decode_content
from app.infrastructure.document_loaders.metadata_extractor import (
    extract_content_stats,
    extract_markdown_front_matter,
)
from app.infrastructure.document_loaders.mime_type_detector import detect_mime_type

logger = logging.getLogger(__name__)


class MarkdownLoader(DocumentLoaderPort):
    async def load(self, source: Path) -> Document:
        return self._load_file(source)

    async def load_many(self, sources: list[Path]) -> list[Document]:
        return [self._load_file(s) for s in sources]

    @property
    def supported_extensions(self) -> set[str]:
        return {".md"}

    def _load_file(self, path: Path) -> Document:
        raw = path.read_bytes()
        text, encoding = decode_content(raw)
        mime_type = detect_mime_type(".md")
        front_matter, body = extract_markdown_front_matter(text)
        title = front_matter.get("title", path.stem)
        checksum = generate_checksum(text)

        file_meta = extract_content_stats(body)

        md_meta_fields = {}
        if "author" in front_matter:
            md_meta_fields["author"] = front_matter["author"]
        if "language" in front_matter or "lang" in front_matter:
            md_meta_fields["language"] = front_matter.get(
                "language"
            ) or front_matter.get("lang")
        custom = {
            k: v
            for k, v in front_matter.items()
            if k not in ("title", "author", "language", "lang")
        }

        stat = os.stat(str(path))

        return Document(
            content=body,
            source_path=path.resolve(),
            filename=path.name,
            title=title,
            checksum=checksum,
            file_type=".md",
            mime_type=mime_type,
            encoding=encoding,
            created_at=(
                datetime.fromtimestamp(stat.st_birthtime)
                if hasattr(stat, "st_birthtime")
                else None
            ),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            metadata=DocumentMetadata(
                author=md_meta_fields.get("author"),
                language=md_meta_fields.get("language"),
                word_count=file_meta.word_count,
                character_count=file_meta.character_count,
                custom=custom,
            ),
        )
