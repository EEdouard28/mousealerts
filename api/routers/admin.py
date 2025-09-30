"""
MouseAlerts API - Admin Router

This router provides administrative endpoints for monitoring and debugging.
These endpoints are restricted to admin users and provide system insights.

Endpoints:
- GET /runs: Get recent watcher runs with results and errors
- GET /metrics: Get system performance metrics
- GET /users: Get user statistics (admin only)

This router is used for:
- Monitoring background worker performance
- Debugging notification delivery issues
- Analyzing system usage patterns
- Managing system health

All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from db import get_db
from deps import get_current_active_user
from models.user import User
from models.watcher_run import WatcherRun
from models.alert import Alert
from models.notification import Notification

router = APIRouter()

def is_admin(user: User) -> bool:
    """Check if user has admin privileges"""
    return user.email in ["admin@mousealerts.app"]  # Simple admin check

@router.get("/runs")
async def get_watcher_runs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent watcher runs for monitoring"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    runs = db.query(WatcherRun).order_by(WatcherRun.run_at.desc()).limit(limit).all()
    return runs

@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get system performance metrics"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get basic metrics
    total_users = db.query(User).count()
    active_alerts = db.query(Alert).filter(Alert.status == "active").count()
    total_notifications = db.query(Notification).count()
    
    # Get recent run stats
    recent_runs = db.query(WatcherRun).filter(
        WatcherRun.run_at >= datetime.utcnow() - timedelta(hours=24)
    ).all()
    
    successful_runs = len([r for r in recent_runs if not r.error])
    failed_runs = len([r for r in recent_runs if r.error])
    
    return {
        "total_users": total_users,
        "active_alerts": active_alerts,
        "total_notifications": total_notifications,
        "recent_runs": {
            "total": len(recent_runs),
            "successful": successful_runs,
            "failed": failed_runs,
            "success_rate": successful_runs / len(recent_runs) if recent_runs else 0
        }
    }

@router.get("/users")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user statistics"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user plan distribution
    plan_stats = db.query(User.plan, db.func.count(User.id)).group_by(User.plan).all()
    
    # Get recent signups
    recent_signups = db.query(User).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return {
        "plan_distribution": dict(plan_stats),
        "recent_signups_7d": recent_signups
    }
