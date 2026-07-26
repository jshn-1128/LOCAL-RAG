"""
Recursive character text splitter.

Purpose: Split documents into chunks using recursive character boundaries.
Implements: ChunkerPort
Inspired by: LangChain's RecursiveCharacterTextSplitter

Splits on paragraph → sentence → word boundaries.
Future milestone: Milestone 7 — Document Chunking.
"""

from app.domain.ports.chunker import ChunkerPort


class RecursiveChunker(ChunkerPort):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
