/**
 * AI Prompt Bar Component
 * 
 * A reusable component that provides natural language input for creating dining alerts.
 * Can be used as a modal, inline component, or embedded in other pages.
 */

'use client'

import { useState } from 'react'
import { 
  SparklesIcon, 
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
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

interface AIPromptBarProps {
  onResult?: (result: ParsedResult) => void
  onSuggestionSelect?: (suggestion: any) => void
  placeholder?: string
  className?: string
  showSuggestions?: boolean
  compact?: boolean
}

const SAMPLE_PROMPTS = [
  "Princess dining Thursday at 7pm",
  "Be Our Guest next Friday evening",
  "Character dining at Magic Kingdom",
  "Something romantic with fireworks view",
  "Family dinner next week"
]

export default function AIPromptBar({ 
  onResult, 
  onSuggestionSelect,
  placeholder = "Describe your ideal Disney dining experience...",
  className = "",
  showSuggestions = true,
  compact = false
}: AIPromptBarProps) {
  const [input, setInput] = useState('')
  const [isParsing, setIsParsing] = useState(false)
  const [parsedResult, setParsedResult] = useState<ParsedResult | null>(null)

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
      
      if (onResult) {
        onResult(result)
      }
      
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

  const handleSuggestionSelect = (suggestion: any) => {
    if (onSuggestionSelect) {
      onSuggestionSelect(suggestion)
    }
  }

  const handleClear = () => {
    setInput('')
    setParsedResult(null)
  }

  if (compact) {
    return (
      <div className={`space-y-3 ${className}`}>
        <div className="flex space-x-2">
          <div className="flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={placeholder}
              className="form-input w-full"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleParse()
                }
              }}
            />
          </div>
          <button
            onClick={handleParse}
            disabled={isParsing || !input.trim()}
            className="btn btn-primary"
          >
            {isParsing ? (
              <div className="loading-spinner w-4 h-4"></div>
            ) : (
              <SparklesIcon className="w-4 h-4" />
            )}
          </button>
          {input && (
            <button
              onClick={handleClear}
              className="btn btn-ghost"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          )}
        </div>

        {parsedResult && showSuggestions && (
          <div className="space-y-2">
            <div className="text-sm text-gray-600">
              <strong>{parsedResult.park}</strong> • {parsedResult.date} • {parsedResult.party_size} people
              {parsedResult.experience_tags.length > 0 && (
                <span className="ml-2">
                  • {parsedResult.experience_tags.slice(0, 2).join(', ')}
                </span>
              )}
            </div>
            {parsedResult.suggestions.length > 0 && (
              <div className="space-y-1">
                {parsedResult.suggestions.slice(0, 2).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionSelect(suggestion)}
                    className="w-full text-left p-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm"
                  >
                    <div className="font-medium">{suggestion.name}</div>
                    <div className="text-gray-500">{suggestion.park} • {Math.round(suggestion.match_score * 100)}% match</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Input Section */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-primary-100 rounded-lg">
              <ChatBubbleLeftRightIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">AI Prompt Bar</h3>
              <p className="text-sm text-gray-600">Describe your dining request in natural language</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="form-group">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={placeholder}
                className="form-input w-full h-20 resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    handleParse()
                  }
                }}
              />
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
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
                    Parse Request
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

            {/* Sample Prompts */}
            <div>
              <p className="text-xs font-medium text-gray-700 mb-2">Try these examples:</p>
              <div className="flex flex-wrap gap-1">
                {SAMPLE_PROMPTS.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(prompt)}
                    className="btn btn-soft btn-xs"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {parsedResult && showSuggestions && (
        <div className="space-y-4">
          {/* Parsed Details */}
          <div className="card">
            <div className="card-body">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">Parsed Details</h4>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  parsedResult.confidence > 0.7 
                    ? 'bg-green-100 text-green-800' 
                    : parsedResult.confidence > 0.4 
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {Math.round(parsedResult.confidence * 100)}% Confidence
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div>
                  <p className="text-gray-500">Park</p>
                  <p className="font-medium">{parsedResult.park}</p>
                </div>
                <div>
                  <p className="text-gray-500">Date</p>
                  <p className="font-medium">{parsedResult.date}</p>
                </div>
                <div>
                  <p className="text-gray-500">Party Size</p>
                  <p className="font-medium">{parsedResult.party_size} people</p>
                </div>
                <div>
                  <p className="text-gray-500">Experience</p>
                  <p className="font-medium">{parsedResult.experience_tags.length} tags</p>
                </div>
              </div>

              {parsedResult.experience_tags.length > 0 && (
                <div className="mt-3">
                  <div className="flex flex-wrap gap-1">
                    {parsedResult.experience_tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs"
                      >
                        {tag.replace('_', ' ')}
                      </span>
                    ))}
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
                  <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-1" />
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Need More Info</h4>
                    <ul className="space-y-1 text-sm">
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
              <div className="card-body">
                <h4 className="font-semibold text-gray-900 mb-3">Restaurant Suggestions</h4>
                <div className="space-y-2">
                  {parsedResult.suggestions.slice(0, 3).map((suggestion, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h5 className="font-medium text-gray-900">{suggestion.name}</h5>
                          <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs">
                            {Math.round(suggestion.match_score * 100)}% match
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {suggestion.park} • {suggestion.type}
                        </div>
                      </div>
                      <button
                        onClick={() => handleSuggestionSelect(suggestion)}
                        className="btn btn-primary btn-sm ml-3"
                      >
                        <ArrowRightIcon className="w-4 h-4" />
                        Select
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
                <h4 className="font-semibold text-gray-900 mb-3">Smart Suggestions</h4>
                <div className="space-y-2">
                  {parsedResult.smart_suggestions.map((suggestion, index) => (
                    <div key={index} className="p-2 bg-accent-50 rounded-lg">
                      <h5 className="font-medium text-gray-900 text-sm">{suggestion.title}</h5>
                      <p className="text-xs text-gray-600">{suggestion.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
