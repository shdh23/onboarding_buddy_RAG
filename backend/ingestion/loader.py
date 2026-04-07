import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from config import SUPPORTED_EXTENSIONS
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def load_document(file_path: Path, doc_id: str, doc_name: str, doc_type: str) -> list[Document]:
    path = Path(file_path)
    ext = path.suffix
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    
    logger.info(f"Loading document: {path}")
    if ext == ".pdf":
        loader = PyPDFLoader(path)
    elif ext == ".docx":
        loader = Docx2txtLoader(path)
    elif ext == ".txt":
        loader = TextLoader(path)
    elif ext == ".md":
        loader = TextLoader(path)

    
    docs = loader.load() # This will list of langchain documents
    if not docs:
        raise RuntimeError(f"No documents loaded from {path}")
    
    for doc in docs:
        doc.metadata.update({
            "doc_id":   doc_id,
            "doc_name": doc_name,
            "doc_type": doc_type,   # "kt_doc" | "transcript"
        })
    
    total_chars = sum(len(doc.page_content) for doc in docs)
    logger.info(f"Loaded {len(docs)} documents with {total_chars} characters")
    return docs

if __name__ == "__main__":
    docs = load_document("test.pdf")
    print(docs)