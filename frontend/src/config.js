/**
 * API Configuration
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  base: API_BASE_URL,
  upload: `${API_BASE_URL}/api/upload`,
  query: `${API_BASE_URL}/api/query`,
  compare: `${API_BASE_URL}/api/compare`,
  documents: `${API_BASE_URL}/api/documents`,
}
