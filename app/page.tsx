"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ImageUpload } from "@/components/image-upload"
import { ResultCard } from "@/components/result-card"
import { Shield, LogOut } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const [result, setResult] = useState<{
    safe: boolean
    message: string
    reasoning?: string
    emails: boolean
    address: boolean
    phoneNumbers: boolean
    licensePlates: boolean
    redactionSuggestions?: string[]
  } | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleLogout = async () => {
    try {
      await fetch("/api/auth/logout", { method: "POST" })
      router.push("/login")
      router.refresh()
    } catch (error) {
      console.error("Error logging out:", error)
    }
  }

  const handleReportIncorrect = async () => {
    if (!result) return

    console.log("[SafePost] User reported incorrect analysis:", {
      result,
      timestamp: new Date().toISOString(),
    })

    try {
      const response = await fetch("/api/report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          result,
          timestamp: new Date().toISOString(),
        }),
      })

      if (response.ok) {
        console.log("[SafePost] Report submitted successfully")
      } else {
        console.error("[SafePost] Failed to submit report:", response.statusText)
      }
    } catch (error) {
      console.error("[SafePost] Error submitting report:", error)
    }
  }

  const handleImageAnalysis = async (file: File) => {
    setIsAnalyzing(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append("image", file)

      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      })

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error("[v0] Error analyzing image:", error)
      setResult({
        safe: false,
        message: "Error analyzing image",
        reasoning: "We encountered an error while processing your image.",
        emails: false,
        address: false,
        phoneNumbers: false,
        licensePlates: false,
        redactionSuggestions: [],
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Shield className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-foreground">SafePost</h1>
                <p className="text-sm text-muted-foreground">Check before you post</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-foreground hover:bg-muted rounded-lg transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-2xl space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">Protect Your Privacy</h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Upload an image to check if it contains personally identifiable information (PII) before sharing on social
              media.
            </p>
          </div>

          <ImageUpload onImageSelect={handleImageAnalysis} isAnalyzing={isAnalyzing} />

          {result && <ResultCard result={result} onReport={handleReportIncorrect} />}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            © 2025 SafePost. Protecting your privacy, one image at a time.
          </p>
        </div>
      </footer>
    </div>
  )
}
