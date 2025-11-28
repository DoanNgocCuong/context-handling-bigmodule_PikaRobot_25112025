"""
Friendship Score Calculation Service.

This service calculates friendship score changes from conversation data.
Follows Single Responsibility Principle (SRP).

================================================================================
SCORING FORMULA - Daily Change Score Calculation
================================================================================

The daily_change_score is calculated using the following formula:

    daily_change_score = base_score + engagement_bonus + emotion_bonus + memory_bonus

Where:

1. BASE SCORE:
   base_score = total_turns * 1
   - total_turns: Number of complete conversation turns (1 turn = 1 pair: pika + user)

2. ENGAGEMENT BONUS:
   engagement_bonus = user_initiated_questions * 3
   - user_initiated_questions: Count of questions the user actively asked (from LLM analysis)

3. EMOTION BONUS:
   emotion_bonus = mapping based on session_emotion:
   - If session_emotion == 'interesting': emotion_bonus = +15
   - If session_emotion == 'boring': emotion_bonus = -15
   - All other emotions: emotion_bonus = 0
   - session_emotion: Overall emotion of the conversation session (from LLM analysis)

4. MEMORY BONUS:
   memory_bonus = new_memories_count * 5
   - new_memories_count: Number of new memories extracted from conversation (from Memory API)

================================================================================
EXAMPLE CALCULATION
================================================================================

Given:
- total_turns = 3
- user_initiated_questions = 1
- session_emotion = 'interesting'
- new_memories_count = 7

Calculation:
- base_score = 3 * 1 = 3.0
- engagement_bonus = 1 * 3 = 3.0
- emotion_bonus = 15.0 (interesting)
- memory_bonus = 7 * 5 = 35.0
- daily_change_score = 3.0 + 3.0 + 15.0 + 35.0 = 56.0

================================================================================
"""
from typing import Dict, List, Any, Optional
from app.utils.logger_setup import get_logger
from app.utils.color_log import success, error, warning, info, key_value
from app.core.exceptions_custom import InvalidScoreError, ConversationNotFoundError
from app.services.utils.llm_analysis_utils import analyze_conversation_with_llm

logger = get_logger(__name__)


