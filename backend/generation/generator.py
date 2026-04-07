import logging
import time
from openai import OpenAI
from langchain_core.documents import Document

from config import (
    OPENAI_API_KEY,
    OPENAI_GENERATION_MODEL,
    MAX_TOKENS,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

REWRITE_PROMPT = """Given the conversation history below and a follow-up question,
rewrite the follow-up question as a fully standalone question that contains
all the context needed to retrieve relevant information.
 
If the follow-up question is already standalone and doesn't reference the history, return it unchanged.
Return ONLY the rewritten question, nothing else.
 
Conversation history:
{history}
 
Follow-up question: {question}
 
Standalone question:"""

def rewrite_question(question: str, history: list[dict]) -> str:
    if not history:
        logger.info("  [Rewrite] No history — skipping rewrite")
        return question
 
    logger.info(f"  [Rewrite] History has {len(history)} messages, using last {min(6, len(history))}")
    history_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in history[-6:]
    )
 
    try:
        t0 = time.time()
        response = client.chat.completions.create(
            model=OPENAI_GENERATION_MODEL,
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": REWRITE_PROMPT.format(
                    history=history_text,
                    question=question,
                )
            }]
        )
        t1 = time.time()
        rewritten = response.choices[0].message.content.strip()
        usage = response.usage
        logger.info(f"  [Rewrite] OpenAI call: {t1 - t0:.2f}s | tokens: {usage.prompt_tokens} in / {usage.completion_tokens} out")
        if rewritten != question:
            logger.info(f"  [Rewrite] \"{question}\" → \"{rewritten}\"")
        else:
            logger.info("  [Rewrite] Question unchanged")
        return rewritten
 
    except Exception as e:
        logger.warning(f"  [Rewrite] Failed: {e}. Using original question.")
        return question
 
def build_context(docs: list[Document]) -> str:
    """
    Formats the reranked chunks into a clearly labeled context block
    that Claude can reason over and cite from.
    """
    context_parts = []
 
    for i, doc in enumerate(docs):
        doc_name = doc.metadata.get("doc_name", "Unknown")
        doc_type = doc.metadata.get("doc_type", "unknown")
        chunk_index = doc.metadata.get("chunk_index", i)
        rerank_score = doc.metadata.get("rerank_score", "")
 
        type_label = "KT Document" if doc_type == "kt_doc" else "Meeting Transcript"
        score_label = f" | relevance: {rerank_score}" if rerank_score else ""
 
        header = f"[SOURCE {i+1}: {doc_name} | {type_label} | chunk {chunk_index}{score_label}]"
        context_parts.append(f"{header}\n{doc.page_content}")
 
    return "\n\n---\n\n".join(context_parts)

def generate_answer(
    question: str,
    docs: list[Document],
    history: list[dict],
) -> str:

    # Step 1 — rewrite question if follow-up
    standalone_question = rewrite_question(question, history)

    # Step 2 — build context
    context = build_context(docs)

    # Step 3 — build messages
    # Inject context into the first user message so it's always visible
    user_message_with_context = f"""Context from uploaded documents:
---
{context}
---
 
Question: {standalone_question}"""
 
    # Build full message list: history + current question with context
    messages = []
 
    # Add prior conversation turns (without context — only current turn gets it)
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })
 
    # Add current question with context attached
    messages.append({
        "role": "user",
        "content": user_message_with_context,
    })
 
    context_chars = sum(len(doc.page_content) for doc in docs)
    logger.info(f"  [Generate] Context: {len(docs)} chunks, {context_chars:,} chars")
    logger.info(f"  [Generate] Calling OpenAI {OPENAI_GENERATION_MODEL} (max_tokens={MAX_TOKENS})...")

    try:
        t0 = time.time()
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = client.chat.completions.create(
            model=OPENAI_GENERATION_MODEL,
            max_tokens=MAX_TOKENS,
            messages=full_messages,
        )
        t1 = time.time()

        answer = response.choices[0].message.content.strip()
        usage = response.usage
        logger.info(f"  [Generate] OpenAI call: {t1 - t0:.2f}s | tokens: {usage.prompt_tokens} in / {usage.completion_tokens} out")
        logger.info(f"  [Generate] Answer: {len(answer)} chars")
        return answer

    except Exception as e:
        logger.error(f"  [Generate] OpenAI FAILED: {e}")
        raise RuntimeError(f"Answer generation failed: {str(e)}")