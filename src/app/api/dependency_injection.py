"""
Dependency injection setup for FastAPI.
"""
from sqlalchemy.orm import Session
from app.db.database_connection import SessionLocal


def get_db() -> Session:
    """
    Get database session dependency.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


