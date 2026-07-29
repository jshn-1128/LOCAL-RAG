"""
Retrieval service.

Purpose: Orchestrate the retrieval pipeline.
  embed query -> search vector store -> MMR rerank -> return ranked chunks

Responsibilities:
  - Convert user query to embedding.
  - Search vector store for similar chunks.
  - Apply MMR (Maximum Marginal Relevance) for diversity.
  - Return ranked results with relevance scores.

Allowed dependencies: app.domain (ports, models)
Forbidden dependencies: app.infrastructure, app.api
"""

from __future__ import annotations

import logging
import math

from app.domain.exceptions import RetrievalError
from app.domain.models.query import Query
from app.domain.models.result import RetrievalResult
from app.domain.ports.embedding import EmbeddingPort
from app.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b, strict=False):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def _mmr_rerank(
    chunk_embeddings: list[list[float]],
    relevance_scores: list[float],
    lambda_param: float = 0.7,
) -> list[int]:
    n = len(relevance_scores)
    if n <= 1:
        return list(range(n))

    sim_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            s = _cosine_similarity(chunk_embeddings[i], chunk_embeddings[j])
            sim_matrix[i][j] = s
            sim_matrix[j][i] = s

    selected: list[int] = []
    candidates = set(range(n))

    first = max(candidates, key=lambda i: relevance_scores[i])
    selected.append(first)
    candidates.remove(first)

    while candidates:
        best_score = -1.0
        best_idx = -1
        for i in candidates:
            max_sim = max(sim_matrix[i][j] for j in selected) if selected else 0.0
            mmr = lambda_param * relevance_scores[i] - (1.0 - lambda_param) * max_sim
            if mmr > best_score:
                best_score = mmr
                best_idx = i
        selected.append(best_idx)
        candidates.remove(best_idx)

    return selected


class RetrievalService:
    def __init__(
        self,
        embedding: EmbeddingPort,
        vector_store: VectorStorePort,
        score_threshold: float = 0.0,
        mmr_lambda: float = 0.7,
        mmr_enabled: bool = True,
    ) -> None:
        self._embedding = embedding
        self._vector_store = vector_store
        self._score_threshold = score_threshold
        self._mmr_lambda = mmr_lambda
        self._mmr_enabled = mmr_enabled

    async def retrieve(self, query: Query) -> RetrievalResult:
        logger.info(
            "Retrieving for query [id=%s, top_k=%s]",
            query.id,
            query.top_k,
        )

        try:
            query_embedding = await self._embedding.embed_text(query.text)
        except Exception as exc:
            raise RetrievalError(f"Failed to generate query embedding: {exc}") from exc

        try:
            result = await self._vector_store.search(query, query_embedding)
        except Exception as exc:
            raise RetrievalError(f"Vector search failed: {exc}") from exc

        if self._score_threshold > 0.0 and result.scores:
            filtered_chunks: list = []
            filtered_scores: list[float] = []
            for chunk, score in zip(result.chunks, result.scores, strict=False):
                if score >= self._score_threshold:
                    filtered_chunks.append(chunk)
                    filtered_scores.append(score)
            result = RetrievalResult(
                query_id=result.query_id,
                chunks=filtered_chunks,
                scores=filtered_scores,
            )

        if self._mmr_enabled and len(result.chunks) > 1:
            try:
                chunk_texts = [c.content for c in result.chunks]
                chunk_embeddings = await self._embedding.embed_texts(chunk_texts)
                valid: list[tuple[int, list[float]]] = [
                    (i, emb)
                    for i, emb in enumerate(chunk_embeddings)
                    if emb and any(v != 0.0 for v in emb)
                ]
                if len(valid) > 1:
                    indices = [v[0] for v in valid]
                    valid_embeddings = [v[1] for v in valid]
                    valid_scores = [result.scores[i] for i in indices]
                    order = _mmr_rerank(
                        valid_embeddings,
                        valid_scores,
                        self._mmr_lambda,
                    )
                    ordered_indices = [indices[o] for o in order]
                    result = RetrievalResult(
                        query_id=result.query_id,
                        chunks=[result.chunks[i] for i in ordered_indices],
                        scores=[result.scores[i] for i in ordered_indices],
                    )
            except Exception as exc:
                logger.warning("MMR reranking failed, using original order: %s", exc)

        logger.info(
            "Retrieval complete [id=%s, results=%s]",
            query.id,
            len(result.chunks),
        )
        return result

    async def count_documents(self) -> int:
        return await self._vector_store.count()
