import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { usePreferences } from '../contexts/PreferencesContext'
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
  const { preferences } = usePreferences()
  const chartType = preferences?.dashboard_chart_type || 'line'
  const isDark = document.documentElement.classList.contains('dark')
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
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 md:mb-8 gap-4 pr-20 md:pr-16">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100">Thống kê Thu Chi</h1>
        <div className="flex flex-wrap gap-2 sm:gap-4 w-full sm:w-auto">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
          <span className="self-center text-gray-700 dark:text-gray-300">đến</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
          <p className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400">Tổng thu nhập</p>
          <p className="text-xl md:text-2xl font-bold text-green-600 dark:text-green-400 mt-1 md:mt-2">
            {stats?.summary?.total_income?.toLocaleString('vi-VN') || 0} ₫
          </p>
        </div>
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
          <p className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400">Tổng chi tiêu</p>
          <p className="text-xl md:text-2xl font-bold text-red-600 dark:text-red-400 mt-1 md:mt-2">
            {stats?.summary?.total_expense?.toLocaleString('vi-VN') || 0} ₫
          </p>
        </div>
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6 sm:col-span-2 md:col-span-1">
          <p className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400">Số dư</p>
          <p className={`text-xl md:text-2xl font-bold mt-1 md:mt-2 ${
            (stats?.summary?.balance || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {stats?.summary?.balance?.toLocaleString('vi-VN') || 0} ₫
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 mb-6 md:mb-8">
        {/* Daily Income/Expense Chart */}
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
          <h2 className="text-lg md:text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">Thu Chi theo Ngày</h2>
          <ResponsiveContainer width="100%" height={250} className="md:h-[300px]">
            {chartType === 'line' ? (
              <LineChart data={stats?.by_date || []}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#6b7280' : '#e5e7eb'} />
                <XAxis dataKey="date" stroke={isDark ? '#9ca3af' : '#6b7280'} />
                <YAxis stroke={isDark ? '#9ca3af' : '#6b7280'} />
                <Tooltip contentStyle={{ 
                  backgroundColor: isDark ? '#374151' : '#ffffff', 
                  border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                  borderRadius: '8px', 
                  color: isDark ? '#f9fafb' : '#111827' 
                }} />
                <Legend wrapperStyle={{ color: isDark ? '#d1d5db' : '#6b7280' }} />
                <Line type="monotone" dataKey="income" stroke="#10B981" name="Thu nhập" />
                <Line type="monotone" dataKey="expense" stroke="#EF4444" name="Chi tiêu" />
              </LineChart>
            ) : chartType === 'bar' ? (
              <BarChart data={stats?.by_date || []}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#6b7280' : '#e5e7eb'} />
                <XAxis dataKey="date" stroke={isDark ? '#9ca3af' : '#6b7280'} />
                <YAxis stroke={isDark ? '#9ca3af' : '#6b7280'} />
                <Tooltip contentStyle={{ 
                  backgroundColor: isDark ? '#374151' : '#ffffff', 
                  border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                  borderRadius: '8px', 
                  color: isDark ? '#f9fafb' : '#111827' 
                }} />
                <Legend wrapperStyle={{ color: isDark ? '#d1d5db' : '#6b7280' }} />
                <Bar dataKey="income" fill="#10B981" name="Thu nhập" />
                <Bar dataKey="expense" fill="#EF4444" name="Chi tiêu" />
              </BarChart>
            ) : (
              <PieChart>
                <Pie
                  data={stats?.by_date?.map(d => ({ name: d.date, income: d.income || 0, expense: d.expense || 0 })) || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name }) => name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="income"
                >
                  {(stats?.by_date || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ 
                  backgroundColor: isDark ? '#374151' : '#ffffff', 
                  border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                  borderRadius: '8px', 
                  color: isDark ? '#f9fafb' : '#111827' 
                }} />
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* Category Pie Chart */}
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
          <h2 className="text-lg md:text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">Chi tiêu theo Danh mục</h2>
          <ResponsiveContainer width="100%" height={250} className="md:h-[300px]">
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
              <Tooltip contentStyle={{ 
                backgroundColor: isDark ? '#374151' : '#ffffff', 
                border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                borderRadius: '8px', 
                color: isDark ? '#f9fafb' : '#111827' 
              }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Bar Chart */}
      <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
        <h2 className="text-lg md:text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">Thống kê theo Danh mục</h2>
        <ResponsiveContainer width="100%" height={300} className="md:h-[400px]">
          {chartType === 'bar' ? (
            <BarChart data={stats?.by_category || []}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#6b7280' : '#e5e7eb'} />
              <XAxis dataKey="category__name" angle={-45} textAnchor="end" height={100} stroke={isDark ? '#9ca3af' : '#6b7280'} />
              <YAxis stroke={isDark ? '#9ca3af' : '#6b7280'} />
              <Tooltip contentStyle={{ 
                backgroundColor: isDark ? '#374151' : '#ffffff', 
                border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                borderRadius: '8px', 
                color: isDark ? '#f9fafb' : '#111827' 
              }} />
              <Legend wrapperStyle={{ color: isDark ? '#d1d5db' : '#6b7280' }} />
              <Bar dataKey="total" fill="#3B82F6" name="Tổng tiền" />
              <Bar dataKey="count" fill="#10B981" name="Số lượng" />
            </BarChart>
          ) : chartType === 'line' ? (
            <LineChart data={stats?.by_category || []}>
              <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#6b7280' : '#e5e7eb'} />
              <XAxis dataKey="category__name" angle={-45} textAnchor="end" height={100} stroke={isDark ? '#9ca3af' : '#6b7280'} />
              <YAxis stroke={isDark ? '#9ca3af' : '#6b7280'} />
              <Tooltip contentStyle={{ 
                backgroundColor: isDark ? '#374151' : '#ffffff', 
                border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                borderRadius: '8px', 
                color: isDark ? '#f9fafb' : '#111827' 
              }} />
              <Legend wrapperStyle={{ color: isDark ? '#d1d5db' : '#6b7280' }} />
              <Line type="monotone" dataKey="total" stroke="#3B82F6" name="Tổng tiền" />
              <Line type="monotone" dataKey="count" stroke="#10B981" name="Số lượng" />
            </LineChart>
          ) : (
            <PieChart>
              <Pie
                data={stats?.by_category || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ category__name, total }) => `${category__name}: ${(total / 1000).toFixed(0)}k`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="total"
              >
                {(stats?.by_category || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ 
                backgroundColor: isDark ? '#374151' : '#ffffff', 
                border: isDark ? '1px solid #4b5563' : '1px solid #e5e7eb', 
                borderRadius: '8px', 
                color: isDark ? '#f9fafb' : '#111827' 
              }} />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default Statistics

