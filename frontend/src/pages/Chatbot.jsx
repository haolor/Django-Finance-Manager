import React, { useState, useRef, useEffect } from 'react'
import api from '../services/api'
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: 'Xin chào! Tôi là chatbot hỗ trợ quản lý tài chính. Tôi có thể giúp bạn:',
    },
    {
      type: 'bot',
      text: '• Hỏi về chi tiêu, thu nhập, số dư\n• Dự đoán chi tiêu\n• Phát hiện bất thường\n• Gợi ý tiết kiệm\n\nHãy thử hỏi: "Tôi đã chi bao nhiêu trong tháng này?"',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { type: 'user', text: userMessage }])
    setLoading(true)

    try {
      const response = await api.post('/chatbot/', { message: userMessage })
      setMessages((prev) => [
        ...prev,
        { type: 'bot', text: response.data.response },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'bot',
          text: 'Xin lỗi, tôi không thể xử lý câu hỏi này. Vui lòng thử lại.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleNlpQuery = async (query) => {
    if (loading) return

    setInput('')
    setMessages((prev) => [...prev, { type: 'user', text: query }])
    setLoading(true)

    try {
      // Kiểm tra nếu là câu hỏi về gợi ý tiết kiệm, dự đoán, bất thường, số dư -> dùng chatbot endpoint
      const queryLower = query.toLowerCase()
      const isSavingsQuery = queryLower.includes('tiết kiệm') || 
                            queryLower.includes('gợi ý') || 
                            queryLower.includes('cắt giảm') ||
                            queryLower.includes('savings')
      const isPredictionQuery = queryLower.includes('dự đoán') || 
                               queryLower.includes('tháng sau') ||
                               queryLower.includes('predict')
      const isAnomalyQuery = queryLower.includes('bất thường') || 
                            queryLower.includes('anomaly') ||
                            queryLower.includes('lạ')
      const isBalanceQuery = queryLower.includes('số dư') || 
                           queryLower.includes('còn lại') ||
                           queryLower.includes('balance')
      const isIncomeQuery = queryLower.includes('thu nhập') || 
                           queryLower.includes('tổng thu')
      
      // Các câu hỏi về chi tiêu, thu nhập, số dư, dự đoán, bất thường, tiết kiệm -> dùng chatbot
      if (isSavingsQuery || isPredictionQuery || isAnomalyQuery || isBalanceQuery || isIncomeQuery) {
        // Dùng chatbot endpoint cho các câu hỏi này
        const response = await api.post('/chatbot/', { message: query })
        setMessages((prev) => [
          ...prev,
          { type: 'bot', text: response.data.response },
        ])
      } else {
        // Dùng nlp_query endpoint cho các truy vấn về transactions (chi tiêu cụ thể)
        const response = await api.post('/transactions/nlp_query/', { text: query })
        setMessages((prev) => [
          ...prev,
          { type: 'bot', text: response.data.result },
        ])
      }
    } catch (error) {
      console.error('Error handling query:', error)
      setMessages((prev) => [
        ...prev,
        {
          type: 'bot',
          text: 'Xin lỗi, tôi không thể xử lý truy vấn này. Vui lòng thử lại.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const quickQueries = [
    'Tôi đã chi bao nhiêu trong tháng này?',
    'Tổng thu nhập của tôi là bao nhiêu?',
    'Số dư hiện tại của tôi?',
    'Dự đoán chi tiêu tháng sau',
    'Có giao dịch bất thường nào không?',
    'Gợi ý kế hoạch tiết kiệm hoặc cắt giảm chi tiêu',
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-12rem)]">
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4 md:mb-6">Chatbot Hỗ trợ</h1>

      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.type === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-300 text-gray-900 dark:text-gray-100'
                }`}
              >
                <p className="whitespace-pre-line">{message.text}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg">
                <p>Đang suy nghĩ...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick queries */}
        <div className="px-6 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">Câu hỏi nhanh:</p>
          <div className="flex flex-wrap gap-2">
            {quickQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => handleNlpQuery(query)}
                disabled={loading}
                className="px-3 py-1 text-sm bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhập câu hỏi của bạn..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Chatbot

