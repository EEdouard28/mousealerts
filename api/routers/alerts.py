"""
MouseAlerts API - Alerts Router

This router handles all alert-related operations for Disney dining reservations.
Users can create, read, update, and delete their reservation alerts.

Endpoints:
- GET /alerts: List user's alerts
- POST /alerts: Create new alert
- GET /alerts/{id}: Get specific alert
- PATCH /alerts/{id}: Update alert
- DELETE /alerts/{id}: Delete alert

Alerts specify what users are looking for:
- Park (Magic Kingdom, EPCOT, etc.)
- Venue (restaurant name)
- Date and time window
- Party size
- Notification preferences

All endpoints require authentication via JWT token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from db import get_db
from deps import get_current_active_user
from models.user import User
from models.alert import Alert
from schemas.alert import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all alerts for the current user"""
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).all()
    return alerts

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new alert"""
    alert = Alert(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **alert_data.dict()
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert

@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    update_data = alert_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    return alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}
