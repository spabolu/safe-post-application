import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET() {
  const cookieStore = await cookies()
  const authCookie = cookieStore.get('auth')
  
  return NextResponse.json({ 
    authenticated: authCookie?.value === 'authenticated' 
  })
}

