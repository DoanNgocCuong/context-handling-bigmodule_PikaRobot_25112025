"""
Models storing persona and prompt templates per friendship phase/topic.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database_connection import Base


class PromptTemplateForLevelFriend(Base):
    """Persona + context template for each friendship phase."""

    __tablename__ = "prompt_template_for_level_friend"

    id = Column(Integer, primary_key=True, autoincrement=True)
    friendship_level = Column(String(50), nullable=False, unique=True, index=True)
    context_style_guideline = Column(Text, nullable=False)
    user_profile = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class PromptTemplateForLevelFriendship(Base):
    """
    Prompt agenda for a given topic/agent/phase.

    Backed by the `agenda_agent_prompting` table described in the v2 DB design.
    It maps `topic_id + friendship_level + agent_type` to a concrete agent_id
    plus the talking agenda/prompt template that should be used.
    """

    __tablename__ = "agenda_agent_prompting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(255), nullable=False, index=True)
    talking_agenda = Column(Text, nullable=False)
    friendship_level = Column(String(50), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    # Legacy tables in current DB do not have timestamps, keep columns optional.
    # Legacy schema currently doesn't have timestamps; omit to match DB.

