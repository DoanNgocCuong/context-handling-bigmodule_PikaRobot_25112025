"""
Repository for friendship_status table.
"""
from typing import Optional, Dict, Any
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
        # Lấy friendship_status hiện tại
        friendship = self.get_by_user_id(user_id)
        if not friendship:
            friendship = self.create_default(user_id)
        
        # Lấy topic_metrics JSONB
        topic_metrics = friendship.topic_metrics or {}
        
        # Nếu topic chưa tồn tại, tạo mới
        if topic_id not in topic_metrics:
            topic_metrics[topic_id] = {
                "score": 0.0,
                "turns": 0,
                "friendship_level": FriendshipLevel.PHASE1_STRANGER.value,
                "last_date": None,
                "agents_used": []
            }
        
        # Cập nhật score và turns
        topic_metrics[topic_id]["score"] = float(topic_metrics[topic_id].get("score", 0.0)) + score_change
        topic_metrics[topic_id]["turns"] = int(topic_metrics[topic_id].get("turns", 0)) + turns_change
        topic_metrics[topic_id]["last_date"] = datetime.utcnow().isoformat() + "Z"
        
        # Thêm bot_id vào agents_used (nếu chưa có)
        agents_used = topic_metrics[topic_id].get("agents_used", [])
        if bot_id not in agents_used:
            agents_used.append(bot_id)
        topic_metrics[topic_id]["agents_used"] = agents_used
        
        # Cập nhật friendship_score chung TRƯỚC để tính friendship_level_of_user chính xác
        old_score = friendship.friendship_score or 0.0
        friendship.friendship_score = max(0.0, old_score + score_change)
        friendship.friendship_level = self._determine_level(friendship.friendship_score).value
        
        # Nâng cấp level cho topic dựa trên logic:
        # - Topic lên PHASE2 nếu: topic_score >= 50 AND friendship_level_of_user >= PHASE2
        # - Topic lên PHASE3 nếu: topic_score >= 150 AND friendship_level_of_user >= PHASE3
        topic_score = topic_metrics[topic_id]["score"]
        # friendship_level_of_user = friendship.friendship_level (đã được cập nhật ở trên)
        friendship_level_of_user = FriendshipLevel(friendship.friendship_level)
        
        current_topic_level = topic_metrics[topic_id].get("friendship_level", FriendshipLevel.PHASE1_STRANGER.value)
        new_topic_level = self._determine_topic_level(topic_score, friendship_level_of_user, current_topic_level)
        topic_metrics[topic_id]["friendship_level"] = new_topic_level.value
        
        # CRITICAL: SQLAlchemy không detect in-place changes trong JSONB
        # Phải gán lại object và flag_modified để force SQLAlchemy detect changes
        friendship.topic_metrics = topic_metrics
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(friendship, "topic_metrics")
        
        friendship.last_interaction_date = datetime.utcnow()
        
        from app.utils.logger_setup import get_logger
        logger = get_logger(__name__)
        logger.info(
            f"📊 Updating topic_metrics for user_id={user_id}, topic_id={topic_id}:\n"
            f"   - Topic score: {topic_score} (was {topic_score - score_change})\n"
            f"   - Topic turns: {topic_metrics[topic_id]['turns']}\n"
            f"   - Topic level: {current_topic_level} -> {new_topic_level.value}\n"
            f"   - User friendship_score: {old_score} -> {friendship.friendship_score}\n"
            f"   - User friendship_level: {friendship.friendship_level}\n"
            f"   - topic_metrics keys: {list(topic_metrics.keys())}"
        )
        
        self.db.commit()
        self.db.refresh(friendship)
        
        logger.info(
            f"✅ topic_metrics updated successfully. Final topic_metrics: {friendship.topic_metrics}"
        )
        
        return topic_metrics[topic_id]
    
    def _determine_topic_level(
        self,
        topic_score: float,
        friendship_level_of_user: FriendshipLevel,
        current_topic_level: str
    ) -> FriendshipLevel:
        """
        Xác định level cho topic dựa trên topic_score và friendship_level_of_user.
        
        Logic:
        - Topic lên PHASE2 nếu: topic_score >= 50 AND friendship_level_of_user >= PHASE2
        - Topic lên PHASE3 nếu: topic_score >= 150 AND friendship_level_of_user >= PHASE3
        
        Args:
            topic_score: Score của topic
            friendship_level_of_user: Level hiện tại của user (friendship level)
            current_topic_level: Level hiện tại của topic (string)
            
        Returns:
            FriendshipLevel mới cho topic
        """
        current_level_enum = FriendshipLevel(current_topic_level) if current_topic_level else FriendshipLevel.PHASE1_STRANGER
        
        # Topic lên PHASE3 nếu: topic_score >= 150 AND friendship_level_of_user >= PHASE3
        if topic_score >= 150.0 and friendship_level_of_user >= FriendshipLevel.PHASE3_FRIEND:
            return FriendshipLevel.PHASE3_FRIEND
        
        # Topic lên PHASE2 nếu: topic_score >= 50 AND friendship_level_of_user >= PHASE2
        if topic_score >= 50.0 and friendship_level_of_user >= FriendshipLevel.PHASE2_ACQUAINTANCE:
            # Nếu đã là PHASE3, giữ nguyên
            if current_level_enum == FriendshipLevel.PHASE3_FRIEND:
                return FriendshipLevel.PHASE3_FRIEND
            return FriendshipLevel.PHASE2_ACQUAINTANCE
        
        # Nếu không đủ điều kiện, giữ nguyên level hiện tại hoặc về PHASE1
        if topic_score < 50.0:
            return FriendshipLevel.PHASE1_STRANGER
        
        # Giữ nguyên level hiện tại nếu không đủ điều kiện nâng cấp
        return current_level_enum

