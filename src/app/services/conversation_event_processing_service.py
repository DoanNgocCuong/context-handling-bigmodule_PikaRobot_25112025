"""
Service that scans pending conversation events and processes them.
"""
from typing import Dict, List, Optional, Any

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
            # Use agent_tag ONLY (no fallback to bot_id)
            agent_tag = event.agent_tag if hasattr(event, 'agent_tag') else None
            bot_id = event.bot_id  # Keep bot_id for logging and agents_used tracking
            
            status = None
            
            # Only query topic_id if agent_tag is provided
            if agent_tag:
                # Get user's friendship_level first to query topic_id from DB
                # get_status() will auto-create record if user doesn't exist
                # If it fails, we'll use default level and apply_score_change will create it
                try:
                    user_status = self.status_update_service.get_status(event.user_id)
                    friendship_level = user_status.get("friendship_level", "PHASE1_STRANGER")
                except Exception as e:
                    logger.warning(
                        f"⚠️  Failed to get/create friendship status for user {event.user_id}: {e}. "
                        f"Using default level, will create record in apply_score_change"
                    )
                    # Use default level - apply_score_change will create the record
                    friendship_level = "PHASE1_STRANGER"
                
                # Get topic_id from DB (agenda_agent_prompting table) using agent_tag
                topic_id = get_topic_id_from_agent_id(
                    bot_id=agent_tag,  # Use agent_tag to query topic_id
                    friendship_level=friendship_level,
                    db=self.db
                )
                logger.info(
                    f"🔍 Got topic_id from agent_id: agent_tag='{agent_tag}', "
                    f"friendship_level='{friendship_level}' -> topic_id='{topic_id}'"
                )
                
                if topic_id:
                    # Calculate turns from conversation log
                    conversation_data = self.score_service.conversation_fetch_service.fetch_by_id(
                        event.conversation_id
                    )
                    conversation_log = conversation_data.get("conversation_log", []) if conversation_data else []
                    # Use same logic as score calculation: count complete turns (pika + user pairs)
                    turns_change = self._count_complete_turns(conversation_log)
                    
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
                    # No topic_id found for agent_tag, just update friendship score
                    logger.warning(
                        f"Could not extract topic_id from agent_tag={agent_tag} for user_id={event.user_id}, "
                        f"using apply_score_change only"
                    )
                    status = self.status_update_service.apply_score_change(
                        user_id=event.user_id,
                        score_change=score_change,
                    )
            else:
                # No agent_tag provided, skip topic_metrics update, only update friendship score
                logger.info(
                    f"⏭️  agent_tag not provided for user_id={event.user_id}, "
                    f"skipping topic_metrics update, using apply_score_change only"
                )
                status = self.status_update_service.apply_score_change(
                    user_id=event.user_id,
                    score_change=score_change,
                )
            
            # Ensure status is set (fallback if somehow status is still None)
            if status is None:
                logger.warning(
                    f"Status is None after processing, applying score change as fallback"
            )
            status = self.status_update_service.apply_score_change(
                user_id=event.user_id,
                    score_change=score_change,
                )

            # Get calculation details from result
            calculation_details = calc_result.get("calculation_details")
            if calculation_details is not None:
                logger.info(
                    f"📊 Saving score_calculation_details for conversation_id={event.conversation_id}: "
                    f"{calculation_details}"
                )
            else:
                logger.warning(
                    f"⚠️  No calculation_details found in calc_result for conversation_id={event.conversation_id}. "
                    f"calc_result keys: {list(calc_result.keys())}"
            )

            self.repository.mark_processed(
                event=event,
                friendship_score_change=calc_result["friendship_score_change"],
                friendship_level=status["friendship_level"],
                score_calculation_details=calculation_details,
            )
            stats["processed"] = 1
        except ConversationNotFoundError as exc:
            # Rollback transaction nếu bị abort
            try:
                self.db.rollback()
            except Exception:
                pass  # Ignore rollback errors
            self._handle_failure(event, "CONVERSATION_NOT_FOUND", str(exc))
            stats["failed"] = 1
        except InvalidScoreError as exc:
            # Rollback transaction nếu bị abort
            try:
                self.db.rollback()
            except Exception:
                pass  # Ignore rollback errors
            self._handle_failure(event, "INVALID_SCORE", str(exc))
            stats["failed"] = 1
        except Exception as exc:  # pragma: no cover
            # FIX: Rollback transaction trước khi handle failure
            # Điều này đảm bảo transaction bị abort được reset
            try:
                self.db.rollback()
            except Exception:
                pass  # Ignore rollback errors
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
                # Use agent_tag ONLY (no fallback to bot_id)
                agent_tag = event.agent_tag if hasattr(event, 'agent_tag') else None
                bot_id = event.bot_id  # Keep bot_id for logging and agents_used tracking
                
                status = None
                
                # Only query topic_id if agent_tag is provided
                if agent_tag:
                    # Get user's friendship_level first to query topic_id from DB
                    user_status = self.status_update_service.get_status(event.user_id)
                    friendship_level = user_status.get("friendship_level", "PHASE1_STRANGER")
                    
                    # Get topic_id from DB (agenda_agent_prompting table) using agent_tag
                    topic_id = get_topic_id_from_agent_id(
                        bot_id=agent_tag,  # Use agent_tag to query topic_id
                        friendship_level=friendship_level,
                        db=self.db
                    )
                    logger.info(
                        f"🔍 Got topic_id from agent_id: agent_tag='{agent_tag}', "
                        f"friendship_level='{friendship_level}' -> topic_id='{topic_id}'"
                    )
                    
                    if topic_id:
                        # Calculate turns from conversation log
                        conversation_data = self.score_service.conversation_fetch_service.fetch_by_id(
                            event.conversation_id
                        )
                        conversation_log = conversation_data.get("conversation_log", []) if conversation_data else []
                        # Use same logic as score calculation: count complete turns (pika + user pairs)
                        turns_change = self._count_complete_turns(conversation_log)
                        
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
                        # No topic_id found for agent_tag, just update friendship score
                        logger.warning(
                            f"Could not extract topic_id from agent_tag={agent_tag} for user_id={event.user_id}, "
                            f"using apply_score_change only"
                        )
                        status = self.status_update_service.apply_score_change(
                            user_id=event.user_id,
                            score_change=score_change,
                        )
                else:
                    # No agent_tag provided, skip topic_metrics update, only update friendship score
                    logger.info(
                        f"⏭️  agent_tag not provided for user_id={event.user_id}, "
                        f"skipping topic_metrics update, using apply_score_change only"
                )
                status = self.status_update_service.apply_score_change(
                    user_id=event.user_id,
                        score_change=score_change,
                    )

                # Get calculation details from result
                calculation_details = calc_result.get("calculation_details")
                if calculation_details is not None:
                    logger.info(
                        f"📊 Saving score_calculation_details for conversation_id={event.conversation_id}: "
                        f"{calculation_details}"
                    )
                else:
                    logger.warning(
                        f"⚠️  No calculation_details found in calc_result for conversation_id={event.conversation_id}. "
                        f"calc_result keys: {list(calc_result.keys())}"
                )

                self.repository.mark_processed(
                    event=event,
                    friendship_score_change=calc_result["friendship_score_change"],
                    friendship_level=status["friendship_level"],
                    score_calculation_details=calculation_details,
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

    def _count_complete_turns(self, conversation_log: List[Dict[str, Any]]) -> int:
        """
        Đếm số turn hoàn chỉnh (1 turn = 1 cặp pika + user).
        
        Logic:
        - Duyệt conversation_log theo thứ tự
        - Đếm số cặp liên tiếp (pika, user) hoặc (user, pika)
        - Bỏ qua các messages đơn lẻ không tạo thành cặp
        
        Args:
            conversation_log: List of conversation messages
            
        Returns:
            Số turn hoàn chỉnh (cặp trao đổi)
        """
        if not conversation_log:
            return 0
        
        turns = 0
        i = 0
        while i < len(conversation_log) - 1:
            current_speaker = conversation_log[i].get("speaker", "").lower()
            next_speaker = conversation_log[i + 1].get("speaker", "").lower()
            
            # Kiểm tra nếu là cặp (pika, user) hoặc (user, pika)
            if (current_speaker == "pika" and next_speaker == "user") or \
               (current_speaker == "user" and next_speaker == "pika"):
                turns += 1
                i += 2  # Bỏ qua cả 2 messages trong cặp
            else:
                i += 1  # Chỉ bỏ qua message hiện tại
        
        return turns

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

