"""
Result entities.

Represents retrieval and generation outputs.
Responsibilities:
  - Bundle query results with source chunks and scores.
  - Separate concerns: retrieval results vs. generation results.
Allowed dependencies: app.domain.models.chunk, stdlib only.
"""

from dataclasses import dataclass
from uuid import UUID

from app.domain.models.chunk import Chunk


@dataclass
class IndexingResult:
    document_id: UUID
    filename: str
    chunk_count: int
    checksum: str
    skipped: bool = False


@dataclass
class RetrievalResult:
    query_id: UUID
    chunks: list[Chunk]
    scores: list[float]


@dataclass
class GenerationResult:
    query_id: UUID
    answer: str
    sources: list[Chunk]
    model: str


@dataclass
class ChatResult:
    query_id: UUID
    conversation_id: UUID
    answer: str
    sources: list[Chunk]
    model: str
    prompt_tokens: int = 0
    scores: list[float] | None = None
