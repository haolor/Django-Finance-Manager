import React, { useEffect, useState } from 'react'
import api from '../services/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline'

function AIInsights() {
  const [trends, setTrends] = useState(null)
  const [predictions, setPredictions] = useState(null)
  const [anomalies, setAnomalies] = useState([])
  const [savings, setSavings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])
  const [filterError, setFilterError] = useState('')

  useEffect(() => {
    fetchAllInsights()
  }, [])

  const fetchAllInsights = async () => {
    setFilterError('')

    if (startDate && endDate && startDate > endDate) {
      setFilterError('Ngày bắt đầu không được lớn hơn ngày kết thúc.')
      return
    }

    try {
      const query = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      })

      const [trendsRes, predictionsRes, anomaliesRes, savingsRes] = await Promise.all([
        api.get(`/ai/trends/?${query.toString()}`),
        api.get(`/ai/predictions/?${query.toString()}`),
        api.get(`/ai/anomalies/?${query.toString()}`),
        api.get(`/ai/savings-suggestions/?${query.toString()}`),
      ])
      setTrends(trendsRes.data)
      setPredictions(predictionsRes.data)
      setAnomalies(anomaliesRes.data.anomalies || [])
      setSavings(savingsRes.data)
    } catch (error) {
      console.error('Error fetching insights:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Đang tải...</div>
  }

  return (
    <div>
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 md:mb-8">AI Insights</h1>
      
      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 mb-4 md:mb-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
          <div className="flex flex-wrap gap-3">
            <div>
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">Từ ngày</p>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-1">Đến ngày</p>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            {filterError && (
              <div className="text-sm text-red-600 dark:text-red-400">
                {filterError}
              </div>
            )}
            <button
              type="button"
              onClick={fetchAllInsights}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium"
            >
              Lọc
            </button>
          </div>
        </div>
      </div>

      {/* Predictions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 mb-4 md:mb-6">
        <div className="flex items-center mb-4">
          <LightBulbIcon className="w-6 h-6 text-yellow-500 dark:text-yellow-400 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Dự đoán Chi tiêu Tháng Tiếp theo</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">Dự đoán</p>
            <p className="text-xl md:text-2xl font-bold text-blue-600 dark:text-blue-400">
              {predictions?.predicted_amount?.toLocaleString('vi-VN') || 0} ₫
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">Độ tin cậy</p>
            <p className="text-xl md:text-2xl font-bold text-gray-700 dark:text-gray-200 capitalize">
              {predictions?.confidence || 'N/A'}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 md:p-4">
            <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">Dựa trên</p>
            <p className="text-xl md:text-2xl font-bold text-gray-700 dark:text-gray-200">
              {predictions?.based_on_months || 0} tháng
            </p>
          </div>
        </div>
      </div>

      {/* Trends */}
      {trends && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 mb-4 md:mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg md:text-xl font-semibold text-gray-900 dark:text-gray-100">Xu hướng Chi tiêu</h2>
            <div className="flex items-center">
              {trends.trend === 'increasing' ? (
                <ArrowTrendingUpIcon className="w-6 h-6 text-red-500 mr-2" />
              ) : (
                <ArrowTrendingDownIcon className="w-6 h-6 text-green-500 mr-2" />
              )}
              <span className={`font-medium ${
                trends.trend === 'increasing' ? 'text-red-600' : 'text-green-600'
              }`}>
                {trends.trend === 'increasing' ? 'Tăng' : 'Giảm'} {trends.trend_percentage}%
              </span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends.weekly_data || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="expense" stroke="#EF4444" name="Chi tiêu" />
              <Line type="monotone" dataKey="income" stroke="#10B981" name="Thu nhập" />
              <Line type="monotone" dataKey="balance" stroke="#3B82F6" name="Số dư" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Anomalies */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6 mb-4 md:mb-6">
        <div className="flex items-center mb-4">
          <ExclamationTriangleIcon className="w-5 h-5 md:w-6 md:h-6 text-orange-500 dark:text-orange-400 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Phát hiện Bất thường</h2>
        </div>
        {anomalies.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">Không phát hiện giao dịch bất thường nào</p>
        ) : (
          <div className="space-y-4">
            {anomalies.map((anomaly) => (
              <div
                key={anomaly.id}
                className="border border-orange-200 dark:border-orange-800 rounded-lg p-4 bg-orange-50 dark:bg-orange-900/20"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">{anomaly.category}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-300">{anomaly.description || 'Không có mô tả'}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Ngày: {anomaly.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-red-600 dark:text-red-400">
                      {anomaly.amount.toLocaleString('vi-VN')} ₫
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Độ lệch: {anomaly.deviation}σ
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Savings Suggestions */}
      {savings && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center mb-4">
            <LightBulbIcon className="w-5 h-5 md:w-6 md:h-6 text-green-500 dark:text-green-400 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Gợi ý Tiết kiệm & Cắt giảm Chi tiêu</h2>
          </div>
          
          {/* Overall Summary */}
          <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3 md:p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">Có thể tiết kiệm mỗi tháng</p>
              <p className="text-xl md:text-2xl font-bold text-green-600 dark:text-green-400">
                {savings.total_potential_savings?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <div className="p-3 md:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">Chi tiêu tháng này</p>
              <p className="text-xl md:text-2xl font-bold text-blue-600 dark:text-blue-400">
                {savings.monthly_expense?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            {savings.savings_rate && (
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Tỷ lệ tiết kiệm tiềm năng</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {savings.savings_rate}%
                </p>
              </div>
            )}
          </div>

          {/* Overall Recommendations */}
          {savings.overall_recommendation && savings.overall_recommendation.length > 0 && (
            <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 dark:border-yellow-500 rounded">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">💡 Khuyến nghị tổng quan:</h3>
              <ul className="space-y-1">
                {savings.overall_recommendation.map((rec, idx) => (
                  <li key={idx} className="text-sm text-gray-700 dark:text-gray-300">{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Suggestions */}
          {savings.suggestions && savings.suggestions.length > 0 ? (
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Gợi ý chi tiết theo danh mục:</h3>
              {savings.suggestions.map((suggestion, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-5 hover:shadow-md transition-shadow bg-white dark:bg-gray-700">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <p className="font-semibold text-lg text-gray-900 dark:text-gray-100">{suggestion.category}</p>
                        {suggestion.priority_score >= 3 && (
                          <span className="px-2 py-1 text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 rounded-full">
                            Ưu tiên cao
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-medium text-green-600 dark:text-green-400 mb-2">
                        {suggestion.suggestion}
                      </p>
                      
                      {/* Reasons */}
                      {suggestion.reasons && suggestion.reasons.length > 0 && (
                        <div className="mb-3">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Lý do:</p>
                          <ul className="list-disc list-inside text-xs text-gray-600 dark:text-gray-300 space-y-1">
                            {suggestion.reasons.map((reason, idx) => (
                              <li key={idx}>{reason}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {/* Stats */}
                      <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400 mt-2">
                        <span>Chi tiêu: {suggestion.current_spending?.toLocaleString('vi-VN')} ₫</span>
                        <span>• {suggestion.percentage}% tổng chi</span>
                        {suggestion.count && <span>• {suggestion.count} lần/tháng</span>}
                        {suggestion.avg_amount && (
                          <span>• TB: {suggestion.avg_amount?.toLocaleString('vi-VN')} ₫/lần</span>
                        )}
                      </div>
                      
                      {/* Actionable Tips */}
                      {suggestion.actionable_tips && suggestion.actionable_tips.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
                          <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">💡 Hành động cụ thể:</p>
                          <ul className="space-y-2">
                            {suggestion.actionable_tips.map((tip, tipIdx) => (
                              <li key={tipIdx} className="text-sm text-gray-600 dark:text-gray-300 flex items-start">
                                <span className="text-green-500 dark:text-green-400 mr-2">•</span>
                                <span>{tip}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        +{suggestion.potential_savings?.toLocaleString('vi-VN')} ₫
                      </p>
                      <p className="text-xs text-gray-500">Tiết kiệm/tháng</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Chi tiêu của bạn đang hợp lý! Không có gợi ý cắt giảm nào.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AIInsights

