"""
Tests for ChatService.

Verifies:
  - Chat flow: retrieve -> build prompt -> generate -> persist -> return result
  - Creates new conversation when no conversation_id provided
  - Loads existing conversation when conversation_id provided
  - Handles empty retrieval (no context)
  - Propagates LLM errors
  - Persists conversation after generation
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.chat.service import ChatService
from app.application.prompt_builder import PromptBuilder
from app.application.retrieval.service import RetrievalService
from app.domain.exceptions import LLMError, RetrievalError
from app.domain.models.chunk import Chunk
from app.domain.models.conversation import Conversation, Message
from app.domain.models.query import Query
from app.domain.models.result import RetrievalResult
from app.domain.ports.llm import LLMPort
from app.domain.ports.memory import MemoryPort


class TestChatService:
    @pytest.fixture
    def retrieval_service(self) -> MagicMock:
        mock = MagicMock(spec=RetrievalService)
        chunk = Chunk(document_id="doc1", content="Retrieved context", index=0)
        mock.retrieve = AsyncMock(
            return_value=RetrievalResult(
                query_id="q1",
                chunks=[chunk],
                scores=[0.95],
            )
        )
        return mock

    @pytest.fixture
    def llm(self) -> MagicMock:
        mock = MagicMock(spec=LLMPort)
        mock.generate_chat = AsyncMock(return_value="This is the answer.")
        mock._model = "test-model"
        return mock

    @pytest.fixture
    def memory(self) -> MagicMock:
        mock = MagicMock(spec=MemoryPort)
        mock.save_conversation = AsyncMock()
        mock.get_conversation = AsyncMock(return_value=None)
        mock.list_conversations = AsyncMock(return_value=[])
        return mock

    @pytest.fixture
    def prompt_builder(self) -> MagicMock:
        mock = MagicMock(spec=PromptBuilder)
        mock.build_chat_messages = MagicMock(
            return_value=[
                {"role": "system", "content": "system prompt"},
                {"role": "user", "content": "context user query"},
            ]
        )
        return mock

    @pytest.fixture
    def service(
        self,
        retrieval_service: MagicMock,
        llm: MagicMock,
        memory: MagicMock,
        prompt_builder: MagicMock,
    ) -> ChatService:
        return ChatService(
            retrieval_service=retrieval_service,
            llm=llm,
            memory=memory,
            prompt_builder=prompt_builder,
        )

    async def test_chat_full_flow(self, service: ChatService):
        result = await service.chat(query=Query(text="Summarize the document"))
        assert result.answer == "This is the answer."
        assert result.sources[0].content == "Retrieved context"
        assert result.model == "test-model"
        assert result.prompt_tokens == 7

    async def test_chat_creates_new_conversation(self, service: ChatService):
        result = await service.chat(query=Query(text="Summarize the document"))
        assert result.conversation_id is not None

    async def test_chat_loads_existing_conversation(
        self, memory: MagicMock, service: ChatService
    ):
        existing = Conversation(messages=[Message(role="user", content="Previous")])
        memory.get_conversation = AsyncMock(return_value=existing)
        result = await service.chat(
            query=Query(text="Follow up"),
            conversation_id=str(existing.id),
        )
        assert result.conversation_id == existing.id

    async def test_chat_empty_retrieval(
        self, retrieval_service: MagicMock, service: ChatService
    ):
        retrieval_service.retrieve = AsyncMock(side_effect=RetrievalError("No results"))
        result = await service.chat(query=Query(text="Summarize the document"))
        assert "couldn't find enough information" in result.answer
        assert len(result.sources) == 0
        assert result.prompt_tokens == 0

    async def test_chat_propagates_llm_error(
        self, llm: MagicMock, service: ChatService
    ):
        llm.generate_chat = AsyncMock(side_effect=RuntimeError("Ollama down"))
        with pytest.raises(LLMError, match="LLM generation failed"):
            await service.chat(query=Query(text="Summarize the document"))

    async def test_chat_persists_conversation(
        self, memory: MagicMock, service: ChatService
    ):
        await service.chat(query=Query(text="Summarize the document"))
        assert memory.save_conversation.call_count == 1
        saved = memory.save_conversation.call_args[0][0]
        assert isinstance(saved, Conversation)
        assert len(saved.messages) == 2
        assert saved.messages[0].role == "user"
        assert saved.messages[0].content == "Summarize the document"
        assert saved.messages[1].role == "assistant"
        assert saved.messages[1].content == "This is the answer."

    async def test_confidence_gate_rejects_insufficient_chunks(
        self, retrieval_service: MagicMock, memory: MagicMock
    ):
        svc = ChatService(
            retrieval_service=retrieval_service,
            llm=MagicMock(spec=LLMPort),
            memory=memory,
            min_evidence_chunks=5,
        )
        result = await svc.chat(query=Query(text="Summarize the document"))
        assert "couldn't find enough information" in result.answer

    async def test_confidence_gate_rejects_low_score(
        self, retrieval_service: MagicMock, memory: MagicMock
    ):
        retrieval_service.retrieve = AsyncMock(
            return_value=RetrievalResult(
                query_id="q1",
                chunks=[Chunk(document_id="doc1", content="low", index=0)],
                scores=[0.1],
            )
        )
        svc = ChatService(
            retrieval_service=retrieval_service,
            llm=MagicMock(spec=LLMPort),
            memory=memory,
            min_evidence_score=0.5,
        )
        result = await svc.chat(query=Query(text="Summarize the document"))
        assert "couldn't find enough information" in result.answer

    async def test_confidence_gate_passes_sufficient_evidence(
        self, llm: MagicMock, retrieval_service: MagicMock, memory: MagicMock
    ):
        svc = ChatService(
            retrieval_service=retrieval_service,
            llm=llm,
            memory=memory,
            min_evidence_chunks=1,
            min_evidence_score=0.0,
        )
        result = await svc.chat(query=Query(text="Summarize the document"))
        assert "couldn't find enough information" not in result.answer

    async def test_get_history(self, memory: MagicMock, service: ChatService):
        conv = Conversation()
        memory.get_conversation = AsyncMock(return_value=conv)
        result = await service.get_history(str(conv.id))
        assert result is conv

    async def test_list_conversations(self, memory: MagicMock, service: ChatService):
        convs = [Conversation(), Conversation()]
        memory.list_conversations = AsyncMock(return_value=convs)
        result = await service.list_conversations()
        assert len(result) == 2
