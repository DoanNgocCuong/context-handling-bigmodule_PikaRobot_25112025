"""
In-memory Friendship Status Store Service.

This service is a placeholder that simulates friendship status updates
without an actual database. It keeps data in-memory for demo/testing purposes.
"""
from typing import Dict, Any
from threading import Lock
from app.core.constants_enums import FriendshipLevel, PHASE3_FRIENDSHIP_SCORE_THRESHOLDS
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class FriendshipStatusStoreService:
    """Simple in-memory store for friendship status."""
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def get_status(self, user_id: str) -> Dict[str, Any]:
        """Get friendship status for user."""
        with self._lock:
            return self._store.get(user_id) or self._create_default_status(user_id)
    
    def apply_score_change(self, user_id: str, score_change: float) -> Dict[str, Any]:
        """Apply score change to user and update friendship level."""
        with self._lock:
            status = self._store.get(user_id)
            if not status:
                status = self._create_default_status(user_id)
            
            status["friendship_score"] = max(0.0, status["friendship_score"] + score_change)
            status["friendship_level"] = self._determine_level(status["friendship_score"])
            status["last_score_change"] = score_change
            
            self._store[user_id] = status
            logger.info(
                "Updated friendship status store",
                extra={
                    "user_id": user_id,
                    "friendship_score": status["friendship_score"],
                    "friendship_level": status["friendship_level"]
                }
            )
            return status
    
    def _create_default_status(self, user_id: str) -> Dict[str, Any]:
        """Create default status for new user."""
        status = {
            "user_id": user_id,
            "friendship_score": 0.0,
            "friendship_level": FriendshipLevel.PHASE1_STRANGER,
            "last_score_change": 0.0
        }
        self._store[user_id] = status
        return status
    
    def _determine_level(self, score: float) -> FriendshipLevel:
        """Determine friendship level based on score thresholds."""
        if score >= PHASE3_FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.PHASE3_FRIEND][0]:
            return FriendshipLevel.PHASE3_FRIEND
        if score >= PHASE3_FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.PHASE2_ACQUAINTANCE][0]:
            return FriendshipLevel.PHASE2_ACQUAINTANCE
        return FriendshipLevel.PHASE1_STRANGER

