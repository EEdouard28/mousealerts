"""
MouseAlerts API - Plan Enforcement Service

This service handles plan limits and feature access control.
It enforces subscription plan restrictions and provides
plan-aware functionality throughout the application.

Features:
- Alert limit enforcement
- Feature access control
- Notification channel restrictions
- Plan upgrade prompts
- Usage tracking and limits

Plan Limits:
- Free: 2 alerts, email only, basic support
- Single Alert: 1 alert, email + SMS, priority support
- Premium: 25 alerts, email + SMS, priority support, AI access
- Family: unlimited alerts, all features, family sharing
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from models.user import User
from models.alert import Alert
from models.subscription import Subscription
from models.plan import Plan
from datetime import datetime, timedelta
import json

class PlanEnforcement:
    """Service for enforcing subscription plan limits and restrictions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_plan(self, user_id: str) -> Dict:
        """Get user's current plan with limits"""
        # Get user's active subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        if not subscription:
            # Default to free plan
            return self._get_free_plan()
        
        # Handle special plan types
        if subscription.plan_id == 'single_alert':
            return self._get_single_alert_plan(subscription)
        
        # Get plan details
        plan = self.db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        if not plan:
            return self._get_free_plan()
        
        return {
            "plan_id": plan.id,
            "plan_name": plan.name,
            "limits": plan.limits,
            "subscription_id": subscription.id,
            "current_period_end": subscription.current_period_end
        }
    
    def _get_free_plan(self) -> Dict:
        """Get free plan configuration"""
        return {
            "plan_id": "free",
            "plan_name": "Free",
            "limits": {
                "alerts_per_user": 2,
                "notification_channels": ["email"],
                "instant_notifications": False,
                "ai_prompt_bar": False,
                "priority_support": False,
                "monitoring_interval": 15  # minutes
            },
            "subscription_id": None,
            "current_period_end": None
        }
    
    def _get_single_alert_plan(self, subscription: Subscription) -> Dict:
        """Get single alert plan configuration"""
        return {
            "plan_id": "single_alert",
            "plan_name": "Single Alert",
            "limits": {
                "alerts_per_user": 1,
                "notification_channels": ["email", "sms"],
                "instant_notifications": True,
                "ai_prompt_bar": False,
                "priority_support": True,
                "monitoring_interval": 5  # minutes
            },
            "subscription_id": subscription.id,
            "current_period_end": subscription.current_period_end
        }
    
    def can_create_alert(self, user_id: str) -> Tuple[bool, str, Dict]:
        """
        Check if user can create a new alert based on their plan
        
        Returns:
        - (can_create: bool, reason: str, plan_info: dict)
        """
        plan_info = self.get_user_plan(user_id)
        limits = plan_info["limits"]
        
        # Count current active alerts
        active_alerts = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.status == "active"
        ).count()
        
        # Check alert limit
        max_alerts = limits.get("alerts_per_user", 0)
        if max_alerts == -1:  # unlimited
            return True, "unlimited", plan_info
        elif active_alerts >= max_alerts:
            return False, f"alert_limit_reached_{max_alerts}", plan_info
        
        return True, "allowed", plan_info
    
    def get_alert_usage(self, user_id: str) -> Dict:
        """Get user's current alert usage and limits"""
        plan_info = self.get_user_plan(user_id)
        limits = plan_info["limits"]
        
        active_alerts = self.db.query(Alert).filter(
            Alert.user_id == user_id,
            Alert.status == "active"
        ).count()
        
        max_alerts = limits.get("alerts_per_user", 0)
        
        return {
            "active_alerts": active_alerts,
            "max_alerts": max_alerts,
            "unlimited": max_alerts == -1,
            "remaining": max_alerts - active_alerts if max_alerts != -1 else -1,
            "plan_name": plan_info["plan_name"]
        }
    
    def can_use_feature(self, user_id: str, feature: str) -> bool:
        """Check if user can use a specific feature"""
        plan_info = self.get_user_plan(user_id)
        limits = plan_info["limits"]
        
        feature_map = {
            "ai_prompt_bar": "ai_prompt_bar",
            "sms_notifications": "notification_channels",
            "instant_notifications": "instant_notifications",
            "priority_support": "priority_support"
        }
        
        if feature not in feature_map:
            return False
        
        limit_key = feature_map[feature]
        
        if limit_key == "notification_channels":
            channels = limits.get(limit_key, [])
            return "sms" in channels
        
        return limits.get(limit_key, False)
    
    def get_notification_channels(self, user_id: str) -> List[str]:
        """Get allowed notification channels for user"""
        plan_info = self.get_user_plan(user_id)
        return plan_info["limits"].get("notification_channels", ["email"])
    
    def get_monitoring_interval(self, user_id: str) -> int:
        """Get monitoring interval in minutes for user's plan"""
        plan_info = self.get_user_plan(user_id)
        return plan_info["limits"].get("monitoring_interval", 15)
    
    def get_upgrade_suggestions(self, user_id: str) -> List[Dict]:
        """Get upgrade suggestions based on current usage"""
        plan_info = self.get_user_plan(user_id)
        current_plan = plan_info["plan_name"]
        usage = self.get_alert_usage(user_id)
        
        suggestions = []
        
        # Alert limit suggestions
        if usage["remaining"] <= 1 and current_plan == "Free":
            suggestions.append({
                "type": "alert_limit",
                "title": "Need more alerts?",
                "description": f"You've used {usage['active_alerts']}/{usage['max_alerts']} alerts. Upgrade for more!",
                "upgrade_to": "Premium",
                "benefit": "25 alerts + SMS notifications"
            })
        
        # Feature suggestions
        if not self.can_use_feature(user_id, "ai_prompt_bar") and current_plan == "Free":
            suggestions.append({
                "type": "feature",
                "title": "Unlock AI Prompt Bar",
                "description": "Describe your dining request in plain English",
                "upgrade_to": "Premium",
                "benefit": "AI-powered alert creation"
            })
        
        if not self.can_use_feature(user_id, "sms_notifications") and current_plan == "Free":
            suggestions.append({
                "type": "feature",
                "title": "Get SMS notifications",
                "description": "Never miss an alert with instant text messages",
                "upgrade_to": "Premium",
                "benefit": "Email + SMS notifications"
            })
        
        return suggestions
    
    def enforce_alert_creation(self, user_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Enforce alert creation limits
        
        Returns:
        - (allowed: bool, error_message: str, upgrade_suggestion: dict)
        """
        can_create, reason, plan_info = self.can_create_alert(user_id)
        
        if can_create:
            return True, "", None
        
        # Get upgrade suggestions
        suggestions = self.get_upgrade_suggestions(user_id)
        upgrade_suggestion = suggestions[0] if suggestions else None
        
        if reason.startswith("alert_limit_reached_"):
            limit = reason.split("_")[-1]
            return False, f"You've reached your {limit} alert limit. Upgrade to create more alerts.", upgrade_suggestion
        
        return False, "Unable to create alert. Please check your plan.", upgrade_suggestion
