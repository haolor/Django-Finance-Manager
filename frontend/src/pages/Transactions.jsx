import React, { useEffect, useState, useRef } from 'react'
import api from '../services/api'
import { format } from 'date-fns'
import { PlusIcon, PencilIcon, TrashIcon, MicrophoneIcon, ChevronLeftIcon, ChevronRightIcon, PhotoIcon } from '@heroicons/react/24/outline'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const [nlpInput, setNlpInput] = useState('')
  const [showNlpModal, setShowNlpModal] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [nlpError, setNlpError] = useState('')
  const [nlpLoading, setNlpLoading] = useState(false)
  const recognitionRef = useRef(null)
  // OCR state
  const [showOcrModal, setShowOcrModal] = useState(false)
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [ocrLoading, setOcrLoading] = useState(false)
  const [ocrResult, setOcrResult] = useState(null)
  const [ocrError, setOcrError] = useState('')
  // Pagination state
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    totalPages: 1,
  })
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    category: '',
    transaction_date: format(new Date(), 'yyyy-MM-dd'),
  })

  useEffect(() => {
    fetchData(1)
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const categoriesRes = await api.get('/categories/')
      setCategories(categoriesRes.data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const fetchData = async (page = 1) => {
    setLoading(true)
    try {
      const transactionsRes = await api.get(`/transactions/?page=${page}`)
      const data = transactionsRes.data
      
      // Handle paginated response
      if (data.results) {
        setTransactions(data.results)
        // Calculate total pages (assuming PAGE_SIZE = 20)
        const totalPages = Math.ceil((data.count || 0) / 20)
        setPagination({
          count: data.count || 0,
          next: data.next,
          previous: data.previous,
          currentPage: page,
          totalPages: totalPages || 1,
        })
      } else {
        // Fallback for non-paginated response
        setTransactions(Array.isArray(data) ? data : [])
        setPagination({
          count: Array.isArray(data) ? data.length : 0,
          next: null,
          previous: null,
          currentPage: 1,
          totalPages: 1,
        })
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePageChange = (page) => {
    if (page >= 1 && page <= pagination.totalPages) {
      fetchData(page)
      // Scroll to top of table
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  // Khởi tạo Speech Recognition
  useEffect(() => {
    if (showNlpModal) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition()
        recognition.lang = 'vi-VN'
        recognition.continuous = false
        recognition.interimResults = false
        
        recognition.onstart = () => {
          setIsListening(true)
          setNlpError('')
        }
        
        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript
          setNlpInput(prev => prev + (prev ? ' ' : '') + transcript)
          setIsListening(false)
        }
        
        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error)
          setIsListening(false)
          if (event.error === 'no-speech') {
            setNlpError('Không phát hiện giọng nói. Vui lòng thử lại.')
          } else if (event.error === 'not-allowed') {
            setNlpError('Vui lòng cho phép truy cập microphone.')
          } else {
            setNlpError('Lỗi nhận diện giọng nói. Vui lòng thử lại.')
          }
        }
        
        recognition.onend = () => {
          setIsListening(false)
        }
        
        recognitionRef.current = recognition
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
        recognitionRef.current = null
      }
    }
  }, [showNlpModal])

  const startListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start()
        setNlpError('')
      } catch (error) {
        console.error('Error starting recognition:', error)
        setNlpError('Không thể bắt đầu nhận diện giọng nói.')
      }
    } else {
      setNlpError('Trình duyệt không hỗ trợ nhận diện giọng nói. Vui lòng sử dụng Chrome hoặc Edge.')
    }
  }

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }

  const handleNlpSubmit = async (e) => {
    e.preventDefault()
    if (!nlpInput.trim()) {
      setNlpError('Vui lòng nhập hoặc nói câu mô tả giao dịch.')
      return
    }
    
    setNlpLoading(true)
    setNlpError('')
    
    try {
      const response = await api.post('/transactions/nlp_input/', { text: nlpInput })
      setNlpInput('')
      setShowNlpModal(false)
      setNlpError('')
      fetchData(1) // Reload first page
      // Hiển thị thông báo thành công
      alert('Đã thêm giao dịch thành công!')
    } catch (error) {
      console.error('NLP error:', error)
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail ||
                          'Không thể xử lý câu nhập liệu. Vui lòng kiểm tra lại định dạng.\n\nVí dụ: "Hôm nay chi 50k ăn sáng", "Chi 100000 mua quần áo"'
      setNlpError(errorMessage)
    } finally {
      setNlpLoading(false)
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
      fetchData(pagination.currentPage) // Reload current page
    } catch (error) {
      alert('Có lỗi xảy ra. Vui lòng thử lại.')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa giao dịch này?')) {
      try {
        await api.delete(`/transactions/${id}/`)
        // If current page becomes empty, go to previous page
        if (transactions.length === 1 && pagination.currentPage > 1) {
          fetchData(pagination.currentPage - 1)
        } else {
          fetchData(pagination.currentPage)
        }
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

  const handleImageSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Kiểm tra định dạng
      if (!file.type.startsWith('image/')) {
        setOcrError('Vui lòng chọn file ảnh (JPG, PNG, WebP)')
        return
      }
      
      // Kiểm tra kích thước (10MB)
      if (file.size > 10 * 1024 * 1024) {
        setOcrError('Kích thước ảnh quá lớn. Vui lòng chọn ảnh nhỏ hơn 10MB')
        return
      }
      
      setSelectedImage(file)
      setOcrError('')
      setOcrResult(null)
      
      // Tạo preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleOcrSubmit = async () => {
    if (!selectedImage) {
      setOcrError('Vui lòng chọn ảnh hóa đơn')
      return
    }
    
    setOcrLoading(true)
    setOcrError('')
    setOcrResult(null)
    
    try {
      const formData = new FormData()
      formData.append('image', selectedImage)
      
      const response = await api.post('/transactions/ocr_receipt/', formData)
      
      setOcrResult(response.data)
      // Tự động đóng modal và reload data
      setTimeout(() => {
        setShowOcrModal(false)
        setSelectedImage(null)
        setImagePreview(null)
        setOcrResult(null)
        fetchData(1)
        alert('Đã thêm giao dịch từ hóa đơn thành công!')
      }, 2000)
      
    } catch (error) {
      console.error('OCR error:', error)
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail ||
                          'Không thể xử lý ảnh. Vui lòng thử lại với ảnh rõ hơn.'
      setOcrError(errorMessage)
      if (error.response?.data?.raw_text) {
        setOcrResult({ raw_text: error.response.data.raw_text })
      }
    } finally {
      setOcrLoading(false)
    }
  }

  const handleOcrCancel = () => {
    setShowOcrModal(false)
    setSelectedImage(null)
    setImagePreview(null)
    setOcrResult(null)
    setOcrError('')
  }

  if (loading) {
    return <div className="text-center py-12">Đang tải...</div>
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 md:mb-8 gap-4 pr-20 md:pr-16">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100">Quản lý Giao dịch</h1>
        <div className="flex flex-wrap gap-2 sm:gap-4 w-full sm:w-auto">
          <button
            onClick={() => {
              setShowOcrModal(true)
              setSelectedImage(null)
              setImagePreview(null)
              setOcrResult(null)
              setOcrError('')
            }}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
          >
            <PhotoIcon className="w-5 h-5 mr-2" />
            Quét hóa đơn
          </button>
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
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Nhập liệu bằng ngôn ngữ tự nhiên</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Ví dụ: "Hôm nay chi 50k ăn sáng", "Chi 100000 mua quần áo", "Nhận lương 10 triệu"
            </p>
            
            {nlpError && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                {nlpError}
              </div>
            )}
            
            <form onSubmit={handleNlpSubmit}>
              <div className="relative mb-4">
                <textarea
                  value={nlpInput}
                  onChange={(e) => {
                    setNlpInput(e.target.value)
                    setNlpError('')
                  }}
                  placeholder="Nhập câu mô tả giao dịch hoặc nhấn nút microphone để nói..."
                  className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg resize-none"
                  rows={4}
                />
                <button
                  type="button"
                  onClick={isListening ? stopListening : startListening}
                  className={`absolute right-2 top-2 p-2 rounded-full transition-colors ${
                    isListening 
                      ? 'bg-red-500 text-white animate-pulse' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                  title={isListening ? 'Dừng ghi âm' : 'Bắt đầu ghi âm'}
                >
                  <MicrophoneIcon className="w-5 h-5" />
                </button>
              </div>
              
              {isListening && (
                <div className="mb-4 text-sm text-purple-600 flex items-center">
                  <div className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></div>
                  Đang nghe... Hãy nói câu mô tả giao dịch của bạn
                </div>
              )}
              
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowNlpModal(false)
                    setNlpInput('')
                    setNlpError('')
                    stopListening()
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  disabled={nlpLoading}
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={nlpLoading || !nlpInput.trim()}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {nlpLoading ? 'Đang xử lý...' : 'Xử lý'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* OCR Modal */}
      {showOcrModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Quét hóa đơn từ ảnh</h2>
            <p className="text-sm text-gray-600 mb-4">
              Upload ảnh hóa đơn để tự động trích xuất thông tin giao dịch
            </p>
            
            {ocrError && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                {ocrError}
              </div>
            )}
            
            {ocrResult && ocrResult.transaction && (
              <div className="mb-4 p-4 bg-green-50 border border-green-400 rounded">
                <p className="text-green-800 font-medium mb-2">✅ Đã trích xuất thành công!</p>
                <div className="text-sm text-green-700 space-y-1">
                  <p>Số tiền: {ocrResult.extracted_info?.amount?.toLocaleString('vi-VN')}₫</p>
                  {ocrResult.extracted_info?.category && <p>Danh mục: {ocrResult.extracted_info.category}</p>}
                  {ocrResult.extracted_info?.description && <p>Mô tả: {ocrResult.extracted_info.description}</p>}
                  {ocrResult.extracted_info?.merchant_name && <p>Cửa hàng: {ocrResult.extracted_info.merchant_name}</p>}
                  {Array.isArray(ocrResult.extracted_info?.items) && ocrResult.extracted_info.items.length > 0 && (
                    <div className="mt-3">
                      <p className="font-medium mb-2">Chi tiết món:</p>
                      <div className="overflow-x-auto border border-green-200 rounded">
                        <table className="min-w-full text-xs md:text-sm">
                          <thead className="bg-green-100">
                            <tr>
                              <th className="text-left px-2 py-1">Tên món</th>
                              <th className="text-right px-2 py-1">SL</th>
                              <th className="text-right px-2 py-1">Giá tiền</th>
                              <th className="text-right px-2 py-1">Thành tiền</th>
                            </tr>
                          </thead>
                          <tbody>
                            {ocrResult.extracted_info.items.map((item, idx) => (
                              <tr key={`${item.name}-${idx}`} className="border-t border-green-100">
                                <td className="px-2 py-1">{item.name}</td>
                                <td className="text-right px-2 py-1">{Number(item.quantity || 1)}</td>
                                <td className="text-right px-2 py-1">{Number(item.unit_price || item.line_total || 0).toLocaleString('vi-VN')}₫</td>
                                <td className="text-right px-2 py-1 font-medium">{Number(item.line_total || 0).toLocaleString('vi-VN')}₫</td>
                              </tr>
                            ))}
                          </tbody>
                          <tfoot>
                            <tr className="border-t border-green-300 bg-green-50">
                              <td className="px-2 py-1 font-semibold" colSpan={3}>Tổng cộng</td>
                              <td className="text-right px-2 py-1 font-semibold">
                                {Number(ocrResult.extracted_info?.amount || 0).toLocaleString('vi-VN')}₫
                              </td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            <div className="space-y-4">
              {/* Image Preview */}
              {imagePreview && (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="max-w-full h-auto max-h-64 mx-auto rounded"
                  />
                </div>
              )}
              
              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chọn ảnh hóa đơn
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  disabled={ocrLoading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Hỗ trợ: JPG, PNG, WebP (tối đa 10MB)
                </p>
              </div>
              
              {/* OCR Text Preview */}
              {ocrResult && ocrResult.raw_text && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Text đã đọc được:</p>
                  <div className="p-3 bg-gray-50 rounded border border-gray-200 max-h-32 overflow-y-auto">
                    <p className="text-xs text-gray-600 whitespace-pre-wrap">{ocrResult.raw_text}</p>
                  </div>
                </div>
              )}
              
              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={handleOcrCancel}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  disabled={ocrLoading}
                >
                  Hủy
                </button>
                <button
                  onClick={handleOcrSubmit}
                  disabled={ocrLoading || !selectedImage}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {ocrLoading ? 'Đang xử lý...' : 'Quét và thêm giao dịch'}
                </button>
              </div>
            </div>
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {/* Mobile Card View */}
        <div className="md:hidden">
          {transactions.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              Chưa có giao dịch nào
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center flex-1 min-w-0">
                      <span className="text-2xl mr-2 flex-shrink-0">{transaction.category_icon || '💰'}</span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {transaction.category_name || 'Khác'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {format(new Date(transaction.transaction_date), 'dd/MM/yyyy')}
                        </p>
                      </div>
                    </div>
                    <p className={`text-sm font-bold ml-2 flex-shrink-0 ${
                      transaction.category_type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                    }`}>
                      {transaction.category_type === 'income' ? '+' : '-'}
                      {parseFloat(transaction.amount).toLocaleString('vi-VN')} ₫
                    </p>
                  </div>
                  {transaction.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 truncate">
                      {transaction.description}
                    </p>
                  )}
                  <div className="flex justify-end space-x-2 mt-2">
                    <button
                      onClick={() => handleEdit(transaction)}
                      className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded"
                    >
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(transaction.id)}
                      className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Desktop Table View */}
        <div className="hidden md:block overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Ngày
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Danh mục
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Mô tả
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Số tiền
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Thao tác
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                    Chưa có giao dịch nào
                  </td>
                </tr>
              ) : (
                transactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {format(new Date(transaction.transaction_date), 'dd/MM/yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-xl md:text-2xl mr-2">{transaction.category_icon || '💰'}</span>
                        <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {transaction.category_name || 'Khác'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {transaction.description || '-'}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${
                      transaction.category_type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                    }`}>
                      {transaction.category_type === 'income' ? '+' : '-'}
                      {parseFloat(transaction.amount).toLocaleString('vi-VN')} ₫
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => handleEdit(transaction)}
                          className="text-blue-600 dark:text-blue-400 hover:text-blue-900 dark:hover:text-blue-300"
                        >
                          <PencilIcon className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(transaction.id)}
                          className="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300"
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
        
        {/* Pagination */}
        {pagination.count > 0 && pagination.totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => handlePageChange(pagination.currentPage - 1)}
                disabled={!pagination.previous}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Trước
              </button>
              <button
                onClick={() => handlePageChange(pagination.currentPage + 1)}
                disabled={!pagination.next}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sau
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Hiển thị{' '}
                  <span className="font-medium">
                    {((pagination.currentPage - 1) * 20) + 1}
                  </span>{' '}
                  đến{' '}
                  <span className="font-medium">
                    {Math.min(pagination.currentPage * 20, pagination.count)}
                  </span>{' '}
                  trong tổng số{' '}
                  <span className="font-medium">{pagination.count}</span> giao dịch
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => handlePageChange(pagination.currentPage - 1)}
                    disabled={!pagination.previous}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeftIcon className="h-5 w-5" />
                  </button>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                    let pageNum
                    if (pagination.totalPages <= 5) {
                      pageNum = i + 1
                    } else if (pagination.currentPage <= 3) {
                      pageNum = i + 1
                    } else if (pagination.currentPage >= pagination.totalPages - 2) {
                      pageNum = pagination.totalPages - 4 + i
                    } else {
                      pageNum = pagination.currentPage - 2 + i
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          pageNum === pagination.currentPage
                            ? 'z-10 bg-purple-50 border-purple-500 text-purple-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                  
                  <button
                    onClick={() => handlePageChange(pagination.currentPage + 1)}
                    disabled={!pagination.next}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRightIcon className="h-5 w-5" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Transactions

