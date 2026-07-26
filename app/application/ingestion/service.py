"""
Ingestion service.

Purpose: Orchestrate the end-to-end document ingestion pipeline.
  load document → chunk → embed chunks → store embeddings → index chunks

Current milestone (Milestone 7): Document loading only.
Future milestones will add chunking, embedding, and storage.

Responsibilities:
  - Validate file paths and directories.
  - Load documents from source via document loader.
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
from app.domain.models.document import Document
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
        """Load a single document file.

        Validates the file, loads via the document loader, and returns
        a domain Document.  Future milestones will chain chunking,
        embedding, and storage.

        Args:
            path: Path to the file to load.

        Returns:
            The loaded Document.
        """
        max_bytes = self._settings.max_file_size_mb * 1024 * 1024
        validate_file(path, max_bytes)
        logger.info("Loading file: %s", path.name)
        return await self._document_loader.load(path)

    async def ingest_files(self, paths: list[Path]) -> list[Document]:
        """Load multiple document files in order.

        Each file is independently validated and loaded.
        Failures raise immediately (fail-fast for explicit lists).

        Args:
            paths: List of file paths to load.

        Returns:
            List of loaded Documents in input order.
        """
        return [await self.ingest_file(p) for p in paths]

    async def ingest_directory(
        self,
        directory: Path,
        recursive: bool = True,
    ) -> list[Document]:
        """Load all supported documents from a directory.

        Scans the directory for supported files, validates each one,
        and loads them.  Invalid files are logged and skipped — the
        batch continues.

        Args:
            directory: Path to the directory to scan.
            recursive: Whether to scan subdirectories.

        Returns:
            List of successfully loaded Documents.
        """
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
