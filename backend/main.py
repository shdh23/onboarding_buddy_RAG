import logging
from contextlib import asynccontextmanager
 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from config import validate_config
 
# Configure logging once at startup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    logger.info("Starting KT Base API...")
    validate_config()
    logger.info("Config validated — all API keys present")
    yield
    logger.info("Shutting down KT Base API")

app = FastAPI(
    title="KT Base API",
    description="RAG-powered knowledge assistant for KT docs and meeting transcripts",
    version="1.0.0",
    lifespan=lifespan,
)
 
app.add_middleware(
    CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import documents, chat

app.include_router(documents.router, prefix="/api/documents",
tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "kt-base-api"}