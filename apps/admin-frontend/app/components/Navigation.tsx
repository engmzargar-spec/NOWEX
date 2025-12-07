"use client"

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@nowex/ui'

const navItems = [
  { name: 'داشبورد', href: '/dashboard', icon: '📊' },
  { name: 'مدیریت کاربران', href: '/users', icon: '👥' },
  { name: 'تایید هویت (KYC)', href: '/kyc', icon: '✅' },
  { name: 'امور مالی', href: '/finance', icon: '💰' },
  { name: 'سیستم امتیازدهی', href: '/scoring', icon: '⭐' },
  { name: 'ارجاع‌ها', href: '/referral', icon: '🔄' },
  { name: 'تنظیمات', href: '/settings', icon: '⚙️' },
  { name: 'گزارش‌ها', href: '/reports', icon: '📈' },
]

export default function Navigation() {
  const pathname = usePathname()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    window.location.href = '/'
  }

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded-md"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
      >
        {isSidebarOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar */}
      <aside className={`
        fixed lg:static top-0 left-0 h-screen bg-gray-900 text-white
        w-64 p-6 z-40 transform transition-transform duration-300
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:w-64
      `}>
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">NOWEX</h1>
          <p className="text-gray-400 text-sm">پنل مدیریت</p>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                ${pathname === item.href
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }
              `}
              onClick={() => window.innerWidth < 1024 && setIsSidebarOpen(false)}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          ))}
        </nav>

        {/* User info & Logout */}
        <div className="absolute bottom-6 left-6 right-6">
          <div className="border-t border-gray-700 pt-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="font-medium">مدیر سیستم</p>
                <p className="text-gray-400 text-sm">admin@nowex.com</p>
              </div>
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white">A</span>
              </div>
            </div>
            <Button
              variant="secondary"
              onClick={handleLogout}
              className="w-full bg-gray-800 hover:bg-gray-700 text-white"
            >
              خروج از سیستم
            </Button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </>
  )
}
