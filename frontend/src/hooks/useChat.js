import { useState, useCallback } from "react"
import { sendMessage } from "../api/client"

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const sendQuestion = useCallback(async (question) => {
    if (!question.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: question,
      sources: [],
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    const history = messages.map((m) => ({
      role: m.role,
      content: m.content,
    }))

    try {
      const result = await sendMessage(question, history)
      setMessages((prev) => [...prev, {
        id: Date.now() + 1,
        role: "assistant",
        content: result.answer,
        sources: result.sources || [],
        rewrittenQuestion: result.rewritten_question || null,
      }])
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.")
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id))
    } finally {
      setIsLoading(false)
    }
  }, [messages, isLoading])

  const clearChat  = useCallback(() => { setMessages([]); setError(null) }, [])
  const clearError = useCallback(() => setError(null), [])

  return { messages, isLoading, error, sendQuestion, clearChat, clearError }
}