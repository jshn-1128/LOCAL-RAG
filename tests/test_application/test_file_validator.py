"""
Tests for file validator.

Verifies:
  - Valid file passes validation
  - Missing file raises UnreadableDocumentError
  - Unsupported extension raises UnsupportedDocumentError
  - Oversized file raises DocumentTooLargeError
  - Directory raises UnreadableDocumentError
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.application.ingestion.file_validator import (
    validate_directory,
    validate_file,
)
from app.domain.exceptions import (
    DocumentTooLargeError,
    UnreadableDocumentError,
    UnsupportedDocumentError,
)


class TestValidateFile:
    def test_valid_file_passes(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        validate_file(f, max_size_bytes=10_000_000)

    def test_missing_file_raises(self, tmp_path: Path):
        f = tmp_path / "missing.txt"
        with pytest.raises(UnreadableDocumentError, match="does not exist"):
            validate_file(f, max_size_bytes=10_000_000)

    def test_unsupported_extension_raises(self, tmp_path: Path):
        f = tmp_path / "test.xyz"
        f.write_text("content")
        with pytest.raises(UnsupportedDocumentError, match="Unsupported"):
            validate_file(f, max_size_bytes=10_000_000)

    def test_oversized_file_raises(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("a" * 100)
        with pytest.raises(DocumentTooLargeError, match="exceeds maximum"):
            validate_file(f, max_size_bytes=50)

    def test_directory_raises(self, tmp_path: Path):
        with pytest.raises(UnreadableDocumentError, match="regular file"):
            validate_file(tmp_path, max_size_bytes=10_000_000)

    def test_custom_supported_extensions(self, tmp_path: Path):
        f = tmp_path / "test.custom"
        f.write_text("content")
        validate_file(f, max_size_bytes=10_000_000, supported_extensions={".custom"})


class TestValidateDirectory:
    def test_valid_directory(self, tmp_path: Path):
        result = validate_directory(tmp_path)
        assert result == tmp_path.resolve()

    def test_missing_directory_raises(self, tmp_path: Path):
        d = tmp_path / "missing"
        with pytest.raises(UnreadableDocumentError, match="does not exist"):
            validate_directory(d)

    def test_file_not_directory_raises(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("x")
        with pytest.raises(UnreadableDocumentError, match="Not a directory"):
            validate_directory(f)
