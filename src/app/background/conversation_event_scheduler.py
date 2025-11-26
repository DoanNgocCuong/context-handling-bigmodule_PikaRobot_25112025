"""
APScheduler job setup for processing conversation events.
"""
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.api.dependency_injection import get_friendship_score_calculation_service
from app.db.database_connection import SessionLocal
from app.services.conversation_event_processing_service import (
    ConversationEventProcessingService,
)
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)

JOB_ID_CONVERSATION_EVENTS = "conversation_event_processor"
_scheduler: Optional[AsyncIOScheduler] = None


def _run_conversation_event_job() -> None:
    """Job entrypoint executed by APScheduler."""
    db = SessionLocal()
    try:
        score_service = get_friendship_score_calculation_service()
        status_service = FriendshipStatusUpdateService(db)
        processor = ConversationEventProcessingService(
            db=db,
            score_service=score_service,
            status_update_service=status_service,
        )
        stats = processor.process_due_events()
        if stats["total"]:
            logger.info(
                "Conversation event job stats: %s processed / %s total",
                stats["processed"],
                stats["total"],
            )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Conversation event job failed: %s", exc, exc_info=True)
    finally:
        db.close()


def start_background_jobs() -> None:
    """Start APScheduler with the conversation-event job."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _run_conversation_event_job,
        trigger=IntervalTrigger(seconds=10),
        id=JOB_ID_CONVERSATION_EVENTS,
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    logger.info("Background scheduler started (conversation events every 10 seconds)")


def shutdown_background_jobs() -> None:
    """Stop scheduler on app shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")

