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
class ConfidenceInfo:
    level: str
    score: float
    reason: str
    agreement: float
    coverage: float
    num_sources: int
    unique_documents: int
    conflicts: list[str] | None = None


@dataclass
class SourceAttribution:
    chunk_id: UUID
    document_id: UUID
    document_filename: str
    document_type: str
    chunk_index: int
    content: str
    score: float
    similarity_label: str
    role: str


@dataclass
class QueryPipelineInfo:
    original_query: str
    rewritten_query: str | None = None
    top_k: int = 4
    num_results: int = 0


@dataclass
class ChatResult:
    query_id: UUID
    conversation_id: UUID
    answer: str
    sources: list[Chunk]
    model: str
    prompt_tokens: int = 0
    scores: list[float] | None = None
    confidence: ConfidenceInfo | None = None
    attributed_sources: list[SourceAttribution] | None = None
    pipeline: QueryPipelineInfo | None = None
