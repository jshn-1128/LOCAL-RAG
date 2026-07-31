from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum, auto

from app.domain.models.chunk import Chunk
from app.domain.models.conversation import Message

logger = logging.getLogger(__name__)


class AnswerStyle(Enum):
    EXPLANATION = auto()
    SUMMARY = auto()
    LIST = auto()
    COMPARISON = auto()
    TIMELINE = auto()
    PROCEDURE = auto()
    PROS_CONS = auto()
    DEFAULT = auto()


_STYLE_FORMAT: dict[AnswerStyle, str] = {
    AnswerStyle.EXPLANATION: (
        "FORMAT: Start with a clear definition. "
        "Then explain key details in short paragraphs. "
        "Add context or use cases if relevant."
    ),
    AnswerStyle.SUMMARY: (
        "FORMAT: Start with 'Summary:' and a one-sentence overview. "
        "List key points as bullets. "
        "End with a one-line conclusion."
    ),
    AnswerStyle.LIST: (
        "FORMAT: Begin with a brief intro sentence. "
        "Then present each item as a bullet with a short description. "
        "Keep bullets parallel in structure."
    ),
    AnswerStyle.COMPARISON: (
        "FORMAT: Use a markdown table for 2+ items. "
        "| Feature | Item A | Item B |. "
        "Add a brief summary row if helpful. "
        "For simple 2-item compares, a short sentence is fine."
    ),
    AnswerStyle.TIMELINE: (
        "FORMAT: List events in chronological order. "
        "Use a bullet for each: '**Date:** Event description'. "
        "Oldest first."
    ),
    AnswerStyle.PROCEDURE: (
        "FORMAT: Start with the goal. "
        "Then use numbered steps (1. 2. 3.) in order. "
        "Mention expected outcome after the last step."
    ),
    AnswerStyle.PROS_CONS: (
        "FORMAT: Two sections: **Advantages** and **Disadvantages**. "
        "Use bullets under each. "
        "End with a balanced 1-sentence conclusion."
    ),
    AnswerStyle.DEFAULT: (
        "FORMAT: Use short paragraphs. "
        "Add headings or bullets when it improves clarity. "
        "Avoid giant walls of text."
    ),
}


_SYSTEM_TEMPLATE: str = (
    "You are an expert research analyst "
    "synthesizing information from multiple documents.\n\n"
    "EVIDENCE ANALYSIS:\n"
    "Before writing your answer, mentally categorize the "
    "available evidence by topic. "
    "Note which claims are supported by multiple excerpts, "
    "identify gaps where evidence is missing, "
    "and flag any conflicting information.\n\n"
    "SYNTHESIS:\n"
    "- COMBINE facts from all relevant documents into one answer. "
    "Do not rely on a single excerpt.\n"
    "- DON'T REPEAT. If multiple documents state the same fact, "
    "mention it once.\n"
    "- CONFLICTS. If documents disagree, present both views "
    "neutrally. Do not invent agreement.\n"
    "- STRUCTURE. Use sections, bullet lists, or comparisons "
    "when helpful. Avoid one giant paragraph.\n"
    "- SOURCES. Reference documents naturally "
    '(e.g., "The product documentation shows..."). '
    'Never say "Document 1" or "chunk."\n'
    "- UNCERTAINTY. If evidence is insufficient, say so. "
    "Never invent facts.\n\n"
    "RULES:\n"
    "- Greetings, thanks, farewells \u2192 respond naturally "
    "without documents.\n"
    "- Code questions \u2192 use code fences. "
    "Everything else \u2192 plain language.\n"
    "- Never mention retrieval, chunks, or system details."
)

_CONTEXT_TEMPLATE: str = "RELEVANT EXCERPTS:\n{context}"

_HISTORY_TEMPLATE: str = "PREVIOUS CONVERSATION:\n{history}"

_USER_TEMPLATE: str = "{query}"

_ASSISTANT_PREFIX: str = ""

_ESTIMATED_CHARS_PER_TOKEN: int = 4

