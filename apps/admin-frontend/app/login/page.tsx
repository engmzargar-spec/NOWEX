"use client"

import { Button, Card, Input } from "@nowex/ui"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const router = useRouter()
  const [isMounted, setIsMounted] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    setIsMounted(true)
    // اگر کاربر قبلا وارد شده به dashboard هدایت شود
    const token = localStorage.getItem('access_token')
    if (token) {
      router.push('/dashboard')
    }
  }, [router])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    // TODO: Call real API
    console.log("Login attempt:", { email, password })
    
    // Mock authentication با تاخیر
    setTimeout(() => {
      localStorage.setItem('access_token', 'mock_jwt_token')
      setIsLoading(false)
      router.push('/dashboard')
    }, 1000)
  }

  if (!isMounted) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">در حال بارگذاری...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">NOWEX Admin</h1>
          <p className="text-gray-600 mt-2">پنل مدیریت صرافی نوکس</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              آدرس ایمیل
            </label>
            <Input
              type="email"
              placeholder="admin@nowex.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              رمز عبور
            </label>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <Button 
            type="submit" 
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                در حال ورود...
              </span>
            ) : 'ورود به سیستم'}
          </Button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600 text-center">
            برای دسترسی آزمایشی از<br />
            <span className="font-mono bg-gray-100 px-2 py-1 rounded mt-1 inline-block">
              admin@nowex.com
            </span> 
            {" "}و رمز{" "}
            <span className="font-mono bg-gray-100 px-2 py-1 rounded">
              password123
            </span>
          </p>
        </div>
      </Card>
    </div>
  )
}
