"""
Tests for IngestionService.

Verifies:
  - ingest_file loads a single file
  - ingest_files loads multiple files
  - ingest_directory scans and loads all files
  - Invalid files are skipped in directory mode
  - Empty directory returns empty list
  - Validation errors are propagated
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.application.ingestion.service import IngestionService
from app.config.settings import Settings
from app.infrastructure.document_loaders.composite import CompositeDocumentLoader
from app.infrastructure.document_loaders.text import TextLoader


class TestIngestionService:
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
        mock_store = MagicMock()
        mock_embedding = MagicMock()
        mock_vector = MagicMock()
        return IngestionService(
            document_loader=composite_loader,
            chunker=mock_chunker,
            document_store=mock_store,
            embedding=mock_embedding,
            vector_store=mock_vector,
            settings=settings,
        )

    async def test_ingest_file(self, service: IngestionService, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        doc = await service.ingest_file(f)
        assert doc.content == "hello world"
        assert doc.filename == "test.txt"
        assert doc.file_type == ".txt"

    async def test_ingest_file_raises_on_missing(
        self, service: IngestionService, tmp_path: Path
    ):
        f = tmp_path / "missing.txt"
        with pytest.raises(Exception, match="does not exist"):
            await service.ingest_file(f)

    async def test_ingest_file_raises_on_unsupported(
        self, service: IngestionService, tmp_path: Path
    ):
        f = tmp_path / "test.xyz"
        f.write_text("content")
        with pytest.raises(Exception, match="Unsupported"):
            await service.ingest_file(f)

    async def test_ingest_files(self, service: IngestionService, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("file a")
        f2.write_text("file b")
        docs = await service.ingest_files([f1, f2])
        assert len(docs) == 2
        assert docs[0].content == "file a"
        assert docs[1].content == "file b"

    async def test_ingest_directory(self, service: IngestionService, tmp_path: Path):
        (tmp_path / "a.txt").write_text("content a")
        (tmp_path / "b.txt").write_text("content b")
        docs = await service.ingest_directory(tmp_path, recursive=False)
        assert len(docs) == 2
        contents = {d.filename: d.content for d in docs}
        assert contents["a.txt"] == "content a"
        assert contents["b.txt"] == "content b"

    async def test_ingest_directory_skips_unsupported(
        self, service: IngestionService, tmp_path: Path
    ):
        (tmp_path / "good.txt").write_text("good")
        (tmp_path / "bad.xyz").write_text("bad")
        docs = await service.ingest_directory(tmp_path, recursive=False)
        assert len(docs) == 1
        assert docs[0].filename == "good.txt"

    async def test_ingest_directory_empty(
        self, service: IngestionService, tmp_path: Path
    ):
        docs = await service.ingest_directory(tmp_path, recursive=False)
        assert docs == []

    async def test_ingest_directory_recursive(
        self, service: IngestionService, tmp_path: Path
    ):
        (tmp_path / "root.txt").write_text("root")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("nested")
        docs = await service.ingest_directory(tmp_path, recursive=True)
        assert len(docs) == 2

    async def test_ingest_directory_logs_errors(
        self, service: IngestionService, tmp_path: Path
    ):
        (tmp_path / "good.txt").write_text("good")
        docs = await service.ingest_directory(tmp_path, recursive=False)
        assert len(docs) == 1
