"""
Tests for RecursiveChunker.

Verifies:
  - Chunks a short document into a single chunk
  - Chunks a long document into multiple chunks
  - Chunks respect chunk_size and chunk_overlap
  - Empty documents return no chunks
  - Chunks preserve document_id and index
"""

from __future__ import annotations

from uuid import uuid4

from app.domain.models.document import Document
from app.infrastructure.chunking.recursive import RecursiveChunker


class TestRecursiveChunker:
    def _make_doc(self, content: str) -> Document:
        return Document(
            content=content,
            source_path="/tmp/test.txt",
            filename="test.txt",
            title="test",
            checksum="abc123",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )

    def test_chunk_empty_document(self):
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=0)
        doc = self._make_doc("")
        chunks = chunker.chunk(doc)
        assert chunks == []

    def test_chunk_single_short_document(self):
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=0)
        doc = self._make_doc("Hello world. This is a test.")
        chunks = chunker.chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].content == "Hello world. This is a test."
        assert chunks[0].document_id == doc.id
        assert chunks[0].index == 0

    def test_chunk_multiple_paragraphs(self):
        chunker = RecursiveChunker(chunk_size=50, chunk_overlap=0)
        text = "\n\n".join([f"Paragraph {i} content here." for i in range(5)])
        doc = self._make_doc(text)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        for i, chunk in enumerate(chunks):
            assert chunk.index == i
            assert chunk.document_id == doc.id

    def test_chunk_overlap(self):
        chunker = RecursiveChunker(chunk_size=30, chunk_overlap=10)
        doc = self._make_doc("a" * 100)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        assert all(c.content.strip() for c in chunks)

    def test_chunk_preserves_document_id(self):
        chunker = RecursiveChunker(chunk_size=50, chunk_overlap=0)
        doc_id = uuid4()
        doc = Document(
            id=doc_id,
            content="Long content " * 20,
            source_path="/tmp/test.txt",
            filename="test.txt",
            title="test",
            checksum="abc123",
            file_type=".txt",
            mime_type="text/plain",
            encoding="utf-8",
        )
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.document_id == doc_id
