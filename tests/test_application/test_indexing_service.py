"""
Tests for IngestionService indexing pipeline.

Verifies:
  - index_file loads, chunks, embeds, and stores a document
  - index_directory indexes all supported files in a directory
  - Returns IndexingResult with correct metadata
  - Handles empty directories gracefully
  - Embedding failures are handled gracefully
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.ingestion.service import IngestionService
from app.config.settings import Settings
from app.infrastructure.document_loaders.composite import CompositeDocumentLoader
from app.infrastructure.document_loaders.text import TextLoader


class TestIndexingService:
    @pytest.fixture
    def text_loader(self) -> TextLoader:
        return TextLoader()

    @pytest.fixture
    def composite_loader(self, text_loader: TextLoader) -> CompositeDocumentLoader:
        return CompositeDocumentLoader([text_loader])

    @pytest.fixture
    def settings(self) -> Settings:
        return Settings()

    @pytest.fixture
    def service(
        self, composite_loader: CompositeDocumentLoader, settings: Settings
    ) -> IngestionService:
        mock_chunker = MagicMock()
        mock_chunker.chunk = MagicMock(return_value=[])  # will be overridden per test
        mock_store = MagicMock()
        mock_store.save = AsyncMock()
        mock_store.delete = AsyncMock()
        mock_store.find_by_source_path = AsyncMock(return_value=None)
        mock_embedding = MagicMock()
        mock_embedding.embed_texts = AsyncMock(return_value=[])
        mock_vector = MagicMock()
        mock_vector.add_chunks = AsyncMock()
        mock_vector.delete_by_document_id = AsyncMock()

        return IngestionService(
            document_loader=composite_loader,
            chunker=mock_chunker,
            document_store=mock_store,
            embedding=mock_embedding,
            vector_store=mock_vector,
            settings=settings,
        )

    async def test_index_file_full_pipeline(
        self, service: IngestionService, tmp_path: Path
    ):
        from uuid import uuid4

        from app.domain.models.chunk import Chunk

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world. This is a test document.")

        doc_id = uuid4()
        chunks = [
            Chunk(document_id=doc_id, content="Hello world.", index=0),
            Chunk(document_id=doc_id, content="This is a test document.", index=1),
        ]
        service._chunker.chunk = MagicMock(return_value=chunks)
        service._embedding.embed_texts = AsyncMock(
            return_value=[[0.1, 0.2], [0.3, 0.4]]
        )

        result = await service.index_file(test_file)

        assert result.filename == "test.txt"
        assert result.chunk_count == 2
        assert len(result.checksum) == 64

        service._vector_store.add_chunks.assert_awaited_once()
        service._document_store.save.assert_awaited_once()

    async def test_index_directory(self, service: IngestionService, tmp_path: Path):
        (tmp_path / "a.txt").write_text("Content A")
        (tmp_path / "b.txt").write_text("Content B")

        from app.domain.models.chunk import Chunk

        def chunk_fn(document):
            return [Chunk(document_id=document.id, content=document.content, index=0)]

        service._chunker.chunk = MagicMock(side_effect=chunk_fn)
        service._embedding.embed_texts = AsyncMock(return_value=[[0.1, 0.2]])

        results = await service.index_directory(tmp_path, recursive=False)

        assert len(results) == 2
        assert results[0].chunk_count == 1
        assert results[1].chunk_count == 1

    async def test_index_empty_directory(
        self, service: IngestionService, tmp_path: Path
    ):
        results = await service.index_directory(tmp_path, recursive=False)
        assert results == []

    async def test_index_handles_embedding_failure(
        self, service: IngestionService, tmp_path: Path
    ):
        from app.domain.models.chunk import Chunk

        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world.")

        doc_id = (
            service._document_loader._extension_map[".txt"]._load_file(test_file).id
        )
        service._chunker.chunk = MagicMock(
            return_value=[Chunk(document_id=doc_id, content="Hello world.", index=0)]
        )
        service._embedding.embed_texts = AsyncMock(
            side_effect=RuntimeError("Model failed")
        )

        result = await service.index_file(test_file)

        assert result.chunk_count == 0
        service._vector_store.add_chunks.assert_not_awaited()
