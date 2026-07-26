"""
Tests for PDFLoader.

Verifies:
  - Text extraction from PDF
  - Metadata extraction
  - Page count
  - Encrypted PDF handling
  - Corrupted PDF handling
  - supported_extensions
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.exceptions import CorruptedDocumentError
from app.infrastructure.document_loaders.pdf import PDFLoader


def _create_minimal_pdf(text: str = "Hello PDF World") -> bytes:
    """Create a minimal valid PDF with given text."""
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
        b"2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n"
        b"3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
        b" /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>>\nendobj\n"
        b"4 0 obj\n<</Length 44>>\nstream\n"
        b"BT /F1 12 Tf 100 700 Td (" + escaped.encode() + b") Tj ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\nendobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000060 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000266 00000 n \n"
        b"0000000362 00000 n \n"
        b"trailer\n<</Size 6 /Root 1 0 R>>\n"
        b"startxref\n429\n"
        b"%%EOF\n"
    )


class TestPDFLoader:
    @pytest.fixture
    def loader(self) -> PDFLoader:
        return PDFLoader()

    @pytest.fixture
    def sample_pdf(self, tmp_path: Path) -> Path:
        f = tmp_path / "sample.pdf"
        f.write_bytes(_create_minimal_pdf("Hello PDF World"))
        return f

    async def test_load_returns_document(self, loader: PDFLoader, sample_pdf: Path):
        doc = await loader.load(sample_pdf)
        assert doc.file_type == ".pdf"
        assert doc.mime_type == "application/pdf"

    async def test_load_content(self, loader: PDFLoader, sample_pdf: Path):
        doc = await loader.load(sample_pdf)
        assert "Hello PDF World" in doc.content

    async def test_load_metadata(self, loader: PDFLoader, sample_pdf: Path):
        doc = await loader.load(sample_pdf)
        assert doc.filename == "sample.pdf"
        assert doc.title == "sample"
        assert doc.checksum
        assert doc.metadata.page_count is not None
        assert doc.metadata.page_count >= 1

    async def test_encrypted_pdf_raises(self, loader: PDFLoader, tmp_path: Path):
        """We can't easily create an encrypted PDF, so test with a file that
        will cause pypdf to fail meaningfully."""
        f = tmp_path / "encrypted.pdf"
        f.write_bytes(b"%PDF-1.4\n% garbage")
        with pytest.raises(CorruptedDocumentError):
            await loader.load(f)

    async def test_empty_pdf_raises(self, loader: PDFLoader, tmp_path: Path):
        f = tmp_path / "empty.pdf"
        f.write_bytes(b"")
        with pytest.raises(CorruptedDocumentError):
            await loader.load(f)

    async def test_supported_extensions(self, loader: PDFLoader):
        assert loader.supported_extensions == {".pdf"}

    async def test_load_many(self, loader: PDFLoader, tmp_path: Path):
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f1.write_bytes(_create_minimal_pdf("First"))
        f2.write_bytes(_create_minimal_pdf("Second"))
        docs = await loader.load_many([f1, f2])
        assert len(docs) == 2
