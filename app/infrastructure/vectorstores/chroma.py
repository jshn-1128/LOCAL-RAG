"""
ChromaDB vector store adapter.

Purpose: Persistent vector storage and similarity search using ChromaDB.
Implements: VectorStorePort
Dependencies: chromadb

Supports local persistence, metadata filtering, and collection management.
"""

from __future__ import annotations

import logging
import uuid

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.domain.exceptions import RetrievalError
from app.domain.models.chunk import Chunk
from app.domain.models.query import Query
from app.domain.models.result import RetrievalResult
from app.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStorePort):
    def __init__(
        self,
        persist_directory: str = "data/vector_store",
        collection_name: str = "documents",
    ) -> None:
        self._persist_directory = persist_directory
        self._collection_name = collection_name
        self._collection: object = None

    async def add_chunks(
        self, chunks: list[Chunk], embeddings: list[list[float]]
    ) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have same length"
            )

        collection = self._get_collection()
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for chunk, _emb in zip(chunks, embeddings, strict=False):
            chunk_id = str(chunk.id)
            ids.append(chunk_id)
            documents.append(chunk.content)
            metadatas.append(
                {
                    "document_id": str(chunk.document_id),
                    "chunk_index": chunk.index,
                    **({"source": str(chunk.metadata)} if chunk.metadata else {}),
                }
            )

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.debug("Added %s chunks to vector store", len(chunks))

    async def search(self, query: Query, embedding: list[float]) -> RetrievalResult:
        collection = self._get_collection()
        n_results = query.top_k

        try:
            results = collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
            )
        except Exception as exc:
            raise RetrievalError(f"Vector search failed: {exc}") from exc

        if not results["ids"] or not results["ids"][0]:
            return RetrievalResult(query_id=query.id, chunks=[], scores=[])

        chunks: list[Chunk] = []
        scores: list[float] = []

        for idx, doc_id in enumerate(results["ids"][0]):
            content = results["documents"][0][idx] if results["documents"] else ""
            metadata = results["metadatas"][0][idx] if results["metadatas"] else {}
            distance = results["distances"][0][idx] if results["distances"] else 0.0

            chunk = Chunk(
                id=uuid.UUID(doc_id),
                document_id=uuid.UUID(metadata.get("document_id", doc_id)),
                content=content,
                index=metadata.get("chunk_index", 0),
                metadata=metadata,
            )
            chunks.append(chunk)
            scores.append(1.0 - distance)

        return RetrievalResult(query_id=query.id, chunks=chunks, scores=scores)

    async def delete(self, chunk_ids: list[str]) -> None:
        collection = self._get_collection()
        collection.delete(ids=chunk_ids)
        logger.debug("Deleted %s chunks from vector store", len(chunk_ids))

    async def delete_by_document_id(self, document_id: str) -> None:
        collection = self._get_collection()
        collection.delete(where={"document_id": document_id})
        logger.debug("Deleted vectors for document: %s", document_id)

    async def count(self) -> int:
        collection = self._get_collection()
        return int(collection.count())

    def _get_collection(self):
        if self._collection is None:
            client = chromadb.PersistentClient(
                path=self._persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "Vector store initialized: %s (%s)",
                self._collection_name,
                self._persist_directory,
            )
        return self._collection
