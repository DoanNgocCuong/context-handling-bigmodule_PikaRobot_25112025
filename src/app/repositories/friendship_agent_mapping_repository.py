"""
Repository for friendship_agent_mapping table.
"""
from typing import List
from sqlalchemy.orm import Session
from app.models.friendship_agent_mapping_model import FriendshipAgentMapping


class FriendshipAgentMappingRepository:
    """Data access for agent mappings."""

    def __init__(self, db: Session):
        self.db = db
        self.model = FriendshipAgentMapping

    def get_by_level_and_type(self, friendship_level: str, agent_type: str) -> List[FriendshipAgentMapping]:
        """Return active agents filtered by level and type."""
        return (
            self.db.query(self.model)
            .filter(
                self.model.friendship_level == friendship_level,
                self.model.agent_type == agent_type,
                self.model.is_active.is_(True),
            )
            .all()
        )

    def get_all_active(self) -> List[FriendshipAgentMapping]:
        """Return all active agents."""
        return (
            self.db.query(self.model)
            .filter(self.model.is_active.is_(True))
            .all()
        )





