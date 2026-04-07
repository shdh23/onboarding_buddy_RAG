import { useState } from "react"

export default function SourceCard({ source }) {
  const [expanded, setExpanded] = useState(false)

  const isKT      = source.doc_type === "kt_doc"
  const typeLabel = isKT ? "KT" : "Transcript"
  const score     = source.rerank_score != null
    ? `${Math.round(source.rerank_score * 100)}%`
    : null

  return (
    <div
      style={{
        border: `1px solid ${isKT ? "rgba(217,119,87,0.15)" : "rgba(91,154,111,0.15)"}`,
        backgroundColor: isKT ? "rgba(217,119,87,0.04)" : "rgba(91,154,111,0.04)",
        borderRadius: "12px",
        cursor: "pointer",
        transition: "all 0.15s",
      }}
      onClick={() => setExpanded((v) => !v)}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "8px 12px", fontSize: "12px" }}>
        <span>{isKT ? "📄" : "🎙️"}</span>
        <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontWeight: 600, color: "#1A1915" }}>{source.doc_name}</span>
        <span style={{ fontSize: "10px", fontWeight: 700, color: "#8B8580", textTransform: "uppercase", letterSpacing: "0.04em" }}>{typeLabel}</span>
        {score && <span style={{ fontSize: "11px", color: "#8B8580" }}>· {score}</span>}
        <svg style={{ width: "12px", height: "12px", color: "#8B8580", transition: "transform 0.15s", transform: expanded ? "rotate(180deg)" : "none" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {expanded && (
        <div style={{ padding: "2px 12px 12px", borderTop: "1px solid rgba(0,0,0,0.06)" }}>
          <p style={{ fontSize: "12px", lineHeight: 1.6, color: "#8B8580" }}>
            {source.chunk_text}
          </p>
        </div>
      )}
    </div>
  )
}
