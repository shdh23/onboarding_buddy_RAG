import { useState, useRef, useEffect } from "react"

export default function ChatInput({ onSend, isLoading, disabled }) {
  const [value, setValue] = useState("")
  const textareaRef = useRef()

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = Math.min(el.scrollHeight, 160) + "px"
  }, [value])

  const handleSend = () => {
    const q = value.trim()
    if (!q || isLoading || disabled) return
    onSend(q)
    setValue("")
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const canSend = value.trim() && !isLoading && !disabled

  return (
    <div className="px-6 py-4 bg-bg">
      <div className={`flex items-end gap-3 bg-surface rounded-2xl pl-6 pr-5 py-3 transition-all duration-150 shadow-soft ${
        disabled ? "opacity-50" : "focus-within:shadow-input"
      }`}>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Upload a document first..." : "Ask a question about your docs..."}
          disabled={isLoading || disabled}
          rows={1}
          style={{ paddingLeft: "8px" }}
          className="flex-1 min-w-0 bg-transparent text-[14px] text-text placeholder-muted resize-none outline-none leading-[1.5] min-h-[36px] py-1.5 disabled:cursor-not-allowed"
        />

        <button
          onClick={handleSend}
          disabled={!canSend}
          style={canSend ? {
            backgroundColor: "#D97757",
            color: "white",
            boxShadow: "0 2px 8px rgba(217,119,87,0.3)"
          } : {
            backgroundColor: "#E5DED4",
            color: "#B8AFA3"
          }}
          className="flex-shrink-0 h-10 w-20 rounded-xl text-[14px] font-bold flex items-center justify-center transition-all duration-150 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              Send
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          )}
        </button>
      </div>

      <p style={{ color: "rgba(139,133,128,0.4)" }} className="text-[11px] mt-2 text-center font-medium">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  )
}
