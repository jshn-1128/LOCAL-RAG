"""
Filesystem document store adapter.

Purpose: Store and retrieve documents from the local filesystem.
Implements: DocumentStorePort
Dependencies: stdlib (pathlib, json)

Documents are stored as JSON files with metadata.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from uuid import UUID

from app.domain.models.document import Document, DocumentMetadata
from app.domain.ports.document_store import DocumentStorePort

logger = logging.getLogger(__name__)


class FileSystemDocumentStore(DocumentStorePort):
    def __init__(self, base_path: str = "data/documents") -> None:
        self._base_path = Path(base_path)

    async def save(self, document: Document) -> None:
        self._base_path.mkdir(parents=True, exist_ok=True)
        doc_file = self._base_path / f"{document.id}.json"

        data = {
            "id": str(document.id),
            "content": document.content,
            "source_path": str(document.source_path),
            "filename": document.filename,
            "title": document.title,
            "checksum": document.checksum,
            "file_type": document.file_type,
            "mime_type": document.mime_type,
            "encoding": document.encoding,
            "created_at": (
                document.created_at.isoformat() if document.created_at else None
            ),
            "modified_at": (
                document.modified_at.isoformat() if document.modified_at else None
            ),
            "loaded_at": document.loaded_at.isoformat(),
            "metadata": {
                "author": document.metadata.author,
                "language": document.metadata.language,
                "page_count": document.metadata.page_count,
                "word_count": document.metadata.word_count,
                "character_count": document.metadata.character_count,
                "tags": document.metadata.tags,
                "custom": document.metadata.custom,
            },
        }

        doc_file.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        logger.debug("Saved document: %s (%s)", document.id, document.filename)

    async def get(self, document_id: str) -> Document | None:
        doc_file = self._base_path / f"{document_id}.json"
        if not doc_file.exists():
            return None
        return self._load_document(doc_file)

    async def delete(self, document_id: str) -> None:
        doc_file = self._base_path / f"{document_id}.json"
        if doc_file.exists():
            doc_file.unlink()
            logger.debug("Deleted document: %s", document_id)

    async def find_by_source_path(self, source_path: str) -> Document | None:
        all_docs = await self.list_documents()
        for doc in all_docs:
            if str(doc.source_path) == source_path:
                return doc
        return None

    async def find_by_checksum(self, checksum: str) -> list[Document]:
        all_docs = await self.list_documents()
        return [doc for doc in all_docs if doc.checksum == checksum]

    async def list_documents(self) -> list[Document]:
        if not self._base_path.exists():
            return []
        documents: list[Document] = []
        for doc_file in sorted(self._base_path.glob("*.json")):
            try:
                doc = self._load_document(doc_file)
                documents.append(doc)
            except Exception as exc:
                logger.warning("Failed to load document %s: %s", doc_file.name, exc)
        return documents

    def _load_document(self, path: Path) -> Document:
        data = json.loads(path.read_text(encoding="utf-8"))
        meta = data.get("metadata", {})

        return Document(
            id=UUID(data["id"]),
            content=data["content"],
            source_path=Path(data["source_path"]),
            filename=data["filename"],
            title=data["title"],
            checksum=data["checksum"],
            file_type=data["file_type"],
            mime_type=data["mime_type"],
            encoding=data["encoding"],
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            modified_at=(
                datetime.fromisoformat(data["modified_at"])
                if data.get("modified_at")
                else None
            ),
            loaded_at=datetime.fromisoformat(data["loaded_at"]),
            metadata=DocumentMetadata(
                author=meta.get("author"),
                language=meta.get("language"),
                page_count=meta.get("page_count"),
                word_count=meta.get("word_count", 0),
                character_count=meta.get("character_count", 0),
                tags=meta.get("tags", []),
                custom=meta.get("custom", {}),
            ),
        )
