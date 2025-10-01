"""
Pytest configuration and fixtures for MouseAlerts API tests
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import app as main_app
from db import get_db, Base, engine
from models.user import User
from models.alert import Alert
from models.plan import Plan
from models.subscription import Subscription
from models.magic_link_token import MagicLinkToken
from services.admin_service import AdminService
import uuid

# Create a test-specific app without TrustedHostMiddleware
app = FastAPI(
    title="MouseAlerts API - Test",
    description="Test API for Disney dining reservation alerts",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Copy all routers from main app
from routers import auth, alerts, admin, nlu, push, billing, worker, scraping_worker, analytics
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(nlu.router, prefix="/api/nlu", tags=["nlu"])
app.include_router(push.router, prefix="/api/push", tags=["push"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(worker.router, prefix="/api/worker", tags=["worker"])
app.include_router(scraping_worker.router, prefix="/api/scraping", tags=["scraping"])
app.include_router(analytics.router, tags=["analytics"])

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MouseAlerts API", "docs": "/docs"}

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

# Authentication dependencies will be mocked in individual tests
# Override the get_current_user dependency for admin tests
from middleware.auth import get_current_user
from fastapi import HTTPException

# Global variable to store the current user for testing
_current_test_user = None

def override_get_current_user():
    """Override get_current_user dependency for testing"""
    global _current_test_user
    if _current_test_user is None:
        raise HTTPException(status_code=401, detail="No test user set")
    return _current_test_user

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def set_current_user():
    """Fixture to set the current user for testing"""
    global _current_test_user
    
    def _set_user(user):
        global _current_test_user
        _current_test_user = user
    
    def _clear_user():
        global _current_test_user
        _current_test_user = None
    
    yield _set_user
    _clear_user()

# Override settings for testing
from config import settings
settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", "test"]

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
        email=f"test-{uuid.uuid4().hex[:8]}@mousealerts.com",
        phone=f"+1555{uuid.uuid4().hex[:7]}",  # Unique phone number
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
        email=f"admin-{uuid.uuid4().hex[:8]}@mousealerts.com",  # Unique email
        phone=f"+1555{uuid.uuid4().hex[:7]}",  # Unique phone number
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
    from datetime import datetime
    
    alert = Alert(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        park="Magic Kingdom",
        restaurant="Cinderella's Royal Table",
        date=datetime(2024, 12, 25),
        time_start="18:00",
        time_end="20:00",
        party_size=4,
        status="active",
        channels={"email": True, "sms": True}
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    from jose import jwt
    from datetime import datetime, timedelta
    from config import settings
    
    # Create a real JWT token for testing
    token_data = {
        "sub": str(test_user.id),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(test_admin_user):
    """Create authentication headers for admin user"""
    return {"Authorization": f"Bearer mock-admin-jwt-token-{test_admin_user.id}"}
