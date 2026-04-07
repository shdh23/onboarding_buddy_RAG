import logging
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from config import CHUNK_BREAKPOINT_TYPE, CHUNK_BREAKPOINT_AMOUNT
from langchain_core.documents import Document
from langsmith import traceable
from config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    CHUNK_BREAKPOINT_TYPE,
    CHUNK_BREAKPOINT_AMOUNT,
)

logger = logging.getLogger(__name__)

def build_chunker() -> SemanticChunker:
    embeddings = OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    chunker = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type=CHUNK_BREAKPOINT_TYPE,
        breakpoint_threshold_amount=CHUNK_BREAKPOINT_AMOUNT
    )
    logger.info(f"Semantic Chunker ready! Built with {CHUNK_BREAKPOINT_TYPE} and {CHUNK_BREAKPOINT_AMOUNT}")

    return chunker

@traceable(name="Semantic Chunking", run_type="chain")
def chunk_documents(docs: list[Document]) -> list[Document]:
    chunker = build_chunker()
    all_chunks: list[Document] = []

    for doc in docs:
        if not doc.page_content.strip():
            logger.warning(f"Skipping empty section in {doc.metadata.get('doc_name')}")
            continue
        
        chunks = chunker.create_documents(
            texts=[doc.page_content],
            metadatas=[doc.metadata])
        
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = total
 
        all_chunks.extend(chunks)
        logger.info(
            f"{doc.metadata.get('doc_name')} → {total} chunk(s)"
        )
 
    logger.info(f"Chunking complete — {len(all_chunks)} total chunks across {len(docs)} document section(s)")
    return all_chunks