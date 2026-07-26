"""
API middleware.

Cross-cutting concerns applied to all HTTP requests.
Middleware stack (outermost to innermost):
  1. RequestLoggingMiddleware  — log all requests with request_id and timing
  2. RequestTimingMiddleware   — add X-Process-Time response header
  3. RequestIDMiddleware       — unique X-Request-ID per request
  4. CORSMiddleware            — cross-origin resource sharing
  5. TrustedHostMiddleware     — validate Host header
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import Response

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self._header_name = header_name

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self._header_name] = request_id
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Process-Time") -> None:
        super().__init__(app)
        self._header_name = header_name

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        request.state.process_time = duration_ms
        response.headers[self._header_name] = f"{duration_ms:.1f}ms"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        request_id = getattr(request.state, "request_id", "unknown")
        process_time = getattr(request.state, "process_time", None)
        if process_time is not None:
            logger.info(
                "%s %s -> %s [request_id=%s, duration=%.1fms]",
                request.method,
                request.url.path,
                response.status_code,
                request_id,
                process_time,
            )
        else:
            logger.info(
                "%s %s -> %s [request_id=%s]",
                request.method,
                request.url.path,
                response.status_code,
                request_id,
            )
        return response


def register_middleware(app: FastAPI, settings: Settings | None = None) -> None:
    """Register all middleware on the FastAPI application.

    Middleware is applied outermost-first. The last registered middleware
    becomes the outermost wrapper (first to receive requests, last to send responses).

    Order (outermost → innermost):
        RequestLoggingMiddleware
        RequestTimingMiddleware
        RequestIDMiddleware
        CORSMiddleware
        TrustedHostMiddleware (innermost)

    If settings are provided, the middleware is configured using those settings.
    Otherwise, permissive development defaults are used.
    """
    if settings is not None:
        allowed_hosts = settings.allowed_hosts
        cors_origins = settings.cors_origins
        cors_credentials = settings.cors_allow_credentials
        cors_methods = settings.cors_methods
        cors_headers = settings.cors_headers
        cors_max_age = settings.cors_max_age
        req_id_header = settings.request_id_header
        timing_header = settings.process_time_header
    else:
        allowed_hosts = ["*"]
        cors_origins = ["*"]
        cors_credentials = True
        cors_methods = ["*"]
        cors_headers = ["*"]
        cors_max_age = 600
        req_id_header = "X-Request-ID"
        timing_header = "X-Process-Time"

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=cors_credentials,
        allow_methods=cors_methods,
        allow_headers=cors_headers,
        max_age=cors_max_age,
    )
    app.add_middleware(RequestIDMiddleware, header_name=req_id_header)
    app.add_middleware(RequestTimingMiddleware, header_name=timing_header)
    app.add_middleware(RequestLoggingMiddleware)
