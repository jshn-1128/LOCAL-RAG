"""
Application factory.

FastAPI application creation, configuration, and lifespan management.
This is the root entry point for running the application server.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import chat, documents, health, search
from app.config import setup_logging
from app.config.settings import Settings
from app.pipeline.factory import RAGPipelineFactory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    setup_logging(settings)

    factory = RAGPipelineFactory(settings)
    app.state.settings = settings
    app.state.ingestion_service = factory.create_ingestion_service()
    app.state.retrieval_service = factory.create_retrieval_service()
    app.state.chat_service = factory.create_chat_service()

    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Local RAG",
        description="Production-grade Local Retrieval-Augmented Generation System",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.include_router(health.router)
    application.include_router(documents.router)
    application.include_router(search.router)
    application.include_router(chat.router)

    from app.api.middleware import register_middleware

    register_middleware(application)

    return application


app = create_app()
