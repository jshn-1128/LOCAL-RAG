"""
Tests for DocxLoader.

Verifies:
  - Text extraction
  - Metadata extraction
  - Checksum generation
  - Corrupted file handling
  - supported_extensions
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.exceptions import CorruptedDocumentError
from app.infrastructure.document_loaders.docx import DocxLoader


def _create_minimal_docx(text: str = "Hello DOCX") -> bytes:
    """Create a minimal valid .docx file (ZIP with OOXML content).

    python-docx is used in the loader itself, so we can't use it here
    to create fixtures. We craft a minimal valid DOCX binary.
    """
    import zipfile
    from io import BytesIO

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                "</Types>"
            ),
        )
        zf.writestr(
            "_rels/.rels",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                "</Relationships>"
            ),
        )
        zf.writestr(
            "word/_rels/document.xml.rels",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
            ),
        )
        zf.writestr(
            "word/document.xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body>"
                f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>"
                "</w:body>"
                "</w:document>"
            ),
        )
    return buf.getvalue()


class TestDocxLoader:
    @pytest.fixture
    def loader(self) -> DocxLoader:
        return DocxLoader()

    @pytest.fixture
    def sample_docx(self, tmp_path: Path) -> Path:
        f = tmp_path / "sample.docx"
        f.write_bytes(_create_minimal_docx("Hello DOCX World"))
        return f

    async def test_load_returns_document(self, loader: DocxLoader, sample_docx: Path):
        doc = await loader.load(sample_docx)
        assert doc.file_type == ".docx"

    async def test_load_content(self, loader: DocxLoader, sample_docx: Path):
        doc = await loader.load(sample_docx)
        assert "Hello DOCX World" in doc.content

    async def test_load_metadata(self, loader: DocxLoader, sample_docx: Path):
        doc = await loader.load(sample_docx)
        assert doc.filename == "sample.docx"
        assert isinstance(doc.title, str) and len(doc.title) > 0
        assert doc.checksum
        assert len(doc.checksum) == 64

    async def test_supported_extensions(self, loader: DocxLoader):
        assert loader.supported_extensions == {".docx"}

    async def test_corrupted_docx_raises(self, loader: DocxLoader, tmp_path: Path):
        f = tmp_path / "bad.docx"
        f.write_bytes(b"not a zip file")
        with pytest.raises(CorruptedDocumentError):
            await loader.load(f)

    async def test_load_many(self, loader: DocxLoader, tmp_path: Path):
        f1 = tmp_path / "a.docx"
        f2 = tmp_path / "b.docx"
        f1.write_bytes(_create_minimal_docx("First"))
        f2.write_bytes(_create_minimal_docx("Second"))
        docs = await loader.load_many([f1, f2])
        assert len(docs) == 2