_SECTION_SEPARATOR: str = "=" * 50
_CHUNK_SEPARATOR: str = "-" * 50

_MIN_CHUNK_LENGTH: int = 30

_BOILERPLATE_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(table of contents|navigation|skip to content|footer|header)$", re.IGNORECASE
    ),
    re.compile(r"^\s*page\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d+\s*$"),
    re.compile(r"^[\s\n\r\t.,;:!?\-_=*#@$%^&()\[\]{}|/\\<>~`'\"]+$"),
]


@dataclass
class Prompt:
    system: str
    context: str
    history: str
    user: str
    full_prompt: str
    estimated_tokens: int = 0


@dataclass
class PromptConfig:
    max_tokens: int = 4096
    max_context_chunks: int = 10
    max_history_turns: int = 10
    system_template: str = _SYSTEM_TEMPLATE
    context_template: str = _CONTEXT_TEMPLATE
    history_template: str = _HISTORY_TEMPLATE
    user_template: str = _USER_TEMPLATE
    assistant_prefix: str = _ASSISTANT_PREFIX


class PromptBuilder:
    def __init__(self, config: PromptConfig | None = None) -> None:
        self._config = config or PromptConfig()

    def build(
        self,
        query: str,
        chunks: list[Chunk],
        scores: list[float] | None = None,
        history: list[Message] | None = None,
    ) -> Prompt:
        context = self._format_context(chunks, scores)
        history_text = self._format_history(history or [])
        system = self._config.system_template
        user = self._config.user_template.format(query=query)

        full_prompt = self._assemble(
            system=system,
            context=context,
            history=history_text,
            user=user,
            assistant_prefix=self._config.assistant_prefix,
        )
        estimated = self._estimate_tokens(full_prompt)

        return Prompt(
            system=system,
            context=context,
            history=history_text,
            user=user,
            full_prompt=full_prompt,
            estimated_tokens=estimated,
        )

    # ── Evidence Packaging ──────────────────────────────────────────

    def _format_context(
        self,
        chunks: list[Chunk],
        scores: list[float] | None = None,
    ) -> str:
        if not chunks:
            return ""

        scored = self._pair_scores(chunks, scores)
        scored = [p for p in scored if self._is_quality_content(p[0])]
        if not scored:
            return ""

        scored = self._deduplicate(scored)
        if not scored:
            return ""

        scored.sort(key=lambda x: x[1], reverse=True)

        scored = self._diversify_documents(scored)
        if not scored:
            return ""

        scored = scored[: self._config.max_context_chunks]

        parts: list[str] = [_SECTION_SEPARATOR, "RELEVANT EVIDENCE"]
        for i, (chunk, score) in enumerate(scored, 1):
            parts.append(self._format_single_chunk(i, chunk, score))

        parts.append(_SECTION_SEPARATOR)
        return "\n".join(parts)

    def _format_single_chunk(self, index: int, chunk: Chunk, score: float) -> str:
        meta = chunk.metadata or {}
        filename = str(meta.get("filename", "Unknown")) if meta else "Unknown"
        file_type = str(meta.get("file_type", "Unknown")) if meta else "Unknown"
        source_path = str(meta.get("source_path", "")) if meta else ""

        excerpt = self._compress_text(chunk.content.strip())

        lines: list[str] = [
            _CHUNK_SEPARATOR,
            f"Document {index}",
            f"Filename: {filename}",
            f"Similarity: {score:.2f}",
            f"Document Type: {file_type}",
        ]
        if source_path:
            lines.append(f"Source: {source_path}")
        lines.extend(["", "Relevant Excerpt:", excerpt])

        return "\n".join(lines)

    # ── Quality Filtering ───────────────────────────────────────────

    @staticmethod
    def _is_quality_content(chunk: Chunk) -> bool:
        content = chunk.content.strip()
        if len(content) < _MIN_CHUNK_LENGTH:
            return False
        return all(not pattern.match(content) for pattern in _BOILERPLATE_PATTERNS)

    # ── Deduplication ───────────────────────────────────────────────

    @staticmethod
    def _deduplicate(
        scored: list[tuple[Chunk, float]],
    ) -> list[tuple[Chunk, float]]:
        seen: dict[str, tuple[Chunk, float]] = {}
        for chunk, score in scored:
            normalized = re.sub(r"\s+", " ", chunk.content.strip())
            if normalized not in seen or score > seen[normalized][1]:
                seen[normalized] = (chunk, score)
        return list(seen.values())

    # ── Document Diversity ──────────────────────────────────────────

    @staticmethod
    def _diversify_documents(
        scored: list[tuple[Chunk, float]],
        top_doc_max: int = 2,
        other_doc_max: int = 1,
    ) -> list[tuple[Chunk, float]]:
        if not scored:
            return []

        groups: dict[str, list[tuple[Chunk, float]]] = {}
        for chunk, score in scored:
            doc_id = str(chunk.document_id)
            if doc_id not in groups:
                groups[doc_id] = []
            groups[doc_id].append((chunk, score))

        for doc_id in groups:
            groups[doc_id].sort(key=lambda x: x[1], reverse=True)

        sorted_groups = sorted(
            groups.values(),
            key=lambda g: g[0][1],
            reverse=True,
        )

        if not sorted_groups:
            return []

        result: list[tuple[Chunk, float]] = list(sorted_groups[0][:top_doc_max])
        for group in sorted_groups[1:]:
            result.extend(group[:other_doc_max])

        return result

    # ── Context Compression ─────────────────────────────────────────

    @staticmethod
    def _compress_text(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" +\n", "\n", text)
        text = re.sub(r"\n +", "\n", text)
        return text.strip()

    # ── Helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _pair_scores(
        chunks: list[Chunk],
        scores: list[float] | None,
    ) -> list[tuple[Chunk, float]]:
        if scores is None:
            return [(c, 0.0) for c in chunks]
        return [
            (chunks[i], scores[i] if i < len(scores) else 0.0)
            for i in range(len(chunks))
        ]

    # ── History Formatting ──────────────────────────────────────────

    def _format_history(self, history: list[Message]) -> str:
        max_turns = self._config.max_history_turns
        recent = history[-max_turns:] if len(history) > max_turns else history
        if not recent:
            return ""
        lines: list[str] = []
        for msg in recent:
            prefix = "User:" if msg.role == "user" else "Assistant:"
            lines.append(f"{prefix} {msg.content}")
        history_text = "\n".join(lines)
        return self._config.history_template.format(history=history_text)

    # ── Assembly ────────────────────────────────────────────────────

    def _assemble(
        self,
        system: str,
        context: str,
        history: str,
        user: str,
        assistant_prefix: str,
    ) -> str:
        parts = [system]
        if context:
            parts.append(context)
        if history:
            parts.append(history)
        parts.append(user)
        parts.append(assistant_prefix)
        return "\n\n".join(parts)

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // _ESTIMATED_CHARS_PER_TOKEN)

    # ── Chat Messages ───────────────────────────────────────────────

    def build_chat_messages(
        self,
        query: str,
        chunks: list[Chunk],
        scores: list[float] | None = None,
        history: list[Message] | None = None,
        style: AnswerStyle | None = None,
    ) -> list[dict[str, str]]:
        system_parts: list[str] = [self._config.system_template]
        context = self._format_context(chunks, scores)
        if context:
            system_parts.append(context)
        history_text = self._format_history(history or [])
        if history_text:
            system_parts.append(history_text)
        if style and style != AnswerStyle.DEFAULT:
            fmt = _STYLE_FORMAT.get(style)
            if fmt:
                system_parts.append(f"RESPONSE {fmt}")
        system_content = "\n\n".join(system_parts)

        messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
        messages.append({"role": "user", "content": query})

        return messages

    def exceeds_max_tokens(self, prompt: Prompt) -> bool:
        return prompt.estimated_tokens > self._config.max_tokens
