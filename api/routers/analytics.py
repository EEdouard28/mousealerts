"""
Revenue and Analytics API endpoints for admin dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any
from db import get_db
from middleware.admin_auth import verify_admin_access
from models.user import User
from models.plan import Plan
from models.subscription import Subscription
from models.alert import Alert
from models.notification import Notification
from models.watcher_run import WatcherRun
from schemas.analytics import (
    RevenueAnalytics,
    ConversionMetrics,
    AlertMetrics,
    SystemHealth,
    AdminDashboard
)

router = APIRouter(prefix="/api/admin/analytics", tags=["admin", "analytics"])


@router.get("/revenue", response_model=RevenueAnalytics)
async def get_revenue_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin_access)
):
    """Get revenue analytics including MRR, conversion rates, and payment metrics"""
    try:
        # Calculate MRR (Monthly Recurring Revenue)
        active_subscriptions = db.query(Subscription).filter(
            Subscription.status == "active"
        ).all()
        
        mrr = 0
        for sub in active_subscriptions:
            plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
            if plan and plan.price_cents:
                mrr += plan.price_cents / 100  # Convert cents to dollars
        
        # Calculate conversion metrics
        total_users = db.query(User).count()
        paid_users = db.query(User).join(Subscription).filter(
            Subscription.status == "active"
        ).count()
        
        conversion_rate = (paid_users / total_users * 100) if total_users > 0 else 0
        
        # Calculate revenue trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_subscriptions = db.query(Subscription).filter(
            Subscription.created_at >= thirty_days_ago
        ).all()
        
        monthly_revenue = 0
        for sub in recent_subscriptions:
            plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
            if plan and plan.price_cents:
                monthly_revenue += plan.price_cents / 100
        
        # Calculate churn rate (simplified)
        cancelled_subscriptions = db.query(Subscription).filter(
            Subscription.status == "cancelled"
        ).count()
        
        churn_rate = (cancelled_subscriptions / total_users * 100) if total_users > 0 else 0
        
        return RevenueAnalytics(
            mrr=mrr,
            conversion_rate=conversion_rate,
            monthly_revenue=monthly_revenue,
            churn_rate=churn_rate,
            total_users=total_users,
            paid_users=paid_users,
            active_subscriptions=len(active_subscriptions)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating revenue analytics: {str(e)}"
        )


@router.get("/alerts", response_model=AlertMetrics)
async def get_alert_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin_access)
):
    """Get alert monitoring metrics including success rates and performance"""
    try:
        # Total alerts
        total_alerts = db.query(Alert).count()
        active_alerts = db.query(Alert).filter(Alert.status == "active").count()
        paused_alerts = db.query(Alert).filter(Alert.status == "paused").count()
        expired_alerts = db.query(Alert).filter(Alert.status == "expired").count()
        
        # Alert success metrics
        successful_notifications = db.query(Notification).filter(
            Notification.status == "sent"
        ).count()
        total_notifications = db.query(Notification).count()
        
        success_rate = (successful_notifications / total_notifications * 100) if total_notifications > 0 else 0
        
        # Recent alert activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_alerts = db.query(Alert).filter(
            Alert.created_at >= seven_days_ago
        ).count()
        
        # Watcher run metrics
        successful_runs = db.query(WatcherRun).filter(
            WatcherRun.error.is_(None)
        ).count()
        total_runs = db.query(WatcherRun).count()
        
        run_success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Average response time (simplified)
        recent_runs = db.query(WatcherRun).filter(
            WatcherRun.run_at >= seven_days_ago
        ).all()
        
        avg_response_time = 0
        if recent_runs:
            total_time = sum([run.latency_ms or 0 for run in recent_runs])
            avg_response_time = total_time / len(recent_runs)
        
        return AlertMetrics(
            total_alerts=total_alerts,
            active_alerts=active_alerts,
            paused_alerts=paused_alerts,
            expired_alerts=expired_alerts,
            success_rate=success_rate,
            recent_alerts=recent_alerts,
            run_success_rate=run_success_rate,
            avg_response_time=avg_response_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating alert metrics: {str(e)}"
        )


@router.get("/system-health", response_model=SystemHealth)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin_access)
):
    """Get system health indicators and performance metrics"""
    try:
        # API status (simplified - in real implementation, check actual services)
        api_status = "healthy"
        
        # Error rates
        total_requests = 1000  # Mock value - in real implementation, track actual requests
        error_count = db.query(WatcherRun).filter(
            WatcherRun.error.isnot(None)
        ).count()
        
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        
        # Last successful operations
        last_successful_run = db.query(WatcherRun).filter(
            WatcherRun.error.is_(None)
        ).order_by(WatcherRun.run_at.desc()).first()
        
        last_success_time = last_successful_run.run_at if last_successful_run else None
        
        # Queue depth (simplified)
        pending_alerts = db.query(Alert).filter(Alert.status == "active").count()
        
        # Database health
        db_status = "healthy"
        try:
            db.execute("SELECT 1")
        except Exception:
            db_status = "unhealthy"
        
        return SystemHealth(
            api_status=api_status,
            db_status=db_status,
            error_rate=error_rate,
            last_success_time=last_success_time,
            pending_alerts=pending_alerts,
            uptime_percentage=99.9  # Mock value
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating system health: {str(e)}"
        )


@router.get("/dashboard", response_model=AdminDashboard)
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_admin_access)
):
    """Get complete admin dashboard data"""
    try:
        # Get all metrics
        revenue_data = await get_revenue_analytics(db, current_user)
        alert_data = await get_alert_metrics(db, current_user)
        system_data = await get_system_health(db, current_user)
        
        return AdminDashboard(
            revenue=revenue_data,
            alerts=alert_data,
            system=system_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating admin dashboard: {str(e)}"
        )
