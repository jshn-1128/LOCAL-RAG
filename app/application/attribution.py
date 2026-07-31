"""
Source attribution engine.

Enriches retrieved chunks with evidence roles and semantic labels.
Orders sources by usefulness (not just similarity).
No LLM calls — computed from retrieval metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.models.chunk import Chunk


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
    page: int | None = None
    section: str | None = None


_ROLE_PRIMARY = "PRIMARY"
_ROLE_SUPPORTING = "SUPPORTING"
_ROLE_BACKGROUND = "BACKGROUND"

_PRIMARY_THRESHOLD = 0.65
_SUPPORTING_THRESHOLD = 0.45


def _label_similarity(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.5:
        return "Medium"
    if score >= 0.25:
        return "Low"
    return "Very Low"


def _extract_page(metadata: dict | None) -> int | None:
    if not metadata:
        return None
    raw = metadata.get("page", metadata.get("page_number"))
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _extract_section(metadata: dict | None) -> str | None:
    if not metadata:
        return None
    for key in ("section", "heading", "title", "chapter"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:200]
    return None


def _assign_role(
    score: float,
    rank: int,
) -> str:
    if rank == 0 and score >= _PRIMARY_THRESHOLD:
        return _ROLE_PRIMARY
    if score >= _SUPPORTING_THRESHOLD:
        return _ROLE_SUPPORTING
    return _ROLE_BACKGROUND


_RANK_NAMES: dict[str, str] = {
    _ROLE_PRIMARY: "Primary source",
    _ROLE_SUPPORTING: "Supporting source",
    _ROLE_BACKGROUND: "Background",
}


def rank_label(role: str) -> str:
    return _RANK_NAMES.get(role, role)


def enrich_sources(
    chunks: list[Chunk],
    scores: list[float],
    document_names: dict[str, str] | None = None,
) -> list[SourceAttribution]:
    if not chunks or not scores:
        return []

    indexed = list(enumerate(zip(chunks, scores, strict=False)))
    indexed.sort(key=lambda x: x[1][1], reverse=True)

    attributed: list[SourceAttribution] = []
    seen_docs: set[str] = set()
    primary_assigned = False

    for rank, (_orig_idx, (chunk, score)) in enumerate(indexed):
        role = _assign_role(score, rank if not primary_assigned else rank + 1)
        if role == _ROLE_PRIMARY:
            primary_assigned = True

        doc_key = str(chunk.document_id)
        if role == _ROLE_BACKGROUND and doc_key in seen_docs:
            role = _ROLE_SUPPORTING
        seen_docs.add(doc_key)

        filename = ""
        doc_type = ""
        if chunk.metadata:
            filename = chunk.metadata.get("filename", "")
            doc_type = chunk.metadata.get("file_type", "")
        if not filename and document_names:
            filename = document_names.get(doc_key, "")

        attributed.append(
            SourceAttribution(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                document_filename=filename,
                document_type=doc_type,
                chunk_index=chunk.index,
                content=chunk.content,
                score=score,
                similarity_label=_label_similarity(score),
                role=role,
                page=_extract_page(chunk.metadata),
                section=_extract_section(chunk.metadata),
            )
        )

    stage_order = {
        _ROLE_PRIMARY: 0,
        _ROLE_SUPPORTING: 1,
        _ROLE_BACKGROUND: 2,
    }
    attributed.sort(key=lambda s: (stage_order.get(s.role, 9), -s.score))

    return attributed
