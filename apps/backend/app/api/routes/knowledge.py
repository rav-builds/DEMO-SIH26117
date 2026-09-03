"""
Knowledge Base & RAG management API routes.
"""

import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.rag.ingest import IngestResult, delete_source, ingest_file
from app.rag.retriever import RetrievedChunk, hybrid_retriever
from app.rag.vector_store import vector_store
from app.schemas.response import APIResponse

router = APIRouter(prefix="/knowledge")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Max matching chunks to return")
    source_filter: Optional[str] = Field(default=None, description="Optional filter by source name")


@router.post("/query", response_model=APIResponse[List[RetrievedChunk]])
async def query_knowledge(req: QueryRequest) -> APIResponse[List[RetrievedChunk]]:
    """Performs hybrid semantic + BM25 keyword search over ingested documents."""
    try:
        results = await hybrid_retriever.retrieve(
            query=req.query,
            top_k=req.top_k,
            source_filter=req.source_filter,
        )
        return APIResponse.ok(data=results)
    except Exception as exc:
        return APIResponse.fail(error=f"Knowledge retrieval failed: {str(exc)}")


@router.post("/ingest", response_model=APIResponse[IngestResult], status_code=status.HTTP_201_CREATED)
async def ingest_document(
    file: UploadFile = File(...),
    source_name: Optional[str] = Form(None),
) -> APIResponse[IngestResult]:
    """Uploads and ingests a document (PDF, DOCX, TXT) into the vector store."""
    filename = file.filename or "uploaded_doc"
    suffix = os.path.splitext(filename)[1].lower()

    if suffix not in (".pdf", ".docx", ".doc", ".txt", ".md", ".csv"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: .pdf, .docx, .txt, .md, .csv",
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        res = await ingest_file(
            file_path=tmp_path,
            source_id=source_name or filename,
        )
        if not res.success:
            return APIResponse.fail(error=res.error or "Ingestion failed")
        return APIResponse.ok(data=res)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
async def get_collection_status() -> APIResponse[Dict[str, Any]]:
    """Returns vector collection statistics."""
    try:
        info = vector_store.get_collection_info()
        return APIResponse.ok(data=info)
    except Exception as exc:
        return APIResponse.fail(error=f"Could not connect to Qdrant: {str(exc)}")


@router.delete("/sources/{source_id}", response_model=APIResponse[Dict[str, str]])
async def delete_knowledge_source(source_id: str) -> APIResponse[Dict[str, str]]:
    """Deletes all indexed chunks associated with a source document."""
    try:
        await delete_source(source_id)
        return APIResponse.ok(data={"message": f"Source '{source_id}' deleted successfully"})
    except Exception as exc:
        return APIResponse.fail(error=f"Failed to delete source: {str(exc)}")
