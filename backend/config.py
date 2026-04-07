import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "kt_documents")

OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))

OPENAI_GENERATION_MODEL = os.getenv("OPENAI_GENERATION_MODEL", "gpt-4o-mini")


CHUNK_BREAKPOINT_TYPE = os.getenv("CHUNK_BREAKPOINT_TYPE", "percentile")
CHUNK_BREAKPOINT_AMOUNT = float(os.getenv("CHUNK_BREAKPOINT_AMOUNT", "70"))

TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "10"))
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))
MULTI_QUERY_COUNT = int(os.getenv("MULTI_QUERY_COUNT", "3"))
RRF_K = int(os.getenv("RRF_K", "60"))

COHERE_RERANK_MODEL = os.getenv("COHERE_RERANK_MODEL", "rerank-english-v3.0")

ANTHROPIC_GENERATION_MODEL = os.getenv("ANTHROPIC_GENERATION_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", 
"""
You are a helpful knowledge assistant for a software team.
You have access to the team's uploaded KT documents and meeting transcripts as context below.
 
Follow these rules STRICTLY. Never deviate from this format:
 
RULE 1 — ALWAYS start your response with either "📄 From Documents" OR "🤖 From Agent" as a standalone label on its own line.
 
RULE 2 — CONTEXT ANSWER:
   If the provided context contains relevant information, you MUST start with:
   📄 From Documents
   (then your answer citing sources in brackets e.g. [auth-service-KT.txt])
 
RULE 3 — LLM FALLBACK:
   If the context has NO relevant information, you MUST start with:
   🤖 From Agent
   This wasn't found in your uploaded documents. Based on general knowledge:
   (then your answer)
 
RULE 4 — MIXED ANSWER (most important):
   If the question can be PARTIALLY answered from context AND requires general knowledge,
   you MUST use BOTH sections in this exact order:
 
   📄 From Documents
   (answer the parts found in context, with citations)
 
   🤖 From Agent
   This wasn't found in your uploaded documents. Based on general knowledge:
   (answer the parts not in context)
 
RULE 5 — Never fabricate document citations. Only cite sources that exist in the provided context.
RULE 6 — Be concise and use bullet points where appropriate.
RULE 7 — The section labels "📄 From Documents" and "🤖 From Agent" must ALWAYS appear on their own line.""")

SUPPORTED_EXTENSIONS = {".pdf",".docx",".txt",".md"}

def validate_config():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set")
    if not COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY is not set")
    if not CHROMA_PERSIST_DIR:
        raise ValueError("CHROMA_PERSIST_DIR is not set")
    if not CHROMA_COLLECTION_NAME:
        raise ValueError("CHROMA_COLLECTION_NAME is not set")
    if not OPENAI_EMBEDDING_MODEL:
        raise ValueError("OPENAI_EMBEDDING_MODEL is not set")
    if not EMBEDDING_DIMENSION:
        raise ValueError("EMBEDDING_DIMENSION is not set")
    if not CHUNK_BREAKPOINT_TYPE:
        raise ValueError("CHUNK_BREAKPOINT_TYPE is not set")
    if not CHUNK_BREAKPOINT_AMOUNT:
        raise ValueError("CHUNK_BREAKPOINT_AMOUNT is not set")
    if not TOP_K_RETRIEVAL:
        raise ValueError("TOP_K_RETRIEVAL is not set")
    if not TOP_K_RERANK:
        raise ValueError("TOP_K_RERANK is not set")
    if not MULTI_QUERY_COUNT:
        raise ValueError("MULTI_QUERY_COUNT is not set")
    if not RRF_K:
        raise ValueError("RRF_K is not set")
    if not COHERE_RERANK_MODEL:
        raise ValueError("COHERE_RERANK_MODEL is not set")
    if not ANTHROPIC_GENERATION_MODEL:
        raise ValueError("ANTHROPIC_GENERATION_MODEL is not set")
    if not MAX_TOKENS:
        raise ValueError("MAX_TOKENS is not set")
    if not SYSTEM_PROMPT:
        raise ValueError("SYSTEM_PROMPT is not set")
    if not SUPPORTED_EXTENSIONS:
        raise ValueError("SUPPORTED_EXTENSIONS is not set")

    print("Config validated successfully")  