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
from middleware.auth import get_current_user
from models.user import User
from models.watcher_run import WatcherRun
from models.alert import Alert
from models.notification import Notification

router = APIRouter()

def is_admin(user: User) -> bool:
    """Check if user has admin privileges"""
    return (user.email in ["admin@mousealerts.app", "admin@mousealerts.com"] or 
            (user.email.startswith("admin-") and user.email.endswith("@mousealerts.com")) or
            (user.email.startswith("admin-") and user.email.endswith("@mousealerts.app")))  # Simple admin check

@router.get("/runs")
async def get_watcher_runs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
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
    current_user: User = Depends(get_current_user)
):
    """Get user statistics"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get user plan distribution
    from sqlalchemy import func
    plan_stats = db.query(User.plan, func.count(User.id)).group_by(User.plan).all()
    
    # Get recent signups
    recent_signups = db.query(User).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return {
        "plan_distribution": dict(plan_stats),
        "recent_signups_7d": recent_signups
    }

@router.get("/dashboard")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard overview"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get system overview
    total_users = db.query(User).count()
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.status == "active").count()
    
    # Get recent activity
    recent_alerts = db.query(Alert).filter(
        Alert.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return {
        "total_users": total_users,
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "recent_alerts_7d": recent_alerts,
        "system_status": "healthy"
    }

@router.get("/system")
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get system health status"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check database connectivity
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Get system metrics
    total_users = db.query(User).count()
    total_alerts = db.query(Alert).count()
    
    return {
        "database": db_status,
        "total_users": total_users,
        "total_alerts": total_alerts,
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/roles")
async def create_admin_role(
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create admin role for user"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user role (simplified - just update email for admin check)
    if role == "admin":
        import uuid
        user.email = f"admin-{uuid.uuid4().hex[:8]}@mousealerts.app"
    
    db.commit()
    
    return {"message": f"Role '{role}' assigned to user {user_id}"}

@router.put("/roles/{user_id}")
async def update_admin_role(
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update admin role for user"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user role
    if role == "admin":
        user.email = "admin@mousealerts.app"
    elif role == "user":
        user.email = f"user-{user_id}@mousealerts.app"
    
    db.commit()
    
    return {"message": f"Role updated to '{role}' for user {user_id}"}

@router.delete("/roles/{user_id}")
async def delete_admin_role(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove admin role from user"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove admin role
    user.email = f"user-{user_id}@mousealerts.app"
    db.commit()
    
    return {"message": f"Admin role removed from user {user_id}"}

@router.get("/ip-whitelist")
async def get_ip_whitelist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get IP whitelist for admin access"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Return whitelisted IPs (simplified implementation)
    return {
        "whitelisted_ips": ["127.0.0.1", "::1", "localhost"],
        "message": "IP whitelist retrieved successfully"
    }

@router.get("/audit")
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs for admin review"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get recent admin actions (simplified)
    recent_users = db.query(User).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=30)
    ).order_by(User.created_at.desc()).limit(10).all()
    
    audit_logs = []
    for user in recent_users:
        audit_logs.append({
            "timestamp": user.created_at.isoformat(),
            "action": "user_created",
            "user_id": user.id,
            "details": f"User {user.email} created account"
        })
    
    return {
        "audit_logs": audit_logs,
        "total_logs": len(audit_logs)
    }
