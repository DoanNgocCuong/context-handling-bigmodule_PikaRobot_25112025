"""
Input validation utilities.
"""
import re
from typing import Optional
from app.core.exceptions_custom import InvalidUserIdError

# Conversation ID pattern: conv_<alphanumeric_with_underscore>
CONVERSATION_ID_PATTERN = re.compile(r'^conv_[a-zA-Z0-9_]+$')
CONVERSATION_ID_MIN_LENGTH = 8  # conv_ + at least 3 chars
CONVERSATION_ID_MAX_LENGTH = 100


def validate_conversation_id(conversation_id: str) -> str:
    """
    Validate conversation_id format.
    
    Format: conv_<alphanumeric_with_underscore>
    Examples:
    - conv_id_2003doanngoccuong ✅
    - conv_123456 ✅
    - conv_test_123 ✅
    - conv-invalid ❌ (no hyphen)
    - abc123 ❌ (missing prefix)
    
    Args:
        conversation_id: Conversation ID to validate
        
    Returns:
        Validated conversation_id
        
    Raises:
        InvalidUserIdError: If format is invalid
    """
    if not conversation_id:
        raise InvalidUserIdError("Conversation ID cannot be empty")
    
    if not isinstance(conversation_id, str):
        raise InvalidUserIdError(f"Conversation ID must be a string, got {type(conversation_id)}")
    
    # Check length
    if len(conversation_id) < CONVERSATION_ID_MIN_LENGTH:
        raise InvalidUserIdError(
            f"Conversation ID too short. Minimum length: {CONVERSATION_ID_MIN_LENGTH}"
        )
    
    if len(conversation_id) > CONVERSATION_ID_MAX_LENGTH:
        raise InvalidUserIdError(
            f"Conversation ID too long. Maximum length: {CONVERSATION_ID_MAX_LENGTH}"
        )
    
    # Check pattern
    if not CONVERSATION_ID_PATTERN.match(conversation_id):
        raise InvalidUserIdError(
            f"Invalid conversation_id format: {conversation_id}. "
            f"Expected format: conv_<alphanumeric_with_underscore>"
        )
    
    return conversation_id

