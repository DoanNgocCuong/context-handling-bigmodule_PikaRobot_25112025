"""
Dependency injection setup for FastAPI.
"""
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.database_connection import SessionLocal
from app.services.friendship_score_calculation_service import FriendshipScoreCalculationService
from app.services.conversation_data_fetch_service import ConversationDataFetchService
from app.services.friendship_status_store_service import FriendshipStatusStoreService
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


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


@lru_cache()
def get_conversation_repository():
    """
    Get conversation repository instance.
    
    TODO: Uncomment when Conversation model is created
    from app.repositories.conversation_repository import ConversationRepository
    from app.models.conversation_model import Conversation
    
    db = next(get_db())
    return ConversationRepository(db=db, conversation_model=Conversation)
    """
    return None  # Placeholder until model is created


@lru_cache()
def get_conversation_fetch_service():
    """
    Get conversation fetch service instance.
    
    This service can fetch from:
    - Database repository (if available)
    - External API client (if available)
    - Mock data (for testing)
    """
    repository = get_conversation_repository()
    # external_api_client = get_external_api_client()  # Add if external API is needed
    
    return ConversationDataFetchService(
        conversation_repository=repository,
        external_api_client=None  # Add if external API is needed
    )


@lru_cache()
def get_friendship_score_calculation_service():
    """
    Get friendship score calculation service instance.
    
    This service calculates friendship score from conversation data.
    """
    conversation_fetch_service = get_conversation_fetch_service()
    return FriendshipScoreCalculationService(
        conversation_fetch_service=conversation_fetch_service
    )


@lru_cache()
def get_friendship_status_store_service():
    """
    Get friendship status store service instance.
    
    This is an in-memory store used for demo purposes.
    """
    return FriendshipStatusStoreService()


def get_friendship_status_update_service(
    db: Session = Depends(get_db),
) -> FriendshipStatusUpdateService:
    """
    Get friendship status update service (database-backed).
    """
    return FriendshipStatusUpdateService(db)


