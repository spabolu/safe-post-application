import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

// Simple hardcoded credentials - in production, use environment variables
const VALID_USERNAME = process.env.AUTH_USERNAME || 'admin'
const VALID_PASSWORD = process.env.AUTH_PASSWORD || 'password'

export async function POST(request: NextRequest) {
  try {
    const { username, password } = await request.json()

    if (!username || !password) {
      return NextResponse.json(
        { error: 'Username and password are required' },
        { status: 400 }
      )
    }

    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
      const cookieStore = await cookies()
      cookieStore.set('auth', 'authenticated', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7, // 7 days
      })

      return NextResponse.json({ success: true })
    }

    return NextResponse.json(
      { error: 'Invalid username or password' },
      { status: 401 }
    )
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    )
  }
}

