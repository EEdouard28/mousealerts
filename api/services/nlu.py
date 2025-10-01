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
from typing import Dict, List, Any, Optional, Tuple
from dateutil import parser as date_parser
from fuzzywuzzy import fuzz, process
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
    "character": ["character", "character dining", "meet characters", "character breakfast"],
    "romantic": ["romantic", "romantic dinner", "date", "anniversary"],
    "family": ["family", "family meal", "family dinner", "kids", "children"],
    "fireworks_view": ["fireworks", "fireworks view", "fireworks viewing"],
    "table_service": ["table service", "sit down", "full service"],
    "buffet": ["buffet", "all you can eat"],
    "fine_dining": ["fine dining", "upscale", "premium"],
    "quick_service": ["quick service", "counter service", "fast food"],
    "outdoor_seating": ["outdoor", "patio", "outside"],
    "waterfront": ["waterfront", "water view", "lake view"]
}

# Smart Templates for common patterns
SMART_TEMPLATES = {
    "princess_dining": {
        "patterns": ["princess", "princess dining", "princess character", "royal", "castle"],
        "suggestions": ["Cinderella's Royal Table", "Akershus Royal Banquet Hall"],
        "tags": ["princess", "character_dining"],
        "parks": ["Magic Kingdom", "EPCOT"]
    },
    "fireworks_dining": {
        "patterns": ["fireworks", "fireworks view", "fireworks viewing", "evening", "night"],
        "suggestions": ["Rose & Crown Pub", "La Hacienda de San Angel", "Spice Road Table"],
        "tags": ["fireworks_view", "waterfront"],
        "parks": ["EPCOT"]
    },
    "character_dining": {
        "patterns": ["character", "character dining", "meet characters", "characters"],
        "suggestions": ["Cinderella's Royal Table", "Be Our Guest", "Akershus Royal Banquet Hall"],
        "tags": ["character_dining"],
        "parks": ["Magic Kingdom", "EPCOT"]
    },
    "romantic_dining": {
        "patterns": ["romantic", "date", "anniversary", "special", "intimate"],
        "suggestions": ["Be Our Guest", "Cinderella's Royal Table", "Rose & Crown Pub"],
        "tags": ["fine_dining", "table_service"],
        "parks": ["Magic Kingdom", "EPCOT"]
    },
    "family_dining": {
        "patterns": ["family", "kids", "children", "family dinner"],
        "suggestions": ["Be Our Guest", "Jungle Navigation Co.", "Akershus Royal Banquet Hall"],
        "tags": ["table_service", "character_dining"],
        "parks": ["Magic Kingdom", "EPCOT"]
    }
}

# Enhanced venue database with more details
VENUE_DATABASE = {
    "Magic Kingdom": [
        {
            "name": "Cinderella's Royal Table", 
            "tags": ["princess", "character_dining", "fine_dining", "romantic"],
            "description": "Dine inside Cinderella Castle with princess characters",
            "price_range": "$$$$",
            "cuisine": "American",
            "special_features": ["Princess meet & greet", "Castle views", "Character dining"]
        },
        {
            "name": "Be Our Guest Restaurant", 
            "tags": ["themed_dining", "table_service", "romantic", "family"],
            "description": "Beauty and the Beast themed dining in Beast's Castle",
            "price_range": "$$$",
            "cuisine": "French",
            "special_features": ["Themed dining", "Beast's Castle", "Be Our Guest song"]
        },
        {
            "name": "Jungle Navigation Co. Ltd. Skipper Canteen", 
            "tags": ["themed_dining", "table_service", "family", "adventure"],
            "description": "Jungle Cruise themed restaurant with skipper humor",
            "price_range": "$$",
            "cuisine": "Asian Fusion",
            "special_features": ["Jungle Cruise theme", "Skipper humor", "Adventure dining"]
        }
    ],
    "EPCOT": [
        {
            "name": "Akershus Royal Banquet Hall", 
            "tags": ["princess", "character_dining", "buffet", "family"],
            "description": "Norwegian castle with princess character dining",
            "price_range": "$$$",
            "cuisine": "Norwegian",
            "special_features": ["Princess meet & greet", "Buffet style", "Norwegian culture"]
        },
        {
            "name": "Rose & Crown Pub & Dining Room", 
            "tags": ["fireworks_view", "table_service", "waterfront", "romantic"],
            "description": "British pub with fireworks viewing and waterfront dining",
            "price_range": "$$",
            "cuisine": "British",
            "special_features": ["Fireworks viewing", "Waterfront", "British pub atmosphere"]
        },
        {
            "name": "La Hacienda de San Angel", 
            "tags": ["fireworks_view", "table_service", "waterfront", "romantic"],
            "description": "Mexican restaurant with fireworks viewing",
            "price_range": "$$",
            "cuisine": "Mexican",
            "special_features": ["Fireworks viewing", "Waterfront", "Mexican cuisine"]
        }
    ]
}

async def parse_natural_language(text: str, db: Session) -> Dict[str, Any]:
    """Parse natural language text into structured alert data with confidence scoring"""
    try:
        # Normalize text
        text_lower = text.lower().strip()
        
        # Extract components with confidence scores
        date_info = extract_date_time(text_lower)
        park = extract_park(text_lower)
        party_size = extract_party_size(text_lower)
        tags = extract_experience_tags(text_lower)
        
        # Apply smart templates for enhanced matching
        template_result = apply_smart_templates(text_lower, tags, park)
        if template_result:
            tags.extend(template_result.get('additional_tags', []))
            if not park or park == "Magic Kingdom":  # Only override if park wasn't specified
                park = template_result.get('suggested_park', park)
        
        # Find venue suggestions with enhanced matching
        suggestions = find_venue_suggestions_enhanced(park, tags, text_lower, template_result)
        
        # Calculate overall confidence
        confidence = calculate_confidence(date_info, park, party_size, tags, suggestions)
        
        # Generate upsell options
        upsell_options = generate_upsell_options(date_info, tags)
        
        # Determine if we need clarification
        needs_clarification = confidence < 0.7
        clarification_questions = []
        smart_suggestions = []
        
        if needs_clarification:
            clarification_questions = generate_clarification_questions(
                date_info, park, party_size, tags, suggestions
            )
            # Generate smart suggestions for unclear inputs
            smart_suggestions = generate_smart_suggestions(text_lower, tags, park)
        
        return {
            "park": park,
            "date": date_info["date"],
            "time_window": date_info["time_window"],
            "party_size": party_size,
            "experience_tags": tags,
            "alternates_ok": True,
            "suggestions": suggestions,
            "upsell_options": upsell_options,
            "confidence": confidence,
            "needs_clarification": needs_clarification,
            "clarification_questions": clarification_questions,
            "smart_suggestions": smart_suggestions
        }
        
    except Exception as e:
        logger.error(f"Failed to parse natural language: {e}")
        raise

def calculate_confidence(date_info: Dict, park: str, party_size: int, tags: List[str], suggestions: List[Dict]) -> float:
    """Calculate overall confidence score for the parsing result"""
    scores = []
    
    # Date/time confidence
    if date_info and date_info.get('date') and date_info.get('time'):
        scores.append(0.95)  # High confidence if both date and time found
    elif date_info and (date_info.get('date') or date_info.get('time')):
        scores.append(0.6)  # Medium confidence if only one found
    else:
        scores.append(0.05)  # Low confidence if neither found
    
    # Park confidence (high if found, medium if defaulted)
    if park and park != "Magic Kingdom":
        park_confidence = 0.95
    elif park == "Magic Kingdom":
        park_confidence = 0.8
    else:
        park_confidence = 0.1  # Very low for unknown parks
    scores.append(park_confidence)
    
    # Party size confidence
    if party_size and party_size != 2:
        party_confidence = 0.95
    elif party_size == 2:
        party_confidence = 0.8
    else:
        party_confidence = 0.1  # Very low for no party size
    scores.append(party_confidence)
    
    # Tags confidence
    tag_confidence = min(len(tags) * 0.8, 1.0) if tags else 0.05
    scores.append(tag_confidence)
    
    # Suggestions confidence
    suggestion_confidence = min(len(suggestions) * 0.6, 0.9) if suggestions else 0.05
    scores.append(suggestion_confidence)
    
    # Return weighted average
    return sum(scores) / len(scores)

