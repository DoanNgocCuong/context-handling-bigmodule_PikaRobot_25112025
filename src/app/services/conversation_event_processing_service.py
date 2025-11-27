"""
Service that scans pending conversation events and processes them.
"""
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.core.constants_enums import ConversationEventStatus
from app.core.exceptions_custom import (
    ConversationNotFoundError,
    InvalidScoreError,
)
from app.repositories.conversation_event_repository import ConversationEventRepository
from app.services.friendship_score_calculation_service import FriendshipScoreCalculationService
from app.services.friendship_status_update_service import FriendshipStatusUpdateService
from app.utils.logger_setup import get_logger
from app.utils.topic_utils import get_topic_id_from_agent_id

logger = get_logger(__name__)


class ConversationEventProcessingService:
    """
    Pulls due conversation events, calculates friendship score, and updates status.
    """

    def __init__(
        self,
        db: Session,
        score_service: FriendshipScoreCalculationService,
        status_update_service: FriendshipStatusUpdateService,
    ):
        self.db = db
        self.repository = ConversationEventRepository(db)
        self.score_service = score_service
        self.status_update_service = status_update_service

    def process_single_event(self, event_id: int) -> Optional[Dict[str, int]]:
        """
        Process a single conversation event by ID.

        Returns optional stats dict for consistency with batch method.
        """
        event = self.repository.get_by_id(event_id)
        if not event:
            logger.warning("Conversation event not found for id=%s", event_id)
            return None

        stats = {"processed": 0, "failed": 0, "total": 1}
        logger.info(
            "Processing single conversation event conversation_id=%s attempt=%s",
            event.conversation_id,
            (event.attempt_count or 0) + 1,
        )
        self.repository.mark_processing(event)
        try:
            calc_result = self.score_service.calculate_score_from_conversation_id(
                event.conversation_id
            )
            score_change = calc_result["friendship_score_change"]
            
            # Try to update topic_metrics first (it also updates friendship_score)
            bot_id = event.bot_id
            
            # Get user's friendship_level first to query topic_id from DB
            user_status = self.status_update_service.get_status(event.user_id)
            friendship_level = user_status.get("friendship_level", "PHASE1_STRANGER")
            
            # Get topic_id from DB (agenda_agent_prompting table)
            topic_id = get_topic_id_from_agent_id(
                bot_id=bot_id,
                friendship_level=friendship_level,
                db=self.db
            )
            logger.info(
                f"🔍 Got topic_id from agent_id: bot_id='{bot_id}', "
                f"friendship_level='{friendship_level}' -> topic_id='{topic_id}'"
            )
            status = None
            
            if topic_id:
                # Calculate turns from conversation log
                conversation_data = self.score_service.conversation_fetch_service.fetch_by_id(
                    event.conversation_id
                )
                conversation_log = conversation_data.get("conversation_log", []) if conversation_data else []
                turns_change = len(conversation_log) // 2  # 1 turn = 1 pair of exchanges
                
                try:
                    self.status_update_service.update_topic_metrics(
                        user_id=event.user_id,
                        topic_id=topic_id,
                        score_change=score_change,
                        bot_id=bot_id,
                        turns_change=turns_change
                    )
                    # Get updated status to get friendship_level
                    status = self.status_update_service.get_status(event.user_id)
                    logger.info(
                        f"Updated topic_metrics for user_id={event.user_id}, "
                        f"topic_id={topic_id}, score_change={score_change}, turns={turns_change}"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to update topic_metrics for user_id={event.user_id}, "
                        f"topic_id={topic_id}: {e}, falling back to apply_score_change"
                    )
                    # Fallback to apply_score_change if update_topic_metrics fails
                    status = self.status_update_service.apply_score_change(
                        user_id=event.user_id,
                        score_change=score_change,
                    )
            else:
                # No topic_id, just update friendship score
                logger.warning(
                    f"Could not extract topic_id from bot_id={bot_id} for user_id={event.user_id}, "
                    f"using apply_score_change only"
                )
                status = self.status_update_service.apply_score_change(
                    user_id=event.user_id,
                    score_change=score_change,
                )

            self.repository.mark_processed(
                event=event,
                friendship_score_change=calc_result["friendship_score_change"],
                friendship_level=status["friendship_level"],
            )
            stats["processed"] = 1
        except ConversationNotFoundError as exc:
            self._handle_failure(event, "CONVERSATION_NOT_FOUND", str(exc))
            stats["failed"] = 1
        except InvalidScoreError as exc:
            self._handle_failure(event, "INVALID_SCORE", str(exc))
            stats["failed"] = 1
        except Exception as exc:  # pragma: no cover
            self._handle_failure(event, "UNEXPECTED_ERROR", str(exc))
            stats["failed"] = 1

        return stats

    def process_due_events(self, batch_size: int = 20) -> Dict[str, int]:
        """
        Process events with next_attempt_at <= now.

        Returns:
            Dict with counters: processed, failed, total
        """
        due_events = self.repository.fetch_due_events(batch_size=batch_size)
        stats = {"processed": 0, "failed": 0, "total": len(due_events)}

        if not due_events:
            return stats

        logger.info("Processing %s due conversation events", len(due_events))

        for event in due_events:
            logger.info(
                "Processing conversation event conversation_id=%s attempt=%s",
                event.conversation_id,
                (event.attempt_count or 0) + 1,
            )
            self.repository.mark_processing(event)
            try:
                calc_result = self.score_service.calculate_score_from_conversation_id(
                    event.conversation_id
                )
                score_change = calc_result["friendship_score_change"]
                
                # Try to update topic_metrics first (it also updates friendship_score)
                bot_id = event.bot_id
                
                # Get user's friendship_level first to query topic_id from DB
                user_status = self.status_update_service.get_status(event.user_id)
                friendship_level = user_status.get("friendship_level", "PHASE1_STRANGER")
                
                # Get topic_id from DB (agenda_agent_prompting table)
                topic_id = get_topic_id_from_agent_id(
                    bot_id=bot_id,
                    friendship_level=friendship_level,
                    db=self.db
                )
                logger.info(
                    f"🔍 Got topic_id from agent_id: bot_id='{bot_id}', "
                    f"friendship_level='{friendship_level}' -> topic_id='{topic_id}'"
                )
                status = None
                
                if topic_id:
                    # Calculate turns from conversation log
                    conversation_data = self.score_service.conversation_fetch_service.fetch_by_id(
                        event.conversation_id
                    )
                    conversation_log = conversation_data.get("conversation_log", []) if conversation_data else []
                    turns_change = len(conversation_log) // 2  # 1 turn = 1 pair of exchanges
                    
                    try:
                        self.status_update_service.update_topic_metrics(
                            user_id=event.user_id,
                            topic_id=topic_id,
                            score_change=score_change,
                            bot_id=bot_id,
                            turns_change=turns_change
                        )
                        # Get updated status to get friendship_level
                        status = self.status_update_service.get_status(event.user_id)
                        logger.info(
                            f"Updated topic_metrics for user_id={event.user_id}, "
                            f"topic_id={topic_id}, score_change={score_change}, turns={turns_change}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to update topic_metrics for user_id={event.user_id}, "
                            f"topic_id={topic_id}: {e}, falling back to apply_score_change"
                        )
                        # Fallback to apply_score_change if update_topic_metrics fails
                        status = self.status_update_service.apply_score_change(
                            user_id=event.user_id,
                            score_change=score_change,
                        )
                else:
                    # No topic_id, just update friendship score
                    logger.warning(
                        f"Could not extract topic_id from bot_id={bot_id} for user_id={event.user_id}, "
                        f"using apply_score_change only"
                    )
                    status = self.status_update_service.apply_score_change(
                        user_id=event.user_id,
                        score_change=score_change,
                    )

                self.repository.mark_processed(
                    event=event,
                    friendship_score_change=calc_result["friendship_score_change"],
                    friendship_level=status["friendship_level"],
                )
                stats["processed"] += 1

            except ConversationNotFoundError as exc:
                self._handle_failure(event, "CONVERSATION_NOT_FOUND", str(exc))
                stats["failed"] += 1
            except InvalidScoreError as exc:
                self._handle_failure(event, "INVALID_SCORE", str(exc))
                stats["failed"] += 1
            except Exception as exc:  # pragma: no cover
                self._handle_failure(event, "UNEXPECTED_ERROR", str(exc))
                stats["failed"] += 1

        logger.info(
            "Conversation event processing completed. processed=%s failed=%s",
            stats["processed"],
            stats["failed"],
        )
        return stats

    def _handle_failure(self, event, error_code: str, error_details: str) -> None:
        """Update event as failed and log."""
        logger.warning(
            "Processing failed for conversation_id=%s error_code=%s error=%s",
            event.conversation_id,
            error_code,
            error_details,
        )
        self.repository.mark_failed(
            event=event,
            error_code=error_code,
            error_details=error_details,
        )

