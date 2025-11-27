"""
Redis-based cache manager for activity candidates.
"""
import json
from typing import Optional, Dict, Any
from app.cache.redis_cache_manager import get_redis_client
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)

DEFAULT_TTL_SECONDS = 86400  # 24 hours


class CandidatesCacheManager:
    """Manage caching of activity suggestions."""

    def __init__(self):
        self.redis = get_redis_client()

    def _build_key(self, user_id: str) -> str:
        return f"candidates:{user_id}"

    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return cached candidates if available."""
        if not self.redis:
            return None
        key = self._build_key(user_id)
        cached = self.redis.get(key)
        if not cached:
            return None
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in cache for key %s", key)
            self.redis.delete(key)
            return None

    def set(self, user_id: str, payload: Dict[str, Any], ttl: int = DEFAULT_TTL_SECONDS):
        """Store candidates in cache."""
        if not self.redis:
            return
        key = self._build_key(user_id)
        self.redis.setex(key, ttl, json.dumps(payload))

    def invalidate(self, user_id: str):
        """Delete cached candidates."""
        if not self.redis:
            return
        key = self._build_key(user_id)
        self.redis.delete(key)






