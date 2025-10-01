"""
MouseAlerts API - Email Service

This service handles all email notifications including:
- Magic link authentication emails
- Alert notifications when reservations are found
- System notifications and updates

Email Types:
- Magic Link: Passwordless authentication
- Alert Notifications: When Disney reservations are found
- System Updates: Plan changes, billing notifications

Uses SendGrid for reliable email delivery with templates
for consistent branding and formatting.
"""

import sendgrid
from sendgrid.helpers.mail import Mail
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize SendGrid client
sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

class EmailService:
    """Email service class for handling all email operations"""
    
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    async def send_magic_link_email(self, email: str, magic_link: str):
        """Send magic link email for authentication"""
        return await send_magic_link_email(email, magic_link)
    
    async def send_alert_notification(self, email: str, alert_data: dict):
        """Send alert notification when reservation is found"""
        return await send_alert_notification(email, alert_data)
    
    async def send_system_notification(self, email: str, subject: str, content: str):
        """Send system notification (plan changes, billing, etc.)"""
        return await send_system_notification(email, subject, content)

async def send_magic_link_email(email: str, magic_link: str):
    """Send magic link email for authentication"""
    try:
        message = Mail(
            from_email='noreply@mousealerts.app',
            to_emails=email,
            subject='Your MouseAlerts Login Link',
            html_content=f"""
            <h2>Welcome to MouseAlerts!</h2>
            <p>Click the link below to sign in to your account:</p>
            <a href="{magic_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Sign In to MouseAlerts
            </a>
            <p>This link will expire in 15 minutes.</p>
            <p>If you didn't request this email, you can safely ignore it.</p>
            """
        )
        
        response = sg.send(message)
        logger.info(f"Magic link email sent to {email}")
        return response
    except Exception as e:
        logger.error(f"Failed to send magic link email: {e}")
        raise

async def send_alert_notification(email: str, alert_data: dict):
    """Send alert notification when reservation is found"""
    try:
        message = Mail(
            from_email='alerts@mousealerts.app',
            to_emails=email,
            subject=f'🎉 Disney Reservation Found: {alert_data["venue"]}',
            html_content=f"""
            <h2>🎉 Great News!</h2>
            <p>A Disney dining reservation has opened up for:</p>
            <ul>
                <li><strong>Restaurant:</strong> {alert_data["venue"]}</li>
                <li><strong>Park:</strong> {alert_data["park"]}</li>
                <li><strong>Date:</strong> {alert_data["date"]}</li>
                <li><strong>Time:</strong> {alert_data["time_start"]} - {alert_data["time_end"]}</li>
                <li><strong>Party Size:</strong> {alert_data["party_size"]}</li>
            </ul>
            <p><a href="{alert_data["booking_url"]}" style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px;">
                Book Now on Disney's Site
            </a></p>
            <p><em>This reservation may be taken quickly, so book soon!</em></p>
            """
        )
        
        response = sg.send(message)
        logger.info(f"Alert notification sent to {email}")
        return response
    except Exception as e:
        logger.error(f"Failed to send alert notification: {e}")
        raise

async def send_system_notification(email: str, subject: str, content: str):
    """Send system notification (plan changes, billing, etc.)"""
    try:
        message = Mail(
            from_email='system@mousealerts.app',
            to_emails=email,
            subject=subject,
            html_content=content
        )
        
        response = sg.send(message)
        logger.info(f"System notification sent to {email}")
        return response
    except Exception as e:
        logger.error(f"Failed to send system notification: {e}")
        raise
