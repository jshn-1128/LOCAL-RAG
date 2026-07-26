"""
PDF file loader (.pdf).

Handles PDF files using pypdf for text extraction, metadata,
and page count.  Handles encrypted and corrupted PDFs gracefully.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader

from app.domain.exceptions import CorruptedDocumentError
from app.domain.models.document import Document, DocumentMetadata
from app.domain.ports.document_loader import DocumentLoaderPort
from app.infrastructure.document_loaders.checksum_generator import generate_checksum
from app.infrastructure.document_loaders.metadata_extractor import (
    extract_content_stats,
    extract_pdf_metadata,
)
from app.infrastructure.document_loaders.mime_type_detector import detect_mime_type

logger = logging.getLogger(__name__)


class PDFLoader(DocumentLoaderPort):
    async def load(self, source: Path) -> Document:
        return self._load_file(source)

    async def load_many(self, sources: list[Path]) -> list[Document]:
        return [self._load_file(s) for s in sources]

    @property
    def supported_extensions(self) -> set[str]:
        return {".pdf"}

    def _load_file(self, path: Path) -> Document:
        mime_type = detect_mime_type(".pdf")

        try:
            reader = PdfReader(path)
        except Exception as exc:
            raise CorruptedDocumentError(f"Failed to read PDF: {path}. {exc}") from exc

        if reader.is_encrypted:
            raise CorruptedDocumentError(f"PDF is encrypted and cannot be read: {path}")

        pages_text: list[str] = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                pages_text.append(page_text)
            except Exception as page_exc:
                logger.warning(
                    "Failed to extract text from page %s of %s: %s",
                    i,
                    path.name,
                    page_exc,
                )
                pages_text.append("")

        text = "\n\n".join(pages_text)
        checksum = generate_checksum(text)
        file_meta = extract_content_stats(text)

        pdf_meta = extract_pdf_metadata(reader.metadata)
        author = pdf_meta.get("author")
        title = pdf_meta.get("title") or path.stem

        stat = os.stat(str(path))

        return Document(
            content=text,
            source_path=path.resolve(),
            filename=path.name,
            title=title,
            checksum=checksum,
            file_type=".pdf",
            mime_type=mime_type,
            encoding="utf-8",
            created_at=(
                datetime.fromtimestamp(stat.st_birthtime)
                if hasattr(stat, "st_birthtime")
                else None
            ),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            metadata=DocumentMetadata(
                author=author,
                page_count=len(reader.pages),
                word_count=file_meta.word_count,
                character_count=file_meta.character_count,
                custom=pdf_meta,
            ),
        )
