import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { format } from 'date-fns'
import {
  ArrowUpIcon,
  ArrowDownIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recentTransactions, setRecentTransactions] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const endDate = format(new Date(), 'yyyy-MM-dd')
      const startDate = format(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd')

      const [statsRes, transactionsRes] = await Promise.all([
        api.get(`/transactions/statistics/?start_date=${startDate}&end_date=${endDate}`),
        api.get('/transactions/?limit=5'),
      ])

      setStats(statsRes.data)
      setRecentTransactions(transactionsRes.data.results || transactionsRes.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Đang tải...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tổng thu nhập</p>
              <p className="text-2xl font-bold text-green-600 mt-2">
                {stats?.summary?.total_income?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <ArrowUpIcon className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tổng chi tiêu</p>
              <p className="text-2xl font-bold text-red-600 mt-2">
                {stats?.summary?.total_expense?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <ArrowDownIcon className="w-12 h-12 text-red-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Số dư</p>
              <p className={`text-2xl font-bold mt-2 ${
                (stats?.summary?.balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats?.summary?.balance?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <CurrencyDollarIcon className="w-12 h-12 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Giao dịch gần đây</h2>
        </div>
        <div className="p-6">
          {recentTransactions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Chưa có giao dịch nào</p>
          ) : (
            <div className="space-y-4">
              {recentTransactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-4">
                    <div
                      className="w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                      style={{ backgroundColor: transaction.category_color + '20' }}
                    >
                      {transaction.category_icon || '💰'}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {transaction.category_name || 'Khác'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {format(new Date(transaction.transaction_date), 'dd/MM/yyyy')}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${
                      transaction.category_type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.category_type === 'income' ? '+' : '-'}
                      {parseFloat(transaction.amount).toLocaleString('vi-VN')} ₫
                    </p>
                    {transaction.description && (
                      <p className="text-sm text-gray-500">{transaction.description}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

