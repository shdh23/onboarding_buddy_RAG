import logging
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
 
from config import OPENAI_API_KEY, MULTI_QUERY_COUNT
 
logger = logging.getLogger(__name__)

MULTI_QUERY_PROMPT = ChatPromptTemplate.from_template(
    """You are an AI assistant helping to retrieve relevant information from a knowledge base.
 
Your task is to generate {count} different phrasings of the user's question below.
Each phrasing should approach the question from a slightly different angle to maximize retrieval coverage.
 
Rules:
- Output ONLY the rephrased questions, one per line
- No numbering, no bullets, no extra text
- Keep each question concise and specific
- Do not change the core intent of the question
 
Original question: {question}
 
{count} alternative phrasings:"""
)

def generate_query_variants(question: str) -> list[str]:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.0,)
    chain = MULTI_QUERY_PROMPT | llm | StrOutputParser()
    logger.info(f"  [MultiQuery] Generating {MULTI_QUERY_COUNT} variants via gpt-4o-mini...")

    try:
        t0 = time.time()
        output = chain.invoke({"question": question, "count": MULTI_QUERY_COUNT})
        t1 = time.time()
        logger.info(f"  [MultiQuery] LLM call: {t1 - t0:.2f}s")

        variants = [
            line.strip()
            for line in output.strip().split("\n")
            if line.strip()
        ]

        all_queries = [question] + variants

        logger.info(f"  [MultiQuery] {len(all_queries)} total queries (1 original + {len(variants)} variants)")
        for i, q in enumerate(all_queries):
            logger.info(f"    [{i}] {q}")

        return all_queries
 
    except Exception as e:
        logger.warning(f"  [MultiQuery] FAILED: {e} — falling back to original question only")
        return [question]