import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // اگر درخواست برای صفحات خطا است، اجازه نده prerender شود
  if (request.nextUrl.pathname.startsWith('/_error') || 
      request.nextUrl.pathname === '/404' ||
      request.nextUrl.pathname === '/500') {
    return NextResponse.rewrite(new URL('/', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
