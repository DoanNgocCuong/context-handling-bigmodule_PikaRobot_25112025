"""
Constants and Enums for the application.
"""
from enum import Enum


class FriendshipLevel(str, Enum):
    """Friendship level enumeration."""
    STRANGER = "STRANGER"
    ACQUAINTANCE = "ACQUAINTANCE"
    FRIEND = "FRIEND"


class AgentType(str, Enum):
    """Agent type enumeration."""
    GREETING = "GREETING"
    TALK = "TALK"
    GAME_ACTIVITY = "GAME_ACTIVITY"


class ConversationEventStatus(str, Enum):
    """Status values for conversation_events processing."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Score thresholds for friendship levels
FRIENDSHIP_SCORE_THRESHOLDS = {
    FriendshipLevel.STRANGER: (0, 500),
    FriendshipLevel.ACQUAINTANCE: (500, 3000),
    FriendshipLevel.FRIEND: (3000, float('inf'))
}

# Default values
DEFAULT_FRIENDSHIP_SCORE = 0.0
DEFAULT_FRIENDSHIP_LEVEL = FriendshipLevel.STRANGER
DEFAULT_STREAK_DAY = 0
DEFAULT_TOPIC_METRICS = {}

# Cache TTL (in seconds)
CACHE_TTL_CANDIDATES = 21600  # 6 hours
CACHE_TTL_DEFAULT = 3600  # 1 hour

# Cache key prefixes
CACHE_KEY_PREFIX_CANDIDATES = "candidates"
CACHE_KEY_PREFIX_FRIENDSHIP = "friendship"

# Conversation event processing defaults
# CONVERSATION_EVENT_RETRY_MINUTES = 1/60  # retry after 1 minute
CONVERSATION_EVENT_RETRY_HOURS = 6  # retry after 6 hours



