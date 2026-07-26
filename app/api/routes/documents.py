"""
Document management routes.

Purpose: CRUD operations for documents.
Endpoints:
  POST   /documents/upload   — Upload and ingest a document.
  GET    /documents/         — List all documents.
  GET    /documents/{id}     — Get document details.
  DELETE /documents/{id}     — Delete a document and its chunks.

Milestone: Document Ingestion (Milestone 7).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])
