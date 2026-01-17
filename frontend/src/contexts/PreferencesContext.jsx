import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const PreferencesContext = createContext()

export function usePreferences() {
  return useContext(PreferencesContext)
}

export function PreferencesProvider({ children }) {
  const [preferences, setPreferences] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPreferences()
  }, [])

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/auth/preferences/')
      setPreferences(response.data)
    } catch (error) {
      // Nếu chưa có preferences, tạo mặc định
      setPreferences({
        theme: 'light',
        primary_color: '#3B82F6',
        sidebar_collapsed: false,
        default_report_period: 'month',
        report_categories: [],
        report_include_charts: true,
        report_include_tables: true,
        report_email_frequency: 'never',
        notify_budget_exceeded: true,
        notify_large_transaction: true,
        notify_anomaly_detected: true,
        large_transaction_threshold: 1000000,
        dashboard_widgets: [],
        dashboard_chart_type: 'line',
      })
    } finally {
      setLoading(false)
    }
  }

  const updatePreferences = async (newPreferences) => {
    try {
      // Dùng PATCH để chỉ cập nhật các field được gửi
      const response = await api.patch('/auth/preferences/', newPreferences)
      setPreferences(response.data)
      
      // Áp dụng theme ngay lập tức
      applyTheme(response.data)
      
      return response.data
    } catch (error) {
      console.error('Error updating preferences:', error)
      // Log chi tiết lỗi để debug
      if (error.response) {
        console.error('Response error:', error.response.data)
        console.error('Status:', error.response.status)
      }
      throw error
    }
  }

  const applyTheme = (prefs) => {
    if (!prefs) return
    
    // Áp dụng primary color
    const root = document.documentElement
    root.style.setProperty('--primary-color', prefs.primary_color)
    
    // Áp dụng theme - đảm bảo loại bỏ dark class khi chọn light
    const htmlElement = document.documentElement
    
    if (prefs.theme === 'dark') {
      htmlElement.classList.add('dark')
    } else if (prefs.theme === 'light') {
      // Loại bỏ hoàn toàn dark class
      htmlElement.classList.remove('dark')
    } else {
      // Auto - dùng system preference
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (isDark) {
        htmlElement.classList.add('dark')
      } else {
        htmlElement.classList.remove('dark')
      }
    }
  }

  // Áp dụng theme khi preferences thay đổi
  useEffect(() => {
    if (preferences) {
      applyTheme(preferences)
    }
  }, [preferences])

  const value = {
    preferences,
    loading,
    updatePreferences,
    refreshPreferences: fetchPreferences,
  }

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  )
}

