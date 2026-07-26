"""
Ingestion service.

Purpose: Orchestrate the end-to-end document ingestion pipeline.
  load document → chunk → embed chunks → store embeddings → index chunks

Responsibilities:
  - Load documents from source via document loader.
  - Coordinate between chunker, embedder, vector store, and document store.
  - Provide a single entry point for adding documents to the system.

Allowed dependencies: app.domain (ports, models)
Forbidden dependencies: app.infrastructure, app.api

Future milestone: Milestone 7 — Document Ingestion.
Extends to: batch ingestion, scheduled ingestion, file watchers.
"""

import logging

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
    ) -> None:
        self._document_loader = document_loader
        self._chunker = chunker
        self._document_store = document_store
        self._embedding = embedding
        self._vector_store = vector_store
