"""
Chat service.

Purpose: Orchestrate the conversational RAG pipeline.
  retrieve context -> build prompt -> generate answer -> store conversation

Responsibilities:
  - Coordinate between retrieval service, LLM, and memory.
  - Build context-augmented prompts.
  - Manage conversation state across turns.

Allowed dependencies: app.domain (ports, models), app.application.retrieval
Forbidden dependencies: app.infrastructure, app.api
"""

from __future__ import annotations

import logging
import re

from app.application.prompt_builder import PromptBuilder
from app.application.retrieval.service import RetrievalService
from app.domain.exceptions import LLMError, RetrievalError
from app.domain.models.conversation import Conversation, Message
from app.domain.models.query import Query
from app.domain.models.result import ChatResult, RetrievalResult
from app.domain.ports.llm import LLMPort
from app.domain.ports.memory import MemoryPort

logger = logging.getLogger(__name__)


_INSUFFICIENT_EVIDENCE_MSG: str = (
    "I couldn't find enough information in the indexed documents "
    "to answer your question."
)

_GREETING_MSG: str = "Hello! How can I help you with your documents today?"
_GRATITUDE_MSG: str = "You're welcome! Let me know if you have any other questions."
_FAREWELL_MSG: str = "Goodbye! Feel free to come back if you need anything else."

_GREETING_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(hi|hello|hey|greetings|good\s*(morning|afternoon|evening))[\s\.,!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(what'?s up|sup|howdy|how are you|how'?s it going)[\s\?!]*$", re.IGNORECASE
    ),
]

_GRATITUDE_PATTERNS: list[re.Pattern] = [
    re.compile(r"^(thanks|thank you|thankyou|ty|thx)[\s\.,!]*$", re.IGNORECASE),
    re.compile(
        r"^(that'?s helpful|appreciate it|much appreciated)[\s\.,!]*$", re.IGNORECASE
    ),
]

_FAREWELL_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(bye|goodbye|see you|talk later|cya|gotta go)[\s\.,!]*$", re.IGNORECASE
    ),
]

_SYSTEM_QUERY_PATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"(how many|number of|count of)\s*(vectors|chunks|embeddings)",
            re.IGNORECASE,
        ),
        "vector_count",
    ),
    (
        re.compile(
            r"what\s*(model|llm|ai)\s*(are you|do you use|is running)", re.IGNORECASE
        ),
        "model",
    ),
    (
        re.compile(r"(what version|which version|version number)", re.IGNORECASE),
        "version",
    ),
    (
        re.compile(r"what('?s| is| are)\s+(your name|your purpose|you)", re.IGNORECASE),
        "app_name",
    ),
]


