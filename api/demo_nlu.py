#!/usr/bin/env python3
"""
Demo script showing the MouseAlerts AI Prompt Bar in action.
This demonstrates the traditional NLP parser we just built.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the API directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.nlu import parse_natural_language

# Mock database session
class MockDB:
    pass

async def demo_ai_prompt_bar():
    """Demonstrate the AI Prompt Bar functionality"""
    
    print("🎭 MouseAlerts AI Prompt Bar Demo")
    print("=" * 50)
    print("Converting natural language to structured alerts...")
    print()
    
    # Test cases that show different capabilities including smart templates
    test_cases = [
        {
            "input": "Princess dining Thursday at 7pm for 4 people",
            "description": "Perfect input with all details"
        },
        {
            "input": "Be Our Guest next Friday evening",
            "description": "Restaurant name + relative date"
        },
        {
            "input": "Character dining at Magic Kingdom tomorrow",
            "description": "Experience type + park + relative date"
        },
        {
            "input": "Something romantic with fireworks view",
            "description": "Smart template matching for romantic + fireworks"
        },
        {
            "input": "Family dinner next week",
            "description": "Family template matching with smart suggestions"
        },
        {
            "input": "I want to eat at the castle",
            "description": "Vague castle reference - smart suggestions"
        },
        {
            "input": "Romantic dinner for anniversary",
            "description": "Romantic template with anniversary context"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['description']}")
        print(f"Input: '{test_case['input']}'")
        print("-" * 40)
        
        try:
            result = await parse_natural_language(test_case['input'], MockDB())
            
            # Display results
            print(f"🏰 Park: {result['park']}")
            print(f"📅 Date: {result['date']}")
            print(f"🕐 Time: {result['time_window'][0]} - {result['time_window'][1]}")
            print(f"👥 Party Size: {result['party_size']}")
            print(f"🏷️  Experience Tags: {', '.join(result['experience_tags']) if result['experience_tags'] else 'None'}")
            print(f"🎯 Confidence: {result['confidence']:.1%}")
            
            if result['suggestions']:
                print(f"🍽️  Restaurant Suggestions:")
                for suggestion in result['suggestions'][:3]:
                    print(f"   • {suggestion['name']} (match: {suggestion['match_score']:.1%})")
            
            if result['needs_clarification']:
                print(f"❓ Needs Clarification:")
                for question in result['clarification_questions']:
                    print(f"   • {question}")
                
                if result.get('smart_suggestions'):
                    print(f"💡 Smart Suggestions:")
                    for suggestion in result['smart_suggestions'][:3]:
                        print(f"   • {suggestion['title']}: {suggestion['description']}")
            else:
                print("✅ Ready to create alert!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    print("=" * 50)
    print("🎉 AI Prompt Bar Demo Complete!")
    print()
    print("💡 Key Features Demonstrated:")
    print("   • Date/time parsing with dateutil")
    print("   • Restaurant matching with fuzzywuzzy")
    print("   • Party size extraction with regex")
    print("   • Experience tag detection")
    print("   • Smart template matching (princess, romantic, family, etc.)")
    print("   • Enhanced restaurant suggestions with descriptions")
    print("   • Confidence scoring and clarification questions")
    print("   • Smart suggestions for vague inputs")
    print("   • Multi-factor scoring (tags + name + text + templates)")
    print()
    print("🚀 This enables users to type natural language")
    print("   and get structured alerts ready for creation!")

if __name__ == "__main__":
    asyncio.run(demo_ai_prompt_bar())
