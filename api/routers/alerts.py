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

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime, date
import uuid
import logging

from db import get_db
from deps import get_current_active_user
from models.user import User
from models.alert import Alert
from schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from services.plan_enforcement import PlanEnforcement

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    status_filter: Optional[str] = Query(None, description="Filter by status: active, expired, cancelled"),
    park_filter: Optional[str] = Query(None, description="Filter by park"),
    restaurant_filter: Optional[str] = Query(None, description="Filter by restaurant name"),
    limit: int = Query(50, ge=1, le=100, description="Number of alerts to return"),
    offset: int = Query(0, ge=0, description="Number of alerts to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all alerts for the current user with optional filtering and pagination.
    
    Args:
        status_filter: Filter by alert status
        park_filter: Filter by park name
        restaurant_filter: Filter by restaurant name
        limit: Maximum number of alerts to return
        offset: Number of alerts to skip
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of user alerts with filtering applied
    """
    try:
        # Base query for user's alerts
        query = db.query(Alert).filter(Alert.user_id == current_user.id)
        
        # Apply filters
        if status_filter:
            query = query.filter(Alert.status == status_filter)
        
        if park_filter:
            query = query.filter(Alert.park.ilike(f"%{park_filter}%"))
        
        if restaurant_filter:
            query = query.filter(Alert.restaurant.ilike(f"%{restaurant_filter}%"))
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Alert.created_at))
        
        # Apply pagination
        alerts = query.offset(offset).limit(limit).all()
        
        logger.info(f"Retrieved {len(alerts)} alerts for user {current_user.id}")
        
        return alerts
        
    except Exception as e:
        logger.error(f"Failed to retrieve alerts for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new dining alert for the current user.
    
    Args:
        alert_data: Alert creation data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Created alert with all details
        
    Raises:
        HTTPException: If alert creation fails
    """
    try:
        # Check plan limits before creating alert
        plan_enforcement = PlanEnforcement(db)
        can_create, error_message, upgrade_suggestion = plan_enforcement.enforce_alert_creation(current_user.id)
        
        if not can_create:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": error_message,
                    "upgrade_suggestion": upgrade_suggestion
                }
            )
        
        # Check notification channel permissions
        allowed_channels = plan_enforcement.get_notification_channels(current_user.id)
        
        # Create new alert with plan-aware notifications
        alert = Alert(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            restaurant=alert_data.restaurant,
            park=alert_data.park,
            date=alert_data.date,
            time=alert_data.time,
            party_size=alert_data.party_size,
            notifications_sms=alert_data.notifications.get('sms', True) and 'sms' in allowed_channels,
            notifications_email=alert_data.notifications.get('email', True) and 'email' in allowed_channels,
            notifications_push=alert_data.notifications.get('push', True) and 'push' in allowed_channels,
            notes=alert_data.notes,
            status='active'
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Created alert {alert.id} for user {current_user.id}")
        
        return alert
        
    except Exception as e:
        logger.error(f"Failed to create alert for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert"
        )

@router.get("/plan-info")
async def get_plan_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's current plan information and usage limits.
    
    Returns:
        Plan details, usage statistics, and upgrade suggestions
    """
    try:
        plan_enforcement = PlanEnforcement(db)
        
        # Get plan information
        plan_info = plan_enforcement.get_user_plan(current_user.id)
        
        # Get usage statistics
        usage = plan_enforcement.get_alert_usage(current_user.id)
        
        # Get upgrade suggestions
        suggestions = plan_enforcement.get_upgrade_suggestions(current_user.id)
        
        # Get feature access
        features = {
            "ai_prompt_bar": plan_enforcement.can_use_feature(current_user.id, "ai_prompt_bar"),
            "sms_notifications": plan_enforcement.can_use_feature(current_user.id, "sms_notifications"),
            "instant_notifications": plan_enforcement.can_use_feature(current_user.id, "instant_notifications"),
            "priority_support": plan_enforcement.can_use_feature(current_user.id, "priority_support")
        }
        
        return {
            "plan": plan_info,
            "usage": usage,
            "features": features,
            "upgrade_suggestions": suggestions,
            "monitoring_interval": plan_enforcement.get_monitoring_interval(current_user.id)
        }
        
    except Exception as e:
        logger.error(f"Failed to get plan info for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan information"
        )

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
    """
    Update an existing alert.
    
    Args:
        alert_id: ID of the alert to update
        alert_data: Updated alert data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Updated alert details
        
    Raises:
        HTTPException: If alert not found or not owned by user
    """
    try:
        # Get existing alert
        alert = db.query(Alert).filter(
            and_(Alert.id == alert_id, Alert.user_id == current_user.id)
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Update fields
        update_data = alert_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(alert, field):
                setattr(alert, field, value)
        
        alert.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Updated alert {alert_id} for user {current_user.id}")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update alert {alert_id} for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert"
        )

@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an alert.
    
    Args:
        alert_id: ID of the alert to delete
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: If alert not found or not owned by user
    """
    try:
        # Get existing alert
        alert = db.query(Alert).filter(
            and_(Alert.id == alert_id, Alert.user_id == current_user.id)
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Delete alert
        db.delete(alert)
        db.commit()
        
        logger.info(f"Deleted alert {alert_id} for user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete alert {alert_id} for user {current_user.id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert"
        )

@router.get("/stats")
async def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get alert statistics for the current user.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Dictionary with alert statistics
    """
    try:
        # Get total alerts
        total_alerts = db.query(Alert).filter(Alert.user_id == current_user.id).count()
        
        # Get active alerts
        active_alerts = db.query(Alert).filter(
            and_(Alert.user_id == current_user.id, Alert.status == 'active')
        ).count()
        
        # Get expired alerts
        expired_alerts = db.query(Alert).filter(
            and_(Alert.user_id == current_user.id, Alert.status == 'expired')
        ).count()
        
        # Get alerts by park
        park_stats = db.query(Alert.park, func.count(Alert.id)).filter(
            Alert.user_id == current_user.id
        ).group_by(Alert.park).all()
        
        stats = {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "expired_alerts": expired_alerts,
            "park_breakdown": {park: count for park, count in park_stats}
        }
        
        logger.info(f"Retrieved stats for user {current_user.id}: {stats}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to retrieve stats for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert statistics"
        )
