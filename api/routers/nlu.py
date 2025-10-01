"""
MouseAlerts API - Natural Language Understanding Router

This router handles the AI Prompt Bar functionality that converts natural language
into structured alert specifications. Users can describe what they want in plain
English and get back structured data for creating alerts.

Endpoints:
- POST /parse: Parse natural language text into alert specifications
- GET /suggestions: Get venue suggestions based on criteria
- GET /tags: Get available experience tags (princess, fireworks_view, etc.)

The NLU pipeline:
1. Parse dates/times using Chrono/Duckling
2. Extract park and venue information
3. Identify experience tags (princess, fireworks_view, etc.)
4. Generate structured JSON for alert creation
5. Provide venue suggestions and upsell options

This enables the "AI Prompt Bar" feature where users can type things like:
"Princess dining Thursday at 7 pm in Magic Kingdom"
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from db import get_db
from deps import get_current_active_user
from models.user import User
from services.nlu import parse_natural_language, get_venue_suggestions

router = APIRouter()

class ParseRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class ParseResponse(BaseModel):
    park: str
    date: str
    time_window: List[str]
    party_size: int
    experience_tags: List[str]
    alternates_ok: bool
    suggestions: List[Dict[str, Any]]
    upsell_options: List[Dict[str, Any]]
    confidence: float
    needs_clarification: bool
    clarification_questions: List[str]

@router.post("/parse", response_model=ParseResponse)
async def parse_nl_text(
    request: ParseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Parse natural language text into alert specifications"""
    try:
        result = await parse_natural_language(request.text, db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse text: {str(e)}"
        )

@router.get("/suggestions")
async def get_venue_suggestions_endpoint(
    park: str,
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get venue suggestions based on park and tags"""
    tag_list = tags.split(",") if tags else []
    suggestions = await get_venue_suggestions(park, tag_list, db)
    return {"suggestions": suggestions}

@router.get("/tags")
async def get_available_tags():
    """Get all available experience tags"""
    return {
        "tags": [
            "princess",
            "character_dining", 
            "fireworks_view",
            "table_service",
            "buffet",
            "fine_dining",
            "quick_service",
            "outdoor_seating",
            "indoor_seating",
            "waterfront",
            "themed_dining"
        ]
    }

@router.get("/test")
async def test_nlu_endpoint():
    """Test endpoint to verify NLU service is working"""
    return {
        "status": "ok",
        "message": "NLU service is running",
        "examples": [
            "Princess dining Thursday at 7pm for 4 people",
            "Be Our Guest next Friday evening", 
            "Character dining at Magic Kingdom tomorrow",
            "Dinner at EPCOT on Saturday",
            "Something romantic with fireworks view"
        ]
    }
