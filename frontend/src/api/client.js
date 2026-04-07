import axios from 'axios'
import { API_ENDPOINTS } from '../config'

// Create axios instance with default config
const apiClient = axios.create({
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.detail || error.response.data?.message || 'Server error'
      throw new Error(message)
    } else if (error.request) {
      // No response received
      throw new Error('Cannot connect to server. Please check if backend is running.')
    } else {
      // Request setup error
      throw new Error(error.message || 'Request failed')
    }
  }
)

/**
 * Upload a document file
 */
export const uploadDocument = async (file, sourceName = null) => {
  const formData = new FormData()
  formData.append('file', file)
  if (sourceName) {
    formData.append('source', sourceName)
  }

  const response = await axios.post(API_ENDPOINTS.upload, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 60 seconds for file upload
  })
  return response.data
}

/**
 * Query/Ask a question
 */
export const queryDocuments = async (question, options = {}) => {
  const payload = {
    question,
    model: options.model || 'qwen2.5:1.5b',
    top_k: options.top_k || 5,
    source_filter: options.source_filter || null,
  }

  const response = await apiClient.post(API_ENDPOINTS.query, payload)
  return response.data
}

/**
 * Compare two versions
 */
export const compareVersions = async (articleName, sourceV1, sourceV2, model = 'qwen2.5:1.5b') => {
  const payload = {
    article_name: articleName,
    source_v1: sourceV1,
    source_v2: sourceV2,
    model,
  }

  const response = await apiClient.post(API_ENDPOINTS.compare, payload)
  return response.data
}

/**
 * List all uploaded documents
 */
export const listDocuments = async () => {
  const response = await apiClient.get(API_ENDPOINTS.documents)
  return response.data
}

/**
 * Get full content of a document by source name
 */
export const getDocumentContent = async (sourceName) => {
  const response = await apiClient.get(`${API_ENDPOINTS.base}/api/document/${sourceName}/content`)
  return response.data
}
