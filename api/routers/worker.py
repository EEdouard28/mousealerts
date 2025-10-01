"""
Background Worker Router

This router provides endpoints for managing background workers and monitoring
Disney dining availability. It handles alert monitoring, notification sending,
and system health checks.

Endpoints:
- POST /worker/start-monitoring - Start alert monitoring
- POST /worker/stop-monitoring - Stop alert monitoring
- GET /worker/status - Get monitoring status
- POST /worker/check-alert/{alert_id} - Check specific alert
- POST /worker/expire-alerts - Expire old alerts
- GET /worker/stats - Get monitoring statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
import asyncio
import logging

from db import get_db
from deps import get_current_active_user
from models.user import User
from services.alert_monitor import (
    start_alert_monitor, 
    check_single_alert, 
    expire_old_alerts, 
    get_monitoring_stats
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Global monitoring state
monitoring_task = None
monitoring_status = "stopped"

@router.post("/start-monitoring")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start the background alert monitoring service.
    
    Args:
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user (admin only)
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If user is not admin or monitoring is already running
    """
    global monitoring_task, monitoring_status
    
    # Check if user is admin (simplified check)
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if monitoring_status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monitoring is already running"
        )
    
    try:
        # Start monitoring in background
        background_tasks.add_task(start_alert_monitor, db, use_mock_api=True)
        monitoring_status = "running"
        
        logger.info("Alert monitoring started")
        
        return {
            "message": "Alert monitoring started successfully",
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start monitoring"
        )

@router.post("/stop-monitoring")
async def stop_monitoring(
    current_user: User = Depends(get_current_active_user)
):
    """
    Stop the background alert monitoring service.
    
    Args:
        current_user: Authenticated user (admin only)
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If user is not admin or monitoring is not running
    """
    global monitoring_status
    
    # Check if user is admin
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if monitoring_status == "stopped":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Monitoring is not running"
        )
    
    try:
        # Stop monitoring
        monitoring_status = "stopped"
        
        logger.info("Alert monitoring stopped")
        
        return {
            "message": "Alert monitoring stopped successfully",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop monitoring"
        )

@router.get("/status")
async def get_monitoring_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current monitoring status.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Current monitoring status and statistics
    """
    global monitoring_status
    
    try:
        return {
            "monitoring_status": monitoring_status,
            "message": f"Alert monitoring is {monitoring_status}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring status"
        )

@router.post("/check-alert/{alert_id}")
async def check_specific_alert(
    alert_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check a specific alert for availability.
    
    Args:
        alert_id: ID of the alert to check
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If alert not found or check fails
    """
    try:
        # Check if alert exists and belongs to user
        from models.alert import Alert
        alert = db.query(Alert).filter(
            Alert.id == alert_id,
            Alert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Check alert in background
        background_tasks.add_task(check_single_alert, alert_id, db, use_mock_api=True)
        
        logger.info(f"Alert check initiated for {alert_id}")
        
        return {
            "message": f"Alert {alert_id} check initiated",
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check alert"
        )

@router.post("/expire-alerts")
async def expire_old_alerts_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Expire old alerts that are past their date.
    
    Args:
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user (admin only)
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If user is not admin or operation fails
    """
    # Check if user is admin
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Expire alerts in background
        background_tasks.add_task(expire_old_alerts, db)
        
        logger.info("Alert expiration initiated")
        
        return {
            "message": "Alert expiration initiated",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Failed to expire alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to expire alerts"
        )

@router.get("/stats")
async def get_worker_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get monitoring statistics and system health.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Monitoring statistics and system health information
    """
    try:
        # Get monitoring stats
        stats = await get_monitoring_stats(db)
        
        # Add global status
        stats['monitoring_status'] = monitoring_status
        
        logger.info(f"Retrieved worker stats: {stats}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get worker stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get worker statistics"
        )

@router.get("/health")
async def worker_health_check():
    """
    Health check endpoint for the worker service.
    
    Returns:
        Health status information
    """
    try:
        return {
            "status": "healthy",
            "monitoring_status": monitoring_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
