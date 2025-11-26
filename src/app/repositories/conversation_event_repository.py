"""
Repository for conversation_events table.
"""
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.conversation_event_model import ConversationEvent


class ConversationEventRepository:
    """Data access helpers for conversation_events."""

    def __init__(self, db: Session):
        self.db = db
        self.model = ConversationEvent

    def get_by_conversation_id(self, conversation_id: str) -> Optional[ConversationEvent]:
        """Return event by unique conversation_id."""
        return (
            self.db.query(self.model)
            .filter(self.model.conversation_id == conversation_id)
            .first()
        )

    def create(self, payload: Dict[str, Any]) -> ConversationEvent:
        """Persist a new event record."""
        event = self.model(**payload)
        self.db.add(event)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(event)
        return event


