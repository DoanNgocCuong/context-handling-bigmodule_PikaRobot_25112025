"""
RabbitMQ Consumer for conversation events.

Consumes messages from RabbitMQ queue and processes conversation events.
"""
import json
import pika
from typing import Optional
from app.core.config_settings import settings
from app.db.database_connection import SessionLocal
from app.repositories.conversation_event_repository import ConversationEventRepository
from app.services.conversation_data_fetch_service import ConversationDataFetchService
from app.services.friendship_score_calculation_service import FriendshipScoreCalculationService
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.services.conversation_event_processing_service import ConversationEventProcessingService
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class RabbitMQConfig:
    """RabbitMQ configuration (same as publisher)."""
    
    @staticmethod
    def get_host() -> str:
        """Get RabbitMQ host."""
        if settings.RABBITMQ_HOST:
            return settings.RABBITMQ_HOST
        if settings.RABBITMQ_URL and "@" in settings.RABBITMQ_URL:
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
        if settings.RABBITMQ_URL and "://" in settings.RABBITMQ_URL:
            try:
                parts = settings.RABBITMQ_URL.split("://")[1].split("@")[0]
                if ":" in parts:
                    return parts.split(":")[1]
            except (IndexError, ValueError):
                pass
        return "guest"
    
    QUEUE_NAME = settings.RABBITMQ_QUEUE_NAME


class RabbitMQConsumer:
    """RabbitMQ consumer for conversation events."""
    
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
                # Queue doesn't exist, create it (durable, no arguments to match existing)
                logger.info(f"📝 Creating queue '{RabbitMQConfig.QUEUE_NAME}'")
                # Reopen channel after error
                if self.connection and not self.connection.is_closed:
                    self.channel = self.connection.channel()
                else:
                    self._connect()  # Reconnect if connection closed
                    return  # _connect will be called recursively, so return here
                
                self.channel.queue_declare(
                    queue=RabbitMQConfig.QUEUE_NAME,
                    durable=True
                )
            
            # Set QoS: Process 1 message at a time
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(
                f"✅ Connected to RabbitMQ as consumer at {RabbitMQConfig.get_host()}:{RabbitMQConfig.get_port()}"
            )
        
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}", exc_info=True)
            raise
    
    def callback(self, ch, method, properties, body):
        """
        Callback function when receiving message from queue.
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body (JSON string)
        """
        conversation_id = None
        db = None  # FIX: Khai báo db ở ngoài để đảm bảo có thể close trong finally
        
        try:
            # Parse message
            message = json.loads(body)
            conversation_id = message.get("conversation_id")
            
            logger.info(f"📥 Processing conversation from queue: {conversation_id}")
            
            # FIX: Tạo session MỚI cho mỗi message để tránh transaction bị "nhiễm" lỗi
            db = SessionLocal()
            
            repo = ConversationEventRepository(db)
            event = repo.get_by_conversation_id(conversation_id)
            
            if not event:
                logger.error(f"❌ Conversation not found in DB: {conversation_id}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Setup services
            conversation_fetch_service = ConversationDataFetchService(
                conversation_repository=repo,
                external_api_client=None
            )
            score_service = FriendshipScoreCalculationService(
                conversation_fetch_service=conversation_fetch_service
            )
            status_service = FriendshipStatusUpdateService(db)
            
            # Process event
            processor = ConversationEventProcessingService(
                db=db,
                score_service=score_service,
                status_update_service=status_service,
            )
            
            result = processor.process_single_event(event.id)
            
            if result:
                logger.info(
                    f"✅ Successfully processed conversation: {conversation_id}, "
                    f"processed={result.get('processed', 0)}"
                )
            else:
                logger.warning(f"⚠️  No result from processing: {conversation_id}")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing message JSON: {str(e)}", exc_info=True)
            # Acknowledge message to remove from queue (invalid format)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        except Exception as e:
            logger.error(
                f"❌ Error processing message for conversation_id={conversation_id}: {str(e)}",
                exc_info=True
            )
            
            # FIX: Rollback transaction nếu có lỗi
            if db:
                try:
                    db.rollback()
                except Exception as rollback_error:
                    logger.warning(f"⚠️ Error during rollback: {str(rollback_error)}")
            
            # Nack message (requeue for retry)
            try:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except Exception as nack_error:
                logger.error(f"❌ Failed to nack message: {str(nack_error)}")
        
        finally:
            # FIX: LUÔN close session để giải phóng connection
            if db:
                try:
                    db.close()
                except Exception as close_error:
                    logger.warning(f"⚠️ Error closing DB session: {str(close_error)}")
    
    def start_consuming(self):
        """Start consuming messages from queue."""
        try:
            self.channel.basic_consume(
                queue=RabbitMQConfig.QUEUE_NAME,
                on_message_callback=self.callback,
                auto_ack=False  # Manual acknowledgment
            )
            
            logger.info(f"🔄 Starting to consume messages from queue: {RabbitMQConfig.QUEUE_NAME}")
            logger.info("Press CTRL+C to stop")
            
            self.channel.start_consuming()
        
        except KeyboardInterrupt:
            logger.info("🛑 Stopping consumer...")
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("✅ Consumer stopped")
        
        except Exception as e:
            logger.error(f"❌ Error in consumer: {str(e)}", exc_info=True)
            raise
    
    def close(self):
        """Close connection."""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("🔌 Closed RabbitMQ consumer connection")
        except Exception as e:
            logger.warning(f"Error closing RabbitMQ connection: {str(e)}")


def start_consumer():
    """Entry point to start consumer."""
    consumer = RabbitMQConsumer()
    try:
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"❌ Consumer failed: {str(e)}", exc_info=True)
        raise
    finally:
        consumer.close()


if __name__ == "__main__":
    start_consumer()
