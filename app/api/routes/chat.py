"""
Chat routes.

Purpose: Conversational RAG endpoint.
Endpoints:
  POST /chat/          -- Send a message and receive an answer.
  GET  /chat/{id}      -- Get conversation history.
  DELETE /chat/{id}    -- Delete a conversation.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_chat_service
from app.application.chat.service import ChatService
from app.domain.models.query import Query

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    top_k: int = 4
    temperature: float = 0.7
    max_tokens: int = 2048


class SourceItem(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    index: int
    score: float | None = None


class AttributedSourceItem(BaseModel):
    chunk_id: str
    document_id: str
    document_filename: str
    document_type: str
    chunk_index: int
    content: str
    score: float
    similarity_label: str
    role: str
    page: int | None = None
    section: str | None = None


class ConfidenceItem(BaseModel):
    level: str
    score: float
    reason: str
    agreement: float
    coverage: float
    num_sources: int
    unique_documents: int
    conflicts: list[str] | None = None


class PipelineInfo(BaseModel):
    original_query: str
    rewritten_query: str | None = None
    top_k: int = 4
    num_results: int = 0


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[dict]
    model: str
    estimated_tokens: int
    confidence: ConfidenceItem | None = None
    attributed_sources: list[AttributedSourceItem] | None = None
    pipeline: PipelineInfo | None = None


class ConversationListItem(BaseModel):
    id: str
    title: str | None = None
    message_count: int
    created_at: str
    updated_at: str | None = None


@router.get("/")
async def list_conversations(
    service: ChatService = Depends(get_chat_service),
):
    convs = await service.list_conversations()
    return {
        "conversations": [
            ConversationListItem(
                id=str(c.id),
                title=c.metadata.get("title") if c.metadata else None,
                message_count=len(c.messages),
                created_at=c.messages[0].timestamp.isoformat() if c.messages else "",
                updated_at=c.messages[-1].timestamp.isoformat() if c.messages else None,
            )
            for c in convs
        ]
    }


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=422, detail="message must not be empty")
    query = Query(text=request.message, top_k=request.top_k)
    result = await service.chat(
        query=query,
        conversation_id=request.conversation_id,
        llm_temperature=request.temperature,
        llm_max_tokens=request.max_tokens,
    )
    source_list = list(result.sources)
    scores_list = result.scores or []
    response = ChatResponse(
        conversation_id=str(result.conversation_id),
        answer=result.answer,
        sources=[
            {
                "chunk_id": str(s.id),
                "document_id": str(s.document_id),
                "content": s.content,
                "index": s.index,
                "score": (
                    round(float(scores_list[i]), 4) if i < len(scores_list) else None
                ),
            }
            for i, s in enumerate(source_list)
        ],
        model=result.model,
        estimated_tokens=result.prompt_tokens,
    )

    if result.confidence is not None:
        response.confidence = ConfidenceItem(
            level=result.confidence.level.value,
            score=round(result.confidence.score, 4),
            reason=result.confidence.reason,
            agreement=round(result.confidence.agreement, 4),
            coverage=round(result.confidence.coverage, 4),
            num_sources=result.confidence.num_sources,
            unique_documents=result.confidence.unique_documents,
            conflicts=result.confidence.conflicts,
        )

    if result.attributed_sources is not None:
        response.attributed_sources = [
            AttributedSourceItem(
                chunk_id=str(a.chunk_id),
                document_id=str(a.document_id),
                document_filename=a.document_filename,
                document_type=a.document_type,
                chunk_index=a.chunk_index,
                content=a.content,
                score=round(a.score, 4),
                similarity_label=a.similarity_label,
                role=a.role,
                page=a.page,
                section=a.section,
            )
            for a in result.attributed_sources
        ]

    if result.pipeline is not None:
        response.pipeline = PipelineInfo(
            original_query=result.pipeline.original_query,
            rewritten_query=result.pipeline.rewritten_query,
            top_k=result.pipeline.top_k,
            num_results=result.pipeline.num_results,
        )

    return response


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    service: ChatService = Depends(get_chat_service),
):
    conv = await service.get_history(conversation_id)
    if conv is None:
        return {"status": "not_found", "conversation_id": conversation_id}
    return {
        "conversation_id": str(conv.id),
        "messages": [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
            for m in conv.messages
        ],
    }


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    service: ChatService = Depends(get_chat_service),
):
    await service.delete_conversation(conversation_id)
    return {"status": "deleted", "conversation_id": conversation_id}
