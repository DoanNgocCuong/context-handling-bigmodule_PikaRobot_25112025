"""
RabbitMQ Consumer for conversation events.

Consumes messages from RabbitMQ queue and processes conversation events.
"""
import json
import time
import pika
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from app.core.config_settings import settings
from app.db.database_connection import SessionLocal
from app.repositories.conversation_event_repository import ConversationEventRepository
from app.services.conversation_data_fetch_service import ConversationDataFetchService
from app.services.friendship_score_calculation_service import FriendshipScoreCalculationService
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.services.conversation_event_processing_service import ConversationEventProcessingService
from app.utils.logger_setup import get_logger
from app.utils.color_log import success, error, warning, info, key_value
from app.utils.color_worker import (
    worker_connected,
    worker_error,
    queue_info,
    message_received,
    message_processed,
    message_failed,
    consumer_starting,
    consumer_stopping,
    consumer_stopped,
    connection_closed,
)

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
    # Đọc từ settings: số message xử lý song song trong 1 worker
    MESSAGE_CONCURRENCY_PER_WORKER = settings.MESSAGE_CONCURRENCY_PER_WORKER


class RabbitMQConsumer:
    """RabbitMQ consumer for conversation events."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize RabbitMQ consumer with thread pool for concurrent processing.
        
        Args:
            max_workers: Number of threads in thread pool. Defaults to MESSAGE_CONCURRENCY_PER_WORKER.
        """
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        # Thread pool để xử lý messages song song
        workers = max_workers or settings.MESSAGE_CONCURRENCY_PER_WORKER
        self.executor = ThreadPoolExecutor(max_workers=workers)
        # Lock để bảo vệ channel operations (Pika channel KHÔNG thread-safe)
        self._channel_lock = Lock()
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
                    retry_delay=2,
                    heartbeat=600,  # Heartbeat every 10 minutes
                    blocked_connection_timeout=300  # Timeout if connection blocked
                )
            )
            
            self.channel = self.connection.channel()
            
            # Check if queue exists first (passive=True)
            try:
                self.channel.queue_declare(
                    queue=RabbitMQConfig.QUEUE_NAME,
                    passive=True  # Only check if queue exists, don't create
                )
                logger.info(
                    f"{success('✅')} {queue_info(RabbitMQConfig.QUEUE_NAME, 'already exists')}"
                )
            except (pika.exceptions.ChannelClosedByBroker, pika.exceptions.ChannelClosed):
                # Queue doesn't exist, create it (durable, no arguments to match existing)
                logger.info(
                    f"{info('📝')} {queue_info(RabbitMQConfig.QUEUE_NAME, 'creating')}"
                )
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
            
            # Set QoS: Process multiple messages concurrently
            prefetch_count = RabbitMQConfig.MESSAGE_CONCURRENCY_PER_WORKER
            self.channel.basic_qos(prefetch_count=prefetch_count)
            
            logger.info(
                worker_connected(
                    f"Connected to RabbitMQ as consumer at "
                    f"{RabbitMQConfig.get_host()}:{RabbitMQConfig.get_port()} "
                    f"(prefetch_count={prefetch_count}, max_workers={self.executor._max_workers})"
                )
            )
        
        except Exception as e:
            logger.error(
                worker_error(f"Failed to connect to RabbitMQ: {str(e)}"),
                exc_info=True
            )
            raise
    
    def callback(self, ch, method, properties, body):
        """
        Callback function when receiving message from queue.
        
        NOTE: Method này chỉ submit task vào thread pool và return ngay.
        Logic xử lý thực sự nằm trong _process_message() để xử lý song song.
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body (JSON string)
        """
        # Submit vào thread pool để xử lý song song
        # Không chờ kết quả, return ngay → callback tiếp theo có thể chạy
        self.executor.submit(
            self._process_message,
            ch, method, properties, body
        )
        # Return ngay lập tức → RabbitMQ có thể gửi message tiếp theo
    
    def _safe_ack(self, ch, method):
        """
        Safely acknowledge message using the original channel from callback.
        
        NOTE: delivery_tag chỉ hợp lệ với channel gốc (ch), không thể dùng channel mới.
        Nếu channel bị đóng, message sẽ được requeue tự động.
        
        Args:
            ch: Channel từ callback (original channel)
            method: Delivery method
        """
        try:
            # Kiểm tra channel gốc có còn valid không
            if not ch or ch.is_closed:
                logger.warning(
                    f"⚠️ Original channel is closed, cannot ACK. Message will be requeued. "
                    f"delivery_tag={method.delivery_tag}"
                )
                return False
            
            # ACK với lock protection (dùng channel gốc)
            with self._channel_lock:
                if not ch.is_closed:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return True
                else:
                    logger.warning(
                        f"⚠️ Channel closed during ACK, message will be requeued. "
                        f"delivery_tag={method.delivery_tag}"
                    )
                    return False
                    
        except (pika.exceptions.StreamLostError,
                pika.exceptions.ConnectionClosed,
                pika.exceptions.ChannelClosed) as e:
            logger.warning(
                f"⚠️ Cannot ACK message (channel closed): {str(e)}. "
                f"Message will be requeued. delivery_tag={method.delivery_tag}"
            )
            return False
        except AttributeError as e:
            logger.warning(
                f"⚠️ Channel attribute error during ACK: {str(e)}. "
                f"Message will be requeued. delivery_tag={method.delivery_tag}"
            )
            return False
        except Exception as e:
            logger.error(
                f"❌ Unexpected error during ACK: {str(e)}. "
                f"delivery_tag={method.delivery_tag}",
                exc_info=True
            )
            return False
    
    def _process_message(self, ch, method, properties, body):
        """
        Xử lý message thực sự (chạy trong thread riêng).
        
        Logic này giống hệt code cũ trong callback(), chỉ tách ra method riêng
        để có thể chạy song song trong thread pool.
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body (JSON string)
        """
        conversation_id = None
        db = None  # Tạo session MỚI cho mỗi thread (QUAN TRỌNG!)
        message_acked = False
        
        try:
            # Parse message
            message = json.loads(body)
            conversation_id = message.get("conversation_id")
            
            logger.info(message_received(conversation_id))
            
            # Tạo session MỚI cho mỗi thread để tránh transaction bị "nhiễm" lỗi
            db = SessionLocal()
            
            repo = ConversationEventRepository(db)
            event = repo.get_by_conversation_id(conversation_id)
            
            if not event:
                logger.error(
                    f"{error('❌ Conversation not found in DB')} | "
                    f"{key_value('conversation_id', conversation_id)}"
                )
                # Safe ACK
                message_acked = self._safe_ack(ch, method)
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
                processed = result.get('processed', 0)
                failed = result.get('failed', 0)
                logger.info(message_processed(conversation_id, processed, failed))
            else:
                logger.warning(
                    f"{warning('⚠️  No result from processing')} | "
                    f"{key_value('conversation_id', conversation_id)}"
                )
            
            # Acknowledge message (safe with retry)
            message_acked = self._safe_ack(ch, method)
        
        except json.JSONDecodeError as e:
            logger.error(
                f"{error('❌ Error parsing message JSON')} | "
                f"{key_value('error', str(e))}",
                exc_info=True
            )
            # Acknowledge message to remove from queue (invalid format, safe)
            message_acked = self._safe_ack(ch, method)
        
        except Exception as e:
            error_msg = str(e)
            logger.error(
                message_failed(conversation_id or 'unknown', error_msg),
                exc_info=True
            )
            
            # Rollback transaction nếu có lỗi
            if db:
                try:
                    db.rollback()
                except Exception as rollback_error:
                    logger.warning(f"⚠️ Error during rollback: {str(rollback_error)}")
            
            # Nack message (requeue for retry, safe) - dùng channel gốc
            if not message_acked:
                try:
                    # Dùng channel gốc từ callback
                    if ch and not ch.is_closed:
                        with self._channel_lock:
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    else:
                        logger.warning(
                            f"⚠️ Cannot NACK: channel is closed. "
                            f"Message will be requeued automatically. "
                            f"delivery_tag={method.delivery_tag}"
                        )
                except (pika.exceptions.StreamLostError,
                        pika.exceptions.ConnectionClosed,
                        pika.exceptions.ChannelClosed) as nack_error:
                    logger.warning(
                        f"⚠️ Cannot NACK message (channel closed): {str(nack_error)}. "
                        f"Message will be requeued automatically. "
                        f"delivery_tag={method.delivery_tag}"
                    )
                except Exception as nack_error:
                    logger.error(
                        f"❌ Failed to nack message: {str(nack_error)}. "
                        f"delivery_tag={method.delivery_tag}",
                        exc_info=True
                    )
        
        finally:
            # LUÔN close session để giải phóng connection
            if db:
                try:
                    db.close()
                except Exception as close_error:
                    logger.warning(f"⚠️ Error closing DB session: {str(close_error)}")
    
    def start_consuming(self):
        """Start consuming messages from queue with connection health monitoring."""
        try:
            self.channel.basic_consume(
                queue=RabbitMQConfig.QUEUE_NAME,
                on_message_callback=self.callback,
                auto_ack=False  # Manual acknowledgment
            )
            
            logger.info(consumer_starting())
            logger.info(f"{info('📋')} {queue_info(RabbitMQConfig.QUEUE_NAME, 'listening')}")
            logger.info(f"{info('💡')} Press CTRL+C to stop")
            
            # Use process_data_events with timeout instead of start_consuming()
            # This allows us to check connection health periodically
            while True:
                try:
                    # Check connection health before processing
                    if not self.connection or self.connection.is_closed:
                        logger.warning("⚠️ Connection closed, reconnecting...")
                        self._connect()
                        # Re-register consumer after reconnect
                        self.channel.basic_consume(
                            queue=RabbitMQConfig.QUEUE_NAME,
                            on_message_callback=self.callback,
                            auto_ack=False
                        )
                        continue
                    
                    if not self.channel or self.channel.is_closed:
                        logger.warning("⚠️ Channel closed, recreating...")
                        if self.connection and not self.connection.is_closed:
                            self.channel = self.connection.channel()
                            self.channel.basic_qos(prefetch_count=RabbitMQConfig.MESSAGE_CONCURRENCY_PER_WORKER)
                            self.channel.basic_consume(
                                queue=RabbitMQConfig.QUEUE_NAME,
                                on_message_callback=self.callback,
                                auto_ack=False
                            )
                        else:
                            self._connect()
                            self.channel.basic_consume(
                                queue=RabbitMQConfig.QUEUE_NAME,
                                on_message_callback=self.callback,
                                auto_ack=False
                            )
                        continue
                    
                    # Process data events with timeout (non-blocking check)
                    # This allows us to periodically check connection health
                    self.connection.process_data_events(time_limit=1.0)
                    
                except (pika.exceptions.StreamLostError,
                        pika.exceptions.ConnectionClosed,
                        pika.exceptions.ChannelClosed) as e:
                    logger.warning(
                        f"⚠️ Connection error during processing: {str(e)}. Reconnecting..."
                    )
                    try:
                        self._connect()
                        # Re-register consumer after reconnect
                        self.channel.basic_consume(
                            queue=RabbitMQConfig.QUEUE_NAME,
                            on_message_callback=self.callback,
                            auto_ack=False
                        )
                    except Exception as reconnect_error:
                        logger.error(
                            worker_error(f"Reconnection failed: {str(reconnect_error)}"),
                            exc_info=True
                        )
                        # Wait before retry
                        time.sleep(5)
                        continue
        
        except KeyboardInterrupt:
            logger.info(consumer_stopping())
            if self.channel:
                try:
                    self.channel.stop_consuming()
                except:
                    pass
            if self.connection and not self.connection.is_closed:
                try:
                    self.connection.close()
                except:
                    pass
            logger.info(consumer_stopped())
        
        except Exception as e:
            logger.error(
                worker_error(f"Fatal error in consumer: {str(e)}"),
                exc_info=True
            )
            raise
    
    def close(self):
        """Close connection and shutdown thread pool."""
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            # Shutdown thread pool (wait up to 30 seconds for tasks to complete)
            self.executor.shutdown(wait=True, timeout=30)
            logger.info(connection_closed())
        except Exception as e:
            logger.warning(
                f"{warning('⚠️')} Error closing RabbitMQ connection: {str(e)}"
            )


