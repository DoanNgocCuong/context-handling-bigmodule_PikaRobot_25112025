"\"\"
Service for updating friendship status in database.
\"\"\"
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.friendship_status_repository import FriendshipStatusRepository
from app.core.exceptions_custom import FriendshipNotFoundError


class FriendshipStatusUpdateService:
    \"\"\"Apply score changes and fetch friendship status records.\"\"\"

    def __init__(self, db: Session):
        self.db = db
        self.repository = FriendshipStatusRepository(db)

    def apply_score_change(self, user_id: str, score_change: float) -> Dict[str, Any]:
        \"\"\"Apply score change and return serialized record.\"\"\"
        status = self.repository.apply_score_change(
            user_id=user_id,
            score_change=score_change,
            last_interaction_date=datetime.utcnow(),
        )
        return self._serialize(status)

    def get_status(self, user_id: str) -> Dict[str, Any]:
        \"\"\"Get friendship status for user.\"\"\"
        status = self.repository.get_by_user_id(user_id)
        if not status:
            raise FriendshipNotFoundError(f\"Friendship status not found for user {user_id}\")
        return self._serialize(status)

    @staticmethod
    def _serialize(status) -> Dict[str, Any]:
        \"\"\"Serialize SQLAlchemy model to dict.\"\"\"
        return {
            \"user_id\": status.user_id,
            \"friendship_score\": status.friendship_score,
            \"friendship_level\": status.friendship_level,
            \"last_interaction_date\": status.last_interaction_date.isoformat() if status.last_interaction_date else None,
            \"streak_day\": status.streak_day,
            \"topic_metrics\": status.topic_metrics or {},
        }

