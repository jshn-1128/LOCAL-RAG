"""
Document management routes.

Purpose: CRUD operations for documents.
Endpoints:
  POST   /documents/index   -- Index a document or directory.
  POST   /documents/upload  -- Upload and index a document.
  GET    /documents/        -- List all documents.
  GET    /documents/{id}    -- Get document details.
  DELETE /documents/{id}    -- Delete a document and its chunks.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.dependencies import get_ingestion_service, get_retrieval_service
from app.application.ingestion.service import IngestionService
from app.application.retrieval.service import RetrievalService
from app.domain.exceptions import DocumentNotFoundError, DomainError

router = APIRouter(prefix="/documents", tags=["documents"])


class IndexRequest(BaseModel):
    path: str
    recursive: bool = True


class IndexResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    checksum: str


class DocumentListResponse(BaseModel):
    documents: list[dict]


@router.post("/index", response_model=list[IndexResponse] | IndexResponse)
async def index_documents(
    request: IndexRequest,
    service: IngestionService = Depends(get_ingestion_service),
):
    file_path = Path(request.path)
    if file_path.is_dir():
        results = await service.index_directory(file_path, recursive=request.recursive)
        return [
            IndexResponse(
                document_id=str(r.document_id),
                filename=r.filename,
                chunk_count=r.chunk_count,
                checksum=r.checksum,
            )
            for r in results
        ]
    else:
        result = await service.index_file(file_path)
        return IndexResponse(
            document_id=str(result.document_id),
            filename=result.filename,
            chunk_count=result.chunk_count,
            checksum=result.checksum,
        )


@router.post("/upload")
async def upload_document(
    file: UploadFile,
    service: IngestionService = Depends(get_ingestion_service),
):
    if not file.filename:
        raise HTTPException(status_code=422, detail="Filename is required")
    suffix = Path(file.filename).suffix.lower()
    supported = service._document_loader.supported_extensions
    if suffix not in supported:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{suffix}'. Supported: {', '.join(supported)}",
        )
    target_dir = service._settings.documents_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file.filename
    try:
        content = await file.read()
        target_path.write_bytes(content)
        result = await service.index_file(target_path)
        return {
            "document_id": str(result.document_id),
            "filename": result.filename,
            "chunk_count": result.chunk_count,
            "checksum": result.checksum,
            "skipped": result.skipped,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/")
async def list_documents(
    service: IngestionService = Depends(get_ingestion_service),
):
    try:
        docs = await service._document_store.list_documents()
    except Exception as exc:
        raise DomainError(f"Failed to list documents: {exc}") from exc
    return {
        "documents": [
            {
                "id": str(d.id),
                "filename": d.filename,
                "title": d.title,
                "file_type": d.file_type,
                "mime_type": d.mime_type,
                "encoding": d.encoding,
                "checksum": d.checksum,
                "source_path": str(d.source_path) if d.source_path else None,
                "loaded_at": d.loaded_at.isoformat(),
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "modified_at": d.modified_at.isoformat() if d.modified_at else None,
            }
            for d in docs
        ]
    }


@router.get("/vector-count")
async def vector_count(
    service: RetrievalService = Depends(get_retrieval_service),
):
    count = await service.count_documents()
    return {"count": count}


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    service: IngestionService = Depends(get_ingestion_service),
):
    doc = await service._document_store.get(document_id)
    if doc is None:
        raise DocumentNotFoundError(f"Document not found: {document_id}")
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "title": doc.title,
        "file_type": doc.file_type,
        "mime_type": doc.mime_type,
        "checksum": doc.checksum,
        "encoding": doc.encoding,
        "word_count": doc.metadata.word_count,
        "character_count": doc.metadata.character_count,
        "loaded_at": doc.loaded_at.isoformat(),
        "source_path": str(doc.source_path) if doc.source_path else None,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "modified_at": doc.modified_at.isoformat() if doc.modified_at else None,
        "content": (
            doc.content if len(doc.content) < 5000 else doc.content[:5000] + "..."
        ),
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    service: IngestionService = Depends(get_ingestion_service),
):
    doc = await service._document_store.get(document_id)
    if doc is None:
        raise DocumentNotFoundError(f"Document not found: {document_id}")
    try:
        await service.delete_document(document_id)
    except Exception as exc:
        raise DomainError(f"Failed to delete document: {exc}") from exc
    return {"status": "deleted", "document_id": document_id}
