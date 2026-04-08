function CodeBlock({ code, lang }) {
  return (
    <div style={{ margin: "8px 0", borderRadius: "12px", overflow: "hidden", border: "1px solid #E5DED4" }}>
      {lang && (
        <div style={{ padding: "6px 16px", backgroundColor: "#F3EDE5", fontSize: "11px", color: "#8B8580", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em", borderBottom: "1px solid #E5DED4" }}>
          {lang}
        </div>
      )}
      <pre style={{ padding: "16px", overflowX: "auto", fontSize: "13px", lineHeight: 1.6, color: "rgba(26,25,21,0.85)", backgroundColor: "#F3EDE5" }}>
        <code>{code}</code>
      </pre>
    </div>
  )
}

function BulletList({ items }) {
  return (
    <ul style={{ margin: "6px 0", paddingLeft: "4px", display: "flex", flexDirection: "column", gap: "4px" }}>
      {items.map((item, i) => (
        <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: "10px", fontSize: "14px", color: "#1A1915", lineHeight: 1.6 }}>
          <span style={{ color: "#D97757", marginTop: "9px", flexShrink: 0, fontSize: "5px" }}>●</span>
          <span dangerouslySetInnerHTML={{ __html: formatInline(item) }} />
        </li>
      ))}
    </ul>
  )
}

function NumberedList({ items }) {
  return (
    <ol style={{ margin: "6px 0", paddingLeft: "4px", display: "flex", flexDirection: "column", gap: "6px", counterReset: "item" }}>
      {items.map((item, i) => (
        <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: "10px", fontSize: "14px", color: "#1A1915", lineHeight: 1.6 }}>
          <span style={{ color: "#D97757", fontWeight: 600, flexShrink: 0, minWidth: "18px" }}>{i + 1}.</span>
          <span dangerouslySetInnerHTML={{ __html: formatInline(item) }} />
        </li>
      ))}
    </ol>
  )
}

function SectionLabel({ text }) {
  return (
    <p style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.04em", marginTop: "16px", marginBottom: "8px", color: "#D97757" }}>
      {text}
    </p>
  )
}

function formatInline(text) {
  return text.replace(/\*\*(.+?)\*\*/g, "<strong style='color:#1A1915;font-weight:600'>$1</strong>")
}

export default function AnswerRenderer({ content }) {
  if (!content) return null

  const lines  = content.split("\n")
  const blocks = []
  let i        = 0

  while (i < lines.length) {
    const line = lines[i]

    if (line.startsWith("```")) {
      const lang      = line.slice(3).trim()
      const codeLines = []
      i++
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i])
        i++
      }
      blocks.push(<CodeBlock key={i} code={codeLines.join("\n")} lang={lang} />)
      i++
      continue
    }

    if (line.startsWith("📄") || line.startsWith("🤖")) {
      blocks.push(<SectionLabel key={i} text={line} />)
      i++
      continue
    }

    if (line.match(/^[-*]\s+/)) {
      const items = []
      while (i < lines.length && lines[i].match(/^[-*]\s+/)) {
        items.push(lines[i].replace(/^[-*]\s+/, "").trim())
        i++
      }
      blocks.push(<BulletList key={i} items={items} />)
      continue
    }

    if (line.match(/^\d+\.\s+/)) {
      const items = []
      while (i < lines.length && lines[i].match(/^\d+\.\s+/)) {
        items.push(lines[i].replace(/^\d+\.\s+/, "").trim())
        i++
      }
      blocks.push(<NumberedList key={i} items={items} />)
      continue
    }

    if (!line.trim()) {
      blocks.push(<div key={i} style={{ height: "8px" }} />)
      i++
      continue
    }

    blocks.push(
      <p
        key={i}
        style={{ fontSize: "14px", color: "#1A1915", lineHeight: 1.6 }}
        dangerouslySetInnerHTML={{ __html: formatInline(line) }}
      />
    )
    i++
  }

  return <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>{blocks}</div>
}
