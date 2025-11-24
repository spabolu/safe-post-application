import { type NextRequest, NextResponse } from "next/server"
import { generateObject } from "ai"
import { z } from "zod"

const piiAnalysisSchema = z.object({
  safe: z.boolean().describe("true if no PII detected, false if PII found"),
  message: z.string().describe("brief summary of the analysis"),
  reasoning: z.string().describe("detailed explanation of why the image is considered safe or unsafe"),
  details: z.array(z.string()).describe("list of specific PII types found, or empty array if safe"),
})

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const image = formData.get("image") as File

    if (!image) {
      return NextResponse.json({ error: "No image provided" }, { status: 400 })
    }

    // Convert image to base64
    const bytes = await image.arrayBuffer()
    const buffer = Buffer.from(bytes)
    const base64Image = buffer.toString("base64")
    const mimeType = image.type

    console.log("[v0] Starting image analysis with AI Gateway")

    const { object } = await generateObject({
      model: "google/gemini-2.5-pro-preview-05-06",
      schema: piiAnalysisSchema,
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: `Analyze this image for personally identifiable information (PII). Look for:
- Names (on documents, badges, signs)
- Addresses (street addresses, house numbers)
- Phone numbers
- Email addresses
- Social Security Numbers
- Credit card numbers
- License plates
- Government ID numbers
- Medical records or health information
- Financial information
- Signatures
- Dates of birth
- Biometric data identifiers

Determine if the image is safe to post on social media. Provide a clear reasoning for your decision.`,
            },
            {
              type: "image",
              image: `data:${mimeType};base64,${base64Image}`,
            },
          ],
        },
      ],
    })

    console.log("[v0] Analysis complete:", object)

    return NextResponse.json(object)
  } catch (error) {
    console.error("[v0] Error in analyze API:", error)
    return NextResponse.json(
      {
        safe: false,
        message: "Error analyzing image",
        reasoning: "We encountered an error while processing your image.",
        details: ["An unexpected error occurred. Please try again."],
      },
      { status: 500 },
    )
  }
}
