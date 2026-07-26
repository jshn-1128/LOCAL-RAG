"""
Tests for encoding detector.

Verifies:
  - UTF-8 detection
  - UTF-16 detection
  - Latin-1 fallback
  - decode_content with explicit encoding
  - decode_content with auto-detect
"""

from __future__ import annotations

import codecs

from app.infrastructure.document_loaders.encoding_detector import (
    decode_content,
    detect_encoding,
)


class TestDetectEncoding:
    def test_detect_utf8(self):
        content = b"hello world"
        assert detect_encoding(content) == "utf-8"

    def test_detect_utf16_le_with_bom(self):
        content = codecs.BOM_UTF16_LE + "hello".encode("utf-16-le")
        assert detect_encoding(content) == "utf-16-le"

    def test_detect_utf16_be_with_bom(self):
        content = codecs.BOM_UTF16_BE + "hello".encode("utf-16-be")
        assert detect_encoding(content) == "utf-16-be"

    def test_latin1_fallback_for_invalid_utf8(self):
        content = bytes(range(0x80, 0x100))
        encoding = detect_encoding(content)
        assert encoding == "latin-1"

    def test_empty_bytes(self):
        assert detect_encoding(b"") == "utf-8"

    def test_utf16_null_byte_heuristic(self):
        """Without BOM, null-byte heuristic chooses LE over BE."""
        content = "hello".encode("utf-16-le")
        assert detect_encoding(content) == "utf-16-le"


class TestDecodeContent:
    def test_decode_utf8(self):
        text, encoding = decode_content(b"hello")
        assert text == "hello"
        assert encoding == "utf-8"

    def test_decode_with_explicit_encoding(self):
        text, encoding = decode_content(
            "hello".encode("utf-16-le"), encoding="utf-16-le"
        )
        assert text == "hello"
        assert encoding == "utf-16-le"

    def test_decode_with_wrong_encoding_falls_back(self):
        text, encoding = decode_content(b"hello", encoding="utf-16-le")
        assert text == "hello"
        assert encoding == "utf-8"

    def test_decode_unicode(self):
        text, encoding = decode_content("héllo wörld ✓".encode())
        assert "héllo wörld ✓" in text
        assert encoding == "utf-8"
