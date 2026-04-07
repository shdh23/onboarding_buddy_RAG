import { useState, useRef } from "react"
import { uploadDocument } from "../api/client"

const DOC_TYPES = [
  { value: "kt_doc",     label: "📄 KT Document",       desc: "Knowledge transfer docs, guides, wikis" },
  { value: "transcript", label: "🎙️ Meeting Transcript", desc: "Meeting notes, call recordings, standups" },
]

const ACCEPTED       = ".pdf,.docx,.txt,.md"
const MAX_SIZE_MB    = 20
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

export default function UploadZone({ onUploadSuccess }) {
  const [pendingFile, setPendingFile] = useState(null)
  const [dragging, setDragging]       = useState(false)
  const [uploading, setUploading]     = useState(false)
  const [error, setError]             = useState(null)
  const inputRef = useRef()

  const validate = (file) => {
    if (!file) return "No file selected."
    const ext = "." + file.name.split(".").pop().toLowerCase()
    if (!ACCEPTED.includes(ext)) return `Unsupported type: ${ext}. Use PDF, DOCX, TXT or MD.`
    if (file.size > MAX_SIZE_BYTES) return `File too large. Max size is ${MAX_SIZE_MB}MB.`
    if (file.size === 0) return "File is empty."
    return null
  }

  const handleFilePicked = (file) => {
    const validationError = validate(file)
    if (validationError) { setError(validationError); return }
    setError(null)
    setPendingFile(file)
  }

  const handleUpload = async (docType) => {
    if (!pendingFile) return
    setUploading(true)
    setError(null)

    try {
      const result = await uploadDocument(pendingFile, docType)
      onUploadSuccess(result)
      setPendingFile(null)
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Please try again.")
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ""
    }
  }

  const handleCancel = () => {
    setPendingFile(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ""
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFilePicked(e.dataTransfer.files[0])
  }

  if (pendingFile && !uploading) {
    return (
      <div className="animate-fade-slide" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", backgroundColor: "#F3EDE5", borderRadius: "12px", padding: "10px 12px" }}>
          <span style={{ fontSize: "14px" }}>📎</span>
          <p style={{ flex: 1, fontSize: "13px", fontWeight: 500, color: "#1A1915", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{pendingFile.name}</p>
          <button onClick={handleCancel} className="text-muted hover:text-danger transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <p style={{ fontSize: "12px", fontWeight: 600, color: "#1A1915" }}>What type of document is this?</p>

        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {DOC_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => handleUpload(t.value)}
              style={{ textAlign: "left", padding: "12px 14px", borderRadius: "12px", border: "1px solid #E5DED4", backgroundColor: "#FAF8F5", cursor: "pointer", transition: "all 0.15s" }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = "#D97757"; e.currentTarget.style.boxShadow = "0 1px 3px rgba(26,25,21,0.05)" }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = "#E5DED4"; e.currentTarget.style.boxShadow = "none" }}
            >
              <p style={{ fontSize: "13px", fontWeight: 600, color: "#1A1915" }}>{t.label}</p>
              <p style={{ fontSize: "11px", color: "#8B8580", marginTop: "2px" }}>{t.desc}</p>
            </button>
          ))}
        </div>

        {error && <p style={{ fontSize: "12px", color: "#C4453A", fontWeight: 500 }}>{error}</p>}
      </div>
    )
  }

  if (uploading) {
    return (
      <div style={{ borderRadius: "12px", border: "2px dashed rgba(217,119,87,0.3)", padding: "24px", textAlign: "center" }} className="animate-fade-slide">
        <div style={{ width: "24px", height: "24px", border: "2px solid rgba(217,119,87,0.3)", borderTop: "2px solid #D97757", borderRadius: "50%", margin: "0 auto" }} className="animate-spin" />
        <p style={{ fontSize: "13px", color: "#1A1915", fontWeight: 600, marginTop: "12px" }}>Ingesting {pendingFile?.name}...</p>
        <p style={{ fontSize: "12px", color: "#8B8580", marginTop: "4px" }}>Chunking + embedding, please wait</p>
      </div>
    )
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        style={{
          borderRadius: "12px",
          padding: "24px",
          textAlign: "center",
          cursor: "pointer",
          transition: "all 0.15s",
          border: dragging ? "2px dashed #D97757" : "2px dashed #E5DED4",
          backgroundColor: dragging ? "rgba(217,119,87,0.04)" : "transparent",
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          style={{ display: "none" }}
          onChange={(e) => handleFilePicked(e.target.files[0])}
        />

        <div style={{ display: "flex", flexDirection: "column", gap: "8px", alignItems: "center" }}>
          <div style={{ width: "40px", height: "40px", borderRadius: "12px", backgroundColor: "#F3EDE5", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg style={{ width: "20px", height: "20px", color: "#8B8580" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <p style={{ fontSize: "13px", color: "#1A1915", fontWeight: 600 }}>Upload file</p>
          <p style={{ fontSize: "12px", color: "#8B8580" }}>PDF, DOCX, TXT, MD · max {MAX_SIZE_MB}MB</p>
        </div>
      </div>

      {error && <p style={{ fontSize: "12px", color: "#C4453A", fontWeight: 500 }}>{error}</p>}
    </div>
  )
}
