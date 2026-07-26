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

from app.application.chat.service import ChatService
from app.application.ingestion.service import IngestionService
from app.application.retrieval.service import RetrievalService
from app.config.settings import Settings


class RAGPipelineFactory:
    """Factory for creating fully wired application components."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_ingestion_service(self) -> IngestionService:
        raise NotImplementedError("Will be implemented in Milestone 7")

    def create_retrieval_service(self) -> RetrievalService:
        raise NotImplementedError("Will be implemented in Milestone 11")

    def create_chat_service(self) -> ChatService:
        raise NotImplementedError("Will be implemented in Milestone 12")
