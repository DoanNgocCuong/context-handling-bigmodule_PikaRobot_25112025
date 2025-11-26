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



