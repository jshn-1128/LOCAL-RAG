"""
Health check routes.

Purpose: Provide liveness and readiness probes for SRE and orchestration.
Endpoints:
  GET /health           — Liveness check (server is alive, returns metadata)
  GET /health/ready     — Readiness check (dependencies ready)

Future extension points (no implementation yet):
  - LLM health check
  - Vector store health check
  - Embedding service health check
  - Memory health check
  - Disk usage check
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(request: Request) -> dict:
    settings = request.app.state.settings
    startup_timestamp = request.app.state.startup_timestamp
    uptime_seconds = time.time() - startup_timestamp

    return {
        "status": "healthy",
        "version": request.app.version,
        "environment": settings.environment,
        "timestamp": time.time(),
        "uptime_seconds": round(uptime_seconds, 2),
        "app_name": settings.app_name,
    }


@router.get("/health/ready")
async def readiness_check(_request: Request) -> dict:
    return {
        "status": "ready",
        "timestamp": time.time(),
    }
