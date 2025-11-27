"""
Worker process to consume messages from RabbitMQ queue.

Run: python src/worker.py
"""
import sys
import os

# Add src/ to path
sys.path.insert(0, os.path.dirname(__file__))

from app.background.rabbitmq_consumer import start_consumer

if __name__ == "__main__":
    start_consumer()

