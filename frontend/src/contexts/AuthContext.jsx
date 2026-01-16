import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Token ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/profile/')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    const response = await api.post('/auth/login/', { username, password })
    const { token, user } = response.data
    localStorage.setItem('token', token)
    api.defaults.headers.common['Authorization'] = `Token ${token}`
    setUser(user)
    return { token, user }
  }

  const register = async (userData) => {
    const response = await api.post('/auth/register/', userData)
    const { token, user } = response.data
    localStorage.setItem('token', token)
    api.defaults.headers.common['Authorization'] = `Token ${token}`
    setUser(user)
    return { token, user }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

