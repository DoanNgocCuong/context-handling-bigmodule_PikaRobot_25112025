"""
Service layer for conversation event operations.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants_enums import (
    CONVERSATION_EVENT_RETRY_HOURS,
    ConversationEventStatus,
)
from app.core.exceptions_custom import (
    ConversationEventAlreadyExistsError,
    ConversationEventValidationError,
)
from app.repositories.conversation_event_repository import ConversationEventRepository
from app.schemas.conversation_event_schemas import ConversationEventCreateRequest
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class ConversationEventService:
    """Orchestrates validation and persistence for conversation events."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ConversationEventRepository(db)

    def create_event(self, request: ConversationEventCreateRequest) -> Dict[str, Any]:
        """
        Store a new conversation event.

        Raises:
            ConversationEventAlreadyExistsError: If conversation_id already stored.
            ConversationEventValidationError: If business validation fails.
        """
        if self.repository.get_by_conversation_id(request.conversation_id):
            raise ConversationEventAlreadyExistsError(
                f"Conversation event already exists for conversation_id={request.conversation_id}"
            )

        duration_seconds = int((request.end_time - request.start_time).total_seconds())
        if duration_seconds <= 0:
            raise ConversationEventValidationError("Conversation duration must be greater than 0 seconds")

        payload = request.model_dump(mode="json")
        payload.pop("duration_seconds", None)
        payload["conversation_log"] = payload.get("conversation_log") or []
        payload["status"] = payload.get("status") or ConversationEventStatus.PENDING.value
        payload["next_attempt_at"] = payload.get("next_attempt_at") or (
            datetime.now(timezone.utc) + timedelta(hours=CONVERSATION_EVENT_RETRY_HOURS)
        )

        try:
            event = self.repository.create(payload)
        except IntegrityError as exc:
            logger.warning("Duplicate conversation event detected: %s", exc)
            raise ConversationEventAlreadyExistsError(
                f"Conversation event already exists for conversation_id={request.conversation_id}"
            ) from exc

        logger.info("Conversation event stored for conversation_id=%s", event.conversation_id)
        return self._serialize(event)

    @staticmethod
    def _serialize(event) -> Dict[str, Any]:
        """Convert ORM model to serializable dict."""
        return {
            "id": event.id,
            "conversation_id": event.conversation_id,
            "user_id": event.user_id,
            "bot_type": event.bot_type,
            "bot_id": event.bot_id,
            "bot_name": event.bot_name,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "duration_seconds": event.duration_seconds,
            "conversation_log": event.conversation_log or [],
            "status": event.status,
            "attempt_count": event.attempt_count,
            "created_at": event.created_at,
            "next_attempt_at": event.next_attempt_at,
            "processed_at": event.processed_at,
            "error_code": event.error_code,
            "error_details": event.error_details,
            "friendship_score_change": event.friendship_score_change,
            "new_friendship_level": event.new_friendship_level,
            "updated_at": event.updated_at,
        }

