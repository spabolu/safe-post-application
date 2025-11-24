"use client"

import type React from "react"

import { useCallback, useState } from "react"
import { Upload, ImageIcon, Loader2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface ImageUploadProps {
  onImageSelect: (file: File) => void
  isAnalyzing: boolean
}

export function ImageUpload({ onImageSelect, isAnalyzing }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files[0]
      if (file && file.type.startsWith("image/")) {
        processFile(file)
      }
    },
    [onImageSelect],
  )

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        processFile(file)
      }
    },
    [onImageSelect],
  )

  const processFile = (file: File) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
    onImageSelect(file)
  }

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all duration-200",
        isDragging && "border-primary bg-primary/5",
        isAnalyzing && "opacity-75",
      )}
    >
      <div onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop} className="relative">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileInput}
          className="absolute inset-0 z-10 cursor-pointer opacity-0"
          disabled={isAnalyzing}
          id="file-upload"
        />

        <div className="flex min-h-[320px] flex-col items-center justify-center gap-4 p-8">
          {isAnalyzing ? (
            <>
              <Loader2 className="h-12 w-12 animate-spin text-primary" />
              <div className="text-center space-y-1">
                <p className="text-lg font-medium text-foreground">Analyzing image...</p>
                <p className="text-sm text-muted-foreground">Checking for personally identifiable information</p>
              </div>
            </>
          ) : preview ? (
            <>
              <div className="relative h-48 w-full overflow-hidden rounded-lg">
                <img src={preview || "/placeholder.svg"} alt="Preview" className="h-full w-full object-contain" />
              </div>
              <p className="text-sm text-muted-foreground">Drop a new image or click to replace</p>
            </>
          ) : (
            <>
              <div className="rounded-full bg-primary/10 p-4">
                {isDragging ? (
                  <ImageIcon className="h-8 w-8 text-primary" />
                ) : (
                  <Upload className="h-8 w-8 text-primary" />
                )}
              </div>
              <div className="text-center space-y-2">
                <p className="text-lg font-medium text-foreground">
                  {isDragging ? "Drop your image here" : "Drag and drop your image"}
                </p>
                <p className="text-sm text-muted-foreground">or click to browse your files</p>
              </div>
              <p className="text-xs text-muted-foreground">Supports JPG, PNG, GIF, and WebP formats</p>
            </>
          )}
        </div>
      </div>
    </Card>
  )
}
