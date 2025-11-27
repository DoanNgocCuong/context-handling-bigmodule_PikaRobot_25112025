"""
Repository for conversation_events table.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants_enums import (
    CONVERSATION_EVENT_RETRY_HOURS,
    ConversationEventStatus,
)
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

    def get_by_id(self, event_id: int) -> Optional[ConversationEvent]:
        """Return event by primary key ID."""
        return self.db.get(self.model, event_id)

    def fetch_due_events(self, batch_size: int = 25) -> List[ConversationEvent]:
        """Return pending/failed events whose next_attempt_at has arrived."""
        now = datetime.now(timezone.utc)
        return (
            self.db.query(self.model)
            .filter(
                self.model.status.in_(
                    [
                        ConversationEventStatus.PENDING.value,
                        ConversationEventStatus.FAILED.value,
                    ]
                )
            )
            .filter(self.model.next_attempt_at <= now)
            .order_by(self.model.next_attempt_at.asc())
            .limit(batch_size)
            .all()
        )

    def mark_processing(self, event: ConversationEvent) -> ConversationEvent:
        """Set status to PROCESSING and increment attempt counter."""
        event.status = ConversationEventStatus.PROCESSING.value
        event.attempt_count = (event.attempt_count or 0) + 1
        event.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_processed(
        self,
        event: ConversationEvent,
        friendship_score_change: float,
        friendship_level: str,
        score_calculation_details: Optional[Dict[str, Any]] = None,
    ) -> ConversationEvent:
        """
        Set status to PROCESSED with processing metadata.
        
        Args:
            event: ConversationEvent to update
            friendship_score_change: Final score change
            friendship_level: New friendship level
            score_calculation_details: Optional detailed breakdown of score calculation
        """
        event.status = ConversationEventStatus.PROCESSED.value
        event.friendship_score_change = friendship_score_change
        event.new_friendship_level = friendship_level
        
        # CRITICAL: SQLAlchemy không detect in-place changes trong JSONB
        # Phải gán lại object và flag_modified để force SQLAlchemy detect changes
        event.score_calculation_details = score_calculation_details
        if score_calculation_details is not None:
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(event, "score_calculation_details")
        
        event.processed_at = datetime.now(timezone.utc)
        event.error_code = None
        event.error_details = None
        event.next_attempt_at = event.processed_at
        event.updated_at = event.processed_at
        self.db.commit()
        self.db.refresh(event)
        return event

    def mark_failed(
        self,
        event: ConversationEvent,
        error_code: str,
        error_details: str,
    ) -> ConversationEvent:
        """Set status to FAILED and schedule retry."""
        event.status = ConversationEventStatus.FAILED.value
        event.error_code = error_code
        event.error_details = error_details
        retry_at = datetime.now(timezone.utc) + timedelta(hours=CONVERSATION_EVENT_RETRY_HOURS)
        event.next_attempt_at = retry_at
        event.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(event)
        return event