def start_consumer():
    """Entry point to start consumer with auto-restart on connection errors."""
    max_restart_attempts = 5
    restart_delay = 5  # seconds
    
    for attempt in range(max_restart_attempts):
        consumer = None
        try:
            consumer = RabbitMQConsumer()
            consumer.start_consuming()
        except (pika.exceptions.StreamLostError,
                pika.exceptions.ConnectionClosed,
                pika.exceptions.ChannelClosed) as e:
            logger.error(
                worker_error(f"Connection lost (attempt {attempt + 1}/{max_restart_attempts}): {str(e)}"),
                exc_info=True
            )
            if consumer:
                try:
                    consumer.close()
                except:
                    pass
            
            if attempt < max_restart_attempts - 1:
                logger.info(f"🔄 Restarting consumer in {restart_delay} seconds...")
                time.sleep(restart_delay)
                continue
            else:
                logger.error("❌ Max restart attempts reached, giving up")
                raise
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
            if consumer:
                try:
                    consumer.close()
                except:
                    pass
            break
        except Exception as e:
            logger.error(
                worker_error(f"Consumer failed: {str(e)}"),
                exc_info=True
            )
            if consumer:
                try:
                    consumer.close()
                except:
                    pass
            raise


if __name__ == "__main__":
    start_consumer()
