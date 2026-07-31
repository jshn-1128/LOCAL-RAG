"""
Confidence engine.

Computes answer confidence from retrieval metadata only.
No LLM calls — pure statistical computation from scores and chunk metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from statistics import mean, stdev

from app.domain.models.chunk import Chunk


class ConfidenceLevel(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


@dataclass
class ConfidenceInfo:
    level: ConfidenceLevel
    score: float
    reason: str
    agreement: float
    coverage: float
    num_sources: int
    unique_documents: int
    conflicts: list[str] | None = None


def _label_similarity(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.5:
        return "Medium"
    if score >= 0.25:
        return "Low"
    return "Very Low"


_VALUE_PATTERNS = (
    r"\$?\d[\d,]*(?:\.\d+)?\s*(?:%|gb|mb|kb|hz|ms|seconds?|minutes?|hours?|"
    r"days?|months?|years?|pages?|users?|dollars?|euros?|k|m|b)?"
)
_CLAIM_PATTERN = re.compile(
    rf"\b([a-z][a-z0-9_ -]{{1,32}}?)\s+(?:is|are|was|were|should be|must be|set to|equals)\s+"
    rf"({_VALUE_PATTERNS})",
    re.IGNORECASE,
)
_CLAIM_SKIP_KEYS = frozenset(
    {
        "it",
        "this",
        "that",
        "there",
        "here",
        "what",
        "which",
        "each",
        "our",
        "their",
        "your",
        "the answer",
        "the question",
        "the problem",
    }
)


def _detect_fact_conflicts(chunks: list[Chunk]) -> list[str]:
    """Detect conflicting factual claims (same key, different values) across chunks.

    Pure regex over retrieved chunk text — no LLM, no extra embeddings.
    Conservative: only flags when the same key claims different values.
    """
    if len(chunks) < 2:
        return []
    claims: dict[str, set[str]] = {}
    for chunk in chunks:
        text = chunk.content or ""
        for match in _CLAIM_PATTERN.finditer(text):
            key = re.sub(r"\s+", " ", match.group(1)).strip().lower()
            key = re.sub(r"^the\s+", "", key)
            if not key or key in _CLAIM_SKIP_KEYS:
                continue
            value = (
                re.sub(r"\s+", " ", match.group(2))
                .strip()
                .rstrip(".")
                .replace(",", "")
                .replace("$", "")
                .lower()
            )
            if not value or value in ("", "0", "1"):
                continue
            claims.setdefault(key, set()).add(value)

    conflicts: list[str] = []
    for key, values in claims.items():
        if len(values) >= 2:
            rendered = " vs ".join(sorted(values, key=lambda v: -len(v)))
            conflicts.append(
                f"Possible conflicting evidence: sources disagree on the {key} ({rendered})."
            )
    return conflicts


def _detect_conflicts(chunks: list[Chunk], scores: list[float]) -> list[str]:
    conflicts = _detect_fact_conflicts(chunks)
    if len(chunks) < 2:
        return conflicts
    score_std = stdev(scores) if len(scores) > 1 else 0.0
    if score_std > 0.25:
        conflicts.append(
            "Retrieved documents vary significantly in relevance to your question."
        )
    unique_docs = len({str(c.document_id) for c in chunks})
    if unique_docs > 1 and len(chunks) / unique_docs < 1.5:
        conflicts.append(
            "Only one chunk per document was retrieved, "
            "which may limit answer completeness."
        )
    return conflicts


_compute_defaults = {
    "relevance_top_weight": 0.60,
    "relevance_avg_weight": 0.40,
}


def compute_confidence(
    scores: list[float],
    chunks: list[Chunk],
    top_k: int = 4,
) -> ConfidenceInfo:
    if not scores or not chunks:
        return ConfidenceInfo(
            level=ConfidenceLevel.VERY_LOW,
            score=0.0,
            reason="No evidence was retrieved.",
            agreement=0.0,
            coverage=0.0,
            num_sources=0,
            unique_documents=0,
        )

    top_score = max(scores)
    avg_score = mean(scores)
    score_std = stdev(scores) if len(scores) > 1 else 0.0
    agreement = max(0.0, 1.0 - score_std)

    unique_docs = len({str(c.document_id) for c in chunks})
    coverage = min(1.0, len(scores) / max(top_k, 1))

    num_sources = len(chunks)

    score = (
        _compute_defaults["relevance_top_weight"] * top_score
        + _compute_defaults["relevance_avg_weight"] * avg_score
    )
    score = round(min(1.0, max(0.0, score)), 4)

    conflicts = _detect_conflicts(chunks, scores)

    if score >= 0.65 and num_sources >= 2 and agreement >= 0.6:
        level = ConfidenceLevel.HIGH
        if conflicts:
            reason = (
                f"Supported by {num_sources} sources "
                f"from {unique_docs} document{'s' if unique_docs > 1 else ''}."
            )
        else:
            reason = (
                f"Strong evidence from {num_sources} sources "
                f"across {unique_docs} document{'s' if unique_docs > 1 else ''} "
                f"with high agreement."
            )
    elif score >= 0.45 and num_sources >= 1:
        level = ConfidenceLevel.MEDIUM
        if num_sources == 1:
            reason = (
                "Only one document discusses this topic. "
                "Some details may be incomplete."
            )
        elif agreement < 0.5:
            reason = (
                "Sources show some disagreement. "
                "Consider reviewing the original documents."
            )
        else:
            reason = (
                f"Moderate evidence from {num_sources} sources "
                f"in {unique_docs} document{'s' if unique_docs > 1 else ''}."
            )
    elif score >= 0.25 and num_sources >= 1:
        level = ConfidenceLevel.LOW
        reason = (
            "Retrieved evidence only partially answers "
            "your question. Some information may be missing."
        )
    else:
        level = ConfidenceLevel.VERY_LOW
        reason = "Very limited evidence available for this question."

    return ConfidenceInfo(
        level=level,
        score=score,
        reason=reason,
        agreement=round(agreement, 4),
        coverage=round(coverage, 4),
        num_sources=num_sources,
        unique_documents=unique_docs,
        conflicts=conflicts or None,
    )
