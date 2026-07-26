"""
Memory port.

Defines the contract for conversation memory persistence.
Implementations: SQLite, Redis (future).
Future milestone: Milestone 15 — Conversation Memory.
"""

from abc import ABC, abstractmethod

from app.domain.models.conversation import Conversation


class MemoryPort(ABC):
    @abstractmethod
    async def save_conversation(self, conversation: Conversation) -> None: ...

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Conversation | None: ...

    @abstractmethod
    async def list_conversations(self) -> list[Conversation]: ...

    @abstractmethod
    async def delete_conversation(self, conversation_id: str) -> None: ...
