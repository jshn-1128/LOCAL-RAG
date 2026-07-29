"""
Centralized exception handlers.

All error responses follow a consistent JSON structure:
{
    "detail": ...,
    "request_id": "..."
}

Current handlers:
  - RequestValidationError -> 422 with validation details
  - HTTPException -> status_code with detail
  - DomainError -> 400/404/413/503 based on error type
  - Exception -> 500 with generic message (no trace leakage)
  - ServiceNotAvailableError -> 503 with service name and metadata
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.domain.exceptions import (
    DocumentNotFoundError,
    DocumentTooLargeError,
    DomainError,
    EmbeddingError,
    LLMError,
    RetrievalError,
    ServiceNotAvailableError,
    UnreadableDocumentError,
    UnsupportedDocumentError,
)

logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str:
    return str(getattr(request.state, "request_id", "unknown"))


def _error_response(status_code: int, detail: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "request_id": request_id,
            "timestamp": time.time(),
        },
    )


async def _validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning(
        "Validation error [request_id=%s, errors=%s]",
        request_id,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "request_id": request_id,
        },
    )


async def _http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.info(
        "HTTP %s [request_id=%s, path=%s]",
        exc.status_code,
        request_id,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id,
        },
    )


async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    request_id = _get_request_id(request)
    status_code: int

    if isinstance(exc, DocumentNotFoundError):
        status_code = 404
    elif isinstance(exc, (UnsupportedDocumentError, UnreadableDocumentError)):
        status_code = 400
    elif isinstance(exc, DocumentTooLargeError):
        status_code = 413
    elif isinstance(exc, (EmbeddingError, RetrievalError, LLMError)):
        status_code = 503
    else:
        status_code = 400

    logger.warning(
        "Domain error [request_id=%s, type=%s, detail=%s]",
        request_id,
        type(exc).__name__,
        str(exc),
    )
    return _error_response(status_code, str(exc), request_id)


async def _service_not_available_handler(
    request: Request, exc: ServiceNotAvailableError
) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning(
        "Service unavailable [request_id=%s, service=%s]",
        request_id,
        exc.service_name,
    )
    return JSONResponse(
        status_code=503,
        content={
            "error_code": "SERVICE_UNAVAILABLE",
            "message": str(exc),
            "service": exc.service_name,
            "request_id": request_id,
            "timestamp": time.time(),
            "status": 503,
        },
    )


async def _unhandled_exception_handler(
    request: Request, _exc: Exception
) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.exception("Unhandled exception [request_id=%s]", request_id)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(DomainError, _domain_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ServiceNotAvailableError, _service_not_available_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_exception_handler)
