"""
Utility functions for topic-related operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.utils.logger_setup import get_logger
from app.repositories.prompt_template_repository import PromptTemplateRepository

logger = get_logger(__name__)


def get_topic_id_from_agent_id(
    bot_id: str,
    friendship_level: str,
    db: Session
) -> Optional[str]:
    """
    Lấy topic_id từ agent_id bằng cách query bảng agenda_agent_prompting.
    
    Args:
        bot_id: Bot/Agent identifier (e.g., "agent_story_telling")
        friendship_level: Friendship level của user (e.g., "PHASE1_STRANGER")
        db: Database session để query từ DB (required)
        
    Returns:
        topic_id nếu tìm thấy trong DB, None nếu không tìm thấy
    """
    if not db:
        logger.error(
            f"get_topic_id_from_agent_id: db session is required for agent_id='{bot_id}'"
        )
        return None
    
    if not friendship_level:
        logger.error(
            f"get_topic_id_from_agent_id: friendship_level is required for agent_id='{bot_id}'"
        )
        return None
    
    try:
        prompt_repo = PromptTemplateRepository(db)
        topic_id = prompt_repo.get_topic_id_by_agent_id(
            agent_id=bot_id,
            friendship_level=friendship_level
        )
        if topic_id:
            logger.debug(
                f"get_topic_id_from_agent_id: Found topic_id='{topic_id}' "
                f"from DB for agent_id='{bot_id}', friendship_level='{friendship_level}'"
            )
        else:
            logger.warning(
                f"get_topic_id_from_agent_id: No topic_id found in DB "
                f"for agent_id='{bot_id}', friendship_level='{friendship_level}'"
            )
        return topic_id
    except Exception as e:
        logger.error(
            f"get_topic_id_from_agent_id: Failed to query DB for agent_id='{bot_id}': {e}",
            exc_info=True
        )
        return None


def extract_topic_id_from_bot_id(bot_id: str) -> Optional[str]:
    """
    Extract topic_id from bot_id.
    
    Examples:
        - "talk_movie_preference" -> "movie"
        - "talk_dreams" -> "dreams"
        - "greeting_welcome" -> "greeting"
        - "game_20questions" -> "game"
        - "agent_sport" -> "sport"
    
    Args:
        bot_id: Bot identifier (e.g., "talk_movie_preference", "agent_sport")
        
    Returns:
        Topic ID extracted from bot_id, or None if cannot extract
    """
    if not bot_id:
        logger.debug("extract_topic_id_from_bot_id: bot_id is empty")
        return None
    
    # Remove prefix (talk_, greeting_, game_, agent_)
    parts = bot_id.split("_", 1)
    if len(parts) > 1:
        # Return the part after prefix (e.g., "movie_preference" -> "movie", "sport" -> "sport")
        # For simplicity, take first meaningful word after prefix
        topic_part = parts[1]
        # If it contains underscore, take first part (e.g., "movie_preference" -> "movie")
        if "_" in topic_part:
            topic_part = topic_part.split("_")[0]
        
        logger.debug(f"extract_topic_id_from_bot_id: '{bot_id}' -> '{topic_part}'")
        return topic_part
    
    # If no underscore, return as-is (fallback)
    logger.debug(f"extract_topic_id_from_bot_id: '{bot_id}' -> '{bot_id}' (no underscore, fallback)")
    return bot_id

