import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 60000,
})

export const uploadDocument = async (file, docType) => {
  const formData = new FormData()
  formData.append("file", file)
  formData.append("doc_type", docType)
  const { data } = await api.post("/api/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export const fetchDocuments = async () => {
  const { data } = await api.get("/api/documents")
  return data
}

export const deleteDocument = async (docId) => {
  const { data } = await api.delete(`/api/documents/${docId}`)
  return data
}

export const sendMessage = async (question, history) => {
  const { data } = await api.post("/api/chat", { question, history })
  return data
}