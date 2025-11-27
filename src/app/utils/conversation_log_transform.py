"""
Conversation log transformation utilities.

Converts conversation logs from API format to standardized format.
"""
from typing import Any, Dict, List
from datetime import datetime
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


def transform_conversation_logs(
    conversation_logs: List[Dict[str, Any]],
    start_time: datetime,
    end_time: datetime,
) -> List[Dict[str, Any]]:
    """
    Transform conversation logs from API format to standardized format.
    
    API Format (Input):
    [
        {"character": "BOT_RESPONSE_CONVERSATION", "content": "Hello!"},
        {"character": "USER_RESPONSE_CONVERSATION", "content": "Hi there!"}
    ]
    
    Standard Format (Output):
    [
        {"speaker": "pika", "turn_id": 1, "text": "Hello!", "timestamp": "..."},
        {"speaker": "user", "turn_id": 2, "text": "Hi there!", "timestamp": "..."}
    ]
    
    Args:
        conversation_logs: List of conversation log items in API format
        start_time: Conversation start timestamp (for calculating turn timestamps)
        end_time: Conversation end timestamp (for calculating turn timestamps)
        
    Returns:
        List of conversation log items in standardized format
    """
    if not conversation_logs:
        logger.warning("Empty conversation_logs provided, returning empty list")
        return []
    
    transformed = []
    total_turns = len(conversation_logs)
    duration_seconds = int((end_time - start_time).total_seconds())
    
    # Calculate time increment per turn (for timestamp estimation)
    time_increment = duration_seconds / max(total_turns, 1) if total_turns > 0 else 0
    
    for index, log_item in enumerate(conversation_logs):
        # Extract character and content
        character = log_item.get("character", "").strip()
        content = log_item.get("content", "").strip()
        
        # Skip empty content
        if not content:
            logger.debug(f"Skipping empty log item at index {index}")
            continue
        
        # Map character to speaker
        speaker = _map_character_to_speaker(character)
        
        # Calculate turn_id (1-indexed)
        turn_id = len(transformed) + 1
        
        # Estimate timestamp (distribute evenly across conversation duration)
        estimated_timestamp = start_time
        if total_turns > 1:
            from datetime import timedelta
            time_offset = timedelta(seconds=int(time_increment * index))
            estimated_timestamp = start_time + time_offset
        
        transformed_item = {
            "speaker": speaker,
            "turn_id": turn_id,
            "text": content,
            "timestamp": estimated_timestamp.isoformat() + "Z"
        }
        
        transformed.append(transformed_item)
    
    logger.info(
        f"Transformed {len(conversation_logs)} log items to {len(transformed)} standardized items"
    )
    
    return transformed


def _map_character_to_speaker(character: str) -> str:
    """
    Map API character field to standardized speaker field.
    
    Args:
        character: Character field from API (e.g., "BOT_RESPONSE_CONVERSATION")
        
    Returns:
        Standardized speaker value ("pika" or "user")
    """
    character_upper = character.upper()
    
    # Bot/Pika variations
    if "BOT" in character_upper or "PIKA" in character_upper:
        return "pika"
    
    # User variations
    if "USER" in character_upper:
        return "user"
    
    # Default fallback: assume bot if unclear
    logger.warning(
        f"Unknown character type '{character}', defaulting to 'pika'"
    )
    return "pika"


def is_api_format(logs: List[Dict[str, Any]]) -> bool:
    """
    Check if conversation logs are in API format (character/content) 
    vs standardized format (speaker/turn_id/text).
    
    Args:
        logs: List of conversation log items
        
    Returns:
        True if logs appear to be in API format, False otherwise
    """
    if not logs:
        return False
    
    first_item = logs[0]
    
    # API format has "character" and "content"
    has_character = "character" in first_item
    has_content = "content" in first_item
    
    # Standard format has "speaker", "turn_id", "text"
    has_speaker = "speaker" in first_item
    has_turn_id = "turn_id" in first_item
    has_text = "text" in first_item
    
    # If has character/content but not speaker/turn_id/text, it's API format
    if has_character and has_content and not (has_speaker and has_turn_id and has_text):
        return True
    
    # If has speaker/turn_id/text, it's already standardized
    if has_speaker and has_turn_id and has_text:
        return False
    
    # Ambiguous case: default to assuming API format if character exists
    return has_character

