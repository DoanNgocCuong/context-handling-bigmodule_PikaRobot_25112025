"""
HTTP status codes and error messages.
"""
from typing import Dict

# HTTP Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_503_SERVICE_UNAVAILABLE = 503

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "USER_NOT_FOUND": "User not found",
    "INVALID_USER_ID": "Invalid user_id format",
    "FRIENDSHIP_NOT_FOUND": "Friendship status not found",
    "CONVERSATION_NOT_FOUND": "Conversation not found",
    "CONVERSATION_EVENT_EXISTS": "Conversation event already exists",
    "CONVERSATION_EVENT_INVALID": "Conversation event payload invalid",
    "AGENT_NOT_FOUND": "Agent not found",
    "INVALID_SCORE": "Invalid score value",
    "DATABASE_ERROR": "Database connection error",
    "CACHE_ERROR": "Cache connection error",
    "QUEUE_ERROR": "Message queue connection error",
    "INTERNAL_ERROR": "Internal server error",
}


# Status Code Constants (for use in API responses)
class StatusCode:
    """Status code constants for API responses."""
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_USER_ID = "INVALID_USER_ID"
    FRIENDSHIP_NOT_FOUND = "FRIENDSHIP_NOT_FOUND"
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    CONVERSATION_EVENT_EXISTS = "CONVERSATION_EVENT_EXISTS"
    CONVERSATION_EVENT_INVALID = "CONVERSATION_EVENT_INVALID"
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    INVALID_SCORE = "INVALID_SCORE"
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    QUEUE_ERROR = "QUEUE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


