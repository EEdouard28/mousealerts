"""
Pydantic schemas for analytics and admin dashboard data
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RevenueAnalytics(BaseModel):
    """Revenue analytics data for admin dashboard"""
    mrr: float  # Monthly Recurring Revenue
    conversion_rate: float  # Free to paid conversion rate
    monthly_revenue: float  # Revenue in last 30 days
    churn_rate: float  # Customer churn rate
    total_users: int
    paid_users: int
    active_subscriptions: int


class ConversionMetrics(BaseModel):
    """Conversion metrics for admin dashboard"""
    free_to_premium: float  # Free to Premium conversion
    free_to_family: float  # Free to Family conversion
    premium_to_family: float  # Premium to Family upgrade
    single_alert_purchases: int  # One-time purchases


class AlertMetrics(BaseModel):
    """Alert monitoring metrics for admin dashboard"""
    total_alerts: int
    active_alerts: int
    paused_alerts: int
    expired_alerts: int
    success_rate: float  # Notification success rate
    recent_alerts: int  # Alerts created in last 7 days
    run_success_rate: float  # Watcher run success rate
    avg_response_time: float  # Average response time in ms


class SystemHealth(BaseModel):
    """System health indicators for admin dashboard"""
    api_status: str  # "healthy", "degraded", "unhealthy"
    db_status: str  # "healthy", "degraded", "unhealthy"
    error_rate: float  # Error rate percentage
    last_success_time: Optional[datetime]  # Last successful operation
    pending_alerts: int  # Number of pending alerts
    uptime_percentage: float  # System uptime percentage


class AdminDashboard(BaseModel):
    """Complete admin dashboard data"""
    revenue: RevenueAnalytics
    alerts: AlertMetrics
    system: SystemHealth
