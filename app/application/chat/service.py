"""
Chat service.

Purpose: Orchestrate the conversational RAG pipeline.
  retrieve context → build prompt → generate answer → store conversation

Responsibilities:
  - Coordinate between retrieval service, LLM, and memory.
  - Build context-augmented prompts.
  - Manage conversation state across turns.

Allowed dependencies: app.domain (ports, models), app.application.retrieval
Forbidden dependencies: app.infrastructure, app.api

Future milestone: Milestone 12 — RAG Pipeline.
Extends to: streaming, prompt templates, multi-turn memory, evaluation.
"""

import logging

from app.application.retrieval.service import RetrievalService
from app.domain.ports.llm import LLMPort
from app.domain.ports.memory import MemoryPort

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm: LLMPort,
        memory: MemoryPort,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._llm = llm
        self._memory = memory
