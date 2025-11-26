"""
API Endpoint: Get Conversation Data by ID (Mock API).

This is a mock API that returns sample conversation data.
Later, this will be replaced with real API call to BE.
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, Any
from app.schemas.conversation_schemas import ConversationResponse
from app.core.exceptions_custom import ConversationNotFoundError
from app.core.status_codes import StatusCode
from app.utils.logger_setup import get_logger
from app.utils.input_validators import validate_conversation_id

logger = get_logger(__name__)

router = APIRouter()


def _generate_mock_conversation_data(conversation_id: str) -> Dict[str, Any]:
    """
    Generate mock conversation data for testing.
    
    This function creates sample conversation data based on conversation_id.
    In production, this will be replaced with actual database/API call.
    
    Args:
        conversation_id: Conversation ID
        
    Returns:
        Dictionary with conversation data
    """
    # Generate different sample data based on conversation_id
    base_time = datetime.utcnow() - timedelta(hours=1)
    
    # Sample conversation logs
    conversation_logs = {
        "conv_id_2003doanngoccuong": [
            {
                "speaker": "pika",
                "turn_id": 1,
                "text": "Hi! What's your favorite movie genre?",
                "timestamp": base_time.isoformat() + "Z"
            },
            {
                "speaker": "user",
                "turn_id": 2,
                "text": "I love animated movies, especially Miyazaki films!",
                "timestamp": (base_time + timedelta(seconds=15)).isoformat() + "Z"
            },
            {
                "speaker": "pika",
                "turn_id": 3,
                "text": "Miyazaki is amazing! Which is your favorite?",
                "timestamp": (base_time + timedelta(seconds=30)).isoformat() + "Z"
            },
            {
                "speaker": "user",
                "turn_id": 4,
                "text": "Spirited Away! The animation is incredible.",
                "timestamp": (base_time + timedelta(seconds=45)).isoformat() + "Z"
            },
            {
                "speaker": "pika",
                "turn_id": 5,
                "text": "Spirited Away is a masterpiece! Have you watched Howl's Moving Castle?",
                "timestamp": (base_time + timedelta(seconds=60)).isoformat() + "Z"
            },
            {
                "speaker": "user",
                "turn_id": 6,
                "text": "Yes! That's my second favorite. The music is beautiful.",
                "timestamp": (base_time + timedelta(seconds=75)).isoformat() + "Z"
            }
        ],
        "conv_test_123": [
            {
                "speaker": "pika",
                "turn_id": 1,
                "text": "Hello! How are you today?",
                "timestamp": base_time.isoformat() + "Z"
            },
            {
                "speaker": "user",
                "turn_id": 2,
                "text": "I'm doing great! Thanks for asking.",
                "timestamp": (base_time + timedelta(seconds=10)).isoformat() + "Z"
            },
            {
                "speaker": "pika",
                "turn_id": 3,
                "text": "That's wonderful! What did you do today?",
                "timestamp": (base_time + timedelta(seconds=25)).isoformat() + "Z"
            }
        ]
    }
    
    # Default conversation log if ID not in mapping
    default_log = conversation_logs.get(
        conversation_id,
        [
            {
                "speaker": "pika",
                "turn_id": 1,
                "text": "Hello! Nice to meet you!",
                "timestamp": base_time.isoformat() + "Z"
            },
            {
                "speaker": "user",
                "turn_id": 2,
                "text": "Hi! Nice to meet you too!",
                "timestamp": (base_time + timedelta(seconds=10)).isoformat() + "Z"
            }
        ]
    )
    
    # Sample metadata
    metadata_samples = {
        "conv_id_2003doanngoccuong": {
            "emotion": "interesting",
            "user_initiated_questions": 2,
            "pika_initiated_topics": 2,
            "new_memories_created": 1
        },
        "conv_test_123": {
            "emotion": "happy",
            "user_initiated_questions": 1,
            "pika_initiated_topics": 1,
            "new_memories_created": 0
        }
    }
    
    default_metadata = metadata_samples.get(
        conversation_id,
        {
            "emotion": "neutral",
            "user_initiated_questions": 0,
            "pika_initiated_topics": 1,
            "new_memories_created": 0
        }
    )
    
    # Determine agent type and ID based on conversation_id
    agent_type = "TALK"
    agent_id = "talk_movie_preference"
    
    if "greeting" in conversation_id.lower():
        agent_type = "GREETING"
        agent_id = "greeting_welcome"
    elif "game" in conversation_id.lower():
        agent_type = "GAME_ACTIVITY"
        agent_id = "game_20questions"
    
    end_time = base_time + timedelta(seconds=1200)
    
    return {
        "conversation_id": conversation_id,
        "user_id": "user_123",  # Default user_id
        "agent_id": agent_id,
        "agent_type": agent_type,
        "start_time": base_time.isoformat() + "Z",
        "end_time": end_time.isoformat() + "Z",
        "duration_seconds": 1200,
        "conversation_log": default_log,
        "metadata": default_metadata
    }


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_by_id(conversation_id: str) -> ConversationResponse:
    """
    Get conversation data by ID (Mock API).
    
    **Note:** This is a mock API for testing purposes.
    In production, this will fetch data from database or external API.
    
    **Conversation ID Format:**
    - Pattern: `conv_<alphanumeric_with_underscore>`
    - Examples: `conv_id_2003doanngoccuong`, `conv_123456`, `conv_test_123`
    
    Args:
        conversation_id: Unique identifier for the conversation
        
    Returns:
        ConversationResponse with conversation data
        
    Raises:
        400: Invalid conversation_id format
        404: Conversation not found
    """
    try:
        # Validate conversation_id format
        validated_id = validate_conversation_id(conversation_id)
        
        logger.info(f"API: Fetching conversation data for conversation_id: {validated_id}")
        
        # Generate mock data
        # TODO: Replace with actual database/API call
        mock_data = _generate_mock_conversation_data(validated_id)
        
        # Convert to response model
        response = ConversationResponse(**mock_data)
        
        logger.info(f"Successfully fetched conversation: {validated_id}")
        
        return response
        
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
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        )

