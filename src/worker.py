"""
Worker process to consume messages from RabbitMQ queue.

Run: python src/worker.py
"""
import sys
import os

# Add src/ to path
sys.path.insert(0, os.path.dirname(__file__))

from app.background.rabbitmq_consumer import start_consumer
from app.utils.logger_setup import get_logger
from app.utils.color_worker import worker_start, worker_stop, consumer_starting

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info(worker_start("Starting RabbitMQ worker..."))
    logger.info(consumer_starting())
    try:
        start_consumer()
    except KeyboardInterrupt:
        logger.info(worker_stop("Worker stopped by user"))
    except Exception as e:
        logger.error(f"❌ Worker crashed: {str(e)}", exc_info=True)
        raise

