"""
Disney Scraping Monitor Service

This service combines web scraping with alert monitoring to provide
real-time Disney dining availability alerts, similar to MouseWatcher.

Features:
- Web scraping integration with Selenium
- Real-time availability monitoring
- Smart notification system
- Rate limiting and compliance
- Error handling and retry logic
- Performance monitoring
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
from services.disney_scraper import DisneyWebScraper, ScrapingResult, ScrapingStatus
from services.sms import SMSService
from services.email import EmailService
from services.push import PushService

logger = logging.getLogger(__name__)

class ScrapingAlertMonitor:
    """
    Enhanced alert monitoring service with web scraping.
    
    This service:
    - Uses web scraping to check Disney's reservation system
    - Monitors user alerts for availability
    - Sends real-time notifications
    - Manages scraping rate limits and compliance
    """
    
    def __init__(self, db_session: Session, headless: bool = True):
        self.db = db_session
        self.headless = headless
        self.sms_service = SMSService()
        self.email_service = EmailService()
        self.push_service = PushService()
        self.is_running = False
        self.monitor_interval = 300  # 5 minutes
        self.batch_size = 10  # Smaller batches for scraping
        self.scraper_pool_size = 3  # Number of concurrent scrapers
        self.rate_limit_delay = 2.0  # Delay between requests
        
    async def start_monitoring(self):
        """Start the scraping-based monitoring process"""
        self.is_running = True
        logger.info("Starting scraping-based alert monitoring")
        
        while self.is_running:
            try:
                await self._monitor_cycle()
                await asyncio.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_monitoring(self):
        """Stop the monitoring process"""
        self.is_running = False
        logger.info("Stopping scraping-based alert monitoring")
    
    async def _monitor_cycle(self):
        """Single monitoring cycle with web scraping"""
        logger.info("Starting scraping monitoring cycle")
        
        # Get active alerts
        active_alerts = await self._get_active_alerts()
        if not active_alerts:
            logger.info("No active alerts to monitor")
            return
        
        logger.info(f"Monitoring {len(active_alerts)} active alerts with web scraping")
        
        # Process alerts in batches with scraping
        for i in range(0, len(active_alerts), self.batch_size):
            batch = active_alerts[i:i + self.batch_size]
            await self._process_alert_batch_with_scraping(batch)
            
            # Rate limiting delay between batches
            if i + self.batch_size < len(active_alerts):
                await asyncio.sleep(self.rate_limit_delay * 2)
        
        logger.info("Scraping monitoring cycle completed")
    
    async def _get_active_alerts(self) -> List[Alert]:
        """Get all active alerts from the database"""
        try:
            alerts = self.db.query(Alert).filter(
                and_(
                    Alert.status == 'active',
                    Alert.date >= datetime.now().date()
                )
            ).all()
            
            logger.info(f"Retrieved {len(alerts)} active alerts for scraping")
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    async def _process_alert_batch_with_scraping(self, alerts: List[Alert]):
        """Process a batch of alerts using web scraping"""
        try:
            # Create scraper instances for concurrent processing
            scrapers = []
            for _ in range(min(self.scraper_pool_size, len(alerts))):
                scraper = DisneyWebScraper(headless=self.headless)
                scrapers.append(scraper)
            
            # Process alerts concurrently
            tasks = []
            for i, alert in enumerate(alerts):
                scraper = scrapers[i % len(scrapers)]
                task = self._scrape_alert_availability(alert, scraper)
                tasks.append(task)
            
            # Wait for all scraping tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for alert, result in zip(alerts, results):
                if isinstance(result, Exception):
                    logger.error(f"Scraping failed for alert {alert.id}: {result}")
                    await self._update_alert_stats(alert, False, error=str(result))
                else:
                    await self._handle_scraping_result(alert, result)
            
            # Cleanup scrapers
            for scraper in scrapers:
                try:
                    await scraper._cleanup_driver()
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Failed to process alert batch with scraping: {e}")
    
    async def _scrape_alert_availability(self, alert: Alert, scraper: DisneyWebScraper) -> ScrapingResult:
        """Scrape availability for a specific alert"""
        try:
            # Convert alert to scraping format
            alert_data = {
                'id': alert.id,
                'restaurant_id': alert.restaurant,  # Assuming restaurant name maps to ID
                'date': alert.date.isoformat(),
                'time': alert.time.isoformat(),
                'party_size': alert.party_size,
                'user_id': alert.user_id
            }
            
            # Scrape availability
            result = await scraper.monitor_alert(alert_data)
            
            logger.info(f"Scraping completed for alert {alert.id}: {result.status}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to scrape alert {alert.id}: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                available_slots=[],
                error_message=str(e)
            )
    
    async def _handle_scraping_result(self, alert: Alert, result: ScrapingResult):
        """Handle the result of a scraping operation"""
        try:
            if result.status == ScrapingStatus.SUCCESS and result.available_slots:
                # Availability found - send notifications
                await self._handle_availability_found(alert, result.available_slots)
                await self._update_alert_stats(alert, True)
            elif result.status == ScrapingStatus.NO_AVAILABILITY:
                # No availability found
                await self._update_alert_stats(alert, False)
            elif result.status == ScrapingStatus.RATE_LIMITED:
                # Rate limited - increase delay
                logger.warning(f"Rate limited for alert {alert.id}")
                await self._update_alert_stats(alert, False, error="Rate limited")
            elif result.status == ScrapingStatus.BLOCKED:
                # Blocked - need to change approach
                logger.error(f"Blocked for alert {alert.id}")
                await self._update_alert_stats(alert, False, error="Blocked")
            else:
                # Failed scraping
                logger.error(f"Scraping failed for alert {alert.id}: {result.error_message}")
                await self._update_alert_stats(alert, False, error=result.error_message)
            
        except Exception as e:
            logger.error(f"Failed to handle scraping result for alert {alert.id}: {e}")
    
    async def _handle_availability_found(self, alert: Alert, available_slots: List[Dict]):
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
            
            # Create notification record
            await self._create_notification_record(alert, user, available_slots)
            
        except Exception as e:
            logger.error(f"Failed to handle availability for alert {alert.id}: {e}")
    
    async def _send_notifications(self, user: User, alert: Alert, available_slots: List[Dict]):
        """Send notifications to user about available slots"""
        try:
            # Prepare notification message
            message = self._prepare_scraping_notification_message(alert, available_slots)
            
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
                    subject=f"🎉 Disney Dining Alert: {alert.restaurant}",
                    message=message
                )
                logger.info(f"Sent email notification to {user.email}")
            
            # Send push notification if enabled
            if alert.notifications_push:
                await self.push_service.send_alert_notification(
                    user_id=user.id,
                    title="🎉 Disney Dining Alert!",
                    message=message
                )
                logger.info(f"Sent push notification to user {user.id}")
            
        except Exception as e:
            logger.error(f"Failed to send notifications for alert {alert.id}: {e}")
    
    def _prepare_scraping_notification_message(self, alert: Alert, available_slots: List[Dict]) -> str:
        """Prepare notification message for available slots from scraping"""
        restaurant_name = alert.restaurant
        date_str = alert.date.strftime('%B %d, %Y')
        
        if len(available_slots) == 1:
            slot = available_slots[0]
            time_str = slot.get('time', 'Unknown time')
            message = f"🎉 Great news! {restaurant_name} has availability on {date_str} at {time_str} for {alert.party_size} people!"
        else:
            times = [slot.get('time', 'Unknown') for slot in available_slots]
            times_str = ', '.join(times)
            message = f"🎉 Great news! {restaurant_name} has availability on {date_str} at {times_str} for {alert.party_size} people!"
        
        message += f"\n\n⚡ Book now at: https://disneyworld.disney.go.com/dining-reservations/"
        message += f"\n\n🔔 This alert was found by MouseAlerts web scraping!"
        return message
    
    async def _update_alert_stats(self, alert: Alert, found_availability: bool, error: str = None):
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
    
    async def _create_notification_record(self, alert: Alert, user: User, available_slots: List[Dict]):
        """Create notification record in database"""
        try:
            notification = Notification(
                user_id=user.id,
                alert_id=alert.id,
                type='availability_found_scraping',
                title=f'🎉 Disney Dining Alert: {alert.restaurant}',
                message=self._prepare_scraping_notification_message(alert, available_slots),
                sent_at=datetime.utcnow(),
                status='sent'
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.info(f"Created scraping notification record for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Failed to create notification record: {e}")
            self.db.rollback()

# Background worker functions
async def start_scraping_monitor(db_session: Session, headless: bool = True):
    """Start the scraping-based monitoring service"""
    monitor = ScrapingAlertMonitor(db_session, headless)
    await monitor.start_monitoring()

async def check_single_alert_with_scraping(alert_id: str, db_session: Session, headless: bool = True):
    """Check a single alert using web scraping"""
    try:
        # Get alert from database
        alert = db_session.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            logger.error(f"Alert {alert_id} not found")
            return
        
        # Scrape availability
        async with DisneyWebScraper(headless=headless) as scraper:
            alert_data = {
                'id': alert.id,
                'restaurant_id': alert.restaurant,
                'date': alert.date.isoformat(),
                'time': alert.time.isoformat(),
                'party_size': alert.party_size
            }
            
            result = await scraper.monitor_alert(alert_data)
            
            if result.status == ScrapingStatus.SUCCESS and result.available_slots:
                logger.info(f"Found {len(result.available_slots)} available slots for alert {alert_id}")
                # Handle availability found
                monitor = ScrapingAlertMonitor(db_session, headless)
                await monitor._handle_availability_found(alert, result.available_slots)
            else:
                logger.info(f"No availability found for alert {alert_id}")
                
    except Exception as e:
        logger.error(f"Failed to check alert {alert_id} with scraping: {e}")

# Utility functions
async def get_scraping_stats(db_session: Session) -> Dict:
    """Get scraping monitoring statistics"""
    try:
        total_alerts = db_session.query(Alert).count()
        active_alerts = db_session.query(Alert).filter(Alert.status == 'active').count()
        expired_alerts = db_session.query(Alert).filter(Alert.status == 'expired').count()
        
        # Get recent scraping notifications
        recent_notifications = db_session.query(Notification).filter(
            and_(
                Notification.sent_at >= datetime.now() - timedelta(hours=24),
                Notification.type == 'availability_found_scraping'
            )
        ).count()
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'expired_alerts': expired_alerts,
            'scraping_notifications_sent_24h': recent_notifications,
            'monitoring_status': 'scraping_active',
            'scraper_pool_size': 3,
            'rate_limit_delay': 2.0
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping stats: {e}")
        return {}
