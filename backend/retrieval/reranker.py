import logging
import time
import cohere
from langchain_core.documents import Document
from config import COHERE_API_KEY, COHERE_RERANK_MODEL, TOP_K_RERANK
from langsmith import traceable
 
logger = logging.getLogger(__name__)
 
co = cohere.Client(COHERE_API_KEY)

@traceable(name="Cohere Rerank", run_type="chain")
def rerank(question: str, docs: list[Document]) -> list[Document]:
    if not docs:
        logger.warning("No documents to rerank — returning empty list")
        return []
    
    # Cohere expects plain strings
    passages = [doc.page_content for doc in docs]

    logger.info(f"  [Rerank] Sending {len(docs)} chunks to Cohere ({COHERE_RERANK_MODEL}, top_n={TOP_K_RERANK})")
    
    try:
        t0 = time.time()
        response = co.rerank(
            model=COHERE_RERANK_MODEL,
            query=question,
            documents=passages,
            top_n=TOP_K_RERANK,
        )
        t1 = time.time()
        logger.info(f"  [Rerank] Cohere API call: {t1 - t0:.2f}s")

        MIN_SCORE = 0.15
        MIN_CHUNKS = 3
        reranked_docs = []
        below_threshold = []
        for result in response.results:
            score = round(result.relevance_score, 4)
            doc = docs[result.index]
            doc.metadata["rerank_score"] = score
            if score >= MIN_SCORE:
                reranked_docs.append(doc)
            else:
                below_threshold.append(doc)

        if len(reranked_docs) < MIN_CHUNKS:
            needed = MIN_CHUNKS - len(reranked_docs)
            reranked_docs.extend(below_threshold[:needed])
            logger.info(f"  [Rerank] Added {needed} low-score chunks to meet minimum of {MIN_CHUNKS}")

        logger.info(f"  [Rerank] Kept {len(reranked_docs)} chunks (min_score={MIN_SCORE}, min_chunks={MIN_CHUNKS})")
        for i, doc in enumerate(reranked_docs):
            logger.info(
                f"    [{i+1}] score={doc.metadata['rerank_score']} "
                f"src={doc.metadata.get('doc_name')} "
                f"chunk={doc.metadata.get('chunk_index')}"
            )

        return reranked_docs
 
    except Exception as e:
        logger.warning(f"  [Rerank] Cohere FAILED: {e} — falling back to RRF order (top {TOP_K_RERANK})")
        return docs[:TOP_K_RERANK]