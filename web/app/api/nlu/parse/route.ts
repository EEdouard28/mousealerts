/**
 * Mock NLU Parse API Route
 * 
 * This is a mock API endpoint for the NLU parsing service.
 * It simulates the backend NLU service for frontend testing.
 */

import { NextRequest, NextResponse } from 'next/server'

// Mock restaurant data
const MOCK_RESTAURANTS = [
  {
    name: "Cinderella's Royal Table",
    park: "Magic Kingdom",
    type: "Table Service",
    description: "Princess character dining in the castle"
  },
  {
    name: "Be Our Guest Restaurant",
    park: "Magic Kingdom", 
    type: "Table Service",
    description: "Beauty and the Beast themed dining"
  },
  {
    name: "La Hacienda de San Angel",
    park: "EPCOT",
    type: "Table Service", 
    description: "Mexican cuisine with fireworks view"
  },
  {
    name: "Rose & Crown Pub & Dining Room",
    park: "EPCOT",
    type: "Table Service",
    description: "British pub with waterfront dining"
  },
  {
    name: "Akershus Royal Banquet Hall",
    park: "EPCOT",
    type: "Table Service",
    description: "Princess character dining in Norway"
  },
  {
    name: "Jungle Navigation Co. Ltd. Skipper Canteen",
    park: "Magic Kingdom",
    type: "Table Service",
    description: "Adventure-themed dining with Skipper"
  }
]

// Mock parsing logic
function mockParseNLU(text: string) {
  const lowerText = text.toLowerCase()
  
  // Extract park
  let park = "Magic Kingdom"
  if (lowerText.includes("epcot")) park = "EPCOT"
  if (lowerText.includes("animal kingdom")) park = "Animal Kingdom"
  if (lowerText.includes("hollywood studios")) park = "Hollywood Studios"
  
  // Extract date
  const today = new Date()
  let date = today.toISOString().split('T')[0]
  
  if (lowerText.includes("tomorrow")) {
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    date = tomorrow.toISOString().split('T')[0]
  } else if (lowerText.includes("next week")) {
    const nextWeek = new Date(today)
    nextWeek.setDate(nextWeek.getDate() + 7)
    date = nextWeek.toISOString().split('T')[0]
  } else if (lowerText.includes("thursday")) {
    const thursday = new Date(today)
    const daysUntilThursday = (4 - today.getDay() + 7) % 7
    thursday.setDate(thursday.getDate() + (daysUntilThursday || 7))
    date = thursday.toISOString().split('T')[0]
  } else if (lowerText.includes("friday")) {
    const friday = new Date(today)
    const daysUntilFriday = (5 - today.getDay() + 7) % 7
    friday.setDate(friday.getDate() + (daysUntilFriday || 7))
    date = friday.toISOString().split('T')[0]
  }
  
  // Extract time
  let timeWindow = ["19:00", "20:00"]
  if (lowerText.includes("7pm") || lowerText.includes("7 pm")) {
    timeWindow = ["19:00", "20:00"]
  } else if (lowerText.includes("evening")) {
    timeWindow = ["18:00", "20:00"]
  } else if (lowerText.includes("lunch")) {
    timeWindow = ["12:00", "14:00"]
  }
  
  // Extract party size
  let partySize = 2
  const partyMatch = lowerText.match(/(\d+)\s*people?/)
  if (partyMatch) {
    partySize = parseInt(partyMatch[1])
  }
  
  // Extract experience tags
  const experienceTags = []
  if (lowerText.includes("princess")) experienceTags.push("princess", "character_dining")
  if (lowerText.includes("character")) experienceTags.push("character_dining")
  if (lowerText.includes("romantic")) experienceTags.push("fine_dining", "table_service")
  if (lowerText.includes("family")) experienceTags.push("table_service", "character_dining")
  if (lowerText.includes("fireworks")) experienceTags.push("fireworks_view", "waterfront")
  if (lowerText.includes("castle")) experienceTags.push("princess", "character_dining")
  
  // Calculate confidence
  let confidence = 0.8
  if (lowerText.includes("something") || lowerText.includes("vague")) confidence = 0.4
  if (lowerText.includes("dinner") && !lowerText.includes("time")) confidence = 0.6
  
  // Generate suggestions
  const suggestions = MOCK_RESTAURANTS
    .filter(r => r.park === park)
    .map(restaurant => ({
      ...restaurant,
      match_score: Math.random() * 0.4 + 0.4 // 40-80% match
    }))
    .sort((a, b) => b.match_score - a.match_score)
    .slice(0, 3)
  
  // Generate clarification questions
  const clarificationQuestions = []
  if (partySize === 2 && !lowerText.includes("people")) {
    clarificationQuestions.push("How many people will be dining?")
  }
  if (confidence < 0.6) {
    clarificationQuestions.push("Do you have a specific restaurant in mind?")
  }
  
  // Generate smart suggestions
  const smartSuggestions = []
  if (lowerText.includes("princess")) {
    smartSuggestions.push({
      title: "Princess Dining Options",
      description: "Both Magic Kingdom and EPCOT offer princess character dining experiences"
    })
  }
  if (lowerText.includes("romantic")) {
    smartSuggestions.push({
      title: "Romantic Dining",
      description: "Consider restaurants with fireworks views or intimate atmospheres"
    })
  }
  
  return {
    park,
    date,
    time_window: timeWindow,
    party_size: partySize,
    experience_tags: experienceTags,
    alternates_ok: true,
    suggestions,
    confidence,
    needs_clarification: confidence < 0.6,
    clarification_questions: clarificationQuestions,
    smart_suggestions: smartSuggestions
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { text } = body
    
    if (!text) {
      return NextResponse.json(
        { error: 'Text is required' },
        { status: 400 }
      )
    }
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const result = mockParseNLU(text)
    
    return NextResponse.json(result)
  } catch (error) {
    console.error('NLU Parse error:', error)
    return NextResponse.json(
      { error: 'Failed to parse request' },
      { status: 500 }
    )
  }
}
