import { useEffect, useRef, useState } from "react"
import SourceCard from "./SourceCard"

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-fade-slide">
      <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#D97757", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <svg style={{ width: "18px", height: "18px", color: "white" }} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2a1 1 0 011 1v1.07A7.002 7.002 0 0119 11v1a3 3 0 013 3v1a3 3 0 01-3 3h-1a5.002 5.002 0 01-4 2H10a5.002 5.002 0 01-4-2H5a3 3 0 01-3-3v-1a3 3 0 013-3v-1a7.002 7.002 0 016-6.93V3a1 1 0 011-1zM7 11a5 5 0 0010 0V10a5 5 0 00-10 0v1zm-2 3a1 1 0 00-1 1v1a1 1 0 001 1h1v-3H5zm14 0h-1v3h1a1 1 0 001-1v-1a1 1 0 00-1-1zm-9.5-3a1.5 1.5 0 100 3 1.5 1.5 0 000-3zm5 0a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>
        </svg>
      </div>
      <div className="bg-surface rounded-2xl rounded-tl-lg px-4 py-3 shadow-soft">
        <div className="flex gap-1.5 items-center h-5">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  )
}

function UserMessage({ message }) {
  return (
    <div className="flex justify-end animate-fade-slide">
      <div className="max-w-[70%] rounded-2xl rounded-br-lg shadow-soft" style={{ backgroundColor: "#2F2F2A", color: "#FAF8F5", padding: "14px 20px" }}>
        <p className="text-[14px] leading-[1.6] whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </div>
  )
}

function SourcesCollapsible({ sources }) {
  const [open, setOpen] = useState(false)

  return (
    <div style={{ marginLeft: "2px" }}>
      <button
        onClick={() => setOpen(v => !v)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          background: "none",
          border: "none",
          cursor: "pointer",
          padding: "6px 12px",
          borderRadius: "8px",
          transition: "background 0.15s",
          backgroundColor: open ? "rgba(217,119,87,0.06)" : "transparent",
        }}
        onMouseEnter={e => { if (!open) e.currentTarget.style.backgroundColor = "rgba(0,0,0,0.03)" }}
        onMouseLeave={e => { if (!open) e.currentTarget.style.backgroundColor = "transparent" }}
      >
        <svg style={{ width: "12px", height: "12px", color: "#8B8580", transition: "transform 0.2s", transform: open ? "rotate(180deg)" : "none" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
        <span style={{ fontSize: "12px", fontWeight: 600, color: "#8B8580" }}>
          {sources.length} source{sources.length > 1 ? "s" : ""} found
        </span>
      </button>

      {open && (
        <div className="animate-fade-slide" style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "8px" }}>
          {sources.map((src, i) => (
            <SourceCard key={i} source={src} />
          ))}
        </div>
      )}
    </div>
  )
}

