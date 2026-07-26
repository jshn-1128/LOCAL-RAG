"""
MIME type detection based on file extension.

Uses the configured extension-to-MIME mapping from constants.
"""

from __future__ import annotations

from app.config.constants import TEXT_MIME_TYPES


def detect_mime_type(file_extension: str) -> str:
    """Return the MIME type for a given file extension.

    Falls back to application/octet-stream for unknown extensions.
    """
    return TEXT_MIME_TYPES.get(file_extension.lower(), "application/octet-stream")
