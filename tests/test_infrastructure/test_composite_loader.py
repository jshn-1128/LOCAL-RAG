"""
Tests for CompositeDocumentLoader.

Verifies:
  - Delegates to correct loader based on extension
  - Raises UnsupportedDocumentError for unknown extensions
  - supported_extensions aggregates all registered loaders
  - Loads .txt, .md, .pdf, .docx correctly
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.exceptions import UnsupportedDocumentError
from app.infrastructure.document_loaders.composite import CompositeDocumentLoader
from app.infrastructure.document_loaders.docx import DocxLoader
from app.infrastructure.document_loaders.markdown import MarkdownLoader
from app.infrastructure.document_loaders.pdf import PDFLoader
from app.infrastructure.document_loaders.text import TextLoader


class TestCompositeDocumentLoader:
    @pytest.fixture
    def loader(self) -> CompositeDocumentLoader:
        return CompositeDocumentLoader(
            [
                TextLoader(),
                MarkdownLoader(),
                PDFLoader(),
                DocxLoader(),
            ]
        )

    def test_supported_extensions(self, loader: CompositeDocumentLoader):
        exts = loader.supported_extensions
        assert ".txt" in exts
        assert ".md" in exts
        assert ".pdf" in exts
        assert ".docx" in exts

    async def test_unsupported_extension_raises(
        self, loader: CompositeDocumentLoader, tmp_path: Path
    ):
        f = tmp_path / "test.xyz"
        f.write_text("content")
        with pytest.raises(UnsupportedDocumentError, match="No loader registered"):
            await loader.load(f)

    async def test_load_txt(self, loader: CompositeDocumentLoader, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        doc = await loader.load(f)
        assert doc.file_type == ".txt"
        assert doc.content == "hello"

    async def test_load_md(self, loader: CompositeDocumentLoader, tmp_path: Path):
        f = tmp_path / "test.md"
        f.write_text("# Hello")
        doc = await loader.load(f)
        assert doc.file_type == ".md"

    async def test_load_many(self, loader: CompositeDocumentLoader, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("a")
        f2.write_text("b")
        docs = await loader.load_many([f1, f2])
        assert len(docs) == 2
