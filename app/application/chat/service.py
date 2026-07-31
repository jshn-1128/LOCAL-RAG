from __future__ import annotations

import logging
import re

from app.application.attribution import enrich_sources
from app.application.chat.router import (
    ClassificationResult,
    QueryCategory,
    QueryRouter,
)
from app.application.confidence import compute_confidence
from app.application.prompt_builder import AnswerStyle, PromptBuilder
from app.application.retrieval.service import RetrievalService
from app.domain.exceptions import LLMError, RetrievalError
from app.domain.models.conversation import Conversation, Message
from app.domain.models.query import Query
from app.domain.models.result import ChatResult, QueryPipelineInfo, RetrievalResult
from app.domain.ports.document_store import DocumentStorePort
from app.domain.ports.llm import LLMPort
from app.domain.ports.memory import MemoryPort

logger = logging.getLogger(__name__)

_INSUFFICIENT_EVIDENCE_MSG: str = (
    "I couldn't find enough information in the indexed documents "
    "to answer your question."
)

_OUT_OF_DOMAIN_MSG: str = (
    "I'm designed to answer questions using your indexed documents. "
    "I can summarize, compare, search, and explain content from "
    "your knowledge base. Try asking me something document-related!"
)

_STYLE_PATTERNS: list[tuple[re.Pattern, AnswerStyle]] = [
    (
        re.compile(
            r"\b(pros?|cons?|advantages?|disadvantages?|benefits?|drawbacks?|strengths?|weaknesses?)\b",
            re.IGNORECASE,
        ),
        AnswerStyle.PROS_CONS,
    ),
    (
        re.compile(
            r"(compare|difference|diff(erent)?|versus|vs\.?)\s",
            re.IGNORECASE,
        ),
        AnswerStyle.COMPARISON,
    ),
    (
        re.compile(
            r"(timeline|chronolog|history|sequence|order of events|put in order)",
            re.IGNORECASE,
        ),
        AnswerStyle.TIMELINE,
    ),
    (
        re.compile(
            r"\b(how\s+(to|do|can|would)\b|steps?\s+to\b|process\s+for\b|procedure|guide|walkthrough|tutorial|setup|install)",
            re.IGNORECASE,
        ),
        AnswerStyle.PROCEDURE,
    ),
    (
        re.compile(
            r"\b(list|types? of|kinds? of|examples? of|categories? of|features? of|benefits? of|products? of)\b",
            re.IGNORECASE,
        ),
        AnswerStyle.LIST,
    ),
    (
        re.compile(
            r"\b(summarize|summary|overview|recap|tl;dr|in short|briefly|give me the key|key points?|main points?)\b",
            re.IGNORECASE,
        ),
        AnswerStyle.SUMMARY,
    ),
    (
        re.compile(
            r"^(what (is|are|does)|define|explain|describe|how does)",
            re.IGNORECASE,
        ),
        AnswerStyle.EXPLANATION,
    ),
]

_QUERY_REWRITE_THRESHOLD: int = 40

_PRONOUN_PATTERN: re.Pattern = re.compile(
    r"^(it|this|that|they|them|these|those|he|she|we)\b",
    re.IGNORECASE,
)

_TOPIC_EXTRACTION_PREFIXES: list[re.Pattern] = [
    re.compile(
        r"(?:tell me about|what (?:is|are|does|do|can)|explain|describe|summarize|compare|overview of)\s+",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:who (?:is|are|was)|when (?:was|is|did)|where (?:is|are)|how (?:does|do|is|are|can|to))\s+",
        re.IGNORECASE,
    ),
    re.compile(r"(?:list|define|show|give me|talk about)\s+", re.IGNORECASE),
]

_STOP_WORDS: frozenset = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "with",
        "and",
        "or",
        "is",
        "are",
        "was",
        "were",
        "be",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
    }
)


