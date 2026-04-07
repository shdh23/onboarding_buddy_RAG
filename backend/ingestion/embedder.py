import logging
import uuid
from datetime import datetime, timezone

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)

logger = logging.getLogger(__name__)

def get_vector_store() -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )
    return vector_store

def embed_and_store(chunks: list[Document], doc_id: str) -> int:
    if not chunks:
        raise ValueError("No chunks provided to embed.")

    vector_store = get_vector_store()

    # Build unique IDs and attach uploaded_at timestamp
    uploaded_at = datetime.now(timezone.utc).isoformat()
    ids = []
   
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_id}_chunk_{i}"
        ids.append(chunk_id)

        chunk.metadata["chunk_id"] = chunk_id
        chunk.metadata["uploaded_at"] = uploaded_at
 
    logger.info(f"Embedding {len(chunks)} chunks for doc_id: {doc_id} ...")

    vector_store.add_documents(documents=chunks, ids=ids)

    logger.info(f"Stored {len(chunks)} chunks in ChromaDB (collection: {CHROMA_COLLECTION_NAME})")
    return len(chunks)

def delete_document(doc_id: str) -> int:
    vector_store = get_vector_store()

    collection = vector_store._collection
    results = collection.get(where={"doc_id": doc_id})
 
    if not results["ids"]:
        logger.warning(f"No chunks found for doc_id: {doc_id}")
        return 0
 
    chunk_ids = results["ids"]
    collection.delete(ids=chunk_ids)
 
    logger.info(f"Deleted {len(chunk_ids)} chunks for doc_id: {doc_id}")
    return len(chunk_ids)

def list_documents() -> list[dict]:
    vector_store = get_vector_store()
    collection = vector_store._collection
 
    results = collection.get(include=["metadatas"])
 
    if not results["metadatas"]:
        return []
 
    # Deduplicate by doc_id — one entry per document
    seen = {}
    for meta in results["metadatas"]:
        doc_id = meta.get("doc_id")
        if doc_id and doc_id not in seen:
            seen[doc_id] = {
                "doc_id":       doc_id,
                "doc_name":     meta.get("doc_name"),
                "doc_type":     meta.get("doc_type"),
                "uploaded_at":  meta.get("uploaded_at"),
                "chunk_count":  0,
            }
        if doc_id:
            seen[doc_id]["chunk_count"] += 1
 
    docs = sorted(seen.values(), key=lambda d: d["uploaded_at"], reverse=True)
    logger.info(f"Found {len(docs)} document(s) in ChromaDB")
    return docs