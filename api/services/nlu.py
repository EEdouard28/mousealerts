"""
MouseAlerts API - Natural Language Understanding Service

This service handles the AI Prompt Bar functionality that converts natural
language descriptions into structured alert specifications. Users can describe
what they want in plain English and get back structured data.

NLU Pipeline:
1. Date/Time Parsing: Extract dates and times using Chrono/Duckling
2. Park Detection: Identify Disney parks (Magic Kingdom, EPCOT, etc.)
3. Venue Matching: Find restaurants using fuzzy matching
4. Tag Extraction: Identify experience tags (princess, fireworks_view, etc.)
5. Structured Output: Generate JSON for alert creation

Example Input: "Princess dining Thursday at 7 pm in Magic Kingdom"
Example Output: {
  "park": "Magic Kingdom",
  "date": "2024-01-18",
  "time_window": ["19:00", "20:00"],
  "party_size": 2,
  "experience_tags": ["princess", "character_dining"],
  "alternates_ok": true
}
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dateutil import parser as date_parser
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Park patterns for matching
PARK_PATTERNS = {
    "Magic Kingdom": ["magic kingdom", "mk", "magic kingdom park"],
    "EPCOT": ["epcot", "epcot center"],
    "Hollywood Studios": ["hollywood studios", "dhs", "disney's hollywood studios"],
    "Animal Kingdom": ["animal kingdom", "dak", "disney's animal kingdom"]
}

# Experience tags
EXPERIENCE_TAGS = {
    "princess": ["princess", "princess dining", "princess character"],
    "character_dining": ["character", "character dining", "meet characters"],
    "fireworks_view": ["fireworks", "fireworks view", "fireworks viewing"],
    "table_service": ["table service", "sit down", "full service"],
    "buffet": ["buffet", "all you can eat"],
    "fine_dining": ["fine dining", "upscale", "premium"],
    "quick_service": ["quick service", "counter service", "fast food"],
    "outdoor_seating": ["outdoor", "patio", "outside"],
    "waterfront": ["waterfront", "water view", "lake view"]
}

# Venue database (simplified for MVP)
VENUE_DATABASE = {
    "Magic Kingdom": [
        {"name": "Cinderella's Royal Table", "tags": ["princess", "character_dining", "fine_dining"]},
        {"name": "Be Our Guest Restaurant", "tags": ["themed_dining", "table_service"]},
        {"name": "Jungle Navigation Co. Ltd. Skipper Canteen", "tags": ["themed_dining", "table_service"]},
    ],
    "EPCOT": [
        {"name": "Akershus Royal Banquet Hall", "tags": ["princess", "character_dining", "buffet"]},
        {"name": "Rose & Crown Pub & Dining Room", "tags": ["fireworks_view", "table_service", "waterfront"]},
        {"name": "La Hacienda de San Angel", "tags": ["fireworks_view", "table_service", "waterfront"]},
    ]
}

async def parse_natural_language(text: str, db: Session) -> Dict[str, Any]:
    """Parse natural language text into structured alert data"""
    try:
        # Normalize text
        text_lower = text.lower().strip()
        
        # Extract date/time
        date_info = extract_date_time(text_lower)
        
        # Extract park
        park = extract_park(text_lower)
        
        # Extract party size
        party_size = extract_party_size(text_lower)
        
        # Extract experience tags
        tags = extract_experience_tags(text_lower)
        
        # Find venue suggestions
        suggestions = find_venue_suggestions(park, tags, text_lower)
        
        # Generate upsell options
        upsell_options = generate_upsell_options(date_info, tags)
        
        return {
            "park": park,
            "date": date_info["date"],
            "time_window": date_info["time_window"],
            "party_size": party_size,
            "experience_tags": tags,
            "alternates_ok": True,
            "suggestions": suggestions,
            "upsell_options": upsell_options
        }
        
    except Exception as e:
        logger.error(f"Failed to parse natural language: {e}")
        raise

def extract_date_time(text: str) -> Dict[str, Any]:
    """Extract date and time information from text"""
    # Simple date/time extraction (would use Chrono/Duckling in production)
    today = datetime.now()
    
    # Look for time patterns
    time_patterns = [
        r'(\d{1,2}):?(\d{2})?\s*(am|pm)',
        r'(\d{1,2})\s*(am|pm)',
        r'(\d{1,2}):(\d{2})'
    ]
    
    time_match = None
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            time_match = match
            break
    
    # Default to 7 PM if no time specified
    hour = 19
    minute = 0
    
    if time_match:
        hour = int(time_match.group(1))
        if time_match.group(2) and 'pm' in time_match.group(2).lower():
            if hour < 12:
                hour += 12
        elif 'am' in time_match.group(2).lower() and hour == 12:
            hour = 0
    
    # Look for day patterns
    if 'thursday' in text or 'thu' in text:
        days_ahead = (3 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
    elif 'friday' in text or 'fri' in text:
        days_ahead = (4 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
    elif 'saturday' in text or 'sat' in text:
        days_ahead = (5 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
    elif 'sunday' in text or 'sun' in text:
        days_ahead = (6 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        target_date = today + timedelta(days=days_ahead)
    else:
        # Default to tomorrow
        target_date = today + timedelta(days=1)
    
    # Create time window (±30 minutes)
    time_start = f"{hour:02d}:{minute:02d}"
    time_end_hour = hour + 1 if minute < 30 else hour + 1
    time_end_minute = (minute + 30) % 60
    time_end = f"{time_end_hour:02d}:{time_end_minute:02d}"
    
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "time_window": [time_start, time_end]
    }

def extract_park(text: str) -> str:
    """Extract Disney park from text"""
    for park, patterns in PARK_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                return park
    
    # Default to Magic Kingdom
    return "Magic Kingdom"

def extract_party_size(text: str) -> int:
    """Extract party size from text"""
    # Look for number patterns
    number_patterns = [
        r'(\d+)\s*(people|guests|party)',
        r'party\s*of\s*(\d+)',
        r'for\s*(\d+)',
        r'(\d+)\s*adults?'
    ]
    
    for pattern in number_patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    
    # Default to 2 people
    return 2

def extract_experience_tags(text: str) -> List[str]:
    """Extract experience tags from text"""
    tags = []
    
    for tag, patterns in EXPERIENCE_TAGS.items():
        for pattern in patterns:
            if pattern in text:
                tags.append(tag)
                break
    
    return tags

def find_venue_suggestions(park: str, tags: List[str], text: str) -> List[Dict[str, Any]]:
    """Find venue suggestions based on park and tags"""
    if park not in VENUE_DATABASE:
        return []
    
    venues = VENUE_DATABASE[park]
    suggestions = []
    
    for venue in venues:
        # Check if venue matches tags
        venue_tags = set(venue["tags"])
        query_tags = set(tags)
        
        if query_tags.intersection(venue_tags):
            suggestions.append({
                "name": venue["name"],
                "tags": venue["tags"],
                "match_score": len(query_tags.intersection(venue_tags)) / len(query_tags)
            })
    
    # Sort by match score
    suggestions.sort(key=lambda x: x["match_score"], reverse=True)
    return suggestions[:3]  # Return top 3 suggestions

def generate_upsell_options(date_info: Dict[str, Any], tags: List[str]) -> List[Dict[str, Any]]:
    """Generate upsell options for enhanced features"""
    upsells = []
    
    # Add backup day option
    upsells.append({
        "id": "backup_day",
        "title": "Add Backup Day",
        "description": "Get notified for the same time the next day if today is full",
        "price": 0
    })
    
    # Add time window expansion
    upsells.append({
        "id": "expand_window",
        "title": "Expand Time Window",
        "description": "Get notified for ±30 minutes around your preferred time",
        "price": 0
    })
    
    # Add cross-park alternates
    if "princess" in tags:
        upsells.append({
            "id": "cross_park_princess",
            "title": "Cross-Park Princess Dining",
            "description": "Also check EPCOT for princess dining options",
            "price": 0
        })
    
    return upsells

async def get_venue_suggestions(park: str, tags: List[str], db: Session) -> List[Dict[str, Any]]:
    """Get venue suggestions based on park and tags"""
    return find_venue_suggestions(park, tags, "")
