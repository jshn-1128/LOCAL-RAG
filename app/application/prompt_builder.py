"""
Prompt Builder.

Isolated component for assembling RAG prompts.
ChatService calls PromptBuilder — it does not build prompts itself.

Responsibilities:
  - System prompt with retrieved context
  - Conversation history formatting
  - User query wrapping
  - Context ordering and size management
  - Prompt metadata (token estimates)

Future: Multiple prompt strategies, template injection, formatting variants.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.domain.models.chunk import Chunk
from app.domain.models.conversation import Message

logger = logging.getLogger(__name__)

_SYSTEM_TEMPLATE: str = (
    "You are a helpful, friendly AI assistant. "
    "You have access to retrieved document context to help answer questions. "
    "Follow these rules:\n"
    "1. Respond naturally to greetings, thanks, and farewells without referring to documents.\n"
    "2. For questions, use the RETRIEVED CONTEXT below as your knowledge source.\n"
    "3. NEVER mention, quote, or reference the retrieval system, context sections, or internal formatting.\n"
    "4. NEVER output raw document text, chunk numbers, similarity scores, or template markers.\n"
    "5. NEVER output JSON, LaTeX, or code fences unless answering a code question.\n"
    "6. If the context contains relevant information, answer naturally using it.\n"
    "7. If no relevant information exists in the context, say you don't know politely.\n"
    "8. Do not fabricate sources or citations."
)

_CONTEXT_TEMPLATE: str = "RETRIEVED CONTEXT:\n{context}"

_HISTORY_TEMPLATE: str = "CONVERSATION HISTORY:\n{history}"

_USER_TEMPLATE: str = "{query}"

_ASSISTANT_PREFIX: str = ""

_ESTIMATED_CHARS_PER_TOKEN: int = 4


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
        history: list[Message] | None = None,
    ) -> Prompt:
        context = self._format_context(chunks)
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

    def _format_context(self, chunks: list[Chunk]) -> str:
        max_chunks = self._config.max_context_chunks
        seen: set[str] = set()
        unique: list[Chunk] = []
        for chunk in chunks:
            if chunk.content not in seen:
                seen.add(chunk.content)
                unique.append(chunk)
        selected = unique[:max_chunks]
        if not selected:
            return ""
        context_parts: list[str] = []
        for i, chunk in enumerate(selected, 1):
            context_parts.append(f"Document {i}:\n{chunk.content}")
        context_text = "\n\n".join(context_parts)
        return self._config.context_template.format(context=context_text)

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

    def build_chat_messages(
        self,
        query: str,
        chunks: list[Chunk],
        history: list[Message] | None = None,
    ) -> list[dict[str, str]]:
        system_parts: list[str] = [self._config.system_template]
        context = self._format_context(chunks)
        if context:
            system_parts.append(context)
        history_text = self._format_history(history or [])
        if history_text:
            system_parts.append(history_text)
        system_content = "\n\n".join(system_parts)

        messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
        messages.append({"role": "user", "content": query})

        return messages

    def exceeds_max_tokens(self, prompt: Prompt) -> bool:
        return prompt.estimated_tokens > self._config.max_tokens
