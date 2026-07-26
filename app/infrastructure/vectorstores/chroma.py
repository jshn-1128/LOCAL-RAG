"""
ChromaDB vector store adapter.

Purpose: Persistent vector storage and similarity search using ChromaDB.
Implements: VectorStorePort
Dependencies: chromadb

Supports local persistence, metadata filtering, and collection management.
Future milestone: Milestone 9 — Vector Store.
"""

from app.domain.ports.vector_store import VectorStorePort


class ChromaVectorStore(VectorStorePort):
    def __init__(self, persist_directory: str = "data/vector_store") -> None:
        self._persist_directory = persist_directory
        self._collection = None