class ChatService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm: LLMPort,
        memory: MemoryPort,
        prompt_builder: PromptBuilder | None = None,
        router: QueryRouter | None = None,
        min_evidence_chunks: int = 1,
        min_evidence_score: float = 0.25,
        app_name: str = "Local RAG",
        app_version: str = "0.1.0",
        document_store: DocumentStorePort | None = None,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._llm = llm
        self._memory = memory
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._router = router or QueryRouter()
        self._min_evidence_chunks = min_evidence_chunks
        self._min_evidence_score = min_evidence_score
        self._app_name = app_name
        self._app_version = app_version
        self._document_store = document_store

    # ── Answer Style Detection ──────────────────────────────────

    @staticmethod
    def _detect_answer_style(text: str) -> AnswerStyle:
        stripped = text.strip().lower()
        for pattern, style in _STYLE_PATTERNS:
            if pattern.search(stripped):
                return style
        return AnswerStyle.DEFAULT

    # ── Query Rewriting ──────────────────────────────────────────

    @staticmethod
    def _extract_topic(message: str) -> str:
        text = message.strip()
        for prefix in _TOPIC_EXTRACTION_PREFIXES:
            m = prefix.match(text)
            if m:
                text = text[m.end() :].strip()
                break
        words = [
            w.strip("?").strip(".").strip("!")
            for w in text.split()
            if w.lower() not in _STOP_WORDS
        ]
        return " ".join(words[:5])

    @staticmethod
    def _build_retrieval_query(query_text: str, history: list[Message]) -> str:
        if len(history) < 2:
            return query_text
        stripped = query_text.strip()
        if len(stripped) > _QUERY_REWRITE_THRESHOLD and not _PRONOUN_PATTERN.match(
            stripped
        ):
            return query_text
        last_user = None
        for msg in reversed(history):
            if msg.role == "user":
                last_user = msg.content
                break
        if not last_user:
            return query_text
        topic = ChatService._extract_topic(last_user)
        if not topic:
            return query_text
        rewritten = f"{topic}: {stripped}"
        logger.info(
            "Query rewritten for retrieval: '%s' -> '%s'",
            stripped[:60],
            rewritten[:120],
        )
        return rewritten

    # ── Category Handlers ────────────────────────────────────────

    async def _handle_system_information(self, intent: str) -> str | None:
        match intent:
            case "vector_count":
                try:
                    count = await self._retrieval_service.count_documents()
                    return f"I currently have {count} vector{'s' if count != 1 else ''} in the index."
                except Exception:
                    return None
            case "llm_model":
                model = getattr(self._llm, "_model", "unknown")
                return f"I'm running the {model} model for text generation."
            case "embedding_model":
                emb = getattr(self._retrieval_service._embedding, "_model_name", None)
                if emb:
                    return f"I use the {emb} model for generating embeddings."
                return "The embedding model information is not available."
            case "vector_store":
                return "I use ChromaDB as my vector store."
            case "version":
                return f"My version is {self._app_version}."
            case "system_status":
                return "All systems are operational."
        return None

    async def _handle_identity(self) -> str:
        msgs = [
            {
                "role": "system",
                "content": (
                    f"You are {self._app_name}, a local, private, "
                    "retrieval-augmented generation system. "
                    "Answer concisely and naturally. "
                    "Mention that you are a private document assistant "
                    "that works 100% locally on the user's machine. "
                    "Do not mention retrieval, vectors, or system details."
                ),
            },
            {"role": "user", "content": "Who are you?"},
        ]
        try:
            return await self._llm.generate_chat(msgs, temperature=0.5, max_tokens=150)
        except Exception:
            return (
                f"I'm {self._app_name}, a local, private document assistant. "
                "I help you search, summarize, compare, and answer questions "
                "using your own documents — all running 100% locally on your machine."
            )

    async def _handle_capabilities(self) -> str:
        msgs = [
            {
                "role": "system",
                "content": (
                    f"You are {self._app_name}, a local document assistant. "
                    "List your capabilities concisely. "
                    "Mention that you can answer questions, summarize, compare, "
                    "search, and explain content from the user's indexed documents. "
                    "Supported file types include PDF, Word, Excel, PowerPoint, "
                    "images (OCR), plain text, CSV, JSON, and Markdown. "
                    "Emphasize that everything runs locally and privately. "
                    "Do not mention retrieval, vectors, or system details."
                ),
            },
            {
                "role": "user",
                "content": "What can you do?",
            },
        ]
        try:
            return await self._llm.generate_chat(msgs, temperature=0.5, max_tokens=200)
        except Exception:
            return (
                "I can help you with your documents! Here's what I can do:\n\n"
                "- Answer questions about your indexed documents\n"
                "- Summarize document content\n"
                "- Compare information across documents\n"
                "- Search for specific topics or keywords\n"
                "- Explain concepts found in your knowledge base\n\n"
                "Supported file types: PDF, Word, Excel, PowerPoint, images, "
                "plain text, CSV, JSON, and Markdown.\n\n"
                "Everything runs locally and privately on your machine."
            )

    async def _handle_out_of_domain(self) -> str:
        return _OUT_OF_DOMAIN_MSG

    async def _handle_mixed(self, query: Query, conv: Conversation) -> ChatResult:
        msgs = [
            {
                "role": "system",
                "content": (
                    f"You are {self._app_name}, a local document assistant. "
                    "The user is asking about your capabilities in relation to "
                    "your document features. Answer naturally, mentioning what "
                    "you can do with documents. If documents are relevant to "
                    "their question, incorporate that context. "
                    "Keep it concise and natural."
                ),
            },
            {"role": "user", "content": query.text},
        ]
        try:
            answer = await self._llm.generate_chat(
                msgs, temperature=0.5, max_tokens=300
            )
        except Exception as exc:
            raise LLMError(f"LLM generation failed: {exc}") from exc

        conv.messages.append(Message(role="assistant", content=answer))
        await self._memory.save_conversation(conv)
        model = getattr(self._llm, "_model", "unknown")
        return ChatResult(
            query_id=query.id,
            conversation_id=conv.id,
            answer=answer,
            sources=[],
            scores=[],
            model=model,
            prompt_tokens=0,
        )

    async def _run_rag_pipeline(
        self,
        query: Query,
        conv: Conversation,
        llm_temperature: float = 0.7,
        llm_max_tokens: int = 2048,
    ) -> ChatResult | None:
        retrieval_result = None
        retrieval_text = self._build_retrieval_query(query.text, conv.messages[:-1])
        retrieval_query: Query
        if retrieval_text != query.text:
            retrieval_query = Query(text=retrieval_text, top_k=query.top_k)
        else:
            retrieval_query = query

        try:
            retrieval_result = await self._retrieval_service.retrieve(retrieval_query)
        except RetrievalError:
            logger.warning("Retrieval returned no results [conversation=%s]", conv.id)

        chunks = retrieval_result.chunks if retrieval_result else []
        scores = retrieval_result.scores if retrieval_result else None

        if not self._has_sufficient_evidence(retrieval_result or None):
            return None

        style = self._detect_answer_style(query.text)
        logger.info(
            "Answer style detected: %s [chunks=%s]",
            style.name,
            len(chunks),
        )

        # Compute confidence & attribution from retrieval metadata
        confidence = compute_confidence(
            scores=scores or [],
            chunks=chunks,
            top_k=query.top_k,
        )
        document_names: dict[str, str] = {}
        if self._document_store is not None:
            missing = {
                str(c.document_id)
                for c in chunks
                if not (c.metadata or {}).get("filename")
            }
            for doc_id in missing:
                try:
                    doc = await self._document_store.get(doc_id)
                except Exception as exc:
                    logger.warning(
                        "Failed to resolve document name for %s: %s", doc_id, exc
                    )
                    doc = None
                if doc is not None:
                    document_names[doc_id] = doc.filename
        attributed = enrich_sources(chunks, scores or [], document_names=document_names)

        messages = self._prompt_builder.build_chat_messages(
            query=query.text,
            chunks=chunks,
            scores=scores,
            history=conv.messages[:-1],
            style=style,
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

        model = getattr(self._llm, "_model", "unknown")
        estimated_tokens = max(1, sum(len(m.get("content", "")) for m in messages) // 4)

        return ChatResult(
            query_id=query.id,
            conversation_id=conv.id,
            answer=answer,
            sources=chunks,
            scores=scores,
            model=model,
            prompt_tokens=estimated_tokens,
            confidence=confidence,
            attributed_sources=attributed,
            pipeline=QueryPipelineInfo(
                original_query=query.text,
                rewritten_query=(
                    retrieval_text if retrieval_text != query.text else None
                ),
                top_k=query.top_k,
                num_results=len(chunks),
            ),
        )

    # ── Main Chat Entry Point ──────────────────────────────────

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

        # ── Classify ────────────────────────────────────────────
        classification: ClassificationResult = self._router.classify(query.text)
        logger.info(
            "Query classified as %s [intent=%s]",
            classification.category.name,
            classification.system_intent or "none",
        )

        category = classification.category

        # ── Static Responses (no retrieval, no LLM) ─────────────
        static = self._router.get_static_response(category)
        if static is not None:
            conv.messages.append(Message(role="assistant", content=static))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=static,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── System Information (no retrieval) ──────────────────
        if category == QueryCategory.SYSTEM_INFORMATION:
            answer = await self._handle_system_information(
                classification.system_intent or ""
            )
            if answer is None:
                answer = "I don't have that information available."
            conv.messages.append(Message(role="assistant", content=answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=answer,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── Assistant Identity (LLM, no retrieval) ──────────────
        if category == QueryCategory.ASSISTANT_IDENTITY:
            answer = await self._handle_identity()
            conv.messages.append(Message(role="assistant", content=answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=answer,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── Assistant Capabilities (LLM, no retrieval) ─────────
        if category == QueryCategory.ASSISTANT_CAPABILITIES:
            answer = await self._handle_capabilities()
            conv.messages.append(Message(role="assistant", content=answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=answer,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── Out of Domain (no retrieval) ────────────────────────
        if category == QueryCategory.OUT_OF_DOMAIN:
            answer = await self._handle_out_of_domain()
            conv.messages.append(Message(role="assistant", content=answer))
            await self._memory.save_conversation(conv)
            model = getattr(self._llm, "_model", "unknown")
            return ChatResult(
                query_id=query.id,
                conversation_id=conv.id,
                answer=answer,
                sources=[],
                scores=[],
                model=model,
                prompt_tokens=0,
            )

        # ── Mixed (capability context + optional retrieval) ────
        if category == QueryCategory.MIXED:
            return await self._handle_mixed(query, conv)

        # ── Document Query — run full RAG pipeline ──────────────
        result = await self._run_rag_pipeline(
            query, conv, llm_temperature=llm_temperature, llm_max_tokens=llm_max_tokens
        )
        if result is not None:
            return result

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
            sources=[],
            scores=[],
            model=model,
            prompt_tokens=0,
        )

    # ── Conversation Management ─────────────────────────────────

    async def get_history(self, conversation_id: str) -> Conversation | None:
        return await self._memory.get_conversation(conversation_id)

    async def list_conversations(self) -> list[Conversation]:
        return await self._memory.list_conversations()

    async def delete_conversation(self, conversation_id: str) -> None:
        await self._memory.delete_conversation(conversation_id)

    # ── Evidence Check ─────────────────────────────────────────

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
