"""
Health check routes.

Purpose: Provide liveness and readiness probes.
Endpoints:
  GET /health              — Basic liveness check.
  GET /health/ready        — Readiness check (dependencies available).

Milestone: FastAPI implementation (Milestone 16+).
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])
