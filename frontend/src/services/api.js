import axios from 'axios'

const coreBaseUrl = import.meta.env.VITE_CORE_API_URL || '/api'
const aiBaseUrl = import.meta.env.VITE_AI_API_URL || '/v1'

const api = axios.create({
  baseURL: coreBaseUrl,
})

export const aiApi = axios.create({
  baseURL: aiBaseUrl,
})

// Set default headers
api.defaults.headers.common['Content-Type'] = 'application/json'
aiApi.defaults.headers.common['Content-Type'] = 'application/json'

// Add token to requests if available
const token = localStorage.getItem('token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Token ${token}`
  aiApi.defaults.headers.common['Authorization'] = `Token ${token}`
}

// Interceptor để tự động thêm token khi có
const attachAuthAndContentType = (config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  // Nếu là FormData, không set Content-Type (để browser tự set với boundary)
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
}

api.interceptors.request.use(attachAuthAndContentType)
aiApi.interceptors.request.use(attachAuthAndContentType)

export default api

