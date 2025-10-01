"""
Alert Monitoring Service

This service monitors user alerts and checks Disney dining availability.
It runs as a background worker to continuously check for available
reservations and send notifications when matches are found.

Features:
- Background monitoring of active alerts
- Batch processing for efficiency
- Notification sending (SMS, email, push)
- Alert status management
- Performance monitoring and logging
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from db import get_db
from models.alert import Alert
from models.user import User
from models.notification import Notification

# Define AvailabilitySlot type for web scraping results
class AvailabilitySlot:
    def __init__(self, date: str, time: str, party_size: int, restaurant: str):
        self.date = date
        self.time = time
        self.party_size = party_size
        self.restaurant = restaurant
# Disney API removed - using web scraping instead
from services.sms import SMSService
from services.email import EmailService
from services.push import PushService

logger = logging.getLogger(__name__)

class AlertMonitor:
    """
    Background service for monitoring Disney dining alerts.
    
    This service:
    - Fetches active alerts from the database
    - Checks Disney API for availability
    - Sends notifications when matches are found
    - Updates alert status and statistics
    """
    
    def __init__(self, db_session: Session, use_mock_api: bool = True):
        self.db = db_session
        self.use_mock_api = use_mock_api
        self.sms_service = SMSService()
        self.email_service = EmailService()
        self.push_service = PushService()
        self.is_running = False
        self.monitor_interval = 300  # 5 minutes
        self.batch_size = 50
        
    async def start_monitoring(self):
        """Start the background monitoring process"""
        self.is_running = True
        logger.info("Starting alert monitoring service")
        
        while self.is_running:
            try:
                await self._monitor_cycle()
                await asyncio.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_monitoring(self):
        """Stop the background monitoring process"""
        self.is_running = False
        logger.info("Stopping alert monitoring service")
    
    async def _monitor_cycle(self):
        """Single monitoring cycle"""
        logger.info("Starting monitoring cycle")
        
        # Get active alerts
        active_alerts = await self._get_active_alerts()
        if not active_alerts:
            logger.info("No active alerts to monitor")
            return
        
        logger.info(f"Monitoring {len(active_alerts)} active alerts")
        
        # Process alerts in batches
        for i in range(0, len(active_alerts), self.batch_size):
            batch = active_alerts[i:i + self.batch_size]
            await self._process_alert_batch(batch)
            
            # Small delay between batches to avoid overwhelming the API
            if i + self.batch_size < len(active_alerts):
                await asyncio.sleep(1)
        
        logger.info("Monitoring cycle completed")
    
    async def _get_active_alerts(self) -> List[Alert]:
        """Get all active alerts from the database"""
        try:
            alerts = self.db.query(Alert).filter(
                and_(
                    Alert.status == 'active',
                    Alert.date >= datetime.now().date()
                )
            ).all()
            
            logger.info(f"Retrieved {len(alerts)} active alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def _process_alert_batch(self, alerts: List[Alert]):
        """Process a batch of alerts"""
        try:
            # Convert alerts to API format
            alert_data = []
            for alert in alerts:
                alert_data.append({
                    'id': alert.id,
                    'restaurant_id': alert.restaurant,  # Assuming restaurant name maps to ID
                    'date': alert.date.isoformat(),
                    'time': alert.time.isoformat(),
                    'party_size': alert.party_size,
                    'user_id': alert.user_id
                })
            
            # Check availability using Disney API
            async with self._get_disney_api() as disney_api:
                results = await disney_api.batch_check_alerts(alert_data)
            
            # Process results and send notifications
            for alert in alerts:
                available_slots = results.get(alert.id, [])
                if available_slots:
                    await self._handle_availability_found(alert, available_slots)
                else:
                    await self._update_alert_stats(alert, False)
            
        except Exception as e:
            logger.error(f"Failed to process alert batch: {e}")
    
    async def _get_disney_api(self):
        """Get Disney API service instance"""
        if self.use_mock_api:
            return MockDisneyAPIService()
        else:
            return DisneyAPIService()
    
    async def _handle_availability_found(self, alert: Alert, available_slots: List[AvailabilitySlot]):
        """Handle when availability is found for an alert"""
        try:
            logger.info(f"Found availability for alert {alert.id}: {len(available_slots)} slots")
            
            # Get user information
            user = self.db.query(User).filter(User.id == alert.user_id).first()
            if not user:
                logger.error(f"User not found for alert {alert.id}")
                return
            
            # Send notifications
            await self._send_notifications(user, alert, available_slots)
            
            # Update alert statistics
            await self._update_alert_stats(alert, True)
            
            # Create notification record
            await self._create_notification_record(alert, user, available_slots)
            
        except Exception as e:
            logger.error(f"Failed to handle availability for alert {alert.id}: {e}")
    
    async def _send_notifications(self, user: User, alert: Alert, available_slots: List[AvailabilitySlot]):
        """Send notifications to user about available slots"""
        try:
            # Prepare notification message
            message = self._prepare_notification_message(alert, available_slots)
            
            # Send SMS if enabled
            if alert.notifications_sms and user.phone:
                await self.sms_service.send_alert_notification(
                    phone=user.phone,
                    message=message
                )
                logger.info(f"Sent SMS notification to {user.phone}")
            
            # Send email if enabled
            if alert.notifications_email and user.email:
                await self.email_service.send_alert_notification(
                    email=user.email,
                    subject=f"Disney Dining Alert: {alert.restaurant}",
                    message=message
                )
                logger.info(f"Sent email notification to {user.email}")
            
            # Send push notification if enabled
            if alert.notifications_push:
                await self.push_service.send_alert_notification(
                    user_id=user.id,
                    title="Disney Dining Alert",
                    message=message
                )
                logger.info(f"Sent push notification to user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to send notifications for alert {alert.id}: {e}")
    
    def _prepare_notification_message(self, alert: Alert, available_slots: List[AvailabilitySlot]) -> str:
        """Prepare notification message for available slots"""
        restaurant_name = alert.restaurant
        date_str = alert.date.strftime('%B %d, %Y')
        
        if len(available_slots) == 1:
            slot = available_slots[0]
            time_str = slot.time.strftime('%I:%M %p')
            message = f"🎉 Great news! {restaurant_name} has availability on {date_str} at {time_str} for {alert.party_size} people!"
        else:
            times = [slot.time.strftime('%I:%M %p') for slot in available_slots]
            times_str = ', '.join(times)
            message = f"🎉 Great news! {restaurant_name} has availability on {date_str} at {times_str} for {alert.party_size} people!"
        
        message += f"\n\nBook now at: https://disneyworld.disney.go.com/dining/"
        return message
    
    async def _update_alert_stats(self, alert: Alert, found_availability: bool):
        """Update alert statistics"""
        try:
            if found_availability:
                # Increment notification count
                alert.notifications_sent = (alert.notifications_sent or 0) + 1
                alert.last_notification_sent = datetime.utcnow()
            
            # Update last checked time
            alert.last_checked = datetime.utcnow()
            
            # Check if alert should be expired
            if alert.date < datetime.now().date():
                alert.status = 'expired'
                logger.info(f"Alert {alert.id} expired")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update alert stats for {alert.id}: {e}")
            self.db.rollback()
    
    async def _create_notification_record(self, alert: Alert, user: User, available_slots: List[AvailabilitySlot]):
        """Create notification record in database"""
        try:
            notification = Notification(
                user_id=user.id,
                alert_id=alert.id,
                type='availability_found',
                title=f'Disney Dining Alert: {alert.restaurant}',
                message=self._prepare_notification_message(alert, available_slots),
                sent_at=datetime.utcnow(),
                status='sent'
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.info(f"Created notification record for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to create notification record: {e}")
            self.db.rollback()

# Background worker functions
async def start_alert_monitor(db_session: Session, use_mock_api: bool = True):
    """Start the alert monitoring service"""
    monitor = AlertMonitor(db_session, use_mock_api)
    await monitor.start_monitoring()

async def check_single_alert(alert_id: str, db_session: Session, use_mock_api: bool = True):
    """Check a single alert for availability"""
    try:
        # Get alert from database
        alert = db_session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            logger.error(f"Alert {alert_id} not found")
            return
        
        # Check availability
        async with MockDisneyAPIService() if use_mock_api else DisneyAPIService() as disney_api:
            available_slots = await disney_api.monitor_alert({
                'id': alert.id,
                'restaurant_id': alert.restaurant,
                'date': alert.date.isoformat(),
                'time': alert.time.isoformat(),
                'party_size': alert.party_size
            })
        
        if available_slots:
            logger.info(f"Found {len(available_slots)} available slots for alert {alert_id}")
            # Handle availability found
            monitor = AlertMonitor(db_session, use_mock_api)
            await monitor._handle_availability_found(alert, available_slots)
        else:
            logger.info(f"No availability found for alert {alert_id}")
            
    except Exception as e:
        logger.error(f"Failed to check alert {alert_id}: {e}")

# Utility functions
async def expire_old_alerts(db_session: Session):
    """Expire alerts that are past their date"""
    try:
        expired_count = db_session.query(Alert).filter(
            and_(
                Alert.status == 'active',
                Alert.date < datetime.now().date()
            )
        ).update({'status': 'expired'})
        
        db_session.commit()
        logger.info(f"Expired {expired_count} old alerts")
        
    except Exception as e:
        logger.error(f"Failed to expire old alerts: {e}")
        db_session.rollback()

async def get_monitoring_stats(db_session: Session) -> Dict:
    """Get monitoring statistics"""
    try:
        total_alerts = db_session.query(Alert).count()
        active_alerts = db_session.query(Alert).filter(Alert.status == 'active').count()
        expired_alerts = db_session.query(Alert).filter(Alert.status == 'expired').count()
        
        # Get recent notifications
        recent_notifications = db_session.query(Notification).filter(
            Notification.sent_at >= datetime.now() - timedelta(hours=24)
        ).count()
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'expired_alerts': expired_alerts,
            'notifications_sent_24h': recent_notifications,
            'monitoring_status': 'active'
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring stats: {e}")
        return {}
