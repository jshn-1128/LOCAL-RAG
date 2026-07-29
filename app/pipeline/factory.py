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

This is the composition root -- the only place where
infrastructure implementations are directly instantiated.
"""

from __future__ import annotations

import logging

from app.application.chat.service import ChatService
from app.application.ingestion.service import IngestionService
from app.application.prompt_builder import PromptBuilder, PromptConfig
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
from app.infrastructure.llm.ollama import OllamaLLM
from app.infrastructure.memory.sqlite import SQLiteMemory
from app.infrastructure.vectorstores.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


class RAGPipelineFactory:
    """Factory for creating fully wired application components.

    Infrastructure instances are created once and shared across services
    to avoid duplicate resource consumption (e.g., embedding models).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._embedding: SentenceTransformerEmbedding | None = None
        self._vector_store: ChromaVectorStore | None = None

    def _get_embedding(self) -> SentenceTransformerEmbedding:
        if self._embedding is None:
            self._embedding = SentenceTransformerEmbedding(
                model_name=self._settings.embedding_model,
            )
        return self._embedding

    def _get_vector_store(self) -> ChromaVectorStore:
        if self._vector_store is None:
            self._vector_store = ChromaVectorStore(
                persist_directory=str(self._settings.vector_store_dir),
                collection_name=self._settings.vector_store_collection,
            )
        return self._vector_store

    def create_ingestion_service(self) -> IngestionService:
        loaders: list = [
            TextLoader(),
            MarkdownLoader(),
            PDFLoader(),
            DocxLoader(),
        ]
        composite_loader = CompositeDocumentLoader(loaders)

        chunker: RecursiveChunker = RecursiveChunker(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
        )
        document_store: FileSystemDocumentStore = FileSystemDocumentStore(
            base_path=str(self._settings.documents_dir),
        )

        return IngestionService(
            document_loader=composite_loader,
            chunker=chunker,
            document_store=document_store,
            embedding=self._get_embedding(),
            vector_store=self._get_vector_store(),
            settings=self._settings,
        )

    def create_retrieval_service(self) -> RetrievalService:
        return RetrievalService(
            embedding=self._get_embedding(),
            vector_store=self._get_vector_store(),
            score_threshold=0.0,
        )

    def create_chat_service(
        self,
        retrieval_service: RetrievalService | None = None,
    ) -> ChatService:
        if retrieval_service is None:
            retrieval_service = self.create_retrieval_service()

        llm: OllamaLLM = OllamaLLM(
            host=self._settings.llm_host,
            model=self._settings.llm_model,
            timeout=self._settings.llm_request_timeout,
        )

        memory: SQLiteMemory = SQLiteMemory(
            db_path=str(self._settings.memory_db_path),
        )

        prompt_config = PromptConfig(
            max_tokens=self._settings.llm_max_tokens,
        )
        prompt_builder: PromptBuilder = PromptBuilder(config=prompt_config)

        return ChatService(
            retrieval_service=retrieval_service,
            llm=llm,
            memory=memory,
            prompt_builder=prompt_builder,
            app_name=self._settings.app_name,
            app_version=self._settings.app_version,
        )
