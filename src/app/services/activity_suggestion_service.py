"""
Service to provide activity suggestions (always recomputed, no cache).
"""
from sqlalchemy.orm import Session
from app.services.agent_selection_service import AgentSelectionService
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class ActivitySuggestionService:
    """Facade for retrieving activity suggestions."""

    def __init__(self, db: Session):
        self.db = db
        self.selection_service = AgentSelectionService(db)

    def get_suggestions(self, user_id: str):
        """Always compute fresh suggestions for the user."""
        logger.info("Computing activity suggestions for user %s", user_id)
        return self.selection_service.compute_candidates(user_id)






