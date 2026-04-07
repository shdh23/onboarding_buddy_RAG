function SkeletonRow() {
  return (
    <div className="animate-pulse" style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px" }}>
      <div style={{ width: "36px", height: "36px", borderRadius: "10px", backgroundColor: "#E5DED4", flexShrink: 0 }} />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "8px" }}>
        <div style={{ height: "12px", backgroundColor: "#E5DED4", borderRadius: "9999px", width: "75%" }} />
        <div style={{ height: "10px", backgroundColor: "rgba(229,222,212,0.6)", borderRadius: "9999px", width: "50%" }} />
      </div>
    </div>
  )
}

export default function LoadingSkeleton({ rows = 3 }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonRow key={i} />
      ))}
    </div>
  )
}
