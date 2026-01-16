import React, { useEffect, useState } from 'react'
import api from '../services/api'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

function Statistics() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split('T')[0]
  )

  useEffect(() => {
    fetchStatistics()
  }, [startDate, endDate])

  const fetchStatistics = async () => {
    try {
      const response = await api.get(
        `/transactions/statistics/?start_date=${startDate}&end_date=${endDate}`
      )
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6']

  if (loading) {
    return <div className="text-center py-12">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Thống kê Thu Chi</h1>
        <div className="flex space-x-4">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
          <span className="self-center">đến</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Tổng thu nhập</p>
          <p className="text-2xl font-bold text-green-600 mt-2">
            {stats?.summary?.total_income?.toLocaleString('vi-VN') || 0} ₫
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Tổng chi tiêu</p>
          <p className="text-2xl font-bold text-red-600 mt-2">
            {stats?.summary?.total_expense?.toLocaleString('vi-VN') || 0} ₫
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Số dư</p>
          <p className={`text-2xl font-bold mt-2 ${
            (stats?.summary?.balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {stats?.summary?.balance?.toLocaleString('vi-VN') || 0} ₫
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Daily Income/Expense Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Thu Chi theo Ngày</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats?.by_date || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="income" stroke="#10B981" name="Thu nhập" />
              <Line type="monotone" dataKey="expense" stroke="#EF4444" name="Chi tiêu" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Category Pie Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Chi tiêu theo Danh mục</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats?.by_category?.filter(c => c.category__type === 'expense') || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ category__name, total }) => `${category__name}: ${(total / 1000).toFixed(0)}k`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="total"
              >
                {(stats?.by_category?.filter(c => c.category__type === 'expense') || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Bar Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Thống kê theo Danh mục</h2>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={stats?.by_category || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category__name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="total" fill="#3B82F6" name="Tổng tiền" />
            <Bar dataKey="count" fill="#10B981" name="Số lượng" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default Statistics

