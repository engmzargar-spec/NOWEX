"use client"

import { Card } from '@nowex/ui'
import { useState, useEffect } from 'react'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    pendingKyc: 0,
    totalTransactions: 0,
    activeTraders: 0,
  })

  const [recentActivities, setRecentActivities] = useState([
    { id: 1, user: 'کاربر ۱', action: 'ثبت‌نام', time: '۲ دقیقه پیش', status: 'success' },
    { id: 2, user: 'کاربر ۲', action: 'تایید KYC', time: '۱۵ دقیقه پیش', status: 'success' },
    { id: 3, user: 'کاربر ۳', action: 'واریز وجه', time: '۱ ساعت پیش', status: 'pending' },
    { id: 4, user: 'کاربر ۴', action: 'معامله', time: '۲ ساعت پیش', status: 'success' },
    { id: 5, user: 'کاربر ۵', action: 'درخواست برداشت', time: '۳ ساعت پیش', status: 'pending' },
  ])

  useEffect(() => {
    // Simulate fetching data
    setTimeout(() => {
      setStats({
        totalUsers: 1245,
        pendingKyc: 23,
        totalTransactions: 84567,
        activeTraders: 342,
      })
    }, 500)
  }, [])

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">داشبورد مدیریت</h1>
        <p className="text-gray-600 mt-2">نمای کلی از فعالیت‌های سیستم NOWEX</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">کاربران کل</p>
              <p className="text-3xl font-bold mt-2">{stats.totalUsers.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">👥</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-green-600 text-sm">↑ ۱۲٪ نسبت به ماه گذشته</p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">درخواست‌های KYC</p>
              <p className="text-3xl font-bold mt-2">{stats.pendingKyc}</p>
            </div>
            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-red-600 text-sm">نیاز به بررسی فوری</p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">تراکنش‌ها</p>
              <p className="text-3xl font-bold mt-2">{stats.totalTransactions.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-green-600 text-sm">↑ ۲۴٪ نسبت به هفته گذشته</p>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm">معامله‌گران فعال</p>
              <p className="text-3xl font-bold mt-2">{stats.activeTraders}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📈</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-green-600 text-sm">↑ ۸٪ نسبت به دیروز</p>
          </div>
        </Card>
      </div>

      {/* Recent Activities */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-6">فعالیت‌های اخیر</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-right py-3 px-4 text-gray-600 font-medium">کاربر</th>
                <th className="text-right py-3 px-4 text-gray-600 font-medium">عملیات</th>
                <th className="text-right py-3 px-4 text-gray-600 font-medium">زمان</th>
                <th className="text-right py-3 px-4 text-gray-600 font-medium">وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {recentActivities.map((activity) => (
                <tr key={activity.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">{activity.user}</td>
                  <td className="py-3 px-4">{activity.action}</td>
                  <td className="py-3 px-4 text-gray-500">{activity.time}</td>
                  <td className="py-3 px-4">
                    <span className={`
                      px-3 py-1 rounded-full text-sm
                      ${activity.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                      }
                    `}>
                      {activity.status === 'success' ? 'موفق' : 'در انتظار'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-6">عملیات سریع</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-right">
            <div className="text-2xl mb-2">👤</div>
            <p className="font-medium">افزودن کاربر جدید</p>
            <p className="text-gray-500 text-sm mt-1">ایجاد حساب کاربری جدید</p>
          </button>
          
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-right">
            <div className="text-2xl mb-2">✅</div>
            <p className="font-medium">بررسی KYC</p>
            <p className="text-gray-500 text-sm mt-1">مدیریت درخواست‌های تایید هویت</p>
          </button>
          
          <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-right">
            <div className="text-2xl mb-2">📊</div>
            <p className="font-medium">گزارش مالی</p>
            <p className="text-gray-500 text-sm mt-1">گزارش‌های مالی روزانه</p>
          </button>
        </div>
      </Card>
    </div>
  )
}
