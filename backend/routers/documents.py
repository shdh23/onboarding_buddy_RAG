from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel
from pathlib import Path

import shutil
import logging
import time
import uuid
from config import SUPPORTED_EXTENSIONS

from ingestion.loader import load_document
from ingestion.chunker import chunk_documents
from ingestion.embedder import embed_and_store, delete_document, list_documents

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class UploadResponse(BaseModel):
    doc_id: str
    doc_name: str
    doc_type: str
    chunk_count: int
    message: str
 
 
class DocumentItem(BaseModel):
    doc_id: str
    doc_name: str
    doc_type: str
    uploaded_at: str
    chunk_count: int
 
 
class DeleteResponse(BaseModel):
    doc_id: str
    chunks_deleted: int
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...), ):
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    if doc_type not in {"kt_doc", "transcript"}:
        raise HTTPException(
            status_code=400,
            detail="doc_type must be 'kt_doc' or 'transcript'"
        )
    
    doc_id = str(uuid.uuid4())
    temp_path = UPLOAD_DIR / f"{doc_id}{ext}"

    pipeline_start = time.time()
    logger.info("=" * 60)
    logger.info(f"INGESTION PIPELINE START — file: \"{file.filename}\" type: {doc_type}")
    logger.info(f"  doc_id: {doc_id}")
    logger.info("=" * 60)

    try:
        # Step 1 — Save upload
        logger.info("[Step 1/4] Saving uploaded file to disk...")
        t0 = time.time()
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        t1 = time.time()
        file_size = temp_path.stat().st_size
        logger.info(f"  Saved: {temp_path} ({file_size:,} bytes)")
        logger.info(f"  ⏱ Step 1 done in {t1 - t0:.2f}s")

        # Step 2 — Load & parse document
        logger.info(f"[Step 2/4] Loading document ({ext} format)...")
        t0 = time.time()
        docs = load_document(
            file_path=str(temp_path),
            doc_id=doc_id,
            doc_name=file.filename,
            doc_type=doc_type,
        )
        t1 = time.time()
        total_chars = sum(len(d.page_content) for d in docs)
        logger.info(f"  Loaded {len(docs)} section(s), {total_chars:,} total characters")
        logger.info(f"  ⏱ Step 2 done in {t1 - t0:.2f}s")

        # Step 3 — Semantic chunking
        logger.info(f"[Step 3/4] Semantic chunking ({len(docs)} sections)...")
        t0 = time.time()
        chunks = chunk_documents(docs)
        t1 = time.time()
        avg_len = sum(len(c.page_content) for c in chunks) // max(len(chunks), 1)
        logger.info(f"  Created {len(chunks)} chunks (avg {avg_len} chars/chunk)")
        logger.info(f"  ⏱ Step 3 done in {t1 - t0:.2f}s")

        # Step 4 — Embed & store in ChromaDB
        logger.info(f"[Step 4/4] Embedding {len(chunks)} chunks & storing in ChromaDB...")
        t0 = time.time()
        chunk_count = embed_and_store(chunks, doc_id=doc_id)
        t1 = time.time()
        logger.info(f"  Stored {chunk_count} chunks in vector store")
        logger.info(f"  ⏱ Step 4 done in {t1 - t0:.2f}s")

        total_time = time.time() - pipeline_start
        logger.info("=" * 60)
        logger.info(f"INGESTION PIPELINE END — {file.filename} → {chunk_count} chunks in {total_time:.2f}s")
        logger.info("=" * 60)

        return UploadResponse(
            doc_id=doc_id,
            doc_name=file.filename,
            doc_type=doc_type,
            chunk_count=chunk_count,
            message=f"Successfully ingested {chunk_count} chunks from '{file.filename}'",
        )
 
    except Exception as e:
        total_time = time.time() - pipeline_start
        logger.error(f"INGESTION PIPELINE FAILED after {total_time:.2f}s — {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
 
    finally:
        if temp_path.exists():
            temp_path.unlink()
            logger.info(f"Cleaned up temp file: {temp_path}")

@router.get("/", response_model=list[DocumentItem])
def get_documents():
    try:
        docs = list_documents()
        return docs
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}", response_model=DeleteResponse)
def remove_document(doc_id: str):
    try:
        chunks_deleted = delete_document(doc_id)
        return DeleteResponse(
            doc_id=doc_id,
            chunks_deleted=chunks_deleted,
            message=f"Successfully deleted {chunks_deleted} chunks for doc_id: {doc_id}",
        )
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
