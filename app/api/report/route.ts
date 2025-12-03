import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { result, timestamp } = body

    console.log("[SafePost] User reported incorrect analysis:")
    console.log("  Timestamp:", timestamp)
    console.log("  Result:", JSON.stringify(result, null, 2))
    console.log("  Safe:", result?.safe)
    console.log("  Message:", result?.message)
    console.log("  Reasoning:", result?.reasoning)
    console.log("  PII Detection:", {
      emails: result?.emails,
      address: result?.address,
      phoneNumbers: result?.phoneNumbers,
      licensePlates: result?.licensePlates,
    })
    console.log("  Redaction Suggestions:", result?.redactionSuggestions)

    return NextResponse.json(
      {
        success: true,
        message: "Report received",
      },
      { status: 200 },
    )
  } catch (error) {
    console.error("[SafePost] Error processing report:", error)
    return NextResponse.json(
      {
        success: false,
        message: "Error processing report",
      },
      { status: 500 },
    )
  }
}

