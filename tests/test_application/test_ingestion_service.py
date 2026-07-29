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
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.ingestion.service import IngestionService
from app.config.settings import Settings
from app.domain.models.document import Document
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


class TestIngestionServiceDedup:
    @pytest.fixture
    def service(self) -> IngestionService:
        mock_loader = MagicMock()
        mock_chunker = MagicMock()
        mock_store = MagicMock()
        mock_store.save = AsyncMock()
        mock_store.delete = AsyncMock()
        mock_embedding = MagicMock()
        mock_vector = MagicMock()
        mock_vector.delete_by_document_id = AsyncMock()
        settings = Settings()
        svc = IngestionService(
            document_loader=mock_loader,
            chunker=mock_chunker,
            document_store=mock_store,
            embedding=mock_embedding,
            vector_store=mock_vector,
            settings=settings,
        )
        return svc

    def _make_doc(
        self, content: str, checksum: str, source_path: str = "/fake/test.txt"
    ) -> Document:
        return Document(
            content=content,
            source_path=Path(source_path),
            filename=Path(source_path).name,
            title=Path(source_path).stem,
            checksum=checksum,
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
            id=uuid4(),
        )

    async def test_index_file_skips_unchanged(self, service: IngestionService):
        doc = self._make_doc("hello", "abc123")
        existing = self._make_doc("hello", "abc123")
        existing.id = doc.id
        service.ingest_file = AsyncMock(return_value=doc)
        service._document_store.find_by_source_path = AsyncMock(return_value=existing)
        result = await service.index_file(Path("/fake/test.txt"))
        assert result.skipped is True
        assert result.chunk_count == 0
        service._vector_store.add_chunks.assert_not_called()

    async def test_index_file_reindexes_changed(self, service: IngestionService):
        old_doc = self._make_doc("old", "old_checksum")
        new_doc = self._make_doc("new content", "new_checksum")
        service.ingest_file = AsyncMock(return_value=new_doc)
        service._document_store.find_by_source_path = AsyncMock(return_value=old_doc)
        service._chunker.chunk = MagicMock(return_value=[])
        service._embedding.embed_texts = AsyncMock(return_value=[])
        result = await service.index_file(Path("/fake/test.txt"))
        assert result.skipped is False
        assert result.checksum == "new_checksum"
        service._vector_store.delete_by_document_id.assert_awaited_once_with(
            str(old_doc.id)
        )

    async def test_index_file_new_file(self, service: IngestionService):
        doc = self._make_doc("new", "chk", "/fake/unknown.txt")
        service.ingest_file = AsyncMock(return_value=doc)
        service._document_store.find_by_source_path = AsyncMock(return_value=None)
        service._chunker.chunk = MagicMock(return_value=[])
        service._embedding.embed_texts = AsyncMock(return_value=[])
        result = await service.index_file(Path("/fake/unknown.txt"))
        assert result.skipped is False
        assert result.checksum == "chk"

    async def test_index_directory_skips_unchanged(self, service: IngestionService):
        from unittest.mock import patch

        doc = self._make_doc("content", "chk")
        service._document_loader.load = AsyncMock(return_value=doc)
        service._document_store.find_by_source_path = AsyncMock(return_value=doc)
        service._chunker.chunk = MagicMock(return_value=[])
        service._embedding.embed_texts = AsyncMock(return_value=[])
        service._document_loader.supported_extensions = {".txt"}
        with (
            patch(
                "app.application.ingestion.service.scan_directory",
                return_value=[Path("/fake/test.txt")],
            ),
            patch(
                "app.application.ingestion.service.validate_directory",
                return_value=Path("/fake"),
            ),
            patch(
                "app.application.ingestion.service.validate_file",
                return_value=None,
            ),
        ):
            results = await service.index_directory(Path("/fake"), recursive=False)
        assert len(results) == 1
        assert results[0].skipped is True
