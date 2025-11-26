"""
Custom exceptions for the application.
"""


class AppException(Exception):
    """Base exception for all application exceptions."""
    pass


class FriendshipNotFoundError(AppException):
    """Raised when friendship status not found."""
    pass


class InvalidScoreError(AppException):
    """Raised when score calculation fails."""
    pass


class AgentSelectionError(AppException):
    """Raised when agent selection fails."""
    pass


class UserNotFoundError(AppException):
    """Raised when user not found."""
    pass


class InvalidUserIdError(AppException):
    """Raised when user_id format is invalid."""
    pass


class ConversationNotFoundError(AppException):
    """Raised when conversation not found."""
    pass


class DatabaseConnectionError(AppException):
    """Raised when database connection fails."""
    pass


class CacheConnectionError(AppException):
    """Raised when cache connection fails."""
    pass


class QueueConnectionError(AppException):
    """Raised when message queue connection fails."""
    pass


