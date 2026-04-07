import { useState, useEffect } from "react"
import UploadZone from "./UploadZone"
import DocList from "./DocList"
import LoadingSkeleton from "./LoadingSkeleton"
import { fetchDocuments } from "../api/client"

export default function Sidebar({ onDocCountChange }) {
  const [docs, setDocs]       = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDocuments()
      .then((data) => setDocs(data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    onDocCountChange?.(docs.length)
  }, [docs.length])

  const handleUploadSuccess = (result) => {
    setDocs((prev) => [
      {
        doc_id:      result.doc_id,
        doc_name:    result.doc_name,
        doc_type:    result.doc_type,
        chunk_count: result.chunk_count,
        uploaded_at: new Date().toISOString(),
      },
      ...prev,
    ])
  }

  const handleDelete = (docId) => {
    setDocs((prev) => prev.filter((d) => d.doc_id !== docId))
  }

  return (
    <aside style={{ width: "280px", flexShrink: 0, backgroundColor: "#EDE7DF", borderRight: "1px solid #E5DED4", display: "flex", flexDirection: "column", overflow: "hidden" }}>

      {/* Upload Section */}
      <div style={{ flexShrink: 0, backgroundColor: "#FAF8F5", padding: "20px 16px 24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "20px" }}>
          <div style={{ width: "24px", height: "24px", borderRadius: "8px", backgroundColor: "rgba(217,119,87,0.12)", display: "flex", alignItems: "center", justifyContent: "center", color: "#8B8580", fontSize: "12px" }}>↑</div>
          <h3 style={{ fontSize: "13px", fontWeight: 800, color: "#1A1915", letterSpacing: "-0.01em" }}>
            Upload
          </h3>
        </div>
        <UploadZone onUploadSuccess={handleUploadSuccess} />
      </div>

      {/* Spacer */}
      <div style={{ minHeight: "20px", flexShrink: 0, backgroundColor: "#EDE7DF", display: "flex", alignItems: "center", padding: "0 16px" }}>
        <div style={{ width: "100%", borderTop: "1px solid #E5DED4" }} />
      </div>

      {/* Documents Section */}
      <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", backgroundColor: "#EDE7DF", padding: "12px 16px 16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ width: "24px", height: "24px", borderRadius: "8px", backgroundColor: "rgba(217,119,87,0.12)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "12px" }}>📄</div>
            <h3 style={{ fontSize: "13px", fontWeight: 800, color: "#1A1915", letterSpacing: "-0.01em" }}>
              Documents
            </h3>
          </div>
          {docs.length > 0 && (
            <span style={{ fontSize: "10px", fontWeight: 700, color: "white", backgroundColor: "#D97757", borderRadius: "9999px", padding: "2px 8px", minWidth: "20px", textAlign: "center" }}>
              {docs.length}
            </span>
          )}
        </div>

        <div style={{ flex: 1, overflowY: "auto", borderRadius: "12px", backgroundColor: "#FAF8F5", border: "1px solid #E5DED4", padding: "8px" }}>
          {loading
            ? <LoadingSkeleton rows={3} />
            : <DocList docs={docs} onDelete={handleDelete} />
          }
        </div>
      </div>

    </aside>
  )
}
