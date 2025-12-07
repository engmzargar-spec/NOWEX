"use client"

import { useEffect } from 'react'
import { Button } from '@nowex/ui'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-red-600 mb-4">مشکلی پیش آمده!</h2>
        <p className="text-gray-600 mb-6">
          خطایی در بارگذاری صفحه رخ داده است.
        </p>
        <Button
          onClick={() => reset()}
          variant="primary"
        >
          تلاش مجدد
        </Button>
      </div>
    </div>
  )
}
