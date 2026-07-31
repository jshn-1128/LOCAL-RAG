"""
Recursive character text splitter.

Purpose: Split documents into chunks using recursive character boundaries.
Implements: ChunkerPort
Inspired by: LangChain's RecursiveCharacterTextSplitter

Splits on paragraph -> sentence -> word boundaries.
"""

from __future__ import annotations

import logging

from app.domain.models.chunk import Chunk
from app.domain.models.document import Document
from app.domain.ports.chunker import ChunkerPort

logger = logging.getLogger(__name__)

_SEPARATORS: list[str] = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]


class RecursiveChunker(ChunkerPort):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk(self, document: Document) -> list[Chunk]:
        return self._split_text(document.content, document.id)

    def _split_text(self, text: str, document_id) -> list[Chunk]:
        chunks: list[Chunk] = []
        index = 0
        start = 0

        while start < len(text):
            end = self._find_chunk_end(text, start)
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(
                    Chunk(
                        document_id=document_id,
                        content=chunk_content,
                        index=index,
                    )
                )
                index += 1
            if end >= len(text):
                break
            start = max(end - self._chunk_overlap, start + 1)

        return chunks

    def _find_chunk_end(self, text: str, start: int) -> int:
        remaining = len(text) - start
        if remaining <= self._chunk_size:
            return len(text)

        end = start + self._chunk_size
        best = end

        for sep in _SEPARATORS:
            if not sep:
                continue
            pos = text.rfind(sep, start, end)
            if pos != -1:
                candidate = pos + len(sep)
                if best >= end or candidate > best:
                    best = candidate

        if best <= start:
            best = end
        return best
