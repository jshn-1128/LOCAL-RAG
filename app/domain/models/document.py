"""
Document entity and metadata.

Represents a source document loaded into the system.
Responsibilities:
  - Carry document content and metadata within the domain.
  - Provide a unique identity for each document.
Allowed dependencies: stdlib only.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class DocumentMetadata:
    source: Path
    filename: str
    content_type: str
    size_bytes: int
    loaded_at: datetime = field(default_factory=datetime.now)


@dataclass
class Document:
    content: str
    metadata: DocumentMetadata | None = None
    id: UUID = field(default_factory=uuid4)
