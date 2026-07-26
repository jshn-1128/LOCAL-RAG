"""
Search routes.

Purpose: Standalone retrieval endpoint without generation.
Endpoints:
  POST /search/    — Retrieve relevant chunks for a query.

Milestone: Retrieval Pipeline (Milestone 11).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/search", tags=["search"])
