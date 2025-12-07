"use client"

import { Inter } from "next/font/google"
import "./globals.css"
import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"
import Navigation from "./components/Navigation"
import Header from "./components/Header"

const inter = Inter({ subsets: ["latin"] })

// صفحاتی که نیاز به layout کامل دارند (صفحات خصوصی)
const PRIVATE_PAGES = ['/dashboard', '/users', '/kyc', '/finance', '/scoring', '/referral', '/settings', '/reports']

// صفحات عمومی (بدون navigation)
const PUBLIC_PAGES = ['/login', '/', '/404', '/500']

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname()
  const [isMounted, setIsMounted] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    setIsMounted(true)
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
  }, [])

  if (!isMounted) {
    return (
      <html lang="fa" dir="rtl">
        <body className={`${inter.className} antialiased`}>
          <div className="min-h-screen flex items-center justify-center">
            در حال بارگذاری...
          </div>
        </body>
      </html>
    )
  }

  // اگر صفحه عمومی است layout ساده نشان بده
  const isPublicPage = PUBLIC_PAGES.some(page => pathname?.startsWith(page))
  
  if (isPublicPage) {
    return (
      <html lang="fa" dir="rtl">
        <body className={`${inter.className} antialiased`}>
          {children}
        </body>
      </html>
    )
  }

  // اگر صفحه خصوصی است اما کاربر وارد نشده به login هدایت کن
  const isPrivatePage = PRIVATE_PAGES.some(page => pathname?.startsWith(page))
  
  if (isPrivatePage && !isAuthenticated && typeof window !== 'undefined') {
    // استفاده از setTimeout برای جلوگیری از خطای hydration
    setTimeout(() => {
      window.location.href = '/login'
    }, 0)
    
    return (
      <html lang="fa" dir="rtl">
        <body className={`${inter.className} antialiased`}>
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">در حال هدایت به صفحه ورود...</p>
            </div>
          </div>
        </body>
      </html>
    )
  }

  // اگر صفحه خصوصی و کاربر وارد شده layout کامل نشان بده
  return (
    <html lang="fa" dir="rtl">
      <body className={`${inter.className} antialiased`}>
        <div className="flex h-screen bg-gray-50">
          {/* Navigation Sidebar */}
          <Navigation />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header />
            
            {/* Page Content */}
            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
            
            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <p>NOWEX Admin Panel v0.1.0</p>
                <p>© 2025 NOWEX Platform. All rights reserved.</p>
              </div>
            </footer>
          </div>
        </div>
      </body>
    </html>
  )
}
