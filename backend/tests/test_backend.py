import requests
import json
import time
 
BASE_URL = "http://localhost:8000"
 
SAMPLE_FILES = [
    ("tests/sample_files/auth-service-KT.txt",   "kt_doc"),
    ("tests/sample_files/sprint-23-meeting.txt",  "transcript"),
]

TEST_QUESTIONS = [
    {
        "label": "Basic KT doc retrieval",
        "question": "How does token refresh work?",
        "history": [],
    },
    {
        "label": "Specific detail from KT doc",
        "question": "What are the error codes in the auth service?",
        "history": [],
    },
    {
        "label": "From transcript only",
        "question": "What was decided about the JWT key rotation schedule?",
        "history": [],
    },
    {
        "label": "Cross-document (both KT + transcript)",
        "question": "What was the bug that caused users to be randomly logged out and how was it fixed?",
        "history": [],
    },
    {
        "label": "Follow-up question (history-aware rewriting)",
        "question": "What was the fix?",
        "history": [
            {"role": "user",      "content": "What caused users to get randomly logged out?"},
            {"role": "assistant", "content": "The refresh token cookie domain was set incorrectly..."},
        ],
    },
    {
        "label": "LLM fallback (not in docs)",
        "question": "What is OAuth2 and how does it differ from JWT?",
        "history": [],
    },
]

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")
 
def print_section(text):
    print(f"\n── {text} ──")
 
def check_health():
    print_header("1. Health Check")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"✅ Server is running: {r.json()}")
 
 
def upload_documents():
    print_header("2. Uploading Sample Documents")
    doc_ids = []
 
    for file_path, doc_type in SAMPLE_FILES:
        with open(file_path, "rb") as f:
            files  = {"file": (file_path.split("/")[-1], f, "text/plain")}
            data   = {"doc_type": doc_type}
            r = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data)
 
        if r.status_code == 200:
            result = r.json()
            doc_ids.append(result["doc_id"])
            print(f"✅ Uploaded: {result['doc_name']}")
            print(f"   doc_id:      {result['doc_id']}")
            print(f"   doc_type:    {result['doc_type']}")
            print(f"   chunk_count: {result['chunk_count']}")
        else:
            print(f"❌ Upload failed for {file_path}: {r.status_code} {r.text}")
 
    return doc_ids
 
 
def list_documents():
    print_header("3. Listing Documents")
    r = requests.get(f"{BASE_URL}/api/documents")
    assert r.status_code == 200, f"List failed: {r.text}"
    docs = r.json()
    print(f"✅ Found {len(docs)} document(s) in ChromaDB:")
    for doc in docs:
        print(f"   - {doc['doc_name']} ({doc['doc_type']}) — {doc['chunk_count']} chunks — uploaded {doc['uploaded_at'][:19]}")
    return docs
 
 
def run_chat_tests():
    print_header("4. Running Chat Tests")
 
    for i, test in enumerate(TEST_QUESTIONS):
        print_section(f"Test {i+1}: {test['label']}")
        print(f"Q: {test['question']}")
 
        payload = {
            "question": test["question"],
            "history":  test["history"],
        }
 
        start = time.time()
        r = requests.post(f"{BASE_URL}/api/chat", json=payload)
        elapsed = round(time.time() - start, 2)
 
        if r.status_code != 200:
            print(f"❌ Chat failed: {r.status_code} {r.text}")
            continue
 
        result = r.json()
 
        # Show rewritten question if it changed
        if result.get("rewritten_question"):
            print(f"🔄 Rewritten to: {result['rewritten_question']}")
 
        print(f"\nA: {result['answer']}")
 
        print(f"\n📎 Sources ({len(result['sources'])}):")
        for src in result["sources"]:
            score = f"score={src['rerank_score']}" if src.get("rerank_score") else ""
            print(f"   - [{src['doc_type']}] {src['doc_name']} chunk {src['chunk_index']} {score}")
            print(f"     \"{src['chunk_text'][:100]}...\"")
 
        print(f"\n⏱  Response time: {elapsed}s")
        time.sleep(1)  # avoid rate limiting
 
 
def delete_documents(doc_ids):
    print_header("5. Cleanup — Deleting Test Documents")
    for doc_id in doc_ids:
        r = requests.delete(f"{BASE_URL}/api/documents/{doc_id}")
        if r.status_code == 200:
            result = r.json()
            print(f"✅ Deleted doc {doc_id[:8]}... — {result['chunks_deleted']} chunks removed")
        else:
            print(f"❌ Delete failed for {doc_id}: {r.status_code} {r.text}")
 
 
# ── Main ──────────────────────────────────────────────────────
 
if __name__ == "__main__":
    print("\n🚀 KT Base Backend Test Suite")
    print("Make sure uvicorn main:app --reload is running\n")
 
    try:
        check_health()
        doc_ids = upload_documents()
 
        if not doc_ids:
            print("\n❌ No documents uploaded. Aborting.")
            exit(1)
 
        print("\n⏳ Waiting 2s for ChromaDB to persist...")
        time.sleep(2)
 
        list_documents()
        run_chat_tests()
 
        # Comment out if you want to keep the docs in ChromaDB after testing
        delete_documents(doc_ids)
 
        print_header("✅ All tests complete")
 
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server.")
        print("   Make sure the server is running: uvicorn main:app --reload")
    except KeyboardInterrupt:
        print("\n\nAborted.")