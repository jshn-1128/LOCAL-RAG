"""
Search routes.

Purpose: Standalone retrieval endpoint without generation.
Endpoints:
  POST /search/    -- Retrieve relevant chunks for a query.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_retrieval_service
from app.application.retrieval.service import RetrievalService
from app.domain.models.query import Query

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 4


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    index: int
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total_results: int


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    service: RetrievalService = Depends(get_retrieval_service),
):
    query = Query(text=request.query, top_k=request.top_k)
    result = await service.retrieve(query)
    return SearchResponse(
        query=request.query,
        results=[
            SearchResultItem(
                chunk_id=str(chunk.id),
                document_id=str(chunk.document_id),
                content=chunk.content,
                index=chunk.index,
                score=score,
            )
            for chunk, score in zip(result.chunks, result.scores, strict=False)
        ],
        total_results=len(result.chunks),
    )
