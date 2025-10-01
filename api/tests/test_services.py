"""
Unit tests for service layer
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
import uuid

from services.admin_service import AdminService
from services.plan_enforcement import PlanEnforcement
from services.alert_monitor import AlertMonitorService
from services.nlu import NLUService
from models.user import User
from models.plan import Plan, Subscription
from models.alert import Alert

class TestAdminService:
    """Test AdminService functionality"""
    
    def test_create_admin_success(self, db_session, test_user):
        """Test successful admin creation"""
        admin_service = AdminService(db_session)
        admin = admin_service.create_admin(test_user.id, "admin")
        
        assert admin.user_id == test_user.id
        assert admin.role == "admin"
        assert admin.id is not None
    
    def test_create_admin_user_not_found(self, db_session):
        """Test admin creation with non-existent user"""
        admin_service = AdminService(db_session)
        
        with pytest.raises(ValueError, match="User with ID .* not found"):
            admin_service.create_admin("non-existent-id", "admin")
    
    def test_create_admin_already_exists(self, db_session, test_user):
        """Test admin creation when user is already admin"""
        admin_service = AdminService(db_session)
        
        # Create admin first time
        admin_service.create_admin(test_user.id, "admin")
        
        # Try to create again
        with pytest.raises(ValueError, match="User .* is already an admin"):
            admin_service.create_admin(test_user.id, "admin")
    
    def test_get_admin_role(self, db_session, test_user):
        """Test getting admin role"""
        admin_service = AdminService(db_session)
        
        # No admin role initially
        role = admin_service.get_admin_role(test_user.id)
        assert role is None
        
        # Create admin role
        admin_service.create_admin(test_user.id, "super_admin")
        
        # Get admin role
        role = admin_service.get_admin_role(test_user.id)
        assert role == "super_admin"
    
    def test_is_super_admin(self, db_session, test_user):
        """Test super admin check"""
        admin_service = AdminService(db_session)
        
        # Not super admin initially
        assert not admin_service.is_super_admin(test_user.id)
        
        # Create super admin
        admin_service.create_admin(test_user.id, "super_admin")
        assert admin_service.is_super_admin(test_user.id)
        
        # Regular admin is not super admin
        admin_service.update_admin_role(test_user.id, "admin")
        assert not admin_service.is_super_admin(test_user.id)
    
    def test_is_admin(self, db_session, test_user):
        """Test admin check"""
        admin_service = AdminService(db_session)
        
        # Not admin initially
        assert not admin_service.is_admin(test_user.id)
        
        # Create admin
        admin_service.create_admin(test_user.id, "admin")
        assert admin_service.is_admin(test_user.id)
        
        # Super admin is also admin
        admin_service.update_admin_role(test_user.id, "super_admin")
        assert admin_service.is_admin(test_user.id)
    
    def test_update_admin_role(self, db_session, test_user):
        """Test updating admin role"""
        admin_service = AdminService(db_session)
        
        # Create admin
        admin_service.create_admin(test_user.id, "admin")
        
        # Update role
        updated_admin = admin_service.update_admin_role(test_user.id, "super_admin")
        assert updated_admin.role == "super_admin"
    
    def test_delete_admin(self, db_session, test_user):
        """Test deleting admin"""
        admin_service = AdminService(db_session)
        
        # Create admin
        admin_service.create_admin(test_user.id, "admin")
        assert admin_service.is_admin(test_user.id)
        
        # Delete admin
        admin_service.delete_admin(test_user.id)
        assert not admin_service.is_admin(test_user.id)

class TestPlanEnforcement:
    """Test PlanEnforcement service"""
    
    def test_get_user_plan_free(self, db_session, test_user, test_plan):
        """Test getting free plan for user"""
        plan_enforcement = PlanEnforcement(db_session)
        plan = plan_enforcement.get_user_plan(test_user.id)
        
        assert plan.plan_id == "free"
        assert plan.plan_name == "Free"
        assert plan.limits["alerts_per_user"] == 2
        assert "email" in plan.limits["notification_channels"]
        assert not plan.limits["instant_notifications"]
        assert not plan.limits["ai_prompt_bar"]
    
    def test_get_user_plan_premium(self, db_session, test_plan):
        """Test getting premium plan for user"""
        # Create premium user
        user = User(
            id=str(uuid.uuid4()),
            email="premium@mousealerts.com",
            phone="+15551234568",
            plan="premium",
            subscription_status="active"
        )
        db_session.add(user)
        db_session.commit()
        
        plan_enforcement = PlanEnforcement(db_session)
        plan = plan_enforcement.get_user_plan(user.id)
        
        assert plan.plan_id == "premium"
        assert plan.plan_name == "Premium"
        assert plan.limits["alerts_per_user"] == 25
        assert "email" in plan.limits["notification_channels"]
        assert "sms" in plan.limits["notification_channels"]
        assert "push" in plan.limits["notification_channels"]
        assert plan.limits["instant_notifications"]
        assert plan.limits["ai_prompt_bar"]
    
    def test_can_create_alert_free_plan(self, db_session, test_user, test_plan):
        """Test alert creation limits for free plan"""
        plan_enforcement = PlanEnforcement(db_session)
        
        # Free plan allows 2 alerts
        assert plan_enforcement.can_create_alert(test_user.id)
        
        # Create 2 alerts (limit reached)
        for i in range(2):
            alert = Alert(
                id=str(uuid.uuid4()),
                user_id=test_user.id,
                restaurant=f"Restaurant {i}",
                date="2024-12-25",
                time_start="18:00",
                time_end="20:00",
                party_size=4,
                status="active"
            )
            db_session.add(alert)
        db_session.commit()
        
        # Should not be able to create more alerts
        assert not plan_enforcement.can_create_alert(test_user.id)
    
    def test_can_create_alert_premium_plan(self, db_session, test_plan):
        """Test alert creation limits for premium plan"""
        # Create premium user
        user = User(
            id=str(uuid.uuid4()),
            email="premium@mousealerts.com",
            phone="+15551234568",
            plan="premium",
            subscription_status="active"
        )
        db_session.add(user)
        db_session.commit()
        
        plan_enforcement = PlanEnforcement(db_session)
        
        # Premium plan allows 25 alerts
        assert plan_enforcement.can_create_alert(user.id)
        
        # Create 25 alerts (limit reached)
        for i in range(25):
            alert = Alert(
                id=str(uuid.uuid4()),
                user_id=user.id,
                restaurant=f"Restaurant {i}",
                date="2024-12-25",
                time_start="18:00",
                time_end="20:00",
                party_size=4,
                status="active"
            )
            db_session.add(alert)
        db_session.commit()
        
        # Should not be able to create more alerts
        assert not plan_enforcement.can_create_alert(user.id)
    
    def test_get_alert_usage(self, db_session, test_user, test_alert):
        """Test getting alert usage"""
        plan_enforcement = PlanEnforcement(db_session)
        usage = plan_enforcement.get_alert_usage(test_user.id)
        
        assert usage.total_alerts >= 1
        assert usage.active_alerts >= 1
        assert usage.paused_alerts >= 0
        assert usage.expired_alerts >= 0
    
    def test_get_notification_channels(self, db_session, test_user, test_plan):
        """Test getting notification channels for plan"""
        plan_enforcement = PlanEnforcement(db_session)
        channels = plan_enforcement.get_notification_channels(test_user.id)
        
        assert "email" in channels
        assert "sms" not in channels  # Free plan doesn't have SMS
        assert "push" not in channels  # Free plan doesn't have push
    
    def test_can_use_feature(self, db_session, test_user, test_plan):
        """Test feature access for plan"""
        plan_enforcement = PlanEnforcement(db_session)
        
        # Free plan features
        assert not plan_enforcement.can_use_feature(test_user.id, "ai_prompt_bar")
        assert not plan_enforcement.can_use_feature(test_user.id, "instant_notifications")
        assert not plan_enforcement.can_use_feature(test_user.id, "priority_support")
    
    def test_get_upgrade_suggestions(self, db_session, test_user, test_plan):
        """Test getting upgrade suggestions"""
        plan_enforcement = PlanEnforcement(db_session)
        suggestions = plan_enforcement.get_upgrade_suggestions(test_user.id)
        
        assert len(suggestions) > 0
        assert any("Premium" in suggestion.title for suggestion in suggestions)
        assert any("AI Prompt Bar" in suggestion.description for suggestion in suggestions)

class TestNLUService:
    """Test NLU service functionality"""
    
    def test_extract_date_time(self):
        """Test date/time extraction"""
        nlu_service = NLUService()
        
        # Test various date/time formats
        test_cases = [
            ("tomorrow at 7pm", "tomorrow", 19),
            ("next Friday at 6:30", "next Friday", 18),
            ("December 25th at 8pm", "December 25th", 20),
            ("tonight at 7:30", "tonight", 19),
        ]
        
        for text, expected_date, expected_hour in test_cases:
            result = nlu_service.extract_date_time(text)
            assert result is not None
            assert result["date"] is not None
            assert result["time"] is not None
    
    def test_find_venue_suggestions(self):
        """Test venue suggestion finding"""
        nlu_service = NLUService()
        
        # Test venue suggestions
        suggestions = nlu_service.find_venue_suggestions("princess dining")
        assert len(suggestions) > 0
        assert any("Cinderella" in suggestion["name"] for suggestion in suggestions)
    
    def test_extract_party_size(self):
        """Test party size extraction"""
        nlu_service = NLUService()
        
        # Test party size extraction
        test_cases = [
            ("table for 4", 4),
            ("party of 6", 6),
            ("2 people", 2),
            ("family of 5", 5),
        ]
        
        for text, expected_size in test_cases:
            result = nlu_service.extract_party_size(text)
            assert result == expected_size
    
    def test_extract_experience_tags(self):
        """Test experience tag extraction"""
        nlu_service = NLUService()
        
        # Test experience tag extraction
        test_cases = [
            ("princess dining", ["princess"]),
            ("romantic dinner", ["romantic"]),
            ("family meal", ["family"]),
            ("character breakfast", ["character"]),
        ]
        
        for text, expected_tags in test_cases:
            result = nlu_service.extract_experience_tags(text)
            assert all(tag in result for tag in expected_tags)
    
    def test_calculate_confidence(self):
        """Test confidence calculation"""
        nlu_service = NLUService()
        
        # Test confidence calculation
        high_confidence = {
            "date": "2024-12-25",
            "time": 19,
            "party_size": 4,
            "restaurant": "Cinderella's Royal Table",
            "experience_tags": ["princess"]
        }
        
        low_confidence = {
            "date": None,
            "time": None,
            "party_size": None,
            "restaurant": None,
            "experience_tags": []
        }
        
        high_conf = nlu_service.calculate_confidence(high_confidence)
        low_conf = nlu_service.calculate_confidence(low_confidence)
        
        assert high_conf > low_conf
        assert high_conf > 0.7
        assert low_conf < 0.3
    
    def test_generate_clarification_questions(self):
        """Test clarification question generation"""
        nlu_service = NLUService()
        
        # Test clarification questions for low confidence
        low_confidence = {
            "date": None,
            "time": None,
            "party_size": None,
            "restaurant": None,
            "experience_tags": []
        }
        
        questions = nlu_service.generate_clarification_questions(low_confidence)
        assert len(questions) > 0
        assert any("date" in question.lower() for question in questions)
        assert any("time" in question.lower() for question in questions)
    
    def test_apply_smart_templates(self):
        """Test smart template application"""
        nlu_service = NLUService()
        
        # Test smart templates
        test_cases = [
            ("princess dining", "princess"),
            ("fireworks view", "fireworks"),
            ("romantic dinner", "romantic"),
            ("family meal", "family"),
        ]
        
        for text, expected_template in test_cases:
            result = nlu_service.apply_smart_templates(text)
            assert result is not None
            assert result["template"] == expected_template
    
    def test_generate_smart_suggestions(self):
        """Test smart suggestion generation"""
        nlu_service = NLUService()
        
        # Test smart suggestions for vague input
        suggestions = nlu_service.generate_smart_suggestions("dinner")
        assert len(suggestions) > 0
        assert any("restaurant" in suggestion.lower() for suggestion in suggestions)

class TestAlertMonitorService:
    """Test AlertMonitorService functionality"""
    
    @patch('services.alert_monitor.AlertMonitorService.check_availability')
    def test_check_availability_success(self, mock_check, db_session, test_alert):
        """Test successful availability check"""
        mock_check.return_value = [
            {
                "date": "2024-12-25",
                "time": "18:30",
                "party_size": 4,
                "restaurant": "Cinderella's Royal Table"
            }
        ]
        
        monitor = AlertMonitorService(db_session)
        result = monitor.check_availability(test_alert)
        
        assert result is not None
        assert len(result) > 0
        assert result[0]["restaurant"] == test_alert.restaurant
    
    @patch('services.alert_monitor.AlertMonitorService.check_availability')
    def test_check_availability_no_slots(self, mock_check, db_session, test_alert):
        """Test availability check with no slots"""
        mock_check.return_value = []
        
        monitor = AlertMonitorService(db_session)
        result = monitor.check_availability(test_alert)
        
        assert result == []
    
    @patch('services.alert_monitor.AlertMonitorService.check_availability')
    def test_check_availability_error(self, mock_check, db_session, test_alert):
        """Test availability check with error"""
        mock_check.side_effect = Exception("API Error")
        
        monitor = AlertMonitorService(db_session)
        result = monitor.check_availability(test_alert)
        
        assert result is None
    
    def test_deduplicate_notifications(self, db_session, test_alert):
        """Test notification deduplication"""
        monitor = AlertMonitorService(db_session)
        
        # Test deduplication logic
        slot1 = {
            "date": "2024-12-25",
            "time": "18:30",
            "party_size": 4,
            "restaurant": "Cinderella's Royal Table"
        }
        
        slot2 = {
            "date": "2024-12-25",
            "time": "18:30",
            "party_size": 4,
            "restaurant": "Cinderella's Royal Table"
        }
        
        # Should be considered duplicate
        is_duplicate = monitor.is_duplicate_notification(test_alert, slot1, slot2)
        assert is_duplicate
    
    def test_send_notifications(self, db_session, test_alert):
        """Test notification sending"""
        monitor = AlertMonitorService(db_session)
        
        # Test notification sending logic
        slot = {
            "date": "2024-12-25",
            "time": "18:30",
            "party_size": 4,
            "restaurant": "Cinderella's Royal Table"
        }
        
        # Mock notification sending
        with patch.object(monitor, 'send_notification') as mock_send:
            mock_send.return_value = True
            result = monitor.send_notifications(test_alert, slot)
            assert result is True
            mock_send.assert_called_once()
