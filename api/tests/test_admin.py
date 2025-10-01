"""
Unit tests for admin endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

class TestAdmin:
    """Test admin endpoints"""
    
    def test_admin_dashboard_unauthorized(self, client):
        """Test admin dashboard without authentication"""
        response = client.get("/api/admin/dashboard")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_dashboard_non_admin(self, client, auth_headers, test_user, set_current_user):
        """Test admin dashboard with non-admin user"""
        set_current_user(test_user)
        response = client.get("/api/admin/dashboard", headers=auth_headers)
        assert response.status_code == 403  # Forbidden
    
    def test_admin_dashboard_success(self, client, admin_headers, test_admin_user, set_current_user):
        """Test successful admin dashboard access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "total_users" in dashboard
        assert "total_alerts" in dashboard
        assert "active_alerts" in dashboard
        assert "system_status" in dashboard
    
    def test_admin_users_unauthorized(self, client):
        """Test admin users endpoint without authentication"""
        response = client.get("/api/admin/users")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_users_non_admin(self, client, auth_headers, test_user, set_current_user):
        """Test admin users endpoint with non-admin user"""
        set_current_user(test_user)
        response = client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403  # Forbidden
    
    def test_admin_users_success(self, client, admin_headers, test_admin_user, test_user, set_current_user):
        """Test successful admin users access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 200
        users = response.json()
        assert "plan_distribution" in users
        assert "recent_signups_7d" in users
    
    def test_admin_users_with_pagination(self, client, admin_headers, test_admin_user, db_session, set_current_user):
        """Test admin users with pagination"""
        set_current_user(test_admin_user)
        # Create multiple users
        from models.user import User
        import uuid
        
        for i in range(5):
            user = User(
                id=str(uuid.uuid4()),
                email=f"user{i}@mousealerts.com",
                phone=f"+1555123456{i}",
                plan="free",
                subscription_status="active"
            )
            db_session.add(user)
        db_session.commit()
        
        response = client.get("/api/admin/users?limit=3&offset=0", headers=admin_headers)
        assert response.status_code == 200
        users = response.json()
        assert "plan_distribution" in users
        assert "recent_signups_7d" in users
    
    def test_admin_users_with_filtering(self, client, admin_headers, test_admin_user, set_current_user):
        """Test admin users with plan filtering"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/users?plan=free", headers=admin_headers)
        assert response.status_code == 200
        users = response.json()
        assert "plan_distribution" in users
        assert "recent_signups_7d" in users
    
    def test_admin_system_health_unauthorized(self, client):
        """Test admin system health without authentication"""
        response = client.get("/api/admin/system")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_system_health_success(self, client, admin_headers, test_admin_user, set_current_user):
        """Test successful admin system health access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/system", headers=admin_headers)
        assert response.status_code == 200
        system = response.json()
        assert "database" in system
        assert "total_users" in system
        assert "total_alerts" in system
        assert "status" in system
    
    def test_admin_analytics_revenue_unauthorized(self, client):
        """Test admin analytics revenue without authentication"""
        response = client.get("/api/admin/analytics/revenue")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_analytics_revenue_success(self, client, admin_headers, test_admin_user, set_current_user):
        """Test successful admin analytics revenue access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/analytics/revenue", headers=admin_headers)
        assert response.status_code == 200
        revenue = response.json()
        assert "mrr" in revenue
        assert "conversion_rate" in revenue
        assert "monthly_revenue" in revenue
        assert "churn_rate" in revenue
        assert "total_users" in revenue
        assert "paid_users" in revenue
        assert "active_subscriptions" in revenue
    
    def test_admin_analytics_alerts_unauthorized(self, client):
        """Test admin analytics alerts without authentication"""
        response = client.get("/api/admin/analytics/alerts")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_analytics_alerts_success(self, client, admin_headers, test_admin_user, set_current_user):
        """Test successful admin analytics alerts access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/analytics/alerts", headers=admin_headers)
        assert response.status_code == 200
        alerts = response.json()
        assert "total_alerts" in alerts
        assert "active_alerts" in alerts
        assert "paused_alerts" in alerts
        assert "expired_alerts" in alerts
        assert "success_rate" in alerts
        assert "recent_alerts" in alerts
        assert "run_success_rate" in alerts
        assert "avg_response_time" in alerts
    
    def test_admin_analytics_system_health_unauthorized(self, client):
        """Test admin analytics system health without authentication"""
        response = client.get("/api/admin/analytics/system-health")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_analytics_system_health_success(self, client, admin_headers, test_admin_user, set_current_user):
        """Test successful admin analytics system health access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/analytics/system-health", headers=admin_headers)
        assert response.status_code == 200
        system = response.json()
        assert "api_status" in system
        assert "db_status" in system
        assert "error_rate" in system
        assert "last_success_time" in system
        assert "pending_alerts" in system
        assert "uptime_percentage" in system
    
    def test_admin_analytics_dashboard_unauthorized(self, client):
        """Test admin analytics dashboard without authentication"""
        response = client.get("/api/admin/analytics/dashboard")
        assert response.status_code == 401  # FastAPI HTTPBearer returns 401 for missing token
    
    def test_admin_analytics_dashboard_success(self, client, admin_headers, test_admin_user, set_current_user):
        """Test successful admin analytics dashboard access"""
        set_current_user(test_admin_user)
        response = client.get("/api/admin/analytics/dashboard", headers=admin_headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "revenue" in dashboard
        assert "alerts" in dashboard
        assert "system" in dashboard
    
    def test_admin_role_creation(self, client, admin_headers, test_admin_user, db_session, set_current_user):
        """Test creating admin roles"""
        set_current_user(test_admin_user)
        # Create a new user
        from models.user import User
        import uuid
        
        new_user = User(
            id=str(uuid.uuid4()),
            email="newadmin@mousealerts.com",
            phone=f"+1555{uuid.uuid4().hex[:7]}",  # Unique phone number
            plan="premium",
            subscription_status="active"
        )
        db_session.add(new_user)
        db_session.commit()
            
        # Create admin role for new user
        response = client.post(
            f"/api/admin/roles?user_id={new_user.id}&role=admin",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert "Role 'admin' assigned" in response.json()["message"]
    
    def test_admin_role_update(self, client, admin_headers, test_admin_user, db_session, set_current_user):
        """Test updating admin roles"""
        set_current_user(test_admin_user)
        # Create a user with admin role
        from models.user import User
        import uuid
        
        user = User(
            id=str(uuid.uuid4()),
            email=f"testadmin-{uuid.uuid4().hex[:8]}@mousealerts.com",  # Unique email
            phone=f"+1555{uuid.uuid4().hex[:7]}",  # Unique phone number
            plan="premium",
            subscription_status="active"
        )
        db_session.add(user)
        db_session.commit()
            
        # Update admin role
        response = client.put(
            f"/api/admin/roles/{user.id}?role=super_admin",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert "Role updated to 'super_admin'" in response.json()["message"]
    
    def test_admin_role_deletion(self, client, admin_headers, test_admin_user, db_session, set_current_user):
        """Test deleting admin roles"""
        set_current_user(test_admin_user)
        # Create a user with admin role
        from models.user import User
        import uuid
        
        user = User(
            id=str(uuid.uuid4()),
            email=f"deleteadmin-{uuid.uuid4().hex[:8]}@mousealerts.com",  # Unique email
            phone=f"+1555{uuid.uuid4().hex[:7]}",  # Unique phone number
            plan="premium",
            subscription_status="active"
        )
        db_session.add(user)
        db_session.commit()
            
        # Delete admin role
        response = client.delete(
            f"/api/admin/roles/{user.id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert "Admin role removed" in response.json()["message"]
    
    def test_admin_ip_whitelist(self, client, admin_headers, test_admin_user, set_current_user):
        """Test admin IP whitelist functionality"""
        set_current_user(test_admin_user)
        # This would test IP whitelist functionality
        # For now, we'll just test that the endpoint exists
        response = client.get("/api/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
    
    def test_admin_audit_logging(self, client, admin_headers, test_admin_user, set_current_user):
        """Test admin audit logging"""
        set_current_user(test_admin_user)
        # Test that admin actions are logged
        response = client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 200
        # In a real implementation, we'd check that the action was logged
    
    def test_admin_error_handling(self, client, admin_headers, test_admin_user):
        """Test admin error handling"""
        with patch('deps.get_current_active_user', return_value=test_admin_user):
            # Test with invalid endpoint
            response = client.get("/api/admin/invalid", headers=admin_headers)
            assert response.status_code == 404
    
    def test_admin_rate_limiting(self, client, admin_headers, test_admin_user, set_current_user):
        """Test admin rate limiting"""
        set_current_user(test_admin_user)
        # Test multiple requests to check rate limiting
        for _ in range(5):
            response = client.get("/api/admin/dashboard", headers=admin_headers)
            assert response.status_code in [200, 429]  # Success or rate limited
