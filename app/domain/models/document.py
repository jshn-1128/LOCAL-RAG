"""
Document entity and metadata.

Represents a source document loaded into the system.
Responsibilities:
  - Carry document content and metadata within the domain.
  - Provide a unique identity for each document.
  - Track file-level attributes (path, type, size, checksum).
  - Store extracted metadata (author, word count, page count, etc.).

All dependencies: stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class DocumentMetadata:
    author: str | None = None
    language: str | None = None
    page_count: int | None = None
    word_count: int = 0
    character_count: int = 0
    tags: list[str] = field(default_factory=list)
    custom: dict[str, object] = field(default_factory=dict)


@dataclass
class Document:
    content: str
    source_path: Path
    filename: str
    title: str
    checksum: str
    file_type: str
    mime_type: str
    encoding: str
    created_at: datetime | None = None
    modified_at: datetime | None = None
    loaded_at: datetime = field(default_factory=datetime.now)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    id: UUID = field(default_factory=uuid4)
