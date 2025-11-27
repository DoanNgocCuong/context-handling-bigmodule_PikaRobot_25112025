"""
Service for updating friendship status in database.
"""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.friendship_status_repository import FriendshipStatusRepository
from app.core.exceptions_custom import FriendshipNotFoundError


class FriendshipStatusUpdateService:
    """Apply score changes and fetch friendship status records."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = FriendshipStatusRepository(db)

    def apply_score_change(self, user_id: str, score_change: float) -> Dict[str, Any]:
        """Apply score change and return serialized record."""
        status = self.repository.apply_score_change(
            user_id=user_id,
            score_change=score_change,
            last_interaction_date=datetime.utcnow(),
        )
        return self._serialize(status)

    def get_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get friendship status for user.
        
        If user doesn't exist, creates a default record automatically.
        
        Args:
            user_id: User ID to get status for
            
        Returns:
            Dictionary with friendship status
            
        Raises:
            Exception: If creation fails (e.g., DB error)
        """
        try:
            status = self.repository.get_by_user_id(user_id)
            if not status:
                # Auto-create default record for new user
                from app.utils.logger_setup import get_logger
                logger = get_logger(__name__)
                logger.info(f"🆕 Creating default friendship status for new user: {user_id}")
                try:
                    status = self.repository.create_default(user_id)
                    logger.info(f"✅ Successfully created friendship status for user: {user_id}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to create default friendship status for user {user_id}: {e}",
                        exc_info=True
                    )
                    # Re-raise to let caller handle
                    raise
            return self._serialize(status)
        except Exception as e:
            from app.utils.logger_setup import get_logger
            logger = get_logger(__name__)
            logger.error(
                f"❌ Error in get_status for user {user_id}: {e}",
                exc_info=True
            )
            raise

    def update_topic_metrics(
        self,
        user_id: str,
        topic_id: str,
        score_change: float,
        bot_id: str,
        turns_change: int = 1
    ) -> Dict[str, Any]:
        """
        Cập nhật topic_metrics trong bảng friendship_status.
        
        Args:
            user_id: User ID
            topic_id: Topic identifier (e.g., "movie", "dreams")
            score_change: Score change to add to topic
            bot_id: Bot identifier used in this conversation
            turns_change: Number of turns to add (default: 1)
            
        Returns:
            Dictionary containing updated topic_metrics entry
        """
        updated_topic = self.repository.update_topic_metrics(
            user_id=user_id,
            topic_id=topic_id,
            score_change=score_change,
            bot_id=bot_id,
            turns_change=turns_change
        )
        return updated_topic
    
    @staticmethod
    def _serialize(status) -> Dict[str, Any]:
        """Serialize SQLAlchemy model to dict."""
        return {
            "user_id": status.user_id,
            "friendship_score": status.friendship_score,
            "friendship_level": status.friendship_level,
            "last_interaction_date": status.last_interaction_date.isoformat() if status.last_interaction_date else None,
            "streak_day": status.streak_day,
            "topic_metrics": status.topic_metrics or {},
        }

