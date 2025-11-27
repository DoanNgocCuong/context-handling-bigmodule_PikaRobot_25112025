"""
API Endpoint: Suggest activities (greeting + talk + game agents).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.api.dependency_injection import get_activity_suggestion_service
from app.services.activity_suggestion_service import ActivitySuggestionService
from app.core.exceptions_custom import FriendshipNotFoundError, AgentSelectionError
from app.schemas.activity_suggestion_schemas import ActivitySuggestionResponse


class ActivitySuggestionRequest(BaseModel):
    """Request schema for activities suggestion."""
    user_id: str = Field(..., description="User ID to fetch suggestions for")


router = APIRouter()


@router.post(
    "/activities/suggest",
    response_model=ActivitySuggestionResponse,
)
async def suggest_activities(
    request: ActivitySuggestionRequest,
    service: ActivitySuggestionService = Depends(get_activity_suggestion_service)
) -> ActivitySuggestionResponse:
    """
    Suggest greeting + talk + game agents for given user.
    """
    try:
        data = service.get_suggestions(request.user_id)
        return ActivitySuggestionResponse(
            success=True,
            data=data,
            message="Activities suggested successfully"
        )
    except FriendshipNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "PHASE3_FRIENDSHIP_NOT_FOUND",
                "message": f"Friendship status not found for user {request.user_id}"
            }
        )
    except AgentSelectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "AGENT_NOT_FOUND",
                "message": str(exc)
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc)
            }
        )

