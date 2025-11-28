"""
Utility functions for topic-related operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.utils.logger_setup import get_logger
from app.repositories.prompt_template_repository import PromptTemplateRepository

logger = get_logger(__name__)


def get_topic_id_from_agent_id(
    *,
    agent_tag: str,
    friendship_level: str,
    db: Session
) -> Optional[str]:
    """
    Lấy topic_id từ agent_id bằng cách query bảng agenda_agent_prompting.
    
    Args:
        agent_tag: Agent identifier sent from BE (e.g., "agent_story_telling")
        friendship_level: Friendship level của user (e.g., "PHASE1_STRANGER")
        db: Database session để query từ DB (required)
        
    Returns:
        topic_id nếu tìm thấy trong DB, None nếu không tìm thấy
    """
    if not db:
        logger.error(
            f"get_topic_id_from_agent_id: db session is required for agent_id='{agent_tag}'"
        )
        return None
    
    if not friendship_level:
        logger.error(
            f"get_topic_id_from_agent_id: friendship_level is required for agent_id='{agent_tag}'"
        )
        return None
    
    try:
        prompt_repo = PromptTemplateRepository(db)
        topic_id = prompt_repo.get_topic_id_by_agent_id(
            agent_id=agent_tag,
            friendship_level=friendship_level
        )
        if topic_id:
            logger.debug(
                f"get_topic_id_from_agent_id: Found topic_id='{topic_id}' "
                f"from DB for agent_id='{agent_tag}', friendship_level='{friendship_level}'"
            )
        else:
            logger.warning(
                f"get_topic_id_from_agent_id: No topic_id found in DB "
                f"for agent_id='{agent_tag}', friendship_level='{friendship_level}'"
            )
        return topic_id
    except Exception as e:
        logger.error(
            f"get_topic_id_from_agent_id: Failed to query DB for agent_id='{agent_tag}': {e}",
            exc_info=True
        )
        return None