class ChatService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm: LLMPort,
        memory: MemoryPort,
        prompt_builder: PromptBuilder | None = None,
        min_evidence_chunks: int = 1,
        min_evidence_score: float = 0.25,
        app_name: str = "Local RAG",
        app_version: str = "0.1.0",
    ) -> None:
        self._retrieval_service = retrieval_service
        self._llm = llm
        self._memory = memory
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._min_evidence_chunks = min_evidence_chunks
        self._min_evidence_score = min_evidence_score
        self._app_name = app_name
        self._app_version = app_version

    @staticmethod
    def _detect_intent(text: str) -> str | None:
        stripped = text.strip()
        for pattern in _GREETING_PATTERNS:
            if pattern.match(stripped):
                return _GREETING_MSG
        for pattern in _GRATITUDE_PATTERNS:
            if pattern.match(stripped):
                return _GRATITUDE_MSG
        for pattern in _FAREWELL_PATTERNS:
            if pattern.match(stripped):
                return _FAREWELL_MSG
        return None

    async def _answer_system_query(self, text: str) -> str | None:
        stripped = text.strip().lower()
        for pattern, intent in _SYSTEM_QUERY_PATTERNS:
            match = pattern.search(stripped)
            if not match:
                continue
            if intent == "vector_count":
                try:
                    count = await self._retrieval_service.count_documents()
                    return f"I currently have {count} vector{'s' if count != 1 else ''} in the index."
                except Exception:
                    return None
            elif intent == "model":
                model = getattr(self._llm, "_model", "unknown")
                return f"I'm running the {model} model for text generation."
            elif intent == "version":
                return f"My version is {self._app_version}."
            elif intent == "app_name":
                return f"I'm {self._app_name}, a local retrieval-augmented generation system."
        return None

    async def chat(
        self,
        query: Query,
        conversation_id: str | None = None,
        llm_temperature: float = 0.7,
        llm_max_tokens: int = 2048,
    ) -> ChatResult:
        conv, is_new = await self._get_or_create_conversation(conversation_id)

        if is_new:
            if conv.metadata is None:
                conv.metadata = {}
            conv.metadata["title"] = query.text[:80]

        conv.messages.append(Message(role="user", content=query.text))
        logger.info(
            "Chat request [conversation=%s, query_id=%s, history=%s turns]",
            conv.id,
            query.id,
            len(conv.messages) // 2,
        )

        # ── Intent Detection ─────────────────────────────────────────────
        intent_answer = self._detect_intent(query.text)
        if intent_answer is not None:
            conv.messages.append(Message(role="assistant", content=intent_answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=intent_answer,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── System Question Detection ────────────────────────────────────
        sys_answer = await self._answer_system_query(query.text)
        if sys_answer is not None:
            conv.messages.append(Message(role="assistant", content=sys_answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=sys_answer,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── Retrieval ────────────────────────────────────────────────────
        retrieval_result = None
        try:
            retrieval_result = await self._retrieval_service.retrieve(query)
        except RetrievalError:
            logger.warning("Retrieval returned no results [conversation=%s]", conv.id)

        chunks = retrieval_result.chunks if retrieval_result else []
        scores = retrieval_result.scores if retrieval_result else None

        if not self._has_sufficient_evidence(retrieval_result or None):
            answer = _INSUFFICIENT_EVIDENCE_MSG
            logger.info(
                "Insufficient evidence for query [id=%s], returning static response",
                query.id,
            )
            conv.messages.append(Message(role="assistant", content=answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=answer,
                sources=chunks,
                scores=scores,
                model=model,
                prompt_tokens=0,
            )

        messages = self._prompt_builder.build_chat_messages(
            query=query.text,
            chunks=chunks,
            history=conv.messages[:-1],
        )

        logger.info(
            "Chat messages built [chunks=%s, history_turns=%s]",
            len(chunks),
            len(conv.messages) // 2,
        )

        try:
            answer = await self._llm.generate_chat(
                messages,
                temperature=llm_temperature,
                max_tokens=llm_max_tokens,
            )
        except Exception as exc:
            raise LLMError(f"LLM generation failed: {exc}") from exc

        conv.messages.append(Message(role="assistant", content=answer))
        await self._memory.save_conversation(conv)

        sources = chunks
        model = getattr(self._llm, "_model", "unknown")
        estimated_tokens = max(1, sum(len(m.get("content", "")) for m in messages) // 4)

        return ChatResult(
            query_id=query.id,
            conversation_id=conv.id,
            answer=answer,
            sources=sources,
            scores=scores,
            model=model,
            prompt_tokens=estimated_tokens,
        )

    async def get_history(self, conversation_id: str) -> Conversation | None:
        return await self._memory.get_conversation(conversation_id)

    async def list_conversations(self) -> list[Conversation]:
        return await self._memory.list_conversations()

    async def delete_conversation(self, conversation_id: str) -> None:
        await self._memory.delete_conversation(conversation_id)

    def _has_sufficient_evidence(
        self, retrieval_result: RetrievalResult | None
    ) -> bool:
        if retrieval_result is None:
            return False
        if len(retrieval_result.chunks) < self._min_evidence_chunks:
            return False
        if self._min_evidence_score > 0.0 and retrieval_result.scores:
            top_score = max(retrieval_result.scores)
            if top_score < self._min_evidence_score:
                return False
        return True

    async def _get_or_create_conversation(
        self,
        conversation_id: str | None,
    ) -> tuple[Conversation, bool]:
        if conversation_id:
            existing = await self._memory.get_conversation(conversation_id)
            if existing is not None:
                return existing, False
        return Conversation(), True