class FriendshipScoreCalculationService:
    """
    Service for calculating friendship score changes from conversation data.
    
    Responsibilities:
    - Calculate base score from conversation turns
    - Calculate engagement bonus from user-initiated questions
    - Calculate emotion bonus from session emotion
    - Calculate memory bonus from new memories
    - Combine all components into final score change
    """
    
    # Score calculation constants (following Open/Closed Principle)
    # Formula: daily_change_score = base_score + engagement_bonus + emotion_bonus + memory_bonus
    BASE_SCORE_PER_TURN: float = 1.0  # base_score = total_turns * 1
    ENGAGEMENT_BONUS_PER_QUESTION: float = 3.0  # engagement_bonus = user_initiated_questions * 3
    MEMORY_BONUS_PER_MEMORY: float = 5.0  # memory_bonus = new_memories_count * 5
    
    # Emotion bonus mapping
    # interesting: +15, boring: -15, others: 0
    EMOTION_BONUS_MAP: Dict[str, float] = {
        "interesting": 15.0,
        "boring": -15.0,
        # Other emotions default to 0.0 (handled by .get(emotion.lower(), 0.0))
        "happy": 0.0,
        "sad": 0.0,
        "neutral": 0.0,
        "angry": 0.0
    }
    
    def __init__(self, conversation_fetch_service=None):
        """
        Initialize service with conversation fetch dependency.
        
        Args:
            conversation_fetch_service: Service to fetch conversation data by ID
        """
        self.conversation_fetch_service = conversation_fetch_service
    
    def calculate_score_from_conversation_id(
        self, 
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Calculate friendship score change from conversation_id.
        
        Main entry point: fetches conversation and calculates score.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary containing:
            - friendship_score_change: float
            - conversation_id: str
            - user_id: str
            - calculation_details: dict with breakdown
            
        Raises:
            ConversationNotFoundError: If conversation not found
            InvalidScoreError: If calculation fails
        """
        try:
            logger.info(f"Calculating friendship score for conversation_id: {conversation_id}")
            
            # Step 1: Fetch conversation data
            if not self.conversation_fetch_service:
                raise InvalidScoreError(
                    "Conversation fetch service not initialized. "
                    "Cannot fetch conversation data."
                )
            
            conversation_data = self.conversation_fetch_service.fetch_by_id(conversation_id)
            
            if not conversation_data:
                raise ConversationNotFoundError(
                    f"Conversation not found: {conversation_id}"
                )
            
            # Step 2: Extract conversation log and metadata
            conversation_log = conversation_data.get("conversation_log", [])
            metadata = conversation_data.get("metadata", {})
            # Add conversation_id and user_id to metadata for LLM/Memory API tracking
            metadata["conversation_id"] = conversation_id
            if "user_id" not in metadata:
                metadata["user_id"] = conversation_data.get("user_id")
            # Add bot_type to metadata for Memory API skip logic
            bot_type = conversation_data.get("bot_type")
            if bot_type:
                metadata["bot_type"] = bot_type
                logger.info(
                    f"🔍 bot_type extracted from conversation_data | "
                    f"bot_type={bot_type} | "
                    f"conversation_id={conversation_id}"
                )
            else:
                logger.warning(
                    f"⚠️  bot_type not found in conversation_data | "
                    f"conversation_id={conversation_id} | "
                    f"available_keys={list(conversation_data.keys())}"
                )
            
            # Step 3: Calculate score change (this will update metadata with LLM results)
            score_change, updated_metadata = self.calculate_friendship_score_change(
                conversation_log=conversation_log,
                metadata=metadata
            )
            
            # Step 4: Get calculation breakdown using updated metadata (with LLM results)
            calculation_details = self._get_calculation_breakdown(
                conversation_log=conversation_log,
                metadata=updated_metadata
            )
            
            result = {
                "friendship_score_change": score_change,
                "conversation_id": conversation_id,
                "user_id": conversation_data.get("user_id"),
                "calculation_details": calculation_details
            }
            
            logger.info(
                f"Score calculation completed for conversation_id: {conversation_id}, "
                f"score_change: {score_change}"
            )
            
            return result
            
        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error calculating friendship score for conversation_id: {conversation_id}, "
                f"error: {str(e)}"
            )
            raise InvalidScoreError(
                f"Failed to calculate friendship score: {str(e)}"
            ) from e
    
    def calculate_friendship_score_change(
        self,
        conversation_log: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> tuple[float, Dict[str, Any]]:
        """
        Calculate friendship score change from conversation log and metadata.
        
        Formula:
        - base_score = total_turns * 0.5
        - engagement_bonus = user_initiated_questions * 3
        - emotion_bonus = mapping (interesting: +15, boring: -15, etc.)
        - memory_bonus = new_memories_count * 5
        - friendship_score_change = base_score + engagement_bonus + emotion_bonus + memory_bonus
        
        Args:
            conversation_log: List of conversation messages
            metadata: Conversation metadata (emotion, user_initiated_questions, etc.)
            
        Returns:
            Tuple of (friendship_score_change, updated_metadata)
            - friendship_score_change: Friendship score change (always >= 0)
            - updated_metadata: Metadata with LLM analysis results merged
        """
        try:
            # Extract metrics
            # 1 turn = 1 cặp trao đổi (pika + user)
            # Đếm số cặp thực sự trong conversation_log
            total_turns = self._count_complete_turns(conversation_log)
            
            # Use LLM analysis if metadata is incomplete
            has_complete_metadata = self._has_complete_metadata(metadata)
            logger.debug(
                f"🔍 Metadata check | "
                f"has_user_questions={'user_initiated_questions' in metadata} | "
                f"has_emotion={'emotion' in metadata or 'session_emotion' in metadata} | "
                f"complete={has_complete_metadata}"
            )
            
            if not has_complete_metadata:
                logger.info("📊 Metadata incomplete, using parallel analysis (2 LLMs + 1 Memory API)")
                # Get conversation_id and user_id from metadata if available (for tracking)
                conversation_id = metadata.get("conversation_id")
                user_id = metadata.get("user_id")
                bot_type = metadata.get("bot_type")  # ADDED: Get bot_type for Memory API skip logic
                llm_analysis = analyze_conversation_with_llm(
                    conversation_log=conversation_log,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    bot_type=bot_type  # ADDED: Pass bot_type to skip Memory API if needed
                )
                # Mark as LLM analyzed to avoid re-running
                llm_analysis["_llm_analyzed"] = True
                # Merge LLM results into metadata (LLM takes precedence)
                metadata = {**metadata, **llm_analysis}
                logger.info(
                    f"✅ LLM analysis completed | "
                    f"user_initiated_questions={llm_analysis.get('user_initiated_questions')} | "
                    f"session_emotion={llm_analysis.get('session_emotion')}"
                )
            else:
                logger.debug("✅ Metadata complete, skipping LLM analysis")
            
            user_initiated_questions = self._count_user_initiated_questions(
                conversation_log, metadata
            )
            # Priority: session_emotion from LLM > emotion from metadata > default
            session_emotion = metadata.get("session_emotion", metadata.get("emotion", "neutral"))
            new_memories_count = metadata.get("new_memories_count", metadata.get("new_memories_created", 0))
            
            # Calculate components
            base_score = self._calculate_base_score(total_turns)
            engagement_bonus = self._calculate_engagement_bonus(user_initiated_questions)
            emotion_bonus = self._calculate_emotion_bonus(session_emotion)
            memory_bonus = self._calculate_memory_bonus(new_memories_count)
            
            # Log calculation breakdown
            logger.info(
                f"📊 {info('Score Calculation Breakdown')} | "
                f"{key_value('total_turns', str(total_turns))} | "
                f"{key_value('user_questions', str(user_initiated_questions))} | "
                f"{key_value('emotion', session_emotion)} | "
                f"{key_value('memories', str(new_memories_count))}"
            )
            logger.info(
                f"💰 {info('Score Components')} | "
                f"{key_value('base_score', f'{base_score:.1f}')} | "
                f"{key_value('engagement_bonus', f'{engagement_bonus:.1f}')} | "
                f"{key_value('emotion_bonus', f'{emotion_bonus:.1f}')} | "
                f"{key_value('memory_bonus', f'{memory_bonus:.1f}')}"
            )
            
            # Combine all components
            friendship_score_change = (
                base_score + 
                engagement_bonus + 
                emotion_bonus + 
                memory_bonus
            )
            
            # Ensure non-negative result
            final_score = max(0.0, friendship_score_change)
            
            if final_score == 0.0:
                logger.warning(
                    f"{warning('⚠️  Final score = 0.0')} | "
                    f"Check: {key_value('total_turns', str(total_turns))}, "
                    f"{key_value('user_questions', str(user_initiated_questions))}, "
                    f"{key_value('emotion', session_emotion)}, "
                    f"{key_value('memories', str(new_memories_count))}"
                )
            
            # Return both score and updated metadata (with LLM results)
            return final_score, metadata
            
        except Exception as e:
            logger.error(f"Error in score calculation: {str(e)}")
            # Return 0.0 and original metadata on error
            return 0.0, metadata
    
    def _calculate_base_score(self, total_turns: int) -> float:
        """Calculate base score from total turns."""
        return float(total_turns) * self.BASE_SCORE_PER_TURN
    
    def _calculate_engagement_bonus(self, user_initiated_questions: int) -> float:
        """Calculate engagement bonus from user-initiated questions."""
        return float(user_initiated_questions) * self.ENGAGEMENT_BONUS_PER_QUESTION
    
    def _calculate_emotion_bonus(self, emotion: str) -> float:
        """Calculate emotion bonus from session emotion."""
        return self.EMOTION_BONUS_MAP.get(emotion.lower(), 0.0)
    
    def _calculate_memory_bonus(self, new_memories_count: int) -> float:
        """Calculate memory bonus from new memories count."""
        return float(new_memories_count) * self.MEMORY_BONUS_PER_MEMORY
    
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
            logger.warning("⚠️  Empty conversation_log, total_turns = 0")
            return 0
        
        # Debug: Đếm số messages theo speaker
        pika_count = sum(1 for msg in conversation_log if msg.get("speaker", "").lower() == "pika")
        user_count = sum(1 for msg in conversation_log if msg.get("speaker", "").lower() == "user")
        
        logger.debug(
            f"📊 Counting turns | total_messages={len(conversation_log)} | "
            f"pika={pika_count} | user={user_count}"
        )
        
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
        
        if turns == 0 and len(conversation_log) > 0:
            logger.warning(
                f"{warning('⚠️  No complete turns found!')} | "
                f"{key_value('total_messages', str(len(conversation_log)))} | "
                f"{key_value('pika', str(pika_count))} | "
                f"{key_value('user', str(user_count))} | "
                f"Reason: Conversation log chỉ có messages từ 1 speaker (không có cặp trao đổi)"
            )
        
        logger.debug(f"{success('✅')} Total complete turns: {turns}")
        return turns
    
    def _count_user_initiated_questions(
        self, 
        conversation_log: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> int:
        """
        Count user-initiated questions.
        
        Priority:
        1. Use metadata.user_initiated_questions if available (from LLM or provided)
        2. Count user messages in conversation_log as fallback
        """
        # Try to get from metadata first (more accurate, especially from LLM)
        if "user_initiated_questions" in metadata:
            return int(metadata["user_initiated_questions"])
        
        # Fallback: count user messages
        user_messages = sum(
            1 for msg in conversation_log 
            if msg.get("speaker", "").lower() == "user"
        )
        return user_messages
    
    def _has_complete_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Check if metadata has all required fields for analysis.
        
        This method checks if metadata has REAL values from LLM analysis.
        Default values like "neutral" emotion or 0 questions are considered incomplete
        and will trigger LLM analysis.
        
        Logic:
        - If metadata has flag "_llm_analyzed" = True, it means LLM already ran → complete
        - If emotion is "neutral" (default), treat as incomplete → need LLM
        - If user_initiated_questions is missing or 0, treat as incomplete → need LLM
        
        Args:
            metadata: Conversation metadata
            
        Returns:
            True if metadata has all required fields with real values, False otherwise
        """
        # Check if LLM already analyzed this conversation
        is_llm_analyzed = metadata.get("_llm_analyzed", False)
        if is_llm_analyzed:
            logger.debug("✅ Metadata already analyzed by LLM, skipping LLM call")
            return True
        
        # Check if we have user_initiated_questions
        # If missing or 0, it might be a default value → need LLM
        has_questions = "user_initiated_questions" in metadata
        questions_value = metadata.get("user_initiated_questions")
        
        # Check if we have session_emotion (not default "neutral")
        emotion_value = metadata.get("emotion") or metadata.get("session_emotion", "neutral")
        emotion_lower = str(emotion_value).lower()
        
        # If emotion is "neutral", it's likely a default value → need LLM
        # If questions is 0 or missing, it's likely a default value → need LLM
        has_real_emotion = emotion_lower != "neutral"
        has_real_questions = has_questions and questions_value is not None and questions_value > 0
        
        # Metadata is complete only if BOTH are real values (not defaults):
        # 1. Emotion is NOT "neutral" (real value from LLM), AND
        # 2. Questions > 0 (real value from LLM or explicitly provided)
        # If either is default, we need LLM to analyze
        is_complete = has_real_emotion and has_real_questions
        
        if not is_complete:
            logger.debug(
                f"⚠️  Metadata incomplete | "
                f"emotion='{emotion_value}' (is_neutral={emotion_lower == 'neutral'}) | "
                f"questions={questions_value} (has_real_value={has_real_questions})"
            )
        
        return is_complete
    
    def _get_calculation_breakdown(
        self,
        conversation_log: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get detailed breakdown of score calculation for transparency.
        
        Returns:
            Dictionary with calculation components
        """
        # 1 turn = 1 cặp trao đổi (pika + user)
        total_turns = self._count_complete_turns(conversation_log)
        user_initiated_questions = self._count_user_initiated_questions(conversation_log, metadata)
        # Priority: session_emotion from LLM > emotion from metadata > default
        session_emotion = metadata.get("session_emotion", metadata.get("emotion", "neutral"))
        new_memories_count = metadata.get("new_memories_count", metadata.get("new_memories_created", 0))
        
        base_score = self._calculate_base_score(total_turns)
        engagement_bonus = self._calculate_engagement_bonus(user_initiated_questions)
        emotion_bonus = self._calculate_emotion_bonus(session_emotion)
        memory_bonus = self._calculate_memory_bonus(new_memories_count)
        
        total_exchange_score = base_score + engagement_bonus + emotion_bonus + memory_bonus
        # Ensure non-negative
        total_exchange_score = max(0.0, total_exchange_score)
        
        return {
            "total_turns": total_turns,
            "session_emotion": session_emotion,
            "user_initiated_questions": user_initiated_questions,
            "new_memories_count": new_memories_count,
            "total_exchange_score": total_exchange_score
        }


