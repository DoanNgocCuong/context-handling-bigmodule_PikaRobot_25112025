"""
Repository helpers for prompt template tables.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.prompt_template_model import (
    PromptTemplateForLevelFriend,
    PromptTemplateForLevelFriendship,
)


class PromptTemplateRepository:
    """Encapsulate access to prompt template tables."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Persona templates per phase
    # ------------------------------------------------------------------
    def get_persona_by_phase(self, friendship_level: str) -> Optional[PromptTemplateForLevelFriend]:
        """Return persona template for a phase."""
        return (
            self.db.query(PromptTemplateForLevelFriend)
            .filter(PromptTemplateForLevelFriend.friendship_level == friendship_level)
            .first()
        )

    # ------------------------------------------------------------------
    # Prompt guides per topic/phase/type
    # ------------------------------------------------------------------
    def get_guides(
        self,
        *,
        friendship_level: str,
        agent_type: str,
        topic_id: Optional[str] = None,
    ) -> List[PromptTemplateForLevelFriendship]:
        """Return guides filtered by phase, type and optional topic."""
        query = self.db.query(PromptTemplateForLevelFriendship).filter(
            PromptTemplateForLevelFriendship.friendship_level == friendship_level,
            PromptTemplateForLevelFriendship.agent_type == agent_type,
        )
        if topic_id:
            query = query.filter(PromptTemplateForLevelFriendship.topic_id == topic_id)
        return query.all()

    def get_guide_by_topic_agent_phase(
        self,
        *,
        topic_id: str,
        agent_id: str,
        friendship_level: str,
    ) -> Optional[PromptTemplateForLevelFriendship]:
        """Return single guide by topic/agent/phase."""
        return (
            self.db.query(PromptTemplateForLevelFriendship)
            .filter(
                PromptTemplateForLevelFriendship.topic_id == topic_id,
                PromptTemplateForLevelFriendship.agent_id == agent_id,
                PromptTemplateForLevelFriendship.friendship_level == friendship_level,
            )
            .first()
        )

