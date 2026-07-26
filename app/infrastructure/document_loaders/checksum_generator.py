"""
SHA-256 checksum generation for document content.

Provides deterministic hashing for duplicate detection,
incremental indexing, and cache invalidation.
"""

from __future__ import annotations

import hashlib


def generate_checksum(content: str) -> str:
    """Generate a SHA-256 hex digest for the given string content.

    The content is UTF-8 encoded before hashing to ensure
    deterministic results across platforms.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
