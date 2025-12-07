"use client"

import { useState } from 'react'
import { Button } from '@nowex/ui'

export default function Header() {
  const [notifications] = useState(3)
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-lg">
          <div className="relative">
            <input
              type="text"
              placeholder="جستجو در سیستم..."
              className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
              🔍
            </div>
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 hover:bg-gray-100 rounded-lg">
            <span className="text-xl">🔔</span>
            {notifications > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {notifications}
              </span>
            )}
          </button>

          {/* Help */}
          <button className="p-2 hover:bg-gray-100 rounded-lg">
            <span className="text-xl">❓</span>
          </button>

          {/* Profile dropdown */}
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="font-medium">مدیر سیستم</p>
              <p className="text-gray-500 text-sm">سطح دسترسی: ادمین</p>
            </div>
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-medium">A</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
