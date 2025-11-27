"""
FriendshipStatus ORM model.
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database_connection import Base


class FriendshipStatus(Base):
    """SQLAlchemy model for friendship_status table."""

    __tablename__ = "friendship_status"

    user_id = Column(String(255), primary_key=True, index=True)
    friendship_score = Column(Float, nullable=False, default=0.0)
    friendship_level = Column(String(50), nullable=False, default="PHASE1_STRANGER")
    last_interaction_date = Column(DateTime(timezone=True), nullable=True)
    streak_day = Column(Integer, nullable=False, default=0)
    topic_metrics = Column(JSONB, nullable=False, default=dict)
    last_emotion = Column(String(50), nullable=True)
    last_followup_topic = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # ------------------------------------------------------------------
    # Backwards compatibility helpers
    # ------------------------------------------------------------------
