import React, { useEffect, useState } from 'react'
import api from '../services/api'
import { format } from 'date-fns'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const [nlpInput, setNlpInput] = useState('')
  const [showNlpModal, setShowNlpModal] = useState(false)
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    category: '',
    transaction_date: format(new Date(), 'yyyy-MM-dd'),
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [transactionsRes, categoriesRes] = await Promise.all([
        api.get('/transactions/'),
        api.get('/categories/'),
      ])
      setTransactions(transactionsRes.data.results || transactionsRes.data)
      setCategories(categoriesRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNlpSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/transactions/nlp_input/', { text: nlpInput })
      setNlpInput('')
      setShowNlpModal(false)
      fetchData()
    } catch (error) {
      alert('Không thể xử lý câu nhập liệu. Vui lòng thử lại.')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingTransaction) {
        await api.put(`/transactions/${editingTransaction.id}/`, formData)
      } else {
        await api.post('/transactions/', formData)
      }
      setShowModal(false)
      setEditingTransaction(null)
      setFormData({
        amount: '',
        description: '',
        category: '',
        transaction_date: format(new Date(), 'yyyy-MM-dd'),
      })
      fetchData()
    } catch (error) {
      alert('Có lỗi xảy ra. Vui lòng thử lại.')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa giao dịch này?')) {
      try {
        await api.delete(`/transactions/${id}/`)
        fetchData()
      } catch (error) {
        alert('Không thể xóa giao dịch.')
      }
    }
  }

  const handleEdit = (transaction) => {
    setEditingTransaction(transaction)
    setFormData({
      amount: transaction.amount,
      description: transaction.description,
      category: transaction.category,
      transaction_date: transaction.transaction_date,
    })
    setShowModal(true)
  }

  if (loading) {
    return <div className="text-center py-12">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Quản lý Giao dịch</h1>
        <div className="space-x-4">
          <button
            onClick={() => {
              setShowNlpModal(true)
              setNlpInput('')
            }}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Nhập bằng giọng nói/NLP
          </button>
          <button
            onClick={() => {
              setEditingTransaction(null)
              setFormData({
                amount: '',
                description: '',
                category: '',
                transaction_date: format(new Date(), 'yyyy-MM-dd'),
              })
              setShowModal(true)
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <PlusIcon className="w-5 h-5 mr-2" />
            Thêm giao dịch
          </button>
        </div>
      </div>

      {/* NLP Modal */}
      {showNlpModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Nhập liệu bằng ngôn ngữ tự nhiên</h2>
            <p className="text-sm text-gray-600 mb-4">
              Ví dụ: "Hôm nay chi 50k ăn sáng", "Chi 100000 mua quần áo"
            </p>
            <form onSubmit={handleNlpSubmit}>
              <textarea
                value={nlpInput}
                onChange={(e) => setNlpInput(e.target.value)}
                placeholder="Nhập câu mô tả giao dịch..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
                rows={3}
                required
              />
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => setShowNlpModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Xử lý
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">
              {editingTransaction ? 'Chỉnh sửa giao dịch' : 'Thêm giao dịch mới'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Số tiền *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Danh mục *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Chọn danh mục</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mô tả
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ngày giao dịch *
                </label>
                <input
                  type="date"
                  value={formData.transaction_date}
                  onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingTransaction(null)
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingTransaction ? 'Cập nhật' : 'Thêm'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transactions List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ngày
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Danh mục
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mô tả
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Số tiền
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Thao tác
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                    Chưa có giao dịch nào
                  </td>
                </tr>
              ) : (
                transactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {format(new Date(transaction.transaction_date), 'dd/MM/yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-2xl mr-2">{transaction.category_icon || '💰'}</span>
                        <span className="text-sm font-medium text-gray-900">
                          {transaction.category_name || 'Khác'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {transaction.description || '-'}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${
                      transaction.category_type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.category_type === 'income' ? '+' : '-'}
                      {parseFloat(transaction.amount).toLocaleString('vi-VN')} ₫
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(transaction)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <PencilIcon className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(transaction.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Transactions

