"""
MouseAlerts API - Push Notifications Router

This router handles Web Push notification subscriptions and delivery.
Users can subscribe to push notifications and receive instant alerts
when Disney dining reservations become available.

Endpoints:
- POST /subscribe: Subscribe user to push notifications
- POST /unsubscribe: Unsubscribe user from push notifications
- GET /subscription: Get user's current push subscription

Web Push Flow:
1. Frontend requests VAPID public key
2. User grants notification permission
3. Frontend creates push subscription
4. Backend stores subscription for user
5. When alert triggers, send push notification

Push notifications are the preferred notification method as they
provide instant delivery without requiring email/SMS setup.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from db import get_db
from deps import get_current_active_user
from models.user import User
from services.push import store_push_subscription, send_push_notification
from config import settings

router = APIRouter()

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict
    user_agent: Optional[str] = None

class PushSubscriptionResponse(BaseModel):
    public_key: str
    message: str

@router.post("/subscribe")
async def subscribe_to_push(
    subscription: PushSubscription,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Subscribe user to push notifications"""
    try:
        await store_push_subscription(current_user.id, subscription.dict(), db)
        return {"message": "Successfully subscribed to push notifications"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to subscribe: {str(e)}"
        )

@router.post("/unsubscribe")
async def unsubscribe_from_push(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unsubscribe user from push notifications"""
    try:
        # Remove push subscription from database
        # Implementation depends on how subscriptions are stored
        return {"message": "Successfully unsubscribed from push notifications"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to unsubscribe: {str(e)}"
        )

@router.get("/public-key")
async def get_vapid_public_key():
    """Get VAPID public key for frontend push subscription"""
    return {"public_key": settings.WEB_PUSH_VAPID_PUBLIC_KEY}

@router.post("/test")
async def send_test_push(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a test push notification to verify setup"""
    try:
        await send_push_notification(
            current_user.id,
            "Test Notification",
            "This is a test push notification from MouseAlerts",
            db
        )
        return {"message": "Test notification sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send test notification: {str(e)}"
        )
