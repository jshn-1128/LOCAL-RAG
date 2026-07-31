"""
Ingestion service.

Purpose: Orchestrate the end-to-end document ingestion pipeline.
  load document -> chunk -> embed chunks -> store embeddings -> index chunks

Responsibilities:
  - Validate file paths and directories.
  - Load documents from source via document loader.
  - Chunk documents into manageable pieces.
  - Generate embeddings for each chunk.
  - Store embeddings in vector store.
  - Persist documents in document store.
  - Coordinate between chunker, embedder, vector store, and document store.
  - Provide a single entry point for adding documents to the system.

Allowed dependencies: app.domain (ports, models), app.config (Settings)
Forbidden dependencies: app.infrastructure, app.api
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.application.ingestion.directory_scanner import scan_directory
from app.application.ingestion.file_validator import (
    validate_directory,
    validate_file,
)
from app.config.settings import Settings
from app.domain.models.chunk import Chunk
from app.domain.models.document import Document
from app.domain.models.result import IndexingResult
from app.domain.ports.chunker import ChunkerPort
from app.domain.ports.document_loader import DocumentLoaderPort
from app.domain.ports.document_store import DocumentStorePort
from app.domain.ports.embedding import EmbeddingPort
from app.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        document_loader: DocumentLoaderPort,
        chunker: ChunkerPort,
        document_store: DocumentStorePort,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        settings: Settings,
    ) -> None:
        self._document_loader = document_loader
        self._chunker = chunker
        self._document_store = document_store
        self._embedding = embedding
        self._vector_store = vector_store
        self._settings = settings

    async def ingest_file(self, path: Path) -> Document:
        max_bytes = self._settings.max_file_size_mb * 1024 * 1024
        validate_file(path, max_bytes)
        logger.info("Loading file: %s", path.name)
        return await self._document_loader.load(path)

    async def ingest_files(self, paths: list[Path]) -> list[Document]:
        return [await self.ingest_file(p) for p in paths]

    async def ingest_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> list[Document]:
        resolved = validate_directory(directory)
        supported = self._document_loader.supported_extensions
        file_paths = scan_directory(
            resolved, recursive=recursive, supported_extensions=supported
        )

        if not file_paths:
            logger.warning("No supported files found in directory: %s", directory)
            return []

        documents: list[Document] = []
        errors: list[tuple[Path, str]] = []

        for file_path in file_paths:
            try:
                max_bytes = self._settings.max_file_size_mb * 1024 * 1024
                validate_file(file_path, max_bytes, supported_extensions=supported)
                doc = await self._document_loader.load(file_path)
                documents.append(doc)
                logger.info("Loaded: %s (%s chars)", file_path.name, len(doc.content))
            except Exception as exc:
                logger.warning("Skipping %s: %s", file_path.name, exc)
                errors.append((file_path, str(exc)))

        if errors:
            logger.warning(
                "Directory ingestion completed with %s error(s) out of %s file(s)",
                len(errors),
                len(file_paths),
            )

        return documents

    async def _find_duplicate(
        self, doc: Document, source_path: str | None = None
    ) -> Document | None:
        if source_path is not None:
            existing = await self._document_store.find_by_source_path(source_path)
            if existing is not None and existing.checksum == doc.checksum:
                return existing
        by_checksum = await self._document_store.find_by_checksum(doc.checksum)
        return by_checksum[0] if by_checksum else None

    async def index_file(self, path: Path) -> IndexingResult:
        doc = await self.ingest_file(path)
        resolved = str(path.resolve())
        existing = await self._document_store.find_by_source_path(resolved)
        if existing is not None:
            if existing.checksum == doc.checksum:
                logger.info("Skipping unchanged file: %s", path.name)
                return IndexingResult(
                    document_id=existing.id,
                    filename=existing.filename,
                    chunk_count=0,
                    checksum=existing.checksum,
                    skipped=True,
                )
            logger.info("File changed, re-indexing: %s", path.name)
            await self.delete_document(str(existing.id))
        else:
            duplicate = await self._find_duplicate(doc)
            if duplicate is not None:
                logger.info("Skipping duplicate content: %s", path.name)
                return IndexingResult(
                    document_id=duplicate.id,
                    filename=duplicate.filename,
                    chunk_count=0,
                    checksum=duplicate.checksum,
                    skipped=True,
                )
        return await self._index_document(doc)

    async def index_files(self, paths: list[Path]) -> list[IndexingResult]:
        return [await self.index_file(p) for p in paths]

    async def index_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> list[IndexingResult]:
        docs = await self.ingest_directory(directory, recursive=recursive)
        if not docs:
            return []

        results: list[IndexingResult] = []
        errors: list[tuple[str, str]] = []

        for doc in docs:
            try:
                existing = await self._document_store.find_by_source_path(
                    str(doc.source_path.resolve())
                )
                if existing is not None:
                    if existing.checksum == doc.checksum:
                        logger.info("Skipping unchanged: %s", doc.filename)
                        results.append(
                            IndexingResult(
                                document_id=existing.id,
                                filename=existing.filename,
                                chunk_count=0,
                                checksum=existing.checksum,
                                skipped=True,
                            )
                        )
                        continue
                    logger.info("File changed, re-indexing: %s", doc.filename)
                    await self.delete_document(str(existing.id))
                else:
                    duplicate = await self._find_duplicate(doc)
                    if duplicate is not None:
                        logger.info("Skipping duplicate content: %s", doc.filename)
                        results.append(
                            IndexingResult(
                                document_id=duplicate.id,
                                filename=duplicate.filename,
                                chunk_count=0,
                                checksum=duplicate.checksum,
                                skipped=True,
                            )
                        )
                        continue
                result = await self._index_document(doc)
                results.append(result)
            except Exception as exc:
                logger.warning("Skipping index for %s: %s", doc.filename, exc)
                errors.append((doc.filename, str(exc)))

        if errors:
            logger.warning(
                "Directory indexing completed with %s error(s) out of %s document(s)",
                len(errors),
                len(docs),
            )

        return results

    async def delete_document(self, document_id: str) -> None:
        await self._vector_store.delete_by_document_id(document_id)
        await self._document_store.delete(document_id)

    async def _index_document(self, doc: Document) -> IndexingResult:
        logger.info(
            "Indexing document: %s [id=%s, size=%s chars]",
            doc.filename,
            doc.id,
            len(doc.content),
        )

        chunks = self._chunker.chunk(doc)
        for chunk in chunks:
            chunk.metadata = {
                "filename": doc.filename,
                "file_type": doc.file_type,
                "source_path": str(doc.source_path),
            }
        logger.debug("Chunked into %s chunks", len(chunks))

        chunk_texts = [c.content for c in chunks]

        if chunk_texts:
            try:
                embeddings = await self._embedding.embed_texts(chunk_texts)
            except Exception as exc:
                logger.error("Embedding failed for %s: %s", doc.filename, exc)
                embeddings = []
        else:
            embeddings = []

        logger.debug("Generated %s embeddings", len(embeddings))

        valid_chunks: list[Chunk] = []
        valid_embeddings: list[list[float]] = []
        for chunk, emb in zip(chunks, embeddings, strict=False):
            if emb and any(v != 0.0 for v in emb):
                valid_chunks.append(chunk)
                valid_embeddings.append(emb)

        if valid_chunks:
            await self._vector_store.add_chunks(valid_chunks, valid_embeddings)

        await self._document_store.save(doc)

        result = IndexingResult(
            document_id=doc.id,
            filename=doc.filename,
            chunk_count=len(valid_chunks),
            checksum=doc.checksum,
        )

        logger.info(
            "Indexed: %s [chunks=%s, vectors=%s]",
            doc.filename,
            len(chunks),
            len(valid_chunks),
        )
        return result