function AssistantMessage({ message }) {
  const hasDocs    = message.sources?.length > 0
  const hasRewrite = message.rewrittenQuestion

  const renderAnswer = (content) => {
    const docSection   = content.includes("📄 From Documents")
    const agentSection = content.includes("🤖 From Agent")

    if (!docSection && !agentSection) {
      return <p className="text-[14px] text-text leading-[1.6] whitespace-pre-wrap">{content}</p>
    }

    return content.split(/(📄 From Documents|🤖 From Agent)/).map((part, i) => {
      if (part === "📄 From Documents") {
        return <p key={i} style={{ fontSize: "12px", fontWeight: 600, color: "#D97757", textTransform: "uppercase", letterSpacing: "0.04em", marginTop: "8px", marginBottom: "8px" }}>📄 From Documents</p>
      }
      if (part === "🤖 From Agent") {
        return <p key={i} style={{ fontSize: "12px", fontWeight: 600, color: "#D97757", textTransform: "uppercase", letterSpacing: "0.04em", marginTop: "24px", marginBottom: "8px" }}>🤖 From Agent</p>
      }
      if (part.trim()) {
        return <p key={i} style={{ fontSize: "14px", color: "#1A1915", lineHeight: 1.6, whiteSpace: "pre-wrap" }}>{part.trim()}</p>
      }
      return null
    })
  }

  return (
    <div className="flex items-start gap-3 animate-fade-slide">
      <div style={{ width: "32px", height: "32px", borderRadius: "10px", background: "#D97757", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
        <svg style={{ width: "18px", height: "18px", color: "white" }} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2a1 1 0 011 1v1.07A7.002 7.002 0 0119 11v1a3 3 0 013 3v1a3 3 0 01-3 3h-1a5.002 5.002 0 01-4 2H10a5.002 5.002 0 01-4-2H5a3 3 0 01-3-3v-1a3 3 0 013-3v-1a7.002 7.002 0 016-6.93V3a1 1 0 011-1zM7 11a5 5 0 0010 0V10a5 5 0 00-10 0v1zm-2 3a1 1 0 00-1 1v1a1 1 0 001 1h1v-3H5zm14 0h-1v3h1a1 1 0 001-1v-1a1 1 0 00-1-1zm-9.5-3a1.5 1.5 0 100 3 1.5 1.5 0 000-3zm5 0a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>
        </svg>
      </div>

      <div className="flex-1 min-w-0 space-y-2.5 max-w-[80%]">
        {hasRewrite && (
          <p className="text-[12px] text-muted italic ml-0.5">
            Interpreted as: "{message.rewrittenQuestion}"
          </p>
        )}

        <div className="bg-surface rounded-2xl rounded-tl-lg shadow-soft" style={{ padding: "16px 20px", display: "flex", flexDirection: "column", gap: "10px" }}>
          {renderAnswer(message.content)}
        </div>

        {hasDocs && (
          <SourcesCollapsible sources={message.sources} />
        )}
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center gap-6 text-center px-8">
      <div style={{ width: "64px", height: "64px", borderRadius: "16px", background: "#D97757", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 16px rgba(217,119,87,0.25)" }}>
        <svg style={{ width: "34px", height: "34px", color: "white" }} fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2a1 1 0 011 1v1.07A7.002 7.002 0 0119 11v1a3 3 0 013 3v1a3 3 0 01-3 3h-1a5.002 5.002 0 01-4 2H10a5.002 5.002 0 01-4-2H5a3 3 0 01-3-3v-1a3 3 0 013-3v-1a7.002 7.002 0 016-6.93V3a1 1 0 011-1zM7 11a5 5 0 0010 0V10a5 5 0 00-10 0v1zm-2 3a1 1 0 00-1 1v1a1 1 0 001 1h1v-3H5zm14 0h-1v3h1a1 1 0 001-1v-1a1 1 0 00-1-1zm-9.5-3a1.5 1.5 0 100 3 1.5 1.5 0 000-3zm5 0a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>
        </svg>
      </div>
      <div className="space-y-3">
        <h1 className="text-[28px] font-extrabold text-text tracking-tight">Onboarding Buddy</h1>
        <p className="text-[15px] text-muted leading-relaxed max-w-md">
          Upload your onboarding docs and meeting transcripts, then ask questions grounded in your team's knowledge.
        </p>
      </div>
      <div style={{ display: "flex", gap: "12px", marginTop: "4px" }}>
        <span className="text-[13px] font-semibold text-text bg-surface rounded-xl px-4 py-2 shadow-soft">📄 KT Docs</span>
        <span className="text-[13px] font-semibold text-text bg-surface rounded-xl px-4 py-2 shadow-soft">🎙️ Transcripts</span>
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return <EmptyState />
  }

  return (
    <div className="flex-1 overflow-y-auto" style={{ paddingLeft: "48px", paddingRight: "48px", paddingTop: "24px", paddingBottom: "24px" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
        {messages.map((msg) =>
          msg.role === "user"
            ? <UserMessage key={msg.id} message={msg} />
            : <AssistantMessage key={msg.id} message={msg} />
        )}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
