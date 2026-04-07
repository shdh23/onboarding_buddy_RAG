import { useState } from "react"
import Sidebar from "./components/Sidebar"
import ChatWindow from "./components/ChatWindow"
import ChatInput from "./components/ChatInput"
import ErrorBanner from "./components/ErrorBanner"
import { useChat } from "./hooks/useChat"

export default function App() {
  const { messages, isLoading, error, sendQuestion, clearChat, clearError } = useChat()
  const [docCount, setDocCount] = useState(0)

  return (
    <div className="h-full flex flex-col bg-bg">
      {/* Header */}
      <header className="flex items-center justify-between px-6 h-14 bg-surface border-b border-border flex-shrink-0">
        <div className="flex items-center gap-3">
          <div style={{ width: "28px", height: "28px", borderRadius: "8px", background: "#D97757", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg style={{ width: "16px", height: "16px", color: "white" }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2a1 1 0 011 1v1.07A7.002 7.002 0 0119 11v1a3 3 0 013 3v1a3 3 0 01-3 3h-1a5.002 5.002 0 01-4 2H10a5.002 5.002 0 01-4-2H5a3 3 0 01-3-3v-1a3 3 0 013-3v-1a7.002 7.002 0 016-6.93V3a1 1 0 011-1zM7 11a5 5 0 0010 0V10a5 5 0 00-10 0v1zm-2 3a1 1 0 00-1 1v1a1 1 0 001 1h1v-3H5zm14 0h-1v3h1a1 1 0 001-1v-1a1 1 0 00-1-1zm-9.5-3a1.5 1.5 0 100 3 1.5 1.5 0 000-3zm5 0a1.5 1.5 0 100 3 1.5 1.5 0 000-3z"/>
            </svg>
          </div>
          <span className="text-[17px] font-bold tracking-tight text-text">
            Onboarding Buddy
          </span>
        </div>
        <div className="flex items-center gap-4">
          {docCount > 0 && (
            <span className="text-[13px] text-muted">
              <strong className="text-text font-semibold">{docCount}</strong> doc{docCount !== 1 ? "s" : ""} loaded
            </span>
          )}
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-[13px] font-medium text-muted hover:text-text px-3 py-1.5 rounded-lg transition-all duration-150"
              style={{ backgroundColor: "rgba(26,25,21,0.04)" }}
            >
              Clear chat
            </button>
          )}
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar onDocCountChange={setDocCount} />

        <main className="flex-1 flex flex-col overflow-hidden">
          <ChatWindow messages={messages} isLoading={isLoading} />

          {error && (
            <ErrorBanner message={error} onDismiss={clearError} />
          )}

          <ChatInput
            onSend={sendQuestion}
            isLoading={isLoading}
            disabled={docCount === 0}
          />
        </main>
      </div>
    </div>
  )
}
