import { Button } from '@nowex/ui'
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">صفحه مورد نظر یافت نشد</h2>
        <p className="text-gray-600 mb-8">
          ممکن است آدرس را اشتباه وارد کرده باشید یا صفحه حذف شده باشد.
        </p>
        <div className="space-y-4">
          <Link href="/">
            <Button variant="primary" className="w-full">
              بازگشت به صفحه اصلی
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
