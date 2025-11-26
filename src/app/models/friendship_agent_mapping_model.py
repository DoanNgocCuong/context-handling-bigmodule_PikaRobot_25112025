"""
FriendshipAgentMapping ORM model.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func, UniqueConstraint
from app.db.database_connection import Base


class FriendshipAgentMapping(Base):
    """SQLAlchemy model for friendship_agent_mapping table."""
    __tablename__ = "friendship_agent_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    friendship_level = Column(String(50), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    agent_id = Column(String(255), nullable=False)
    agent_name = Column(String(255), nullable=False)
    agent_description = Column(String, nullable=True)
    weight = Column(Float, nullable=False, default=1.0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("friendship_level", "agent_type", "agent_id", name="uq_level_type_agent"),
    )

