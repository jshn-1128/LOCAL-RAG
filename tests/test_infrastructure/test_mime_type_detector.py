"""
Tests for MIME type detector.

Verifies:
  - Known extensions return correct MIME types
  - Unknown extensions return application/octet-stream
"""

from __future__ import annotations

from app.infrastructure.document_loaders.mime_type_detector import detect_mime_type


class TestMimeTypeDetector:
    def test_txt_mime_type(self):
        assert detect_mime_type(".txt") == "text/plain"

    def test_md_mime_type(self):
        assert detect_mime_type(".md") == "text/markdown"

    def test_pdf_mime_type(self):
        assert detect_mime_type(".pdf") == "application/pdf"

    def test_docx_mime_type(self):
        assert (
            detect_mime_type(".docx")
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_unknown_extension(self):
        assert detect_mime_type(".unknown") == "application/octet-stream"

    def test_case_insensitive(self):
        assert detect_mime_type(".TXT") == "text/plain"
