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
from app.services.conversation_data_fetch_service import ConversationDataFetchService
from app.services.conversation_event_processing_service import (
    ConversationEventProcessingService,
)
from app.services.friendship_score_calculation_service import (
    FriendshipScoreCalculationService,
)
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.utils.logger_setup import get_logger
from app.utils.conversation_log_transform import (
    transform_conversation_logs,
    is_api_format,
)

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
        
        # Transform conversation_logs if in API format
        raw_logs = payload.get("conversation_log") or []
        
        # Store raw data before transformation
        if raw_logs and is_api_format(raw_logs):
            logger.info(
                f"Detected API format conversation_logs, transforming to standardized format "
                f"for conversation_id={request.conversation_id}"
            )
            # Save raw format to raw_conversation_log
            payload["raw_conversation_log"] = raw_logs
            # Transform to standardized format
            payload["conversation_log"] = transform_conversation_logs(
                conversation_logs=raw_logs,
                start_time=request.start_time,
                end_time=request.end_time,
            )
        else:
            # If already in standard format, keep as-is
            payload["conversation_log"] = raw_logs
            # If raw_conversation_log was provided, use it; otherwise set to None
            if "raw_conversation_log" not in payload:
                payload["raw_conversation_log"] = None
        
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

        # Immediately trigger processing for this single event (primary path).
        try:
            conversation_fetch_service = ConversationDataFetchService(
                conversation_repository=None,
                external_api_client=None,
            )
            score_service = FriendshipScoreCalculationService(
                conversation_fetch_service=conversation_fetch_service
            )
            status_service = FriendshipStatusUpdateService(self.db)
            processor = ConversationEventProcessingService(
                db=self.db,
                score_service=score_service,
                status_update_service=status_service,
            )
            processor.process_single_event(event.id)
        except Exception as exc:  # pragma: no cover - defensive
            # Do not fail API; fallback scheduler will retry pending events.
            logger.error(
                "Immediate processing for conversation_id=%s failed: %s",
                event.conversation_id,
                exc,
                exc_info=True,
            )

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
            "raw_conversation_log": event.raw_conversation_log,
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

