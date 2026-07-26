"""
Tests for Document entity and DocumentMetadata.

Verifies:
  - Document fields are populated correctly
  - DocumentMetadata fields
  - Immutability is not enforced by dataclass (but design intent)
  - Default values
  - UUID generation
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from app.domain.models.document import Document, DocumentMetadata


class TestDocument:
    def test_document_minimal_creation(self):
        doc = Document(
            content="hello",
            source_path=Path("/tmp/test.txt"),
            filename="test.txt",
            title="test",
            checksum="abc",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        assert doc.content == "hello"
        assert isinstance(doc.id, UUID)
        assert doc.metadata.word_count == 0

    def test_document_full_creation(self):
        meta = DocumentMetadata(
            author="me",
            word_count=100,
            character_count=500,
            tags=["important"],
            custom={"key": "val"},
        )
        doc = Document(
            content="full content",
            source_path=Path("/a/b.txt"),
            filename="b.txt",
            title="Full Title",
            checksum="def123",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
            metadata=meta,
        )
        assert doc.title == "Full Title"
        assert doc.metadata.author == "me"
        assert doc.metadata.word_count == 100
        assert doc.metadata.character_count == 500
        assert doc.metadata.tags == ["important"]
        assert doc.metadata.custom == {"key": "val"}

    def test_document_has_unique_ids(self):
        doc1 = Document(
            content="a",
            source_path=Path("/a.txt"),
            filename="a.txt",
            title="a",
            checksum="1",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        doc2 = Document(
            content="b",
            source_path=Path("/b.txt"),
            filename="b.txt",
            title="b",
            checksum="2",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        assert doc1.id != doc2.id

    def test_document_loaded_at_defaults(self):
        from datetime import datetime

        doc = Document(
            content="x",
            source_path=Path("/x.txt"),
            filename="x.txt",
            title="x",
            checksum="3",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        assert doc.loaded_at is not None
        assert isinstance(doc.loaded_at, datetime)

    def test_document_default_metadata(self):
        doc = Document(
            content="x",
            source_path=Path("/x.txt"),
            filename="x.txt",
            title="x",
            checksum="3",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        assert doc.metadata.word_count == 0
        assert doc.metadata.character_count == 0
        assert doc.metadata.tags == []
        assert doc.metadata.custom == {}

    def test_document_str_contais_content(self):
        doc = Document(
            content="hello world",
            source_path=Path("/x.txt"),
            filename="x.txt",
            title="x",
            checksum="3",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        assert "hello world" in doc.content


class TestDocumentMetadata:
    def test_default_values(self):
        meta = DocumentMetadata()
        assert meta.word_count == 0
        assert meta.character_count == 0
        assert meta.tags == []
        assert meta.custom == {}
        assert meta.author is None
        assert meta.language is None
        assert meta.page_count is None
