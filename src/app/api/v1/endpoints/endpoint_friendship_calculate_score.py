"""
API Endpoint: Calculate Friendship Score from Conversation ID.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.api.dependency_injection import get_friendship_score_calculation_service
from app.services.friendship_score_calculation_service import FriendshipScoreCalculationService
from app.schemas.conversation_schemas import (
    FriendshipScoreCalculationResponse,
    FriendshipScoreCalculationAPIResponse
)
from app.core.exceptions_custom import ConversationNotFoundError, InvalidScoreError
from app.core.status_codes import StatusCode
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/friendship_status/calculate-score/{conversation_id}",
    response_model=FriendshipScoreCalculationAPIResponse
)
async def calculate_friendship_score_from_conversation_id(
    conversation_id: str,
    service: FriendshipScoreCalculationService = Depends(get_friendship_score_calculation_service)
) -> FriendshipScoreCalculationAPIResponse:
    """
    Calculate friendship score from conversation_id.
    
    This endpoint:
    1. Validates conversation_id format
    2. Fetches conversation data by conversation_id
    3. Calculates friendship score change
    4. Returns score change and calculation details
    
    **Conversation ID Format:**
    - Pattern: `conv_<alphanumeric_with_underscore>`
    - Examples: `conv_id_2003doanngoccuong`, `conv_123456`, `conv_test_123`
    - Minimum length: 8 characters
    - Maximum length: 100 characters
    
    **Score Calculation Formula:**
    - base_score = total_turns * 0.5
    - engagement_bonus = user_initiated_questions * 3
    - emotion_bonus = mapping (interesting: +15, boring: -15, happy: +10, sad: -5, neutral: 0)
    - memory_bonus = new_memories_count * 5
    - friendship_score_change = base_score + engagement_bonus + emotion_bonus + memory_bonus
    - Result is clamped to >= 0 (never negative)
    
    Args:
        conversation_id: Unique identifier for the conversation
                        Format: conv_<alphanumeric_with_underscore>
        service: Injected friendship score calculation service
        
    Returns:
        Dictionary containing:
        - success: bool
        - data: FriendshipScoreCalculationResponse
        - message: str
        
    Raises:
        400: Invalid conversation_id format or score calculation error
        404: Conversation not found
        500: Internal server error
    """
    try:
        logger.info(f"API: Calculating friendship score for conversation_id: {conversation_id}")
        
        # Calculate score
        result = service.calculate_score_from_conversation_id(conversation_id)
        
        # Format response
        response_data = FriendshipScoreCalculationAPIResponse(
            success=True,
            data=result,
            message="Friendship score calculated successfully"
        )
        
        logger.info(
            f"Score calculation completed for conversation_id: {conversation_id}, "
            f"score_change: {result.get('friendship_score_change', 0)}"
        )
        
        return response_data
        
    except ConversationNotFoundError as e:
        logger.warning(f"Conversation not found: {conversation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": StatusCode.CONVERSATION_NOT_FOUND,
                "message": str(e)
            }
        )
    
    except InvalidScoreError as e:
        logger.error(f"Invalid score calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "INVALID_SCORE_CALCULATION",
                "message": str(e)
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error calculating score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )

