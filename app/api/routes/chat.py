"""
Chat routes.

Purpose: Conversational RAG endpoint.
Endpoints:
  POST /chat/          — Send a message and receive an answer.
  GET  /chat/{id}      — Get conversation history.
  DELETE /chat/{id}    — Delete a conversation.

Milestone: RAG Pipeline (Milestone 12), Streaming (Milestone 14).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])
