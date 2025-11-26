"""
Friendship Score Calculation Service.

This service calculates friendship score changes from conversation data.
Follows Single Responsibility Principle (SRP).
"""
from typing import Dict, List, Any, Optional
from app.utils.logger_setup import get_logger
from app.core.exceptions_custom import InvalidScoreError, ConversationNotFoundError

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
    BASE_SCORE_PER_TURN: float = 0.5
    ENGAGEMENT_BONUS_PER_QUESTION: float = 3.0
    MEMORY_BONUS_PER_MEMORY: float = 5.0
    
    # Emotion bonus mapping
    EMOTION_BONUS_MAP: Dict[str, float] = {
        "interesting": 15.0,
        "boring": -15.0,
        "happy": 10.0,
        "sad": -5.0,
        "neutral": 0.0,
        "angry": -10.0
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
            
            # Step 3: Calculate score change
            score_change = self.calculate_friendship_score_change(
                conversation_log=conversation_log,
                metadata=metadata
            )
            
            # Step 4: Get calculation breakdown for transparency
            calculation_details = self._get_calculation_breakdown(
                conversation_log=conversation_log,
                metadata=metadata
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
    ) -> float:
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
            Friendship score change (always >= 0)
        """
        try:
            # Extract metrics
            total_turns = len(conversation_log)
            user_initiated_questions = self._count_user_initiated_questions(
                conversation_log, metadata
            )
            session_emotion = metadata.get("emotion", metadata.get("session_emotion", "neutral"))
            new_memories_count = metadata.get("new_memories_count", metadata.get("new_memories_created", 0))
            
            # Calculate components
            base_score = self._calculate_base_score(total_turns)
            engagement_bonus = self._calculate_engagement_bonus(user_initiated_questions)
            emotion_bonus = self._calculate_emotion_bonus(session_emotion)
            memory_bonus = self._calculate_memory_bonus(new_memories_count)
            
            # Combine all components
            friendship_score_change = (
                base_score + 
                engagement_bonus + 
                emotion_bonus + 
                memory_bonus
            )
            
            # Ensure non-negative result
            return max(0.0, friendship_score_change)
            
        except Exception as e:
            logger.error(f"Error in score calculation: {str(e)}")
            raise InvalidScoreError(f"Score calculation failed: {str(e)}") from e
    
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
    
    def _count_user_initiated_questions(
        self, 
        conversation_log: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> int:
        """
        Count user-initiated questions.
        
        Priority:
        1. Use metadata.user_initiated_questions if available
        2. Count user messages in conversation_log as fallback
        """
        # Try to get from metadata first (more accurate)
        if "user_initiated_questions" in metadata:
            return int(metadata["user_initiated_questions"])
        
        # Fallback: count user messages
        user_messages = sum(
            1 for msg in conversation_log 
            if msg.get("speaker", "").lower() == "user"
        )
        return user_messages
    
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
        total_turns = len(conversation_log)
        user_initiated_questions = self._count_user_initiated_questions(conversation_log, metadata)
        session_emotion = metadata.get("emotion", metadata.get("session_emotion", "neutral"))
        new_memories_count = metadata.get("new_memories_count", metadata.get("new_memories_created", 0))
        
        base_score = self._calculate_base_score(total_turns)
        engagement_bonus = self._calculate_engagement_bonus(user_initiated_questions)
        emotion_bonus = self._calculate_emotion_bonus(session_emotion)
        memory_bonus = self._calculate_memory_bonus(new_memories_count)
        
        total_score = base_score + engagement_bonus + emotion_bonus + memory_bonus
        final_score = max(0.0, total_score)
        
        return {
            "total_turns": total_turns,
            "user_initiated_questions": user_initiated_questions,
            "session_emotion": session_emotion,
            "new_memories_count": new_memories_count,
            "base_score": base_score,
            "engagement_bonus": engagement_bonus,
            "emotion_bonus": emotion_bonus,
            "memory_bonus": memory_bonus,
            "total_score_before_clamp": total_score,
            "final_score_change": final_score
        }


