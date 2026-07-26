"""
Filesystem document store adapter.

Purpose: Store and retrieve documents from the local filesystem.
Implements: DocumentStorePort
Dependencies: stdlib (pathlib, json)

Documents are stored as JSON files with metadata.
Future milestone: Milestone 7 — Document Ingestion.
"""

from app.domain.ports.document_store import DocumentStorePort


class FileSystemDocumentStore(DocumentStorePort):
    def __init__(self, base_path: str = "data/documents") -> None:
        self._base_path = base_path
