"""
Application factory.

FastAPI application creation, configuration, and lifespan management.
This module does not create any application instance at import time.
Use create_app() to build an instance, or import from app.main for uvicorn.

Startup sequence:
  1. Settings loaded (Settings() -- in create_app or passed in)
  2. Middleware configured with settings (create_app)
  3. Logging initialized (lifespan)
  4. Pipeline factory created (lifespan)
  5. Service slots initialized in app.state (lifespan)
  6. Startup timestamp recorded (lifespan)

Shutdown sequence:
  1. Log shutdown
  2. Resources released
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.middleware import register_middleware
from app.api.routes import chat, documents, health, search
from app.config import Settings, setup_logging
from app.pipeline.factory import RAGPipelineFactory

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    startup_time = time.perf_counter()

    settings: Settings = app.state.settings

    # 1. Initialize logging
    setup_logging(settings)
    logger.info("Application starting... [environment=%s]", settings.environment)

    # 2. Build dependency graph
    factory = RAGPipelineFactory(settings)
    app.state.pipeline_factory = factory
    logger.info("Pipeline factory created")

    # 3. Initialize application services
    app.state.ingestion_service = factory.create_ingestion_service()
    logger.info("Ingestion service initialized")

    retrieval_service = factory.create_retrieval_service()
    app.state.retrieval_service = retrieval_service
    logger.info("Retrieval service initialized")

    app.state.chat_service = factory.create_chat_service(
        retrieval_service=retrieval_service,
    )
    logger.info("Chat service initialized")

    # 4. Store startup timestamp
    app.state.startup_timestamp = time.time()
    logger.info("Application state initialized")

    duration_ms = (time.perf_counter() - startup_time) * 1000
    logger.info("Application started [duration=%.1fms]", duration_ms)

    yield

    # -- Shutdown -------------------------------------------------
    shutdown_time = time.perf_counter()
    logger.info("Application shutting down...")
    logger.info(
        "Application stopped [duration=%.1fms]",
        (time.perf_counter() - shutdown_time) * 1000,
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    Args:
        settings: Optional Settings instance. If not provided, Settings()
                 is loaded from environment. Passing settings explicitly
                 allows test injection and production hardening.

    Returns:
        Fully configured FastAPI application (lifespan not yet started).
    """
    if settings is None:
        settings = Settings()

    application = FastAPI(
        title="Local RAG",
        description="Production-grade Local Retrieval-Augmented Generation System",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Pre-register settings so lifespan and middleware can access it
    application.state.settings = settings

    register_middleware(application, settings)

    application.include_router(health.router)
    application.include_router(documents.router)
    application.include_router(search.router)
    application.include_router(chat.router)

    register_error_handlers(application)

    return application
