"""
Tests for RetrievalService.

Verifies:
  - Retrieves chunks for a query using mocked embedding and vector store
  - Returns empty result when no chunks match
  - Score threshold filters low-scoring results
  - Propagates embedding errors
  - Propagates vector store errors
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.retrieval.service import RetrievalService
from app.domain.exceptions import RetrievalError
from app.domain.models.chunk import Chunk
from app.domain.models.query import Query
from app.domain.models.result import RetrievalResult
from app.domain.ports.embedding import EmbeddingPort
from app.domain.ports.vector_store import VectorStorePort


class TestRetrievalService:
    @pytest.fixture
    def embedding(self) -> MagicMock:
        mock = MagicMock(spec=EmbeddingPort)
        mock.embed_text = AsyncMock(return_value=[0.1, 0.2, 0.3])
        return mock

    @pytest.fixture
    def vector_store(self) -> MagicMock:
        mock = MagicMock(spec=VectorStorePort)
        chunk1 = Chunk(document_id="doc1", content="Result 1", index=0)
        chunk2 = Chunk(document_id="doc1", content="Result 2", index=1)
        mock.search = AsyncMock(
            return_value=RetrievalResult(
                query_id="q1",
                chunks=[chunk1, chunk2],
                scores=[0.95, 0.85],
            )
        )
        return mock

    @pytest.fixture
    def service(
        self, embedding: MagicMock, vector_store: MagicMock
    ) -> RetrievalService:
        return RetrievalService(
            embedding=embedding,
            vector_store=vector_store,
            score_threshold=0.0,
        )

    async def test_retrieve_returns_chunks(self, service: RetrievalService):
        query = Query(text="test query", top_k=4)
        result = await service.retrieve(query)
        assert len(result.chunks) == 2
        assert result.chunks[0].content == "Result 1"
        assert result.chunks[1].content == "Result 2"

    async def test_retrieve_empty_result(self, service: RetrievalService):
        service._vector_store.search = AsyncMock(
            return_value=RetrievalResult(query_id="q1", chunks=[], scores=[])
        )
        query = Query(text="empty query")
        result = await service.retrieve(query)
        assert len(result.chunks) == 0

    async def test_score_threshold_filters_low_scores(self):
        embedding = MagicMock(spec=EmbeddingPort)
        embedding.embed_text = AsyncMock(return_value=[0.1, 0.2, 0.3])
        vector_store = MagicMock(spec=VectorStorePort)
        chunk1 = Chunk(document_id="doc1", content="High score", index=0)
        chunk2 = Chunk(document_id="doc1", content="Low score", index=1)
        vector_store.search = AsyncMock(
            return_value=RetrievalResult(
                query_id="q1",
                chunks=[chunk1, chunk2],
                scores=[0.95, 0.3],
            )
        )
        service = RetrievalService(
            embedding=embedding,
            vector_store=vector_store,
            score_threshold=0.5,
        )
        result = await service.retrieve(Query(text="test"))
        assert len(result.chunks) == 1
        assert result.chunks[0].content == "High score"

    async def test_retrieve_propagates_embedding_error(self, service: RetrievalService):
        service._embedding.embed_text = AsyncMock(
            side_effect=RuntimeError("Model failed")
        )
        with pytest.raises(RetrievalError, match="Failed to generate"):
            await service.retrieve(Query(text="test"))

    async def test_retrieve_propagates_vector_store_error(
        self, service: RetrievalService
    ):
        service._vector_store.search = AsyncMock(
            side_effect=RuntimeError("Chroma unavailable")
        )
        with pytest.raises(RetrievalError, match="Vector search failed"):
            await service.retrieve(Query(text="test"))


class TestMmr:
    @pytest.fixture
    def embedding(self) -> MagicMock:
        mock = MagicMock(spec=EmbeddingPort)
        mock.embed_text = AsyncMock(return_value=[1.0, 0.0, 0.0])
        return mock

    @pytest.fixture
    def vector_store(self) -> MagicMock:
        mock = MagicMock(spec=VectorStorePort)
        chunk_a = Chunk(document_id="doc1", content="A", index=0)
        chunk_b = Chunk(document_id="doc1", content="B", index=1)
        chunk_c = Chunk(document_id="doc2", content="C", index=0)
        mock.search = AsyncMock(
            return_value=RetrievalResult(
                query_id="q1",
                chunks=[chunk_a, chunk_b, chunk_c],
                scores=[0.9, 0.85, 0.8],
            )
        )
        return mock

    @pytest.fixture
    def service(
        self, embedding: MagicMock, vector_store: MagicMock
    ) -> RetrievalService:
        return RetrievalService(
            embedding=embedding,
            vector_store=vector_store,
            mmr_enabled=True,
            mmr_lambda=0.7,
        )

    async def test_mmr_differentiates_redundant_chunks(self, service: RetrievalService):
        service._embedding.embed_texts = AsyncMock(
            return_value=[
                [1.0, 0.0, 0.0],
                [0.99, 0.01, 0.0],
                [0.0, 1.0, 0.0],
            ]
        )
        result = await service.retrieve(Query(text="test", top_k=5))
        assert len(result.chunks) == 3
        assert result.chunks[0].content == "A"

    async def test_mmr_with_single_chunk_returns_unchanged(
        self, service: RetrievalService
    ):
        service._vector_store.search = AsyncMock(
            return_value=RetrievalResult(
                query_id="q1",
                chunks=[Chunk(document_id="doc1", content="Only result", index=0)],
                scores=[0.9],
            )
        )
        result = await service.retrieve(Query(text="test"))
        assert len(result.chunks) == 1
        assert result.chunks[0].content == "Only result"

    async def test_mmr_disabled_returns_original_order(
        self, embedding: MagicMock, vector_store: MagicMock
    ):
        svc = RetrievalService(
            embedding=embedding,
            vector_store=vector_store,
            mmr_enabled=False,
        )
        result = await svc.retrieve(Query(text="test"))
        assert len(result.chunks) == 3
        assert result.chunks[0].content == "A"
        assert result.chunks[1].content == "B"
        assert result.chunks[2].content == "C"

    async def test_cosine_similarity_identical_vectors(self):
        from app.application.retrieval.service import _cosine_similarity

        v = [1.0, 2.0, 3.0]
        assert _cosine_similarity(v, v) == pytest.approx(1.0)

    async def test_cosine_similarity_orthogonal_vectors(self):
        from app.application.retrieval.service import _cosine_similarity

        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    async def test_cosine_similarity_zero_vector(self):
        from app.application.retrieval.service import _cosine_similarity

        assert _cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0
