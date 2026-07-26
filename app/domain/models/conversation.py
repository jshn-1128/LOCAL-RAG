"""
Conversation entity and message value object.

Represents a multi-turn conversation between user and assistant.
Responsibilities:
  - Maintain ordered message history.
  - Support conversation-level metadata.
Allowed dependencies: stdlib only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    id: UUID = field(default_factory=uuid4)
    messages: list[Message] = field(default_factory=list)
    metadata: dict | None = None
