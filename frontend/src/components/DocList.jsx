import { useState } from "react"
import { deleteDocument } from "../api/client"

export default function DocList({ docs, onDelete }) {
  const [deletingId, setDeletingId] = useState(null)

  const handleDelete = async (docId) => {
    setDeletingId(docId)
    try {
      await deleteDocument(docId)
      onDelete(docId)
    } catch (err) {
      console.error("Delete failed:", err)
    } finally {
      setDeletingId(null)
    }
  }

  if (docs.length === 0) {
    return (
      <div style={{ padding: "40px 0", textAlign: "center" }}>
        <p style={{ fontSize: "13px", color: "#8B8580", fontWeight: 500 }}>No documents yet</p>
        <p style={{ fontSize: "12px", color: "rgba(139,133,128,0.5)", marginTop: "4px" }}>Upload a file to get started</p>
      </div>
    )
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      {docs.map((doc) => {
        const isKT = doc.doc_type === "kt_doc"
        const isDeleting = deletingId === doc.doc_id

        return (
          <div
            key={doc.doc_id}
            className="group"
            style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px", borderRadius: "12px", transition: "background 0.1s", cursor: "default" }}
            onMouseEnter={e => e.currentTarget.style.backgroundColor = "rgba(243,237,229,0.6)"}
            onMouseLeave={e => e.currentTarget.style.backgroundColor = "transparent"}
          >
            <div style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: "#F3EDE5", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "14px", flexShrink: 0 }}>
              {isKT ? "📄" : "🎙️"}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontSize: "13px", fontWeight: 500, color: "#1A1915", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{doc.doc_name}</p>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "2px" }}>
                <span style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  padding: "2px 6px",
                  borderRadius: "6px",
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                  backgroundColor: isKT ? "rgba(217,119,87,0.1)" : "rgba(91,154,111,0.1)",
                  color: isKT ? "#D97757" : "#5B9A6F",
                }}>
                  {isKT ? "KT" : "Transcript"}
                </span>
                <span style={{ fontSize: "11px", color: "#8B8580" }}>{doc.chunk_count} chunks</span>
              </div>
            </div>

            <button
              onClick={() => handleDelete(doc.doc_id)}
              disabled={isDeleting}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
              style={{ color: "#8B8580", flexShrink: 0, cursor: isDeleting ? "not-allowed" : "pointer", background: "none", border: "none" }}
              title="Delete document"
            >
              <svg style={{ width: "16px", height: "16px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )
      })}
    </div>
  )
}