def generate_clarification_questions(date_info: Dict, park: str, party_size: int, tags: List[str], suggestions: List[Dict]) -> List[str]:
    """Generate clarification questions for low-confidence parsing"""
    questions = []
    
    # Check if we need to clarify date/time
    if not date_info or not date_info.get('date') or not date_info.get('time'):
        questions.append("What date and time would you like to dine?")
    
    # Check if we need to clarify park
    if not park or park == "Magic Kingdom":
        questions.append("Which Disney park would you like to visit?")
    
    # Check if we need to clarify party size
    if not party_size or party_size == 2:
        questions.append("How many people will be dining?")
    
    # Check if we need to clarify restaurant
    if not suggestions or not any(s.get('match_score', 0) > 0.3 for s in suggestions):
        questions.append("Do you have a specific restaurant in mind?")
    
    return questions[:3]  # Limit to 3 questions

def apply_smart_templates(text: str, existing_tags: List[str], current_park: str) -> Optional[Dict[str, Any]]:
    """Apply smart templates to enhance parsing results"""
    text_lower = text.lower()
    
    # Find matching templates
    matching_templates = []
    for template_name, template_data in SMART_TEMPLATES.items():
        for pattern in template_data["patterns"]:
            if pattern in text_lower:
                matching_templates.append((template_name, template_data))
                break
    
    if not matching_templates:
        return None
    
    # Get the best matching template
    best_template = matching_templates[0]  # Could be enhanced with scoring
    template_name, template_data = best_template
    
    # Extract additional tags not already present
    additional_tags = []
    for tag in template_data["tags"]:
        if tag not in existing_tags:
            additional_tags.append(tag)
    
    # Suggest park if not specified or defaulted
    suggested_park = None
    if current_park == "Magic Kingdom" and template_data["parks"]:
        suggested_park = template_data["parks"][0]  # Use first park from template
    
    # Map template names to expected test values
    template_mapping = {
        "princess_dining": "princess",
        "fireworks_dining": "fireworks",
        "character_dining": "character",
        "romantic_dining": "romantic",
        "family_dining": "family"
    }
    
    return {
        "template": template_mapping.get(template_name, template_name),
        "template_name": template_name,
        "additional_tags": additional_tags,
        "suggested_park": suggested_park,
        "template_suggestions": template_data["suggestions"],
        "confidence_boost": 0.2  # Boost confidence when template matches
    }

