"""
Service layer for conversation event operations.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from zoneinfo import ZoneInfo

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
from app.utils.color_log import success, error, warning, info, key_value
from app.utils.conversation_log_transform import (
    transform_conversation_logs,
    is_api_format,
)

logger = get_logger(__name__)


def _generate_timestamp_suffix() -> str:
    """
    Generate timestamp suffix in format _YYYYMMDD_HHMMSS.
    Sử dụng múi giờ Hà Nội, Việt Nam (UTC+7).
    
    Returns:
        String suffix like "_20251128_032315" (theo giờ Việt Nam)
    """
    # Sử dụng múi giờ Hà Nội, Việt Nam (Asia/Ho_Chi_Minh = UTC+7)
    vietnam_tz = ZoneInfo("Asia/Ho_Chi_Minh")
    now = datetime.now(vietnam_tz)
    return now.strftime("_%Y%m%d_%H%M%S")


class ConversationEventService:
    """Orchestrates validation and persistence for conversation events."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ConversationEventRepository(db)

    def create_event(self, request: ConversationEventCreateRequest) -> Dict[str, Any]:
        """
        Store a new conversation event.
        
        Nếu conversation_id đã tồn tại, tự động thêm suffix timestamp (_YYYYMMDD_HHMMSS)
        và retry insert với conversation_id mới.

        Raises:
            ConversationEventValidationError: If business validation fails.
        """
        duration_seconds = int((request.end_time - request.start_time).total_seconds())
        if duration_seconds <= 0:
            raise ConversationEventValidationError("Conversation duration must be greater than 0 seconds")

        # Kiểm tra và xử lý duplicate conversation_id
        original_conversation_id = request.conversation_id
        current_conversation_id = original_conversation_id
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            # Kiểm tra conversation_id đã tồn tại chưa
            if self.repository.get_by_conversation_id(current_conversation_id):
                retry_count += 1
                if retry_count >= max_retries:
                    # Nếu đã retry quá nhiều lần, log warning và raise error
                    logger.warning(
                        f"{warning('⚠️')} Failed to generate unique conversation_id after {max_retries} attempts | "
                        f"{key_value('original_id', original_conversation_id)} | "
                        f"{key_value('last_tried', current_conversation_id)}"
                    )
                    raise ConversationEventAlreadyExistsError(
                        f"Conversation event already exists and cannot generate unique ID after {max_retries} retries. "
                        f"Original conversation_id={original_conversation_id}"
                    )
                
                # Generate suffix và append vào conversation_id
                suffix = _generate_timestamp_suffix()
                current_conversation_id = f"{original_conversation_id}{suffix}"
                logger.info(
                    f"{info('🔄')} Conversation_id already exists, generating new ID | "
                    f"{key_value('original', original_conversation_id)} | "
                    f"{key_value('new_id', current_conversation_id)} | "
                    f"{key_value('retry', f'{retry_count}/{max_retries}')}"
                )
            else:
                # conversation_id chưa tồn tại, có thể dùng
                break
        
        # Nếu conversation_id đã thay đổi, cập nhật vào request
        if current_conversation_id != original_conversation_id:
            logger.info(
                f"{success('✅')} Using modified conversation_id | "
                f"{key_value('original', original_conversation_id)} | "
                f"{key_value('final', current_conversation_id)}"
            )
            # Tạo request mới với conversation_id đã được modify
            request_dict = request.model_dump()
            request_dict["conversation_id"] = current_conversation_id
            request = ConversationEventCreateRequest(**request_dict)

        payload = request.model_dump(mode="json")
        payload.pop("duration_seconds", None)
        
        # Transform conversation_logs if in API format
        raw_logs = payload.get("conversation_log") or []
        
        # Debug: Log raw logs trước khi transform
        if raw_logs:
            bot_count = sum(1 for item in raw_logs if "BOT" in str(item.get("character", "")).upper())
            user_count = sum(1 for item in raw_logs if "USER" in str(item.get("character", "")).upper())
            logger.info(
                f"📥 {info('Raw conversation_logs received')} | "
                f"{key_value('conversation_id', request.conversation_id)} | "
                f"{key_value('total', str(len(raw_logs)))} | "
                f"{key_value('BOT', str(bot_count))} | "
                f"{key_value('USER', str(user_count))}"
            )
        
        # Store raw data before transformation
        if raw_logs and is_api_format(raw_logs):
            logger.info(
                f"🔄 Detected API format, transforming to standardized format | "
                f"conversation_id={request.conversation_id}"
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
            # Nếu vẫn bị IntegrityError (race condition), thử lại với suffix mới
            failed_conversation_id = payload.get("conversation_id", current_conversation_id)
            logger.warning(
                f"{warning('⚠️')} IntegrityError detected (race condition) | "
                f"{key_value('conversation_id', failed_conversation_id)} | "
                f"{key_value('error', str(exc))}"
            )
            
            # Retry một lần nữa với suffix mới
            suffix = _generate_timestamp_suffix()
            new_conversation_id = f"{original_conversation_id}{suffix}"
            payload["conversation_id"] = new_conversation_id
            
            logger.info(
                f"{info('🔄')} Retrying with new conversation_id after IntegrityError | "
                f"{key_value('failed_id', failed_conversation_id)} | "
                f"{key_value('new_id', new_conversation_id)}"
            )
            
            try:
                event = self.repository.create(payload)
            except IntegrityError as retry_exc:
                logger.error(
                    f"{error('❌')} Still duplicate after retry | "
                    f"{key_value('conversation_id', new_conversation_id)}"
                )
                raise ConversationEventAlreadyExistsError(
                    f"Conversation event already exists for conversation_id={new_conversation_id} "
                    f"(original: {original_conversation_id})"
                ) from retry_exc

        logger.info(
            f"{success('✅')} Conversation event stored | "
            f"{key_value('conversation_id', event.conversation_id)} | "
            f"{key_value('original_id', original_conversation_id if event.conversation_id != original_conversation_id else 'same')}"
        )

        # NOTE: Immediate processing removed - events will be processed by RabbitMQ worker
        # Background scheduler will still retry failed events as fallback

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
            "agent_tag": event.agent_tag if hasattr(event, 'agent_tag') else None,  # ADDED: agent_tag for topic mapping
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
            "score_calculation_details": event.score_calculation_details,
            "updated_at": event.updated_at,
        }

