/**
 * AI Prompt Bar Page
 * 
 * This page provides the AI-powered natural language interface for creating dining alerts.
 * Users can type in natural language like "Princess dining Thursday at 7pm for 4 people"
 * and get intelligent suggestions for restaurants, times, and experiences.
 */

'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { 
  SparklesIcon, 
  ChatBubbleLeftRightIcon,
  LightBulbIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  MapPinIcon,
  UserGroupIcon,
  TagIcon,
  ArrowRightIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface ParsedResult {
  park: string
  date: string
  time_window: string[]
  party_size: number
  experience_tags: string[]
  alternates_ok: boolean
  suggestions: Array<{
    name: string
    park: string
    type: string
    match_score: number
    description?: string
  }>
  confidence: number
  needs_clarification: boolean
  clarification_questions: string[]
  smart_suggestions: Array<{
    title: string
    description: string
  }>
}

const SAMPLE_PROMPTS = [
  "Princess dining Thursday at 7pm for 4 people",
  "Be Our Guest next Friday evening",
  "Character dining at Magic Kingdom tomorrow",
  "Something romantic with fireworks view",
  "Family dinner next week",
  "I want to eat at the castle",
  "Romantic dinner for anniversary"
]

export default function AIPromptPage() {
  const { user, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const [input, setInput] = useState('')
  const [isParsing, setIsParsing] = useState(false)
  const [parsedResult, setParsedResult] = useState<ParsedResult | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/login')
    }
  }, [user, authLoading, router])

  const handleParse = async () => {
    if (!input.trim()) {
      toast.error('Please enter a dining request')
      return
    }

    setIsParsing(true)
    try {
      const response = await fetch('/api/nlu/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input }),
      })

      if (!response.ok) {
        throw new Error('Failed to parse request')
      }

      const result = await response.json()
      setParsedResult(result)
      setShowSuggestions(true)
      
      if (result.confidence > 0.7) {
        toast.success('Great! I understood your request perfectly!')
      } else if (result.needs_clarification) {
        toast('I need a bit more information to help you better', {
          icon: '🤔',
        })
      }
    } catch (error) {
      console.error('Parse error:', error)
      toast.error('Sorry, I had trouble understanding that. Try rephrasing your request.')
    } finally {
      setIsParsing(false)
    }
  }

  const handleCreateAlert = (suggestion: any) => {
    // Navigate to alert creation with pre-filled data
    const params = new URLSearchParams({
      restaurant: suggestion.name,
      park: suggestion.park,
      date: parsedResult?.date || '',
      time: parsedResult?.time_window[0] || '',
      party_size: parsedResult?.party_size.toString() || '2',
      experience_tags: parsedResult?.experience_tags.join(',') || '',
    })
    
    router.push(`/alerts/create?${params.toString()}`)
  }

  const handleClear = () => {
    setInput('')
    setParsedResult(null)
    setShowSuggestions(false)
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50 flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-accent-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-xl">
                <SparklesIcon className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Prompt Bar</h1>
                <p className="text-sm text-gray-600">Tell me what you're looking for in plain English</p>
              </div>
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="btn btn-ghost btn-sm"
            >
              <XMarkIcon className="w-4 h-4" />
              Close
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Main Input Section */}
        <div className="card card-glass mb-8">
          <div className="card-body">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-500 to-accent-500 rounded-2xl mb-4">
                <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                What kind of Disney dining experience are you looking for?
              </h2>
              <p className="text-gray-600">
                Just describe what you want in natural language - I'll figure out the details!
              </p>
            </div>

            {/* Input Form */}
            <div className="space-y-4">
              <div className="form-group">
                <label className="form-label">Your dining request</label>
                <div className="relative">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Try: 'Princess dining Thursday at 7pm for 4 people' or 'Something romantic with fireworks view'"
                    className="form-input w-full h-24 resize-none"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                        handleParse()
                      }
                    }}
                  />
                  <div className="absolute bottom-3 right-3 text-xs text-gray-400">
                    Press Cmd+Enter to parse
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleParse}
                  disabled={isParsing || !input.trim()}
                  className="btn btn-primary flex-1"
                >
                  {isParsing ? (
                    <>
                      <div className="loading-spinner w-4 h-4"></div>
                      Parsing...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-4 h-4" />
                      Parse My Request
                    </>
                  )}
                </button>
                
                {input && (
                  <button
                    onClick={handleClear}
                    className="btn btn-outline"
                  >
                    <XMarkIcon className="w-4 h-4" />
                    Clear
                  </button>
                )}
              </div>
            </div>

            {/* Sample Prompts */}
            <div className="mt-6">
              <p className="text-sm font-medium text-gray-700 mb-3">Try these examples:</p>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_PROMPTS.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(prompt)}
                    className="btn btn-soft btn-sm text-xs"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        {parsedResult && (
          <div className="space-y-6">
            {/* Parsed Details */}
            <div className="card">
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Parsed Details</h3>
                  <div className="flex items-center space-x-2">
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                      parsedResult.confidence > 0.7 
                        ? 'bg-green-100 text-green-800' 
                        : parsedResult.confidence > 0.4 
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {Math.round(parsedResult.confidence * 100)}% Confidence
                    </div>
                  </div>
                </div>
              </div>
              <div className="card-body">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="flex items-center space-x-3">
                    <MapPinIcon className="w-5 h-5 text-primary-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{parsedResult.park}</p>
                      <p className="text-xs text-gray-500">Park</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <ClockIcon className="w-5 h-5 text-primary-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{parsedResult.date}</p>
                      <p className="text-xs text-gray-500">Date</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <UserGroupIcon className="w-5 h-5 text-primary-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{parsedResult.party_size} people</p>
                      <p className="text-xs text-gray-500">Party Size</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <TagIcon className="w-5 h-5 text-primary-500" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {parsedResult.experience_tags.length} tags
                      </p>
                      <p className="text-xs text-gray-500">Experience</p>
                    </div>
                  </div>
                </div>

                {parsedResult.experience_tags.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Experience Tags:</p>
                    <div className="flex flex-wrap gap-2">
                      {parsedResult.experience_tags.map((tag, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                        >
                          {tag.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {parsedResult.time_window.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Time Window:</p>
                    <div className="flex items-center space-x-2">
                      <span className="px-3 py-1 bg-accent-100 text-accent-800 rounded-full text-sm">
                        {parsedResult.time_window[0]} - {parsedResult.time_window[1]}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Clarification Questions */}
            {parsedResult.needs_clarification && parsedResult.clarification_questions.length > 0 && (
              <div className="card card-gradient">
                <div className="card-body">
                  <div className="flex items-start space-x-3">
                    <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        I need a bit more information
                      </h3>
                      <ul className="space-y-2">
                        {parsedResult.clarification_questions.map((question, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <span className="text-yellow-600">•</span>
                            <span className="text-gray-700">{question}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Restaurant Suggestions */}
            {parsedResult.suggestions.length > 0 && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-lg font-semibold text-gray-900">Restaurant Suggestions</h3>
                  <p className="text-sm text-gray-600">
                    Based on your request, here are the best matches:
                  </p>
                </div>
                <div className="card-body">
                  <div className="space-y-4">
                    {parsedResult.suggestions.slice(0, 3).map((suggestion, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h4 className="font-semibold text-gray-900">{suggestion.name}</h4>
                            <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs">
                              {Math.round(suggestion.match_score * 100)}% match
                            </span>
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-gray-600">
                            <span className="flex items-center space-x-1">
                              <MapPinIcon className="w-4 h-4" />
                              {suggestion.park}
                            </span>
                            <span className="flex items-center space-x-1">
                              <TagIcon className="w-4 h-4" />
                              {suggestion.type}
                            </span>
                          </div>
                          {suggestion.description && (
                            <p className="text-sm text-gray-500 mt-1">{suggestion.description}</p>
                          )}
                        </div>
                        <button
                          onClick={() => handleCreateAlert(suggestion)}
                          className="btn btn-primary btn-sm ml-4"
                        >
                          <ArrowRightIcon className="w-4 h-4" />
                          Create Alert
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Smart Suggestions */}
            {parsedResult.smart_suggestions.length > 0 && (
              <div className="card card-glass">
                <div className="card-body">
                  <div className="flex items-start space-x-3">
                    <LightBulbIcon className="w-6 h-6 text-accent-500 flex-shrink-0 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">
                        Smart Suggestions
                      </h3>
                      <div className="space-y-2">
                        {parsedResult.smart_suggestions.map((suggestion, index) => (
                          <div key={index} className="p-3 bg-accent-50 rounded-lg">
                            <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
                            <p className="text-sm text-gray-600">{suggestion.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
