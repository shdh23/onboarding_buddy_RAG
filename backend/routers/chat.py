from fastapi import APIRouter, HTTPException
import logging
import time
from pydantic import BaseModel
from retrieval.retriever import retrieve
from retrieval.reranker import rerank
from generation.generator import generate_answer, rewrite_question
 
router = APIRouter()
logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str    # "user" | "assistant"
    content: str
 
class ChatRequest(BaseModel):
    question: str
    history: list[Message] = []
 
class SourceResult(BaseModel):
    doc_name: str
    doc_type: str
    chunk_text: str
    chunk_index: int
    rerank_score: float | None = None
 
class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResult]
    rewritten_question: str | None = None


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    history = [msg.model_dump() for msg in request.history]


    pipeline_start = time.time()
    logger.info("=" * 60)
    logger.info(f"CHAT PIPELINE START — question: \"{request.question}\"")
    logger.info(f"  History length: {len(history)} messages")
    logger.info("=" * 60)

    try:
        # Step 1 — Rewrite question (if follow-up)
        logger.info("[Step 1/5] Rewriting question...")
        t0 = time.time()
        standalone = rewrite_question(request.question, history)
        t1 = time.time()
        if standalone != request.question:
            logger.info(f"  Rewritten: \"{standalone}\"")
        else:
            logger.info("  No rewrite needed (standalone question)")
        logger.info(f"  ⏱ Step 1 done in {t1 - t0:.2f}s")

        # Step 2 — Multi-query retrieval + RRF
        logger.info("[Step 2/5] Retrieving relevant chunks (multi-query + RRF)...")
        t0 = time.time()
        retrieved_docs = retrieve(standalone)
        t1 = time.time()
        logger.info(f"  Retrieved {len(retrieved_docs)} unique chunks")
        logger.info(f"  ⏱ Step 2 done in {t1 - t0:.2f}s")

        if not retrieved_docs:
            logger.warning("  No relevant documents found — returning early")
            logger.info(f"CHAT PIPELINE END — total: {time.time() - pipeline_start:.2f}s (no docs)")
            return ChatResponse(
                answer="No relevant documents found. Please upload some KT docs first.",
                sources=[],
                rewritten_question=standalone,
            )

        # Step 3 — Cohere rerank
        logger.info(f"[Step 3/5] Reranking {len(retrieved_docs)} chunks with Cohere...")
        t0 = time.time()
        reranked_docs = rerank(standalone, retrieved_docs)
        t1 = time.time()
        logger.info(f"  Kept {len(reranked_docs)} chunks after reranking")
        for i, doc in enumerate(reranked_docs):
            score = doc.metadata.get("rerank_score", "N/A")
            name = doc.metadata.get("doc_name", "unknown")
            logger.info(f"    [{i+1}] {name} (chunk {doc.metadata.get('chunk_index', '?')}) — score: {score}")
        logger.info(f"  ⏱ Step 3 done in {t1 - t0:.2f}s")

        # Step 4 — Generate answer
        logger.info(f"[Step 4/5] Generating answer with OpenAI ({len(reranked_docs)} context chunks)...")
        t0 = time.time()
        answer = generate_answer(question=request.question, docs=reranked_docs, history=history)
        t1 = time.time()
        logger.info(f"  Answer length: {len(answer)} chars")
        logger.info(f"  ⏱ Step 4 done in {t1 - t0:.2f}s")

        # Step 5 — Build response
        logger.info("[Step 5/5] Building response...")
        answered_from_docs = "📄 From Documents" in answer or "[SOURCE" in answer
        sources = []
        if answered_from_docs:
            sources = [
                SourceResult(
                    doc_name=doc.metadata.get("doc_name", "unknown"),
                    doc_type=doc.metadata.get("doc_type", "unknown"),
                    chunk_text=doc.page_content,
                    chunk_index=doc.metadata.get("chunk_index", 0),
                    rerank_score=doc.metadata.get("rerank_score"),
                )
                for doc in reranked_docs
            ]
        logger.info(f"  Sources included: {len(sources)}")
        logger.info(f"  Answer type: {'from_docs' if answered_from_docs else 'from_agent'}")

        total_time = time.time() - pipeline_start
        logger.info("=" * 60)
        logger.info(f"CHAT PIPELINE END — total: {total_time:.2f}s")
        logger.info("=" * 60)

        return ChatResponse(
            answer=answer,
            sources=sources,
            rewritten_question=standalone if standalone != request.question else None,
        )
 
    except Exception as e:
        total_time = time.time() - pipeline_start
        logger.error(f"CHAT PIPELINE FAILED after {total_time:.2f}s — {e}")
        raise HTTPException(status_code=500, detail=str(e))