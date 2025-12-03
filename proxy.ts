import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const authCookie = request.cookies.get('auth')
  const isAuthenticated = authCookie?.value === 'authenticated'
  const pathname = request.nextUrl.pathname
  const isLoginPage = pathname === '/login'
  const isAuthApiRoute = pathname.startsWith('/api/auth')

  // Allow auth API routes to pass through
  if (isAuthApiRoute) {
    return NextResponse.next()
  }

  // If not authenticated and trying to access protected routes
  if (!isAuthenticated && !isLoginPage) {
    // For API routes, return 401 instead of redirect
    if (pathname.startsWith('/api')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // If authenticated and trying to access login page, redirect to home
  if (isAuthenticated && isLoginPage) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}

