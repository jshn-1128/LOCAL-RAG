"""
Chunker port.

Defines the contract for document chunking strategies.
Implementations: RecursiveCharacterTextSplitter, SemanticChunker.
Future milestone: Milestone 7 — Document Chunking.
"""

from abc import ABC, abstractmethod

from app.domain.models.chunk import Chunk
from app.domain.models.document import Document


class ChunkerPort(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]: ...
