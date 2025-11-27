"""
Redis cache manager for caching operations.
"""
import redis
from typing import Optional
from app.core.config_settings import settings
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client instance (singleton pattern).
    
    Returns:
        Optional[redis.Redis]: Redis client instance or None if connection fails
    """
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        redis_url = settings.REDIS_URL
        if not redis_url:
            logger.warning("REDIS_URL not configured")
            return None
        
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Test connection
        _redis_client.ping()
        logger.info("Redis client connected successfully")
        
        return _redis_client
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        _redis_client = None
        return None


def close_redis_client():
    """Close Redis client connection."""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")








