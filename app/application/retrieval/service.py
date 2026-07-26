"""
Retrieval service.

Purpose: Orchestrate the retrieval pipeline.
  embed query → search vector store → return ranked chunks

Responsibilities:
  - Convert user query to embedding.
  - Search vector store for similar chunks.
  - Return ranked results with relevance scores.

Allowed dependencies: app.domain (ports, models)
Forbidden dependencies: app.infrastructure, app.api

Future milestone: Milestone 11 — Retrieval Pipeline.
Extends to: hybrid search, reranking, filtering.
"""

import logging

from app.domain.ports.embedding import EmbeddingPort
from app.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(
        self,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
    ) -> None:
        self._embedding = embedding
        self._vector_store = vector_store
