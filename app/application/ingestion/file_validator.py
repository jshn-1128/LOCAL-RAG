"""
File validation for document loading.

Ensures files exist, are readable, are regular files,
have supported extensions, and do not exceed size limits.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from app.config.constants import SUPPORTED_DOCUMENT_EXTENSIONS
from app.domain.exceptions import (
    DocumentTooLargeError,
    UnreadableDocumentError,
    UnsupportedDocumentError,
)

logger = logging.getLogger(__name__)


def validate_file(
    path: Path,
    max_size_bytes: int,
    supported_extensions: set[str] | None = None,
) -> None:
    """Validate a file path for document loading.

    Args:
        path: File path to validate.
        max_size_bytes: Maximum allowed file size in bytes.
        supported_extensions: Set of allowed extensions. Defaults to global set.

    Raises:
        UnreadableDocumentError: If file does not exist, is not readable,
            is a directory, or is a broken symlink.
        UnsupportedDocumentError: If extension is not in supported set.
        DocumentTooLargeError: If file exceeds max_size_bytes.
    """
    if supported_extensions is None:
        supported_extensions = SUPPORTED_DOCUMENT_EXTENSIONS

    extension = path.suffix.lower()

    if not path.exists():
        raise UnreadableDocumentError(f"File does not exist: {path}")
    if not path.is_file():
        raise UnreadableDocumentError(f"Not a regular file: {path}")
    if not os.access(str(path), os.R_OK):
        raise UnreadableDocumentError(f"File is not readable: {path}")
    if extension not in supported_extensions:
        raise UnsupportedDocumentError(
            f"Unsupported file extension '{extension}'. "
            f"Supported: {', '.join(sorted(supported_extensions))}"
        )

    stat = path.stat()
    size = stat.st_size
    if size > max_size_bytes:
        raise DocumentTooLargeError(
            f"File size {size} bytes exceeds maximum of {max_size_bytes} bytes"
        )


def validate_directory(path: Path) -> Path:
    """Validate that path is an existing readable directory.

    Returns the resolved absolute path.
    """
    resolved = path.resolve()
    if not resolved.exists():
        raise UnreadableDocumentError(f"Directory does not exist: {resolved}")
    if not resolved.is_dir():
        raise UnreadableDocumentError(f"Not a directory: {resolved}")
    if not os.access(str(resolved), os.R_OK):
        raise UnreadableDocumentError(f"Directory is not readable: {resolved}")
    return resolved
