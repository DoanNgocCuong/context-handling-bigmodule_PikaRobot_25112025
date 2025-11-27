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
from app.utils.logger_setup import get_logger

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

    The record is persisted immediately and will be processed asynchronously.
    """
    try:
        data = service.create_event(request)
        return ConversationEventCreateResponse(
            success=True,
            message="Conversation event accepted for processing",
            data=data,
        )
    except ConversationEventAlreadyExistsError as exc:
        logger.warning("Duplicate conversation event: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": StatusCode.CONVERSATION_EVENT_EXISTS,
                "message": str(exc),
            },
        ) from exc
    except ConversationEventValidationError as exc:
        logger.warning("Invalid conversation event payload: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": StatusCode.CONVERSATION_EVENT_INVALID,
                "message": str(exc),
            },
        ) from exc
    except Exception as exc:  # pragma: no cover - defensive programming
        logger.error("Unexpected error while storing conversation event: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": StatusCode.INTERNAL_ERROR,
                "message": "Cannot store conversation event right now",
            },
        ) from exc






