"""
MouseAlerts API - Database Configuration

This module handles all database-related setup:
- Creates SQLAlchemy engine with connection pooling
- Sets up session factory for database operations
- Defines the declarative base for all models
- Provides get_db() dependency for FastAPI route injection
- Provides transaction context manager for consistent error handling

The database connection uses PostgreSQL with psycopg2 driver.
Connection pooling is configured for production reliability.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import settings

# Create database engine
# Using psycopg2-binary which works with standard postgresql:// URLs
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.APP_ENV == "dev"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_transaction(db: Session):
    """
    Context manager for database transactions.
    Automatically commits on success and rolls back on error.
    
    Usage:
        with db_transaction(db) as session:
            session.add(new_object)
            # Automatically commits if no exception
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
