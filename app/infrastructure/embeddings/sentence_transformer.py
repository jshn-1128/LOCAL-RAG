"""
Sentence Transformers embedding adapter.

Purpose: Generate embeddings using local Sentence Transformers models.
Implements: EmbeddingPort
Dependencies: sentence-transformers, torch

Runs entirely on-device. Supports Apple Silicon MPS acceleration.
Future milestone: Milestone 8 — Embeddings.
"""

from app.domain.ports.embedding import EmbeddingPort


class SentenceTransformerEmbedding(EmbeddingPort):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model = None

    @property
    def dimensions(self) -> int:
        return 384  # all-MiniLM-L6-v2 output dimension
