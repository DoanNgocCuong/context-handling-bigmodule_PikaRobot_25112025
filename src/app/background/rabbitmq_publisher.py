"""
RabbitMQ Publisher for conversation events.

Publishes conversation events to RabbitMQ queue for asynchronous processing.
"""
import json
import pika
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.config_settings import settings
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class RabbitMQConfig:
    """RabbitMQ configuration."""
    
    @staticmethod
    def get_host() -> str:
        """Get RabbitMQ host."""
        if settings.RABBITMQ_HOST:
            return settings.RABBITMQ_HOST
        # Parse from URL if available
        if settings.RABBITMQ_URL and "@" in settings.RABBITMQ_URL:
            # Extract host from amqp://user:pass@host:port/
            parts = settings.RABBITMQ_URL.split("@")
            if len(parts) > 1:
                host_part = parts[1].split(":")[0].split("/")[0]
                return host_part
        return "localhost"
    
    @staticmethod
    def get_port() -> int:
        """Get RabbitMQ port."""
        if settings.RABBITMQ_PORT:
            return settings.RABBITMQ_PORT
        # Parse from URL if available
        if settings.RABBITMQ_URL and ":" in settings.RABBITMQ_URL:
            try:
                parts = settings.RABBITMQ_URL.split(":")
                if len(parts) >= 3:
                    port_str = parts[2].split("/")[0]
                    return int(port_str)
            except (ValueError, IndexError):
                pass
        return 5672
    
    @staticmethod
    def get_username() -> str:
        """Get RabbitMQ username."""
        if settings.RABBITMQ_USERNAME:
            return settings.RABBITMQ_USERNAME
        # Parse from URL if available
        if settings.RABBITMQ_URL and "://" in settings.RABBITMQ_URL:
            try:
                parts = settings.RABBITMQ_URL.split("://")[1].split("@")[0]
                if ":" in parts:
                    return parts.split(":")[0]
            except (IndexError, ValueError):
                pass
        return "guest"
    
    @staticmethod
    def get_password() -> str:
        """Get RabbitMQ password."""
        if settings.RABBITMQ_PASSWORD:
            return settings.RABBITMQ_PASSWORD
        # Parse from URL if available
        if settings.RABBITMQ_URL and "://" in settings.RABBITMQ_URL:
            try:
                parts = settings.RABBITMQ_URL.split("://")[1].split("@")[0]
                if ":" in parts:
                    return parts.split(":")[1]
            except (IndexError, ValueError):
                pass
        return "guest"
    
    QUEUE_NAME = settings.RABBITMQ_QUEUE_NAME
    EXCHANGE_NAME = settings.RABBITMQ_EXCHANGE_NAME
    ROUTING_KEY = settings.RABBITMQ_ROUTING_KEY


class RabbitMQPublisher:
    """RabbitMQ publisher for conversation events."""
    
    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self._connect()
    
    def _connect(self):
        """Connect to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                RabbitMQConfig.get_username(),
                RabbitMQConfig.get_password()
            )
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RabbitMQConfig.get_host(),
                    port=RabbitMQConfig.get_port(),
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=2
                )
            )
            
            self.channel = self.connection.channel()
            
            # Check if queue exists first (passive=True)
            try:
                self.channel.queue_declare(
                    queue=RabbitMQConfig.QUEUE_NAME,
                    passive=True  # Only check if queue exists, don't create
                )
                logger.info(f"✅ Queue '{RabbitMQConfig.QUEUE_NAME}' already exists")
            except (pika.exceptions.ChannelClosedByBroker, pika.exceptions.ChannelClosed):
                # Queue doesn't exist, create it with arguments
                logger.info(f"📝 Creating queue '{RabbitMQConfig.QUEUE_NAME}' with arguments")
                # Reopen channel after error
                if self.connection and not self.connection.is_closed:
                    self.channel = self.connection.channel()
                else:
                    self._connect()  # Reconnect if connection closed
                    return  # _connect will be called recursively, so return here
                
                self.channel.queue_declare(
                    queue=RabbitMQConfig.QUEUE_NAME,
                    durable=True,
                    arguments={
                        'x-message-ttl': 86400000,  # 24 hours
                        'x-max-length': 100000  # Max 100k messages
                    }
                )
            
            logger.info(
                f"✅ Connected to RabbitMQ at {RabbitMQConfig.get_host()}:{RabbitMQConfig.get_port()}"
            )
        
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}", exc_info=True)
            raise
    
    def publish(self, message: Dict[str, Any]):
        """
        Publish message to queue.
        
        Args:
            message: Dictionary containing conversation event data
        """
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            
            self.channel.basic_publish(
                exchange='',
                routing_key=RabbitMQConfig.QUEUE_NAME,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json',
                    timestamp=int(datetime.utcnow().timestamp())
                )
            )
            
            logger.info(
                f"📤 Published message to queue '{RabbitMQConfig.QUEUE_NAME}': "
                f"conversation_id={message.get('conversation_id')}"
            )
        
        except Exception as e:
            logger.error(f"❌ Failed to publish message: {str(e)}", exc_info=True)
            raise
    
    def close(self):
        """Close connection."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("🔌 Closed RabbitMQ connection")
        except Exception as e:
            logger.warning(f"Error closing RabbitMQ connection: {str(e)}")


# Singleton instance
_publisher: Optional[RabbitMQPublisher] = None


def get_publisher() -> RabbitMQPublisher:
    """Get singleton RabbitMQ publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
    return _publisher


async def publish_conversation_event(
    conversation_id: str,
    user_id: str,
    bot_id: str,
    conversation_log: list
):
    """
    Publish conversation event to RabbitMQ queue.
    
    Args:
        conversation_id: Unique conversation identifier
        user_id: User identifier
        bot_id: Bot identifier
        conversation_log: Conversation log data
    """
    try:
        publisher = get_publisher()
        
        message = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "bot_id": bot_id,
            "conversation_log": conversation_log,
            "enqueued_at": datetime.utcnow().isoformat()
        }
        
        publisher.publish(message)
        
    except Exception as e:
        logger.error(
            f"❌ Failed to publish conversation event {conversation_id}: {str(e)}",
            exc_info=True
        )
        # Don't raise - allow API to return 202 even if publish fails
        # Background scheduler will retry pending events
