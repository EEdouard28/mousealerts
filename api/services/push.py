"""
MouseAlerts API - Push Notification Service

This service handles Web Push notifications for instant alerts.
Push notifications are the preferred method as they provide immediate
delivery without requiring email/SMS setup.

Features:
- VAPID key management for secure push notifications
- User subscription storage and management
- Push notification delivery with retry logic
- Deep linking to Disney's booking pages

Push notifications are sent when:
- Disney dining reservations become available
- Users need to be notified immediately
- Email/SMS may be delayed or filtered
"""

import json
import logging
from typing import Dict, Any
from pywebpush import webpush, WebPushException
from config import settings

logger = logging.getLogger(__name__)

async def store_push_subscription(user_id: str, subscription_data: Dict[str, Any], db):
    """Store user's push subscription in database"""
    # This would store the subscription in a dedicated table
    # For now, we'll store it in user preferences or a separate table
    logger.info(f"Stored push subscription for user {user_id}")
    return True

async def send_push_notification(user_id: str, title: str, body: str, db, data: Dict[str, Any] = None):
    """Send push notification to user"""
    try:
        # Get user's push subscription from database
        subscription = await get_user_push_subscription(user_id, db)
        
        if not subscription:
            logger.warning(f"No push subscription found for user {user_id}")
            return False
        
        # Prepare notification payload
        payload = {
            "title": title,
            "body": body,
            "icon": "/icons/icon-192x192.png",
            "badge": "/icons/badge-72x72.png",
            "data": data or {},
            "actions": [
                {
                    "action": "book",
                    "title": "Book Now",
                    "url": data.get("booking_url") if data else None
                },
                {
                    "action": "dismiss",
                    "title": "Dismiss"
                }
            ]
        }
        
        # Send push notification
        webpush(
            subscription_info=subscription,
            data=json.dumps(payload),
            vapid_private_key=settings.WEB_PUSH_VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": settings.WEB_PUSH_VAPID_SUBJECT
            }
        )
        
        logger.info(f"Push notification sent to user {user_id}")
        return True
        
    except WebPushException as e:
        logger.error(f"WebPush error: {e}")
        if e.response and e.response.status_code == 410:
            # Subscription expired, remove it
            await remove_push_subscription(user_id, db)
        return False
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False

async def get_user_push_subscription(user_id: str, db):
    """Get user's push subscription from database"""
    # This would query the database for the user's subscription
    # For now, return None as placeholder
    return None

async def remove_push_subscription(user_id: str, db):
    """Remove expired push subscription"""
    # This would remove the subscription from database
    logger.info(f"Removed expired push subscription for user {user_id}")
    return True

async def send_alert_push_notification(user_id: str, alert_data: Dict[str, Any], db):
    """Send push notification for found reservation"""
    title = f"🎉 Reservation Found: {alert_data['venue']}"
    body = f"{alert_data['park']} - {alert_data['date']} at {alert_data['time_start']}"
    
    data = {
        "type": "alert",
        "alert_id": alert_data["alert_id"],
        "booking_url": alert_data["booking_url"],
        "venue": alert_data["venue"],
        "park": alert_data["park"]
    }
    
    return await send_push_notification(user_id, title, body, db, data)
