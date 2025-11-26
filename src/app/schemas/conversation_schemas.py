"""
Pydantic Schemas for Conversation Data.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class ConversationLogItem(BaseModel):
    """Schema for a single conversation log item."""
    speaker: Literal["pika", "user"] = Field(..., description="Speaker: pika or user")
    turn_id: int = Field(..., description="Turn number in conversation", ge=1)
    text: str = Field(..., description="Message content", min_length=1)
    timestamp: datetime = Field(..., description="Message timestamp (ISO 8601)")

    class Config:
        json_schema_extra = {
            "example": {
                "speaker": "pika",
                "turn_id": 1,
                "text": "Hi! What's your favorite movie genre?",
                "timestamp": "2025-11-25T18:00:00Z"
            }
        }


class ConversationMetadata(BaseModel):
    """Schema for conversation metadata."""
    emotion: Literal["interesting", "boring", "happy", "sad", "neutral", "angry"] = Field(
        default="neutral",
        description="Session emotion"
    )
    user_initiated_questions: int = Field(
        default=0,
        description="Number of questions user initiated",
        ge=0
    )
    pika_initiated_topics: int = Field(
        default=0,
        description="Number of topics Pika initiated",
        ge=0
    )
    new_memories_created: int = Field(
        default=0,
        description="Number of new memories created",
        ge=0
    )
    
    # Optional fields (có thể có thêm)
    session_emotion: Optional[str] = Field(
        default=None,
        description="Alternative emotion field name"
    )
    new_memories_count: Optional[int] = Field(
        default=None,
        description="Alternative new memories field name",
        ge=0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "emotion": "interesting",
                "user_initiated_questions": 2,
                "pika_initiated_topics": 2,
                "new_memories_created": 1
            }
        }


class ConversationResponse(BaseModel):
    """Schema for GET /conversations/{conversation_id} response."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="User identifier")
    agent_id: str = Field(..., description="Agent identifier used in conversation")
    agent_type: Literal["GREETING", "TALK", "GAME_ACTIVITY"] = Field(
        ...,
        description="Type of agent"
    )
    start_time: datetime = Field(..., description="Conversation start time (ISO 8601)")
    end_time: datetime = Field(..., description="Conversation end time (ISO 8601)")
    duration_seconds: int = Field(..., description="Conversation duration in seconds", ge=0)
    conversation_log: List[ConversationLogItem] = Field(
        ...,
        description="List of conversation turns",
        min_items=1
    )
    metadata: ConversationMetadata = Field(..., description="Conversation metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_id_2003doanngoccuong",
                "user_id": "user_123",
                "agent_id": "talk_movie_preference",
                "agent_type": "TALK",
                "start_time": "2025-11-25T18:00:00Z",
                "end_time": "2025-11-25T18:20:00Z",
                "duration_seconds": 1200,
                "conversation_log": [
                    {
                        "speaker": "pika",
                        "turn_id": 1,
                        "text": "Hi! What's your favorite movie genre?",
                        "timestamp": "2025-11-25T18:00:00Z"
                    },
                    {
                        "speaker": "user",
                        "turn_id": 2,
                        "text": "I love animated movies!",
                        "timestamp": "2025-11-25T18:00:15Z"
                    }
                ],
                "metadata": {
                    "emotion": "interesting",
                    "user_initiated_questions": 2,
                    "pika_initiated_topics": 2,
                    "new_memories_created": 1
                }
            }
        }


class FriendshipScoreCalculationDetails(BaseModel):
    """Schema for friendship score calculation breakdown."""
    total_turns: int = Field(..., description="Total number of conversation turns")
    user_initiated_questions: int = Field(..., description="Number of user-initiated questions")
    session_emotion: str = Field(..., description="Session emotion")
    new_memories_count: int = Field(..., description="Number of new memories")
    base_score: float = Field(..., description="Base score (turns * 0.5)")
    engagement_bonus: float = Field(..., description="Engagement bonus (questions * 3)")
    emotion_bonus: float = Field(..., description="Emotion bonus")
    memory_bonus: float = Field(..., description="Memory bonus (memories * 5)")
    total_score_before_clamp: float = Field(..., description="Total score before clamping to 0")
    final_score_change: float = Field(..., description="Final score change (>= 0)")


class FriendshipScoreCalculationResponse(BaseModel):
    """Schema for friendship score calculation response."""
    friendship_score_change: float = Field(..., description="Friendship score change", ge=0)
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    calculation_details: FriendshipScoreCalculationDetails = Field(
        ...,
        description="Detailed calculation breakdown"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "friendship_score_change": 29.0,
                "conversation_id": "conv_id_2003doanngoccuong",
                "user_id": "user_123",
                "calculation_details": {
                    "total_turns": 6,
                    "user_initiated_questions": 2,
                    "session_emotion": "interesting",
                    "new_memories_count": 1,
                    "base_score": 3.0,
                    "engagement_bonus": 6.0,
                    "emotion_bonus": 15.0,
                    "memory_bonus": 5.0,
                    "total_score_before_clamp": 29.0,
                    "final_score_change": 29.0
                }
            }
        }


class FriendshipScoreCalculationAPIResponse(BaseModel):
    """API response schema for friendship score calculation endpoint."""
    success: bool = Field(True, description="Operation success status")
    data: FriendshipScoreCalculationResponse = Field(..., description="Calculation result data")
    message: str = Field(..., description="Response message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "friendship_score_change": 29,
                    "conversation_id": "conv_id_2003doanngoccuong",
                    "user_id": "user_123",
                    "calculation_details": {
                        "total_turns": 6,
                        "user_initiated_questions": 2,
                        "session_emotion": "interesting",
                        "new_memories_count": 1,
                        "base_score": 3,
                        "engagement_bonus": 6,
                        "emotion_bonus": 15,
                        "memory_bonus": 5,
                        "total_score_before_clamp": 29,
                        "final_score_change": 29
                    }
                },
                "message": "Friendship score calculated successfully"
            }
        }

