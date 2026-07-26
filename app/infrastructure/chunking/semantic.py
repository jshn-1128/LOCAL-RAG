"""
Semantic chunking adapter.

Purpose: Split documents into chunks based on semantic similarity boundaries.
Implements: ChunkerPort

Groups sentences by embedding similarity.
More computationally expensive but produces coherent chunks.
Future milestone: Milestone 7 — Document Chunking (advanced).
"""

from app.domain.ports.chunker import ChunkerPort


class SemanticChunker(ChunkerPort):
    def __init__(self, threshold: float = 0.5) -> None:
        self._threshold = threshold
