"""
Service to provide activity suggestions with caching.
"""
from sqlalchemy.orm import Session
from app.services.agent_selection_service import AgentSelectionService
from app.cache.candidates_cache_manager import CandidatesCacheManager, DEFAULT_TTL_SECONDS
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class ActivitySuggestionService:
    """Facade for retrieving activity suggestions (with cache)."""

    def __init__(self, db: Session):
        self.db = db
        self.selection_service = AgentSelectionService(db)
        self.cache_manager = CandidatesCacheManager()

    def get_suggestions(self, user_id: str):
        """Return suggestion payload from cache or compute fresh."""
        cached = self.cache_manager.get(user_id)
        if cached:
            logger.info("Cache hit for user %s", user_id)
            return cached

        logger.info("Cache miss for user %s, computing suggestions", user_id)
        suggestions = self.selection_service.compute_candidates(user_id)
        self.cache_manager.set(user_id, suggestions, ttl=DEFAULT_TTL_SECONDS)
        return suggestions

