import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// Set default headers
api.defaults.headers.common['Content-Type'] = 'application/json'

// Add token to requests if available
const token = localStorage.getItem('token')
if (token) {
  api.defaults.headers.common['Authorization'] = `Token ${token}`
}

// Interceptor để tự động thêm token khi có
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  // Nếu là FormData, không set Content-Type (để browser tự set với boundary)
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

export default api

