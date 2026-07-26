"""
API dependencies.

FastAPI dependency injection for accessing application services.
Services are stored in app.state during application startup.

Each dependency retrieves the service from request.app.state.
This prevents circular imports and keeps DI clean.
"""

from fastapi import Request

from app.application.chat.service import ChatService
from app.application.ingestion.service import IngestionService
from app.application.retrieval.service import RetrievalService
from app.config.settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[no-any-return]


def get_ingestion_service(request: Request) -> IngestionService:
    return request.app.state.ingestion_service  # type: ignore[no-any-return]


def get_retrieval_service(request: Request) -> RetrievalService:
    return request.app.state.retrieval_service  # type: ignore[no-any-return]


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service  # type: ignore[no-any-return]