def find_venue_suggestions_enhanced(park: str, tags: List[str], text: str, template_result: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Enhanced venue suggestions using smart templates and better scoring"""
    if park not in VENUE_DATABASE:
        return []
    
    venues = VENUE_DATABASE[park]
    suggestions = []
    
    # Extract restaurant names from text for fuzzy matching
    restaurant_names = extract_restaurant_names(text)
    
    for venue in venues:
        venue_tags = set(venue["tags"])
        query_tags = set(tags)
        
        # Calculate tag match score
        tag_score = len(query_tags.intersection(venue_tags)) / max(len(query_tags), 1)
        
        # Calculate name match score using fuzzy matching
        name_score = 0
        if restaurant_names:
            best_match = process.extractOne(venue["name"], restaurant_names, scorer=fuzz.partial_ratio)
            if best_match:
                name_score = best_match[1] / 100.0
        
        # Calculate text similarity score
        text_score = 0
        if text:
            text_score = fuzz.partial_ratio(text.lower(), venue["name"].lower()) / 100.0
        
        # Template boost score
        template_boost = 0
        if template_result and venue["name"] in template_result.get("template_suggestions", []):
            template_boost = 0.3
        
        # Special features matching
        features_score = 0
        if venue.get("special_features"):
            for feature in venue["special_features"]:
                if any(word in text.lower() for word in feature.lower().split()):
                    features_score += 0.1
        
        # Combined score (weighted)
        combined_score = (
            tag_score * 0.4 + 
            name_score * 0.25 + 
            text_score * 0.15 + 
            template_boost * 0.15 + 
            features_score * 0.05
        )
        
        if combined_score > 0.05:  # Lower threshold for more suggestions
            suggestions.append({
                "name": venue["name"],
                "description": venue.get("description", ""),
                "tags": venue["tags"],
                "price_range": venue.get("price_range", ""),
                "cuisine": venue.get("cuisine", ""),
                "special_features": venue.get("special_features", []),
                "match_score": combined_score,
                "tag_score": tag_score,
                "name_score": name_score,
                "text_score": text_score,
                "template_boost": template_boost,
                "features_score": features_score
            })
    
    # Sort by combined score
    suggestions.sort(key=lambda x: x["match_score"], reverse=True)
    return suggestions[:5]  # Return top 5 suggestions

def generate_smart_suggestions(text: str, tags: List[str], park: str) -> List[str]:
    """Generate smart suggestions for unclear or vague inputs"""
    suggestions = []
    
    # If no tags detected, suggest popular experiences
    if not tags:
        suggestions.extend([
            "Try princess character dining at Cinderella's Royal Table",
            "Consider fireworks view dining at Rose & Crown Pub",
            "Explore themed dining at Be Our Guest Restaurant"
        ])
    
    # If park not specified, suggest parks based on tags
    if park == "Magic Kingdom" and tags:
        if "fireworks_view" in tags:
            suggestions.append("EPCOT has the best fireworks viewing restaurants")
        elif "princess" in tags:
            suggestions.append("Princess dining available at both Magic Kingdom and EPCOT")
    
    # Suggest time improvements
    suggestions.extend([
        "Evening dining offers better atmosphere and entertainment",
        "Lunch reservations are typically easier to get than dinner"
    ])
    
    return suggestions[:5]  # Limit to 5 suggestions

def extract_date_time(text: str) -> Dict[str, Any]:
    """Extract date and time information using dateutil and regex patterns"""
    today = datetime.now()
    
    # Try dateutil first (handles most cases)
    try:
        parsed = date_parser.parse(text, fuzzy=True, default=today)
        if parsed.date() != today.date():  # Only use if it found a different date
            target_date = parsed.date()
            target_time = parsed.time()
        else:
            target_date = None
            target_time = None
    except:
        target_date = None
        target_time = None
    
    # Fallback to manual parsing if dateutil didn't work
    if not target_date:
        target_date = extract_date_manual(text, today)
    
    if not target_time:
        target_time = extract_time_manual(text)
    
    # Create time window (±30 minutes)
    if isinstance(target_time, int):
        # If target_time is an integer (hour), convert to time object
        hour = target_time
        minute = 0
    else:
        hour = target_time.hour
        minute = target_time.minute
    
    time_start = f"{hour:02d}:{minute:02d}"
    time_end_hour = hour + 1 if minute < 30 else hour + 1
    time_end_minute = (minute + 30) % 60
    time_end = f"{time_end_hour:02d}:{time_end_minute:02d}"
    
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "time": target_time,
        "time_window": [time_start, time_end],
        "confidence": 0.9 if target_date and target_time else 0.6
    }

def extract_date_manual(text: str, today: datetime) -> datetime:
    """Manual date extraction for cases dateutil misses"""
    text_lower = text.lower()
    
    # Day of week patterns
    day_patterns = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    for day_name, day_num in day_patterns.items():
        if day_name in text_lower:
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7  # Next week
            return today + timedelta(days=days_ahead)
    
    # Relative patterns
    if 'tomorrow' in text_lower:
        return today + timedelta(days=1)
    elif 'next week' in text_lower:
        return today + timedelta(days=7)
    elif 'this weekend' in text_lower:
        # Find next Saturday
        days_ahead = (5 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)
    
    # Default to tomorrow
    return today + timedelta(days=1)

def extract_time_manual(text: str) -> int:
    """Manual time extraction for cases dateutil misses"""
    text_lower = text.lower()
    
    # Time patterns
    time_patterns = [
        r'(\d{1,2}):?(\d{2})?\s*(am|pm)',
        r'(\d{1,2})\s*(am|pm)',
        r'(\d{1,2}):(\d{2})',
        r'(\d{1,2})'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text_lower)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
            
            # Handle AM/PM
            if len(match.groups()) > 2 and match.group(3):
                if 'pm' in match.group(3) and hour < 12:
                    hour += 12
                elif 'am' in match.group(3) and hour == 12:
                    hour = 0
            
            # Default to PM if no AM/PM specified and hour < 12
            elif hour < 12:
                hour += 12
            
            return hour
    
    # Time of day patterns
    if 'morning' in text_lower:
        return 9
    elif 'lunch' in text_lower or 'noon' in text_lower:
        return 12
    elif 'afternoon' in text_lower:
        return 14
    elif 'evening' in text_lower:
        return 18
    elif 'dinner' in text_lower:
        return 19
    elif 'late' in text_lower:
        return 20
    
    # Default to 7 PM
    return 19

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
        r'(\d+)\s*adults?',
        r'table\s*for\s*(\d+)',
        r'family\s*of\s*(\d+)',
        r'(\d+)\s*people'
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
    """Find venue suggestions using fuzzy matching and tag scoring"""
    if park not in VENUE_DATABASE:
        return []
    
    venues = VENUE_DATABASE[park]
    suggestions = []
    
    # Extract restaurant names from text for fuzzy matching
    restaurant_names = extract_restaurant_names(text)
    
    for venue in venues:
        venue_tags = set(venue["tags"])
        query_tags = set(tags)
        
        # Calculate tag match score
        tag_score = len(query_tags.intersection(venue_tags)) / max(len(query_tags), 1)
        
        # Calculate name match score using fuzzy matching
        name_score = 0
        if restaurant_names:
            best_match = process.extractOne(venue["name"], restaurant_names, scorer=fuzz.partial_ratio)
            if best_match:
                name_score = best_match[1] / 100.0
        
        # Calculate text similarity score
        text_score = 0
        if text:
            text_score = fuzz.partial_ratio(text.lower(), venue["name"].lower()) / 100.0
        
        # Combined score (weighted)
        combined_score = (tag_score * 0.5) + (name_score * 0.3) + (text_score * 0.2)
        
        if combined_score > 0.1:  # Only include if there's some relevance
            suggestions.append({
                "name": venue["name"],
                "tags": venue["tags"],
                "match_score": combined_score,
                "tag_score": tag_score,
                "name_score": name_score,
                "text_score": text_score
            })
    
    # Sort by combined score
    suggestions.sort(key=lambda x: x["match_score"], reverse=True)
    return suggestions[:5]  # Return top 5 suggestions

def extract_restaurant_names(text: str) -> List[str]:
    """Extract potential restaurant names from text"""
    # Common restaurant name patterns
    restaurant_patterns = [
        r'at\s+([A-Z][a-zA-Z\s&\']+)',
        r'([A-Z][a-zA-Z\s&\']+)\s+restaurant',
        r'([A-Z][a-zA-Z\s&\']+)\s+dining',
        r'([A-Z][a-zA-Z\s&\']+)\s+table'
    ]
    
    names = []
    for pattern in restaurant_patterns:
        matches = re.findall(pattern, text)
        names.extend(matches)
    
    # Also look for quoted names
    quoted_names = re.findall(r'"([^"]+)"', text)
    names.extend(quoted_names)
    
    return [name.strip() for name in names if len(name.strip()) > 2]

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
