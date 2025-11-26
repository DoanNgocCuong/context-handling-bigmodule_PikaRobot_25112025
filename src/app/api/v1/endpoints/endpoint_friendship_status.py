"""
API Endpoints: Friendship Status operations (calculate & update).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.api.dependency_injection import (
    get_friendship_score_calculation_service,
    get_friendship_status_update_service
)
from app.services.friendship_score_calculation_service import FriendshipScoreCalculationService
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.core.exceptions_custom import ConversationNotFoundError, InvalidScoreError
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)

router = APIRouter()


class FriendshipScoreUpdateRequest(BaseModel):
    """Request schema for calculate-score-and-update endpoint."""
    user_id: str = Field(..., description="User ID to apply score change")
    conversation_id: str = Field(..., description="Conversation ID to compute score from")


@router.post("/friendship_status/calculate-score-and-update")
async def calculate_and_update_friendship_status_route(
    request: FriendshipScoreUpdateRequest,
    score_service: FriendshipScoreCalculationService = Depends(get_friendship_score_calculation_service),
    update_service: FriendshipStatusUpdateService = Depends(get_friendship_status_update_service)
) -> Dict[str, Any]:
    """
    Calculate score from conversation_id and immediately update friendship status for the user.
    """
    try:
        # Step 1: Calculate score change from conversation
        result = score_service.calculate_score_from_conversation_id(request.conversation_id)
        score_change = result.get("friendship_score_change", 0.0)
        
        # Step 2: Apply score change to user (in-memory store for demo)
        updated_status = update_service.apply_score_change(request.user_id, score_change)
        
        response = {
            "success": True,
            "data": {
                "calculation_result": result,
                "updated_status": updated_status
            },
            "message": "Friendship score calculated and status updated successfully"
        }
        return response
    
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "CONVERSATION_NOT_FOUND",
                "message": str(e)
            }
        )
    except InvalidScoreError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "INVALID_SCORE_CALCULATION",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in calculate-score-and-update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )

