"""
Chunk entity.

Represents a segment of a document after chunking.
Responsibilities:
  - Carry chunk content and position metadata.
  - Link back to the source document via document_id.
Allowed dependencies: stdlib only.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Chunk:
    document_id: UUID
    content: str
    index: int
    metadata: dict | None = None
    id: UUID = field(default_factory=uuid4)
