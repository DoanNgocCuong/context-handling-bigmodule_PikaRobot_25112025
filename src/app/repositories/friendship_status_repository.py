"""
Repository for friendship_status table.
"""
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.friendship_status_model import FriendshipStatus
from app.core.constants_enums import FriendshipLevel, PHASE3_FRIENDSHIP_SCORE_THRESHOLDS
from app.core.exceptions_custom import FriendshipNotFoundError


class FriendshipStatusRepository:
    """Data access layer for friendship_status."""

    def __init__(self, db: Session):
        self.db = db
        self.model = FriendshipStatus

    def get_by_user_id(self, user_id: str) -> Optional[FriendshipStatus]:
        """Fetch friendship status by user_id."""
        return (
            self.db.query(self.model)
            .filter(self.model.user_id == user_id)
            .first()
        )

    def create_default(self, user_id: str) -> FriendshipStatus:
        """Create default friendship status for new user."""
        status = self.model(
            user_id=user_id,
            friendship_score=0.0,
            friendship_level=FriendshipLevel.PHASE1_STRANGER.value,
            streak_day=0,
            topic_metrics={},
            last_interaction_date=datetime.utcnow(),
        )
        self.db.add(status)
        self.db.commit()
        self.db.refresh(status)
        return status

    def apply_score_change(
        self,
        user_id: str,
        score_change: float,
        last_interaction_date: Optional[datetime] = None,
    ) -> FriendshipStatus:
        """Apply score change to user and update friendship level."""
        status = self.get_by_user_id(user_id)
        if not status:
            status = self.create_default(user_id)

        status.friendship_score = max(0.0, (status.friendship_score or 0.0) + score_change)
        status.friendship_level = self._determine_level(status.friendship_score).value
        status.last_interaction_date = last_interaction_date or datetime.utcnow()
        self.db.commit()
        self.db.refresh(status)
        return status

    def _determine_level(self, score: float) -> FriendshipLevel:
        """Determine friendship level from score thresholds."""
        if score >= PHASE3_FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.PHASE3_FRIEND][0]:
            return FriendshipLevel.PHASE3_FRIEND
        if score >= PHASE3_FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.PHASE2_ACQUAINTANCE][0]:
            return FriendshipLevel.PHASE2_ACQUAINTANCE
        return FriendshipLevel.PHASE1_STRANGER

