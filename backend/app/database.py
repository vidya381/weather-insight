"""
Database Configuration
SQLAlchemy setup and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
# For development, we'll use regular SQLAlchemy (not async for simplicity)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True to see SQL queries (useful for debugging)
)

# Create SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session
    Use with FastAPI Depends()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    Base.metadata.create_all(bind=engine)
