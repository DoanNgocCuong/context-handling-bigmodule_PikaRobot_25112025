"""
API Endpoint: Store conversation end events.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependency_injection import get_conversation_event_service
from app.core.exceptions_custom import (
    ConversationEventAlreadyExistsError,
    ConversationEventValidationError,
)
from app.core.status_codes import StatusCode
from app.schemas.conversation_event_schemas import (
    ConversationEventCreateRequest,
    ConversationEventCreateResponse,
)
from app.services.conversation_event_service import ConversationEventService
from app.background.rabbitmq_publisher import publish_conversation_event
from app.utils.logger_setup import get_logger
from app.utils.color_log import success, error, warning, info, key_value, status_code

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/conversations/end",
    response_model=ConversationEventCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Store conversation event for async processing",
)
async def create_conversation_event(
    request: ConversationEventCreateRequest,
    service: ConversationEventService = Depends(get_conversation_event_service),
) -> ConversationEventCreateResponse:
    """
    Store a conversation event that backend submits after each session.

    The record is persisted immediately, published to RabbitMQ queue,
    and will be processed asynchronously by background worker.
    
    Returns 202 Accepted immediately without waiting for processing.
    """
    conversation_id = request.conversation_id
    user_id = request.user_id
    bot_id = request.bot_id
    log_count = len(request.conversation_log) if request.conversation_log else 0
    
    # 📥 LOG: Nhận request
    logger.info(
        f"📥 POST /conversations/end | "
        f"{key_value('conversation_id', conversation_id)} | "
        f"{key_value('user_id', user_id)} | "
        f"{key_value('bot_id', bot_id)} | "
        f"{key_value('logs', f'{log_count} items')}"
    )
    
    try:
        # STEP 1: Create event (save to DB, status=PENDING)
        logger.debug(f"💾 Saving conversation event to DB: {conversation_id}")
        data = service.create_event(request)
        logger.info(
            f"{success('✅ Saved to DB')} | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('event_id', str(data.get('id')))}"
        )
        
        # STEP 2: Publish to RabbitMQ queue for async processing
        logger.debug(f"📤 Publishing to RabbitMQ queue: {conversation_id}")
        try:
            await publish_conversation_event(
                conversation_id=data["conversation_id"],
                user_id=data["user_id"],
                bot_id=data["bot_id"],
                conversation_log=data.get("conversation_log", [])
            )
            logger.info(
                f"{success('✅ Published to queue')} | "
                f"{key_value('conversation_id', conversation_id)}"
            )
        except Exception as publish_error:
            # Don't fail API if publish fails - background scheduler will retry
            logger.warning(
                f"{warning('⚠️  Failed to publish to RabbitMQ')} | "
                f"{key_value('conversation_id', conversation_id)} | "
                f"{key_value('error', str(publish_error))} | "
                f"Background scheduler will retry"
            )
        
        # STEP 3: Return 202 Accepted immediately
        logger.info(
            f"{success('✅')} {status_code(202)} Accepted | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('response_time', '<100ms (async processing)')}"
        )
        return ConversationEventCreateResponse(
            success=True,
            message="Conversation event accepted for processing",
            data=data,
        )
    except ConversationEventAlreadyExistsError as exc:
        logger.warning(
            f"{error('❌')} {status_code(409)} Conflict | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('error', 'Duplicate conversation event')}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": StatusCode.CONVERSATION_EVENT_EXISTS,
                "message": str(exc),
            },
        ) from exc
    except ConversationEventValidationError as exc:
        logger.warning(
            f"{error('❌')} {status_code(400)} Bad Request | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('error', f'Invalid payload: {str(exc)}')}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": StatusCode.CONVERSATION_EVENT_INVALID,
                "message": str(exc),
            },
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive programming
        logger.error(
            f"{error('❌')} {status_code(500)} Internal Error | "
            f"{key_value('conversation_id', conversation_id)} | "
            f"{key_value('error', str(exc))}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": StatusCode.INTERNAL_ERROR,
                "message": "Cannot store conversation event right now",
            },
        ) from exc






