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
