"""
Disney Scraping Worker Router

This router provides endpoints for managing web scraping-based alert monitoring.
It handles the MouseWatcher-style approach of monitoring Disney's reservation
system through web scraping and sending real-time alerts.

Endpoints:
- POST /scraping/start-monitoring - Start scraping-based monitoring
- POST /scraping/stop-monitoring - Stop scraping monitoring
- GET /scraping/status - Get scraping monitoring status
- POST /scraping/check-alert/{alert_id} - Check specific alert with scraping
- GET /scraping/stats - Get scraping statistics
- GET /scraping/health - Health check for scraping service
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
import asyncio
import logging
from datetime import datetime

from db import get_db
from deps import get_current_active_user
from models.user import User
from services.scraping_monitor import (
    start_scraping_monitor, 
    check_single_alert_with_scraping, 
    get_scraping_stats
)
from services.disney_scraper import test_scraper_connection, get_scraper_stats

router = APIRouter()
logger = logging.getLogger(__name__)

# Global scraping monitoring state
scraping_monitoring_task = None
scraping_monitoring_status = "stopped"

@router.post("/start-monitoring")
async def start_scraping_monitoring(
    background_tasks: BackgroundTasks,
    headless: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start the scraping-based alert monitoring service.
    
    Args:
        background_tasks: FastAPI background tasks
        headless: Whether to run browser in headless mode
        db: Database session
        current_user: Authenticated user (admin only)
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If user is not admin or monitoring is already running
    """
    global scraping_monitoring_task, scraping_monitoring_status
    
    # Check if user is admin (simplified check)
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if scraping_monitoring_status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scraping monitoring is already running"
        )
    
    try:
        # Test scraper connection first
        connection_ok = await test_scraper_connection()
        if not connection_ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to Disney's website"
            )
        
        # Start scraping monitoring in background
        background_tasks.add_task(start_scraping_monitor, db, headless)
        scraping_monitoring_status = "running"
        
        logger.info("Scraping-based alert monitoring started")
        
        return {
            "message": "Scraping-based alert monitoring started successfully",
            "status": "running",
            "headless_mode": headless,
            "connection_tested": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start scraping monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start scraping monitoring"
        )

@router.post("/stop-monitoring")
async def stop_scraping_monitoring(
    current_user: User = Depends(get_current_active_user)
):
    """
    Stop the scraping-based monitoring service.
    
    Args:
        current_user: Authenticated user (admin only)
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If user is not admin or monitoring is not running
    """
    global scraping_monitoring_status
    
    # Check if user is admin
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if scraping_monitoring_status == "stopped":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scraping monitoring is not running"
        )
    
    try:
        # Stop monitoring
        scraping_monitoring_status = "stopped"
        
        logger.info("Scraping-based alert monitoring stopped")
        
        return {
            "message": "Scraping-based alert monitoring stopped successfully",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop scraping monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop scraping monitoring"
        )

@router.get("/status")
async def get_scraping_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current scraping monitoring status.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Current scraping monitoring status and statistics
    """
    global scraping_monitoring_status
    
    try:
        # Get scraper stats
        scraper_stats = await get_scraper_stats()
        
        return {
            "monitoring_status": scraping_monitoring_status,
            "message": f"Scraping monitoring is {scraping_monitoring_status}",
            "scraper_stats": scraper_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get scraping status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scraping status"
        )

@router.post("/check-alert/{alert_id}")
async def check_specific_alert_with_scraping(
    alert_id: str,
    headless: bool = True,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check a specific alert using web scraping.
    
    Args:
        alert_id: ID of the alert to check
        headless: Whether to run browser in headless mode
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
        
        # Check alert with scraping in background
        background_tasks.add_task(check_single_alert_with_scraping, alert_id, db, headless)
        
        logger.info(f"Scraping alert check initiated for {alert_id}")
        
        return {
            "message": f"Alert {alert_id} scraping check initiated",
            "alert_id": alert_id,
            "headless_mode": headless
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check alert {alert_id} with scraping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check alert with scraping"
        )

@router.get("/stats")
async def get_scraping_worker_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get scraping monitoring statistics and system health.
    
    Args:
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Scraping monitoring statistics and system health information
    """
    try:
        # Get scraping stats
        stats = await get_scraping_stats(db)
        
        # Add global status
        stats['monitoring_status'] = scraping_monitoring_status
        
        logger.info(f"Retrieved scraping worker stats: {stats}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get scraping worker stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scraping worker statistics"
        )

@router.get("/health")
async def scraping_health_check():
    """
    Health check endpoint for the scraping service.
    
    Returns:
        Health status information
    """
    try:
        # Test scraper connection
        connection_ok = await test_scraper_connection()
        
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "monitoring_status": scraping_monitoring_status,
            "scraper_connection": connection_ok,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Scraping health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/test-connection")
async def test_scraping_connection(
    current_user: User = Depends(get_current_active_user)
):
    """
    Test the scraping connection to Disney's website.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Connection test results
    """
    try:
        connection_ok = await test_scraper_connection()
        
        if connection_ok:
            return {
                "status": "success",
                "message": "Successfully connected to Disney's website",
                "connection_ok": True
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to connect to Disney's website",
                "connection_ok": False
            }
        
    except Exception as e:
        logger.error(f"Scraping connection test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test scraping connection"
        )
