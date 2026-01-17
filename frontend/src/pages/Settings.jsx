import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { usePreferences } from '../contexts/PreferencesContext'
import {
  PaintBrushIcon,
  ChartBarIcon,
  BellIcon,
  ViewColumnsIcon,
} from '@heroicons/react/24/outline'

function Settings() {
  const { preferences, updatePreferences, loading: prefsLoading } = usePreferences()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')

  const [formData, setFormData] = useState({
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

  useEffect(() => {
    fetchCategories()
    if (preferences) {
      setFormData({
        theme: preferences.theme || 'light',
        primary_color: preferences.primary_color || '#3B82F6',
        sidebar_collapsed: preferences.sidebar_collapsed || false,
        default_report_period: preferences.default_report_period || 'month',
        report_categories: preferences.report_categories || [],
        report_include_charts: preferences.report_include_charts !== false,
        report_include_tables: preferences.report_include_tables !== false,
        report_email_frequency: preferences.report_email_frequency || 'never',
        notify_budget_exceeded: preferences.notify_budget_exceeded !== false,
        notify_large_transaction: preferences.notify_large_transaction !== false,
        notify_anomaly_detected: preferences.notify_anomaly_detected !== false,
        large_transaction_threshold: preferences.large_transaction_threshold || 1000000,
        dashboard_widgets: preferences.dashboard_widgets || [],
        dashboard_chart_type: preferences.dashboard_chart_type || 'line',
      })
    }
  }, [preferences])

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories/')
      setCategories(response.data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleCategoryToggle = (categoryId) => {
    setFormData(prev => ({
      ...prev,
      report_categories: prev.report_categories.includes(categoryId)
        ? prev.report_categories.filter(id => id !== categoryId)
        : [...prev.report_categories, categoryId]
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSaveMessage('')

    try {
      // Đảm bảo report_categories và dashboard_widgets là array
      const dataToSave = {
        ...formData,
        report_categories: Array.isArray(formData.report_categories) 
          ? formData.report_categories 
          : [],
        dashboard_widgets: Array.isArray(formData.dashboard_widgets) 
          ? formData.dashboard_widgets 
          : [],
      }
      
      await updatePreferences(dataToSave)
      setSaveMessage('Đã lưu cài đặt thành công!')
      setTimeout(() => setSaveMessage(''), 3000)
    } catch (error) {
      let errorMessage = 'Có lỗi xảy ra khi lưu cài đặt'
      if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = `Lỗi: ${error.response.data.error}`
        } else if (error.response.data.details) {
          errorMessage = `Lỗi xác thực: ${JSON.stringify(error.response.data.details)}`
        } else {
          errorMessage = `Lỗi: ${JSON.stringify(error.response.data)}`
        }
      }
      setSaveMessage(errorMessage)
      console.error('Error saving preferences:', error)
    } finally {
      setSaving(false)
    }
  }

  const presetColors = [
    { name: 'Xanh dương', value: '#3B82F6' },
    { name: 'Xanh lá', value: '#10B981' },
    { name: 'Tím', value: '#8B5CF6' },
    { name: 'Hồng', value: '#EC4899' },
    { name: 'Cam', value: '#F59E0B' },
    { name: 'Đỏ', value: '#EF4444' },
  ]

  if (loading || prefsLoading) {
    return <div className="text-center py-12">Đang tải...</div>
  }

  return (
    <div>
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 md:mb-8">Cài đặt</h1>

      {saveMessage && (
        <div className={`mb-4 p-4 rounded-lg ${
          saveMessage.includes('thành công') 
            ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300' 
            : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300'
        }`}>
          {saveMessage}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Giao diện */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center mb-4">
            <PaintBrushIcon className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Giao diện</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Chủ đề
              </label>
              <select
                value={formData.theme}
                onChange={(e) => handleChange('theme', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="light">Sáng</option>
                <option value="dark">Tối</option>
                <option value="auto">Tự động</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Màu chủ đạo
              </label>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-2">
                {presetColors.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => handleChange('primary_color', color.value)}
                    className={`h-10 rounded-lg border-2 transition-all ${
                      formData.primary_color === color.value
                        ? 'border-gray-900 dark:border-gray-100 scale-110'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.name}
                  />
                ))}
              </div>
              <input
                type="color"
                value={formData.primary_color}
                onChange={(e) => handleChange('primary_color', e.target.value)}
                className="w-full h-10 rounded-lg border border-gray-300 dark:border-gray-600 cursor-pointer"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="sidebar_collapsed"
                checked={formData.sidebar_collapsed}
                onChange={(e) => handleChange('sidebar_collapsed', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="sidebar_collapsed" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Thu gọn sidebar mặc định
              </label>
            </div>
          </div>
        </div>

        {/* Báo cáo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center mb-4">
            <ChartBarIcon className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Báo cáo</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Kỳ báo cáo mặc định
              </label>
              <select
                value={formData.default_report_period}
                onChange={(e) => handleChange('default_report_period', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="week">Tuần</option>
                <option value="month">Tháng</option>
                <option value="quarter">Quý</option>
                <option value="year">Năm</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Danh mục hiển thị trong báo cáo
              </label>
              <div className="max-h-48 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded-lg p-3 bg-white dark:bg-gray-700">
                {categories.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">Đang tải...</p>
                ) : (
                  <div className="space-y-2">
                    {categories.map((category) => (
                      <label
                        key={category.id}
                        className="flex items-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600 p-2 rounded"
                      >
                        <input
                          type="checkbox"
                          checked={formData.report_categories.includes(category.id)}
                          onChange={() => handleCategoryToggle(category.id)}
                          className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                          {category.icon} {category.name}
                        </span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Để trống để hiển thị tất cả danh mục
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="report_include_charts"
                  checked={formData.report_include_charts}
                  onChange={(e) => handleChange('report_include_charts', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
                />
                <label htmlFor="report_include_charts" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Bao gồm biểu đồ trong báo cáo
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="report_include_tables"
                  checked={formData.report_include_tables}
                  onChange={(e) => handleChange('report_include_tables', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
                />
                <label htmlFor="report_include_tables" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Bao gồm bảng dữ liệu trong báo cáo
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Tần suất gửi email báo cáo
              </label>
              <select
                value={formData.report_email_frequency}
                onChange={(e) => handleChange('report_email_frequency', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="never">Không gửi</option>
                <option value="daily">Hàng ngày</option>
                <option value="weekly">Hàng tuần</option>
                <option value="monthly">Hàng tháng</option>
              </select>
            </div>
          </div>
        </div>

        {/* Thông báo */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center mb-4">
            <BellIcon className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Thông báo</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="notify_budget_exceeded"
                checked={formData.notify_budget_exceeded}
                onChange={(e) => handleChange('notify_budget_exceeded', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="notify_budget_exceeded" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Thông báo khi vượt ngân sách
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="notify_large_transaction"
                checked={formData.notify_large_transaction}
                onChange={(e) => handleChange('notify_large_transaction', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="notify_large_transaction" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Thông báo giao dịch lớn
              </label>
            </div>

            {formData.notify_large_transaction && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Ngưỡng giao dịch lớn (₫)
                </label>
                <input
                  type="number"
                  value={formData.large_transaction_threshold}
                  onChange={(e) => handleChange('large_transaction_threshold', parseFloat(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  min="0"
                  step="1000"
                />
              </div>
            )}

            <div className="flex items-center">
              <input
                type="checkbox"
                id="notify_anomaly_detected"
                checked={formData.notify_anomaly_detected}
                onChange={(e) => handleChange('notify_anomaly_detected', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="notify_anomaly_detected" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Thông báo khi phát hiện bất thường
              </label>
            </div>
          </div>
        </div>

        {/* Dashboard */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center mb-4">
            <ViewColumnsIcon className="w-6 h-6 text-blue-600 dark:text-blue-400 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Dashboard</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Loại biểu đồ mặc định
              </label>
              <select
                value={formData.dashboard_chart_type}
                onChange={(e) => handleChange('dashboard_chart_type', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="line">Đường</option>
                <option value="bar">Cột</option>
                <option value="pie">Tròn</option>
              </select>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Đang lưu...' : 'Lưu cài đặt'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default Settings

