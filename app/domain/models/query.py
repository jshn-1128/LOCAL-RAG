"""
Query value object.

Represents a user's search or question.
Responsibilities:
  - Carry the query text and search parameters.
  - Provide a unique identity for tracing.
Allowed dependencies: stdlib only.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Query:
    text: str
    top_k: int = 4
    filters: dict | None = None
    id: UUID = field(default_factory=uuid4)
