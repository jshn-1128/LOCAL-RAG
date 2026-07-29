"""
Sentence Transformers embedding adapter.

Purpose: Generate embeddings using local Sentence Transformers models.
Implements: EmbeddingPort
Dependencies: sentence-transformers, torch

Runs entirely on-device. Supports Apple Silicon MPS acceleration.
"""

from __future__ import annotations

import logging
from typing import Any

from app.domain.ports.embedding import EmbeddingPort

logger = logging.getLogger(__name__)

_MODEL_DIMENSIONS: dict[str, int] = {
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "nomic-embed-text": 768,
    "snowflake-arctic-embed-l": 1024,
}


class SentenceTransformerEmbedding(EmbeddingPort):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: Any = None

    async def embed_text(self, text: str) -> list[float]:
        model = self._get_model()
        result = model.encode(text, normalize_embeddings=True)
        return result.tolist()  # type: ignore[no-any-return]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._get_model()
        encoded = model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return [emb.tolist() for emb in encoded]

    @property
    def dimensions(self) -> int:
        if self._model is not None:
            return self._model.get_sentence_embedding_dimension()  # type: ignore[no-any-return]
        return _MODEL_DIMENSIONS.get(self._model_name, 384)

    def _get_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading SentenceTransformer model: %s", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            logger.info(
                "Model loaded: %s (dim=%s)",
                self._model_name,
                self._model.get_sentence_embedding_dimension(),
            )
        return self._model
