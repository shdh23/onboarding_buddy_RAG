import { useEffect, useState } from "react"

export default function ErrorBanner({ message, onDismiss }) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false)
      onDismiss?.()
    }, 5000)

    return () => clearTimeout(timer)
  }, [message])

  if (!visible || !message) return null

  return (
    <div
      className="animate-fade-slide"
      style={{ margin: "8px 24px 0", display: "flex", alignItems: "center", gap: "12px", backgroundColor: "rgba(196,69,58,0.08)", border: "1px solid rgba(196,69,58,0.15)", borderRadius: "12px", padding: "12px 16px" }}
    >
      <span style={{ color: "#C4453A", fontSize: "14px", flexShrink: 0 }}>⚠</span>
      <p style={{ flex: 1, fontSize: "13px", color: "#C4453A", fontWeight: 500, lineHeight: 1.5 }}>{message}</p>
      <button
        onClick={() => { setVisible(false); onDismiss?.() }}
        style={{ color: "rgba(196,69,58,0.4)", flexShrink: 0, background: "none", border: "none", cursor: "pointer" }}
      >
        <svg style={{ width: "16px", height: "16px" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}
