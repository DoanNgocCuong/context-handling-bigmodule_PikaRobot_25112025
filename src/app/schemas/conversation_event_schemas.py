"""
Schemas for conversation event operations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, Field, model_validator

from app.core.constants_enums import ConversationEventStatus


class ConversationEventCreateRequest(BaseModel):
    """Request payload for creating a conversation event."""

    conversation_id: str = Field(..., min_length=3, max_length=255, description="Unique conversation identifier")
    user_id: str = Field(..., min_length=3, max_length=255, description="User identifier")
    bot_type: str = Field(..., max_length=50, description="Bot type that handled the session (accepts any string value)")
    bot_id: str = Field(..., max_length=255, description="Bot identifier")
    bot_name: str = Field(..., max_length=255, description="Human readable bot name")
    start_time: datetime = Field(..., description="Conversation start timestamp")
    end_time: datetime = Field(..., description="Conversation end timestamp")
    conversation_log: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Standardized conversation log (transformed from raw format)",
        validation_alias=AliasChoices("conversation_log", "conversation_logs"),
    )
    raw_conversation_log: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Raw conversation log in original API format (before transformation)",
    )
    status: ConversationEventStatus = Field(default=ConversationEventStatus.PENDING, description="Initial processing status")
    attempt_count: int = Field(default=0, ge=0, description="Number of processing attempts")
    next_attempt_at: Optional[datetime] = Field(default=None, description="Next scheduled processing time")
    processed_at: Optional[datetime] = Field(default=None, description="Actual processing time when completed")
    error_code: Optional[str] = Field(default=None, max_length=50, description="Error code from last failure")
    error_details: Optional[str] = Field(default=None, description="Verbose error information")
    friendship_score_change: Optional[float] = Field(default=None, description="Calculated friendship score delta")
    new_friendship_level: Optional[str] = Field(default=None, max_length=50, description="New friendship level outcome")

    @model_validator(mode="after")
    def validate_time_window(self) -> "ConversationEventCreateRequest":
        """Ensure end_time is after start_time."""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be greater than start_time")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_20251126_001",
                "user_id": "user_doanngoccuong",
                "bot_type": "TALK",
                "bot_id": "talk_movie_preference",
                "bot_name": "Movie Preference Talk",
                "start_time": "2025-11-26T10:00:00Z",
                "end_time": "2025-11-26T10:20:00Z",
                "conversation_log": [
                    {
                        "speaker": "pika",
                        "turn_id": 1,
                        "text": "Hello! Ready to talk about movies?",
                        "timestamp": "2025-11-26T10:00:00Z"
                    }
                ],
                "status": "PENDING"
            }
        }


class ConversationEventData(BaseModel):
    """Serialized conversation event record."""

    id: int
    conversation_id: str
    user_id: str
    bot_type: str
    bot_id: str
    bot_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    conversation_log: List[Dict[str, Any]]
    raw_conversation_log: Optional[List[Dict[str, Any]]]
    status: ConversationEventStatus
    attempt_count: int
    created_at: datetime
    next_attempt_at: datetime
    processed_at: Optional[datetime]
    error_code: Optional[str]
    error_details: Optional[str]
    friendship_score_change: Optional[float]
    new_friendship_level: Optional[str]
    score_calculation_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed breakdown of friendship score calculation"
    )
    updated_at: datetime


class ConversationEventCreateResponse(BaseModel):
    """API response for conversation event creation."""

    success: bool = Field(True, description="Operation status flag")
    message: str = Field(..., description="Human readable status message")
    data: ConversationEventData = Field(..., description="Stored event payload")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Conversation event stored",
                "data": {
                    "id": 1,
                    "conversation_id": "conv_20251126_001",
                    "user_id": "user_doanngoccuong",
                    "bot_type": "TALK",
                    "bot_id": "talk_movie_preference",
                    "bot_name": "Movie Preference Talk",
                    "start_time": "2025-11-26T10:00:00Z",
                    "end_time": "2025-11-26T10:20:00Z",
                    "duration_seconds": 1200,
                    "conversation_log": [
                        {
                            "speaker": "pika",
                            "turn_id": 1,
                            "text": "Hello! Ready to talk about movies?",
                            "timestamp": "2025-11-26T10:00:00Z"
                        }
                    ],
                    "raw_conversation_log": [
                        {
                            "character": "BOT_RESPONSE_CONVERSATION",
                            "content": "Hello! Ready to talk about movies?"
                        }
                    ],
                    "status": "PENDING",
                    "attempt_count": 0,
                    "created_at": "2025-11-26T10:20:01Z",
                    "next_attempt_at": "2025-11-26T16:20:01Z",
                    "processed_at": None,
                    "error_code": None,
                    "error_details": None,
                    "friendship_score_change": None,
                    "new_friendship_level": None,
                    "updated_at": "2025-11-26T10:20:01Z"
                }
            }
        }


