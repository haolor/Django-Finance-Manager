import React, { useState, useEffect, useRef } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { format } from 'date-fns'
import {
  HomeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  Cog6ToothIcon,
  BellIcon,
} from '@heroicons/react/24/outline'

function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showNotifications, setShowNotifications] = useState(false)
  const notificationRef = useRef(null)
  
  // Fetch notifications
  useEffect(() => {
    fetchNotifications()
    fetchUnreadCount()
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => {
      fetchNotifications()
      fetchUnreadCount()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false)
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])
  
  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notifications/?limit=10')
      setNotifications(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching notifications:', error)
    }
  }
  
  const fetchUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread_count/')
      setUnreadCount(response.data.unread_count || 0)
    } catch (error) {
      console.error('Error fetching unread count:', error)
    }
  }
  
  const markAsRead = async (notificationId) => {
    try {
      await api.post(`/notifications/${notificationId}/mark_read/`)
      fetchNotifications()
      fetchUnreadCount()
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }
  
  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark_all_read/')
      fetchNotifications()
      fetchUnreadCount()
    } catch (error) {
      console.error('Error marking all as read:', error)
    }
  }

  // Map notification type to styling
  const getNotificationStyle = (type) => {
    const styles = {
      budget_exceeded: {
        emoji: '⚠️',
        bgGradient: 'from-amber-400 to-orange-500',
        cardBg: 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20',
        borderColor: 'border-l-4 border-amber-500',
        label: 'Vượt ngân sách'
      },
      large_transaction: {
        emoji: '💳',
        bgGradient: 'from-blue-400 to-cyan-500',
        cardBg: 'bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20',
        borderColor: 'border-l-4 border-blue-500',
        label: 'Giao dịch lớn'
      },
      anomaly_detected: {
        emoji: '🚨',
        bgGradient: 'from-red-400 to-pink-500',
        cardBg: 'bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20',
        borderColor: 'border-l-4 border-red-500',
        label: 'Phát hiện bất thường'
      },
      report_ready: {
        emoji: '📊',
        bgGradient: 'from-green-400 to-emerald-500',
        cardBg: 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20',
        borderColor: 'border-l-4 border-green-500',
        label: 'Báo cáo'
      },
      system: {
        emoji: 'ℹ️',
        bgGradient: 'from-purple-400 to-indigo-500',
        cardBg: 'bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20',
        borderColor: 'border-l-4 border-purple-500',
        label: 'Thông báo'
      },
    }
    return styles[type] || styles.system
  }

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Giao dịch', href: '/transactions', icon: CurrencyDollarIcon },
    { name: 'Thống kê', href: '/statistics', icon: ChartBarIcon },
    { name: 'AI Insights', href: '/ai-insights', icon: SparklesIcon },
    { name: 'Chatbot', href: '/chatbot', icon: ChatBubbleLeftRightIcon },
    { name: 'Cài đặt', href: '/settings', icon: Cog6ToothIcon },
  ]

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile menu button */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="fixed top-4 left-4 z-50 p-2 rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 shadow-md hover:bg-gray-100 dark:hover:bg-gray-600 md:hidden transition-colors"
        aria-label="Toggle menu"
      >
        {sidebarOpen ? (
          <XMarkIcon className="w-6 h-6" />
        ) : (
          <Bars3Icon className="w-6 h-6" />
        )}
      </button>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 shadow-lg z-40 transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div 
            className="flex items-center justify-between h-16 px-4"
            style={{ backgroundColor: 'var(--primary-color)' }}
          >
            <h1 className="text-xl font-bold text-white">💰 Finance Manager</h1>
            <button
              onClick={() => setSidebarOpen(false)}
              className="md:hidden p-1 text-white hover:opacity-80 rounded transition-opacity"
              aria-label="Close menu"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive(item.href)
                      ? 'text-white'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                  style={isActive(item.href) ? { 
                    backgroundColor: 'var(--primary-color)',
                    opacity: 0.9
                  } : {}}
                >
                  <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User info */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{user?.username}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-2 flex-shrink-0" />
              Đăng xuất
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="md:pl-64">
        {/* Notification Bell - Fixed top right with proper spacing */}
        <div className="fixed top-4 right-4 md:top-6 md:right-6 z-50" ref={notificationRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className={`relative p-3 rounded-full transition-all duration-300 backdrop-blur-sm ${
              unreadCount > 0
                ? 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-lg shadow-red-500/50 hover:shadow-red-500/70 hover:scale-110'
                : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-600'
            }`}
            aria-label="Notifications"
            style={unreadCount > 0 ? { animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' } : {}}
          >
            <BellIcon className="w-6 h-6" />
            {unreadCount > 0 && (
              <span className="absolute -top-2 -right-2 block h-6 w-6 rounded-full bg-gradient-to-br from-yellow-300 to-orange-500 text-white text-xs font-bold flex items-center justify-center border-2 border-white dark:border-gray-900 shadow-lg animate-bounce">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>
          
          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-3 w-96 max-w-[calc(100vw-2rem)] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50" style={{
              animation: 'slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
              transformOrigin: 'top right'
            }}>
              <style>{`
                @keyframes slideDown {
                  from { opacity: 0; transform: translateY(-8px) scale(0.95); }
                  to { opacity: 1; transform: translateY(0) scale(1); }
                }
                @keyframes pulse {
                  0%, 100% { opacity: 1; }
                  50% { opacity: 0.7; }
                }
              `}</style>
              
              {/* Header with gradient */}
              <div className="bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 dark:from-blue-800 dark:via-blue-700 dark:to-cyan-700 px-6 py-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                      <BellIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">Thông báo</h3>
                      <p className="text-xs text-blue-100">{notifications.length} thông báo</p>
                    </div>
                  </div>
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="px-3 py-1.5 rounded-full bg-white/20 hover:bg-white/30 text-white text-xs font-semibold transition-all duration-200 hover:scale-105"
                    >
                      Đánh dấu tất cả
                    </button>
                  )}
                </div>
              </div>
              
              <div className="overflow-y-auto max-h-[450px]">
                {notifications.length === 0 ? (
                  <div className="p-12 text-center">
                    <div className="mx-auto mb-4 p-4 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-full w-fit">
                      <BellIcon className="w-8 h-8 text-gray-400 dark:text-gray-500" />
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 font-semibold">Không có thông báo</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Bạn sẽ nhận được thông báo khi có sự kiện quan trọng</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100 dark:divide-gray-700">
                    {notifications.map((notification) => {
                      const style = getNotificationStyle(notification.type)
                      return (
                        <div
                          key={notification.id}
                          className={`px-5 py-4 transition-all duration-200 cursor-pointer group ${
                            !notification.is_read 
                              ? `${style.cardBg}` 
                              : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                          }`}
                          onClick={() => {
                            if (!notification.is_read) {
                              markAsRead(notification.id)
                            }
                          }}
                        >
                          <div className="flex items-start gap-4">
                            {/* Emoji icon in gradient circle */}
                            <div className={`flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br ${style.bgGradient} flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow text-xl mt-0.5`}>
                              {style.emoji}
                            </div>
                            
                            {/* Content */}
                            <div className="flex-1 min-w-0 py-1">
                              <div className="flex items-start justify-between gap-2">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <p className="text-sm font-bold text-gray-900 dark:text-gray-100">
                                      {notification.title}
                                    </p>
                                    <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gradient-to-r ${style.bgGradient} text-white opacity-75">
                                      {style.label}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-700 dark:text-gray-300 mt-1.5 leading-relaxed">
                                    {notification.message}
                                  </p>
                                  <div className="flex items-center justify-between mt-2.5">
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                      {format(new Date(notification.created_at), 'dd/MM/yyyy HH:mm')}
                                    </p>
                                    {!notification.is_read && (
                                      <div className="text-xs font-semibold text-blue-600 dark:text-blue-400">Mới</div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            {/* Unread indicator */}
                            {!notification.is_read && (
                              <div className="flex-shrink-0 mt-1">
                                <div className="w-3 h-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full shadow-md animate-pulse"></div>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
              
              {/* Footer */}
              {notifications.length > 0 && (
                <div className="px-5 py-3 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-600/50 border-t border-gray-200 dark:border-gray-700 text-center">
                  <button className="text-sm font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
                    Xem tất cả thông báo →
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Main content with padding to avoid bell icon */}
        <main className="p-4 md:p-8 pt-20 md:pt-8 pr-20 md:pr-16">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout

