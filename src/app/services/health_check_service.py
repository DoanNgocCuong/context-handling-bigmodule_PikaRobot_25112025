"""
Health check service to verify service dependencies.
"""
from datetime import datetime
from typing import Dict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database_connection import SessionLocal
from app.cache.redis_cache_manager import get_redis_client
from app.core.config_settings import settings
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class HealthCheckService:
    """Service to check health of dependencies."""
    
    def __init__(self):
        self.db_status = "unknown"
        self.cache_status = "unknown"
        self.queue_status = "unknown"
    
    def check_database(self) -> str:
        """
        Check database connection.
        
        Returns:
            str: "connected" if database is accessible, "disconnected" otherwise
        """
        try:
            db: Session = SessionLocal()
            try:
                # Simple query to test connection
                db.execute(text("SELECT 1"))
                self.db_status = "connected"
                logger.debug("Database health check: connected")
                return "connected"
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                self.db_status = "disconnected"
                return "disconnected"
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            self.db_status = "disconnected"
            return "disconnected"
    
    def check_cache(self) -> str:
        """
        Check Redis cache connection.
        
        Returns:
            str: "connected" if Redis is accessible, "disconnected" otherwise
        """
        try:
            redis_client = get_redis_client()
            if redis_client:
                # Ping Redis
                redis_client.ping()
                self.cache_status = "connected"
                logger.debug("Cache health check: connected")
                return "connected"
            else:
                self.cache_status = "disconnected"
                logger.warning("Redis client not available")
                return "disconnected"
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            self.cache_status = "disconnected"
            return "disconnected"
    
    def check_queue(self) -> str:
        """
        Check RabbitMQ message queue connection.
        
        Returns:
            str: "connected" if RabbitMQ is accessible, "disconnected" or "not_configured" otherwise
        """
        try:
            import pika
            
            # Parse RabbitMQ URL
            rabbitmq_url = settings.RABBITMQ_URL
            if not rabbitmq_url:
                self.queue_status = "not_configured"
                return "not_configured"
            
            # Extract connection parameters
            from urllib.parse import urlparse
            parsed = urlparse(rabbitmq_url)
            
            credentials = pika.PlainCredentials(
                parsed.username or 'guest',
                parsed.password or 'guest'
            )
            parameters = pika.ConnectionParameters(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 5672,
                virtual_host=parsed.path.lstrip('/') or '/',
                credentials=credentials,
                connection_attempts=1,
                socket_timeout=2
            )
            
            # Try to connect
            connection = pika.BlockingConnection(parameters)
            if connection.is_open:
                connection.close()
                self.queue_status = "connected"
                logger.debug("Queue health check: connected")
                return "connected"
            else:
                self.queue_status = "disconnected"
                return "disconnected"
                
        except ImportError:
            logger.warning("pika not installed, skipping queue health check")
            self.queue_status = "not_configured"
            return "not_configured"
        except Exception as e:
            logger.error(f"Queue health check failed: {e}")
            self.queue_status = "disconnected"
            return "disconnected"
    
    def get_health_status(self) -> Dict:
        """
        Get overall health status of the service.
        
        Returns:
            Dict: Health status with all component checks
        """
        database_status = self.check_database()
        cache_status = self.check_cache()
        queue_status = self.check_queue()
        
        # Overall status
        overall_status = "ok"
        if database_status != "connected" or (cache_status != "connected" and cache_status != "not_configured"):
            overall_status = "degraded"
        if database_status == "disconnected":
            overall_status = "down"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "database": database_status,
            "cache": cache_status,
            "queue": queue_status,
            "version": getattr(settings, "PROJECT_VERSION", "1.0.0"),
            "environment": settings.ENVIRONMENT
        }

