"""
Pytest configuration and fixtures for MouseAlerts API tests
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db import get_db, Base
from models.user import User
from models.alert import Alert
from models.plan import Plan, Subscription
from models.magic_link_token import MagicLinkToken
from services.admin_service import AdminService
import uuid

# Test database URL (in-memory SQLite for fast tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    """Create database session for testing"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="test@mousealerts.com",
        phone="+15551234567",
        plan="free",
        subscription_status="active"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user"""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@mousealerts.com",
        phone="+15551234568",
        plan="premium",
        subscription_status="active"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create admin role
    admin_service = AdminService(db_session)
    admin_service.create_admin(user.id, "admin")
    
    return user

@pytest.fixture
def test_plan(db_session):
    """Create test plans"""
    plans = [
        Plan(
            id="free",
            name="Free",
            price_cents=0,
            limits={
                "alerts_per_user": 2,
                "notification_channels": ["email"],
                "instant_notifications": False,
                "ai_prompt_bar": False,
                "priority_support": False,
                "monitoring_interval": 300
            }
        ),
        Plan(
            id="premium",
            name="Premium",
            price_cents=999,
            limits={
                "alerts_per_user": 25,
                "notification_channels": ["email", "sms", "push"],
                "instant_notifications": True,
                "ai_prompt_bar": True,
                "priority_support": True,
                "monitoring_interval": 60
            }
        )
    ]
    
    for plan in plans:
        db_session.add(plan)
    db_session.commit()
    return plans

@pytest.fixture
def test_alert(db_session, test_user):
    """Create a test alert"""
    alert = Alert(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        restaurant="Cinderella's Royal Table",
        date="2024-12-25",
        time_start="18:00",
        time_end="20:00",
        party_size=4,
        status="active",
        notification_channels=["email", "sms"]
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    # In a real implementation, you'd generate a proper JWT token
    # For testing, we'll use a mock token
    return {"Authorization": f"Bearer mock-jwt-token-{test_user.id}"}

@pytest.fixture
def admin_headers(test_admin_user):
    """Create authentication headers for admin user"""
    return {"Authorization": f"Bearer mock-admin-jwt-token-{test_admin_user.id}"}
