import { type NextRequest, NextResponse } from "next/server"
import { GoogleGenAI, Type } from "@google/genai"

export async function POST(request: NextRequest) {
  try {
    // Validate API key is present
    const apiKey = process.env.GEMINI_API_KEY
    if (!apiKey) {
      console.error("[v0] GEMINI_API_KEY environment variable is not set")
      return NextResponse.json(
        {
          safe: false,
          message: "Configuration error",
          reasoning: "API key is not configured. Please set GEMINI_API_KEY environment variable in your .env.local file.",
          emails: false,
          address: false,
          phoneNumbers: false,
          licensePlates: false,
          redactionSuggestions: [],
        },
        { status: 500 },
      )
    }

    // Initialize client with API key
    const ai = new GoogleGenAI({
      apiKey: apiKey,
    })

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

    console.log("[v0] Starting image analysis with Google GenAI")

    const prompt = `You are a strict PII detection system. Analyze this image thoroughly for personally identifiable information (PII) in these 4 categories:

1. EMAIL ADDRESSES: Any visible email addresses anywhere in the image (including screenshots, documents, signs, business cards, or text overlays). Be strict - flag even partial or obscured emails.

2. ADDRESSES: Any street addresses, house numbers, postal addresses, or location identifiers visible in the image (on documents, signs, mail, packages, or any text). Be strict - flag any address-like information.

3. PHONE NUMBERS: Any visible phone numbers in any format (with or without dashes, parentheses, spaces, country codes). Include numbers on screenshots, documents, signs, business cards, or any text. Be strict - flag any sequence that could be a phone number.

4. LICENSE PLATES: Any vehicle license plates visible in the image, regardless of clarity or partial visibility. Be strict - flag even partially visible plates.

IMPORTANT RULES:
- Treat screenshots, text overlays, and embedded text the same as any other content - analyze them strictly.
- Ignore QR codes completely - do not analyze their contents.
- Be strict: when in doubt, flag as detected (true).
- The image is ONLY safe to post if ALL 4 categories are false (no PII detected in any category).

OUTPUT REQUIREMENTS:
- reasoning: Provide ONE specific sentence or phrase describing what PII was found (or confirm none found). Be concise and specific about location/type if found.
- redactionSuggestions: If PII is detected, provide short, actionable suggestions for redaction (e.g., "Blur email in top-right corner", "Cover license plate with rectangle"). If safe, provide empty array.`

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: [
        {
          inlineData: {
            data: base64Image,
            mimeType: mimeType,
          },
        },
        prompt,
      ],
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            safe: {
              type: Type.BOOLEAN,
              description: "true if no PII detected in any category, false if any PII is found",
            },
            message: {
              type: Type.STRING,
              description: "brief summary of the analysis",
            },
            reasoning: {
              type: Type.STRING,
              description: "One specific sentence or phrase describing what PII was found or confirming none found. Be concise and specific about location/type if detected.",
            },
            redactionSuggestions: {
              type: Type.ARRAY,
              items: {
                type: Type.STRING,
              },
              description: "Short, actionable suggestions for redacting detected PII (e.g., 'Blur email in top-right corner', 'Cover license plate'). Empty array if image is safe.",
            },
            emails: {
              type: Type.BOOLEAN,
              description: "true if email addresses are detected in the image, false otherwise",
            },
            address: {
              type: Type.BOOLEAN,
              description: "true if addresses (street addresses, house numbers) are detected in the image, false otherwise",
            },
            phoneNumbers: {
              type: Type.BOOLEAN,
              description: "true if phone numbers are detected in the image, false otherwise",
            },
            licensePlates: {
              type: Type.BOOLEAN,
              description: "true if license plates are detected in the image, false otherwise",
            },
          },
          required: ["safe", "message", "reasoning", "emails", "address", "phoneNumbers", "licensePlates"],
          propertyOrdering: ["safe", "message", "reasoning", "emails", "address", "phoneNumbers", "licensePlates", "redactionSuggestions"],
        },
      },
    })

    if (!response.text) {
      throw new Error("No response text from model")
    }

    const result = JSON.parse(response.text.trim())
    console.log("[v0] Analysis complete:", result)

    return NextResponse.json(result)
  } catch (error) {
    console.error("[v0] Error in analyze API:", error)
      return NextResponse.json(
        {
          safe: false,
          message: "Error analyzing image",
          reasoning: "We encountered an error while processing your image.",
          emails: false,
          address: false,
          phoneNumbers: false,
          licensePlates: false,
          redactionSuggestions: [],
        },
        { status: 500 },
      )
  }
}
