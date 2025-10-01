"""
MouseAlerts API - Main FastAPI Application

This is the entry point for the MouseAlerts API server. It:
- Initializes the FastAPI application with CORS and security middleware
- Sets up Sentry monitoring for production
- Includes all API routers (auth, alerts, admin, nlu, push, billing)
- Provides health check and root endpoints
- Handles database table creation on startup

Usage: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from config import settings
from db import engine, Base
from routers import auth, alerts, admin, nlu, push, billing, worker, scraping_worker

# Initialize Sentry
if settings.APP_ENV == "production":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration(auto_enabling_instrumentations=False)],
        traces_sample_rate=0.1,
    )

# Create FastAPI app
app = FastAPI(
    title="MouseAlerts API",
    description="API for Disney dining reservation alerts",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(nlu.router, prefix="/api/nlu", tags=["nlu"])
app.include_router(push.router, prefix="/api/push", tags=["push"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(worker.router, prefix="/api/worker", tags=["worker"])
app.include_router(scraping_worker.router, prefix="/api/scraping", tags=["scraping"])

@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MouseAlerts API", "docs": "/docs"}
