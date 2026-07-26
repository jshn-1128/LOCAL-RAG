"""
Tests for TextLoader.

Verifies:
  - Basic text file loading
  - Unicode content
  - Encoding detection
  - Metadata extraction
  - Checksum generation
  - supported_extensions property
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.models.document import Document
from app.infrastructure.document_loaders.text import TextLoader


class TestTextLoader:
    @pytest.fixture
    def loader(self) -> TextLoader:
        return TextLoader()

    @pytest.fixture
    def sample_file(self, tmp_path: Path) -> Path:
        f = tmp_path / "sample.txt"
        f.write_text(
            "Hello, this is a test document.\nIt has multiple lines.", encoding="utf-8"
        )
        return f

    async def test_load_returns_document(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert isinstance(doc, Document)

    async def test_load_content(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert "Hello, this is a test document." in doc.content
        assert "It has multiple lines." in doc.content

    async def test_load_metadata(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert doc.filename == "sample.txt"
        assert doc.file_type == ".txt"
        assert doc.mime_type == "text/plain"
        assert doc.title == "sample"
        assert doc.encoding == "utf-8"

    async def test_load_checksum(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert len(doc.checksum) == 64
        assert isinstance(doc.checksum, str)

    async def test_load_word_count(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert doc.metadata.word_count > 0

    async def test_load_character_count(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert doc.metadata.character_count > 0

    async def test_load_timestamps(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert doc.loaded_at is not None
        assert doc.modified_at is not None
        # st_birthtime may not exist on all platforms (e.g., Linux vs macOS), skip assertion
        assert doc.modified_at is not None

    async def test_load_source_path(self, loader: TextLoader, sample_file: Path):
        doc = await loader.load(sample_file)
        assert doc.source_path == sample_file.resolve()

    async def test_unicode_content(self, loader: TextLoader, tmp_path: Path):
        f = tmp_path / "unicode.txt"
        f.write_text("héllo wörld © 2024", encoding="utf-8")
        doc = await loader.load(f)
        assert "héllo wörld" in doc.content

    def test_supported_extensions(self, loader: TextLoader):
        assert loader.supported_extensions == {".txt"}

    async def test_load_many(self, loader: TextLoader, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("file a")
        f2.write_text("file b")
        docs = await loader.load_many([f1, f2])
        assert len(docs) == 2
        assert docs[0].filename == "a.txt"
        assert docs[1].filename == "b.txt"

    async def test_deterministic_checksum(self, loader: TextLoader, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("deterministic content")
        doc1 = await loader.load(f)
        doc2 = await loader.load(f)
        assert doc1.checksum == doc2.checksum
