"""
Semantic chunking adapter.

Purpose: Split documents into chunks based on semantic similarity boundaries.
Implements: ChunkerPort

Groups sentences by embedding similarity.
More computationally expensive but produces coherent chunks.
"""

from __future__ import annotations

from app.domain.models.chunk import Chunk
from app.domain.models.document import Document
from app.domain.ports.chunker import ChunkerPort


class SemanticChunker(ChunkerPort):
    """Semantic chunker stub — reserved for future implementation."""

    def __init__(self, threshold: float = 0.5) -> None:
        self._threshold = threshold

    def chunk(self, document: Document) -> list[Chunk]:
        msg = "SemanticChunker is not yet implemented. Use RecursiveChunker."
        raise NotImplementedError(msg)
