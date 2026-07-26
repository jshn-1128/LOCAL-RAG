"""
Encoding detection for text-based files.

Tries BOM markers first, then common encodings.
Avoids external dependencies — pure stdlib approach.
"""

from __future__ import annotations

import codecs
import logging

logger = logging.getLogger(__name__)

_BOM_MAP: list[tuple[bytes, str]] = [
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
]

_ENCODING_CANDIDATES: list[str] = [
    "utf-8",
    "utf-16-le",
    "utf-16-be",
    "latin-1",
]

_DEFAULT_ENCODING: str = "latin-1"


def _has_bom(content: bytes) -> str | None:
    """Check for BOM markers and return the encoding if found."""
    for bom, encoding in _BOM_MAP:
        if content.startswith(bom):
            return encoding
    return None


def _has_null_bytes(content: bytes) -> bool:
    """Check if content has null bytes (indicating UTF-16 or similar)."""
    return b"\x00" in content


def detect_encoding(content: bytes) -> str:
    """Detect the encoding of byte content.

    Strategy:
      1. Check for BOM markers.
      2. Try UTF-8 first.
      3. If null bytes present, try UTF-16 before UTF-8.
      4. Fall back to latin-1 (never fails).
    """
    bom_encoding = _has_bom(content)
    if bom_encoding:
        return bom_encoding

    if _has_null_bytes(content):
        candidates = ["utf-16-le", "utf-16-be", "utf-8", "latin-1"]
    else:
        candidates = _ENCODING_CANDIDATES

    for enc in candidates:
        try:
            content.decode(enc)
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue

    logger.warning("Falling back to %s for undetectable encoding", _DEFAULT_ENCODING)
    return _DEFAULT_ENCODING


def decode_content(content: bytes, encoding: str | None = None) -> tuple[str, str]:
    """Decode byte content to str, returning (text, encoding_used).

    If encoding is None, auto-detect it.
    """
    if encoding is not None:
        try:
            return content.decode(encoding), encoding
        except (UnicodeDecodeError, UnicodeError):
            logger.warning(
                "Specified encoding %s failed, falling back to detection", encoding
            )

    detected = detect_encoding(content)
    return content.decode(detected), detected
