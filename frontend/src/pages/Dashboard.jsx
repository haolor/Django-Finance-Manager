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
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 md:mb-8">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400">Tổng thu nhập</p>
              <p className="text-xl md:text-2xl font-bold text-green-600 dark:text-green-400 mt-1 md:mt-2 truncate">
                {stats?.summary?.total_income?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <ArrowUpIcon className="w-8 h-8 md:w-12 md:h-12 text-green-500 dark:text-green-400 flex-shrink-0 ml-2" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400">Tổng chi tiêu</p>
              <p className="text-xl md:text-2xl font-bold text-red-600 dark:text-red-400 mt-1 md:mt-2 truncate">
                {stats?.summary?.total_expense?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <ArrowDownIcon className="w-8 h-8 md:w-12 md:h-12 text-red-500 dark:text-red-400 flex-shrink-0 ml-2" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-700 rounded-lg shadow p-4 md:p-6 sm:col-span-2 md:col-span-1">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400">Số dư</p>
              <p className={`text-xl md:text-2xl font-bold mt-1 md:mt-2 truncate ${
                (stats?.summary?.balance || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              }`}>
                {stats?.summary?.balance?.toLocaleString('vi-VN') || 0} ₫
              </p>
            </div>
            <CurrencyDollarIcon className="w-8 h-8 md:w-12 md:h-12 text-blue-500 dark:text-blue-400 flex-shrink-0 ml-2" />
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white dark:bg-gray-700 rounded-lg shadow">
        <div className="p-4 md:p-6 border-b border-gray-200 dark:border-gray-600">
          <h2 className="text-lg md:text-xl font-semibold text-gray-900 dark:text-gray-100">Giao dịch gần đây</h2>
        </div>
        <div className="p-4 md:p-6">
          {recentTransactions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Chưa có giao dịch nào</p>
          ) : (
            <div className="space-y-3 md:space-y-4">
              {recentTransactions.map((transaction) => {
                // Giới hạn description để tránh quá dài
                const maxDescriptionLength = 50
                const truncatedDescription = transaction.description 
                  ? (transaction.description.length > maxDescriptionLength 
                      ? transaction.description.substring(0, maxDescriptionLength) + '...' 
                      : transaction.description)
                  : null
                
                return (
                  <div
                    key={transaction.id}
                    className="flex flex-col md:flex-row md:items-center md:justify-between p-3 md:p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 gap-2 md:gap-0"
                  >
                    <div className="flex items-center space-x-2 md:space-x-4 flex-1 min-w-0">
                      <div
                        className="w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center text-xl md:text-2xl flex-shrink-0"
                        style={{ backgroundColor: transaction.category_color + '20' }}
                      >
                        {transaction.category_icon || '💰'}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 dark:text-gray-100 truncate text-sm md:text-base">
                          {transaction.category_name || 'Khác'}
                        </p>
                        <p className="text-xs md:text-sm text-gray-500 dark:text-gray-400">
                          {format(new Date(transaction.transaction_date), 'dd/MM/yyyy')}
                        </p>
                        {truncatedDescription && (
                          <p 
                            className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1 max-w-full"
                            title={transaction.description}
                          >
                            {truncatedDescription}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0 ml-0 md:ml-2">
                      <p className={`font-bold text-sm md:text-base whitespace-nowrap ${
                        transaction.category_type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                        {transaction.category_type === 'income' ? '+' : '-'}
                        {parseFloat(transaction.amount).toLocaleString('vi-VN')} ₫
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

