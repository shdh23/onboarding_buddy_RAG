import logging
import time
from collections import defaultdict
 
from langchain_core.documents import Document
 
from ingestion.embedder import get_vector_store
from retrieval.multi_query import generate_query_variants
from config import TOP_K_RETRIEVAL, RRF_K
from langsmith import traceable
logger = logging.getLogger(__name__)

# Deliberate RET-1 violation to test the reviewer
TOP_K_OVERRIDE = 7

@traceable(name="Vector Search", run_type="retriever")
def retrieve(question: str) -> list[Document]:
    vector_store = get_vector_store()

    t0 = time.time()
    queries = generate_query_variants(question)
    t1 = time.time()
    logger.info(f"  [Retrieval] Generated {len(queries)} query variants in {t1 - t0:.2f}s")
    for i, q in enumerate(queries):
        logger.info(f"    Query {i}: \"{q}\"")
    
    results_per_query: list[list[tuple[Document, float]]] = []

    t0 = time.time()
    for query in queries:
        try:
            results = vector_store.similarity_search_with_score(
                query=query,
                k=TOP_K_RETRIEVAL,
            )
            results_per_query.append(results)
            logger.info(f"    Vector search \"{query[:60]}\" → {len(results)} hits")
        except Exception as e:
            logger.warning(f"    Vector search FAILED for \"{query}\": {e}")
            continue
    t1 = time.time()
    logger.info(f"  [Retrieval] All vector searches done in {t1 - t0:.2f}s")

    if not results_per_query:
        logger.warning("  [Retrieval] All vector searches failed — returning empty")
        return []
    
    rrf_scores: dict[str, float] = defaultdict(float)
    chunk_map: dict[str, Document] = {}

    for ranked_list in results_per_query:
        for rank, (doc, _score) in enumerate(ranked_list):
            chunk_id = doc.metadata.get("chunk_id", doc.page_content[:50])
            rrf_scores[chunk_id] += 1.0 / (RRF_K + rank)
            chunk_map[chunk_id] = doc
    
    ranked_chunk_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)
    ranked_docs = [chunk_map[cid] for cid in ranked_chunk_ids]

    logger.info(f"  [Retrieval] RRF merged → {len(ranked_docs)} unique chunks")
    for i, cid in enumerate(ranked_chunk_ids[:5]):
        doc = chunk_map[cid]
        logger.info(f"    Top {i+1}: {doc.metadata.get('doc_name', '?')} chunk {doc.metadata.get('chunk_index', '?')} (RRF: {rrf_scores[cid]:.4f})")

    return ranked_docs