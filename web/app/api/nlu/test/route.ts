/**
 * Mock NLU Test API Route
 * 
 * This is a mock API endpoint for testing the NLU service.
 */

import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: "ok",
    message: "NLU service is running (mock mode)",
    examples: [
      "Princess dining Thursday at 7pm for 4 people",
      "Be Our Guest next Friday evening", 
      "Character dining at Magic Kingdom tomorrow",
      "Dinner at EPCOT on Saturday",
      "Something romantic with fireworks view"
    ]
  })
}
