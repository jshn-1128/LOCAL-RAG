"""
API dependencies.

FastAPI dependency injection for accessing application services.
Services are stored in app.state during application startup.

Each dependency retrieves the service from request.app.state.
This prevents circular imports and keeps DI clean.

Unimplemented services raise ServiceNotAvailableError with a
structured 503 response rather than exposing AttributeError.
"""

from fastapi import Request

from app.application.chat.service import ChatService
from app.application.ingestion.service import IngestionService
from app.application.retrieval.service import RetrievalService
from app.config.settings import Settings
from app.domain.exceptions import ServiceNotAvailableError


def get_settings(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[no-any-return]


def get_ingestion_service(request: Request) -> IngestionService:
    service: IngestionService | None = request.app.state.ingestion_service
    if service is None:
        raise ServiceNotAvailableError("ingestion_service")
    return service


def get_retrieval_service(request: Request) -> RetrievalService:
    service: RetrievalService | None = request.app.state.retrieval_service
    if service is None:
        raise ServiceNotAvailableError("retrieval_service")
    return service


def get_chat_service(request: Request) -> ChatService:
    service: ChatService | None = request.app.state.chat_service
    if service is None:
        raise ServiceNotAvailableError("chat_service")
    return service
