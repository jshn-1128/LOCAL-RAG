"""
RAG pipeline factory.

Purpose: Assembly point for dependency injection.
Creates, configures, and wires all application components.

Responsibilities:
  - Read configuration.
  - Instantiate infrastructure adapters.
  - Wrap adapters in domain ports.
  - Create application services with injected dependencies.
  - Expose ready-to-use services.

This is the composition root — the only place where
infrastructure implementations are directly instantiated.
"""

from __future__ import annotations

import logging

from app.application.chat.service import ChatService
from app.application.ingestion.service import IngestionService
from app.application.retrieval.service import RetrievalService
from app.config.settings import Settings
from app.infrastructure.chunking.recursive import RecursiveChunker
from app.infrastructure.document_loaders.composite import CompositeDocumentLoader
from app.infrastructure.document_loaders.docx import DocxLoader
from app.infrastructure.document_loaders.markdown import MarkdownLoader
from app.infrastructure.document_loaders.pdf import PDFLoader
from app.infrastructure.document_loaders.text import TextLoader
from app.infrastructure.document_stores.filesystem import FileSystemDocumentStore
from app.infrastructure.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from app.infrastructure.vectorstores.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


class RAGPipelineFactory:
    """Factory for creating fully wired application components."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_ingestion_service(self) -> IngestionService:
        loaders: list = [
            TextLoader(),
            MarkdownLoader(),
            PDFLoader(),
            DocxLoader(),
        ]
        composite_loader = CompositeDocumentLoader(loaders)

        chunker: RecursiveChunker = RecursiveChunker(  # type: ignore[abstract]
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )
        document_store: FileSystemDocumentStore = FileSystemDocumentStore(  # type: ignore[abstract]
            base_path=str(self._settings.documents_dir),
        )
        embedding: SentenceTransformerEmbedding = SentenceTransformerEmbedding(  # type: ignore[abstract]
            model_name=self._settings.embedding_model,
        )
        vector_store: ChromaVectorStore = ChromaVectorStore(  # type: ignore[abstract]
            persist_directory=str(self._settings.vector_store_dir),
        )

        return IngestionService(
            document_loader=composite_loader,
            chunker=chunker,
            document_store=document_store,
            embedding=embedding,
            vector_store=vector_store,
            settings=self._settings,
        )

    def create_retrieval_service(self) -> RetrievalService:
        raise NotImplementedError("Will be implemented in Milestone 11")

    def create_chat_service(self) -> ChatService:
        raise NotImplementedError("Will be implemented in Milestone 12")
