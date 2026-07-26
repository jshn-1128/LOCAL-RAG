"""
Tests for checksum generator.

Verifies:
  - SHA-256 hex digest generation
  - Deterministic hashing (same input → same output)
  - Different inputs → different hashes
"""

from __future__ import annotations

from app.infrastructure.document_loaders.checksum_generator import generate_checksum


class TestChecksumGenerator:
    def test_returns_hex_string(self):
        checksum = generate_checksum("hello")
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_deterministic(self):
        c1 = generate_checksum("same content")
        c2 = generate_checksum("same content")
        assert c1 == c2

    def test_different_inputs_different_hashes(self):
        c1 = generate_checksum("content a")
        c2 = generate_checksum("content b")
        assert c1 != c2

    def test_empty_string(self):
        checksum = generate_checksum("")
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_unicode_content(self):
        c1 = generate_checksum("héllo wörld")
        c2 = generate_checksum("héllo wörld")
        assert c1 == c2
