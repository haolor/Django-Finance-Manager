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

  useEffect(() => {
    fetchAllInsights()
  }, [])

  const fetchAllInsights = async () => {
    try {
      const [trendsRes, predictionsRes, anomaliesRes, savingsRes] = await Promise.all([
        api.get('/ai/trends/'),
        api.get('/ai/predictions/'),
        api.get('/ai/anomalies/'),
        api.get('/ai/savings-suggestions/'),
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
      <h1 className="text-3xl font-bold text-gray-900 mb-8">AI Insights</h1>

      {/* Predictions */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center mb-4">
          <LightBulbIcon className="w-6 h-6 text-yellow-500 mr-2" />
          <h2 className="text-xl font-semibold">Dự đoán Chi tiêu Tháng Tiếp theo</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Dự đoán</p>
            <p className="text-2xl font-bold text-blue-600">
              {predictions?.predicted_amount?.toLocaleString('vi-VN') || 0} ₫
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Độ tin cậy</p>
            <p className="text-2xl font-bold text-gray-700 capitalize">
              {predictions?.confidence || 'N/A'}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">Dựa trên</p>
            <p className="text-2xl font-bold text-gray-700">
              {predictions?.based_on_months || 0} tháng
            </p>
          </div>
        </div>
      </div>

      {/* Trends */}
      {trends && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Xu hướng Chi tiêu</h2>
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
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center mb-4">
          <ExclamationTriangleIcon className="w-6 h-6 text-orange-500 mr-2" />
          <h2 className="text-xl font-semibold">Phát hiện Bất thường</h2>
        </div>
        {anomalies.length === 0 ? (
          <p className="text-gray-500">Không phát hiện giao dịch bất thường nào</p>
        ) : (
          <div className="space-y-4">
            {anomalies.map((anomaly) => (
              <div
                key={anomaly.id}
                className="border border-orange-200 rounded-lg p-4 bg-orange-50"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-900">{anomaly.category}</p>
                    <p className="text-sm text-gray-600">{anomaly.description || 'Không có mô tả'}</p>
                    <p className="text-sm text-gray-500 mt-1">Ngày: {anomaly.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-red-600">
                      {anomaly.amount.toLocaleString('vi-VN')} ₫
                    </p>
                    <p className="text-xs text-gray-500">
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
      {savings && savings.suggestions && savings.suggestions.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <LightBulbIcon className="w-6 h-6 text-green-500 mr-2" />
            <h2 className="text-xl font-semibold">Gợi ý Tiết kiệm</h2>
          </div>
          <div className="mb-4 p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-600">Tổng có thể tiết kiệm mỗi tháng</p>
            <p className="text-2xl font-bold text-green-600">
              {savings.total_potential_savings.toLocaleString('vi-VN')} ₫
            </p>
          </div>
          <div className="space-y-3">
            {savings.suggestions.map((suggestion, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{suggestion.category}</p>
                    <p className="text-sm text-gray-600 mt-1">{suggestion.suggestion}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Chi tiêu hiện tại: {suggestion.current_spending.toLocaleString('vi-VN')} ₫
                      ({suggestion.percentage}% tổng chi)
                    </p>
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-lg font-bold text-green-600">
                      +{suggestion.potential_savings.toLocaleString('vi-VN')} ₫
                    </p>
                    <p className="text-xs text-gray-500">Có thể tiết kiệm</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AIInsights

