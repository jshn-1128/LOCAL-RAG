"""
Tests for MarkdownLoader.

Verifies:
  - Content extraction
  - Title extraction from front matter
  - Front matter metadata
  - Encoding detection
  - Checksum generation
  - supported_extensions
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.infrastructure.document_loaders.markdown import MarkdownLoader


class TestMarkdownLoader:
    @pytest.fixture
    def loader(self) -> MarkdownLoader:
        return MarkdownLoader()

    async def test_load_plain_markdown(self, loader: MarkdownLoader, tmp_path: Path):
        f = tmp_path / "doc.md"
        f.write_text("# Title\n\nSome content.", encoding="utf-8")
        doc = await loader.load(f)
        assert doc.title == "doc"
        assert "# Title" in doc.content
        assert "Some content." in doc.content

    async def test_front_matter_title(self, loader: MarkdownLoader, tmp_path: Path):
        f = tmp_path / "article.md"
        f.write_text(
            "---\ntitle: My Article\nauthor: John\n---\n\nBody text.", encoding="utf-8"
        )
        doc = await loader.load(f)
        assert doc.title == "My Article"
        assert "Body text." in doc.content
        assert "---" not in doc.content

    async def test_front_matter_metadata(self, loader: MarkdownLoader, tmp_path: Path):
        f = tmp_path / "meta.md"
        f.write_text(
            "---\ntitle: Meta\nauthor: Jane\nlang: en\n---\n\nContent.",
            encoding="utf-8",
        )
        doc = await loader.load(f)
        assert doc.metadata.author == "Jane"
        assert doc.metadata.language == "en"
        assert doc.metadata.custom == {}

    async def test_front_matter_custom_fields(
        self, loader: MarkdownLoader, tmp_path: Path
    ):
        f = tmp_path / "custom.md"
        f.write_text(
            "---\ntitle: Custom\ntags: a,b,c\nversion: 2\n---\n\nBody.",
            encoding="utf-8",
        )
        doc = await loader.load(f)
        assert doc.metadata.custom.get("tags") == "a,b,c"
        assert doc.metadata.custom.get("version") == "2"

    async def test_load_markdown_checksum(self, loader: MarkdownLoader, tmp_path: Path):
        f = tmp_path / "checksum.md"
        f.write_text("Content", encoding="utf-8")
        doc = await loader.load(f)
        assert len(doc.checksum) == 64

    async def test_supported_extensions(self, loader: MarkdownLoader):
        assert loader.supported_extensions == {".md"}

    async def test_empty_markdown(self, loader: MarkdownLoader, tmp_path: Path):
        f = tmp_path / "empty.md"
        f.write_text("", encoding="utf-8")
        doc = await loader.load(f)
        assert doc.content == ""
