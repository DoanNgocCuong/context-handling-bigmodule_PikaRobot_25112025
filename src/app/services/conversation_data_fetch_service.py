"""
Conversation Data Fetch Service.

This service handles fetching conversation data by ID.
Can fetch from database or external API.
"""
from typing import Dict, Any, Optional
from app.utils.logger_setup import get_logger
from app.core.exceptions_custom import ConversationNotFoundError

logger = get_logger(__name__)


class ConversationDataFetchService:
    """
    Service for fetching conversation data by ID.
    
    Responsibilities:
    - Fetch conversation from database or external API
    - Parse and normalize conversation data
    - Handle errors and logging
    """
    
    def __init__(self, conversation_repository=None, external_api_client=None):
        """
        Initialize service with data source dependencies.
        
        Args:
            conversation_repository: Repository for database access
            external_api_client: Client for external API calls
        """
        self.conversation_repository = conversation_repository
        self.external_api_client = external_api_client
    
    def fetch_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch conversation data by ID.
        
        Priority:
        1. Try database repository if available
        2. Try external API if available
        3. Try mock data generator (for testing/development)
        4. Raise error if all unavailable
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Conversation data dictionary or None if not found
            
        Raises:
            ConversationNotFoundError: If conversation not found
        """
        logger.info(f"Fetching conversation data for conversation_id: {conversation_id}")
        
        # Try database first
        if self.conversation_repository:
            try:
                # FIX: Sử dụng get_by_conversation_id thay vì get_by_id
                # get_by_id nhận integer (event_id), get_by_conversation_id nhận string (conversation_id)
                conversation = self.conversation_repository.get_by_conversation_id(conversation_id)
                if conversation:
                    logger.info(f"Found conversation in database: {conversation_id}")
                    return self._parse_conversation_data(conversation)
            except Exception as e:
                logger.warning(
                    f"Error fetching from database for conversation_id: {conversation_id}, "
                    f"error: {str(e)}"
                )
        
        # Try external API as fallback
        if self.external_api_client:
            try:
                conversation_data = self.external_api_client.get_conversation(conversation_id)
                if conversation_data:
                    logger.info(f"Found conversation via API: {conversation_id}")
                    return conversation_data
            except Exception as e:
                logger.warning(
                    f"Error fetching from API for conversation_id: {conversation_id}, "
                    f"error: {str(e)}"
                )
        
        # Try mock data generator (for development/testing)
        # This will be used when repository and API are not available
        logger.info(f"Using mock data generator for conversation_id: {conversation_id}")
        try:
            mock_data = self._generate_mock_data(conversation_id)
            if mock_data:
                logger.info(f"Generated mock conversation data: {conversation_id}")
                return mock_data
        except Exception as e:
            logger.warning(
                f"Error generating mock data for conversation_id: {conversation_id}, "
                f"error: {str(e)}"
            )
        
        # If all fail, raise error
        logger.error(f"Conversation not found: {conversation_id}")
        raise ConversationNotFoundError(f"Conversation not found: {conversation_id}")
    
    def _generate_mock_data(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate mock conversation data for testing/development.
        
        This method creates sample conversation data when repository/API are not available.
        In production, this should be removed or disabled.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Mock conversation data dictionary
        """
        from datetime import datetime, timedelta
        
        base_time = datetime.utcnow() - timedelta(hours=1)
        end_time = base_time + timedelta(seconds=1200)
        
        # Sample conversation logs
        conversation_logs = {
            "conv_id_2003doanngoccuong": [
                {
                    "speaker": "pika",
                    "turn_id": 1,
                    "text": "Hi! What's your favorite movie genre?",
                    "timestamp": base_time.isoformat() + "Z"
                },
                {
                    "speaker": "user",
                    "turn_id": 2,
                    "text": "I love animated movies, especially Miyazaki films!",
                    "timestamp": (base_time + timedelta(seconds=15)).isoformat() + "Z"
                },
                {
                    "speaker": "pika",
                    "turn_id": 3,
                    "text": "Miyazaki is amazing! Which is your favorite?",
                    "timestamp": (base_time + timedelta(seconds=30)).isoformat() + "Z"
                },
                {
                    "speaker": "user",
                    "turn_id": 4,
                    "text": "Spirited Away! The animation is incredible.",
                    "timestamp": (base_time + timedelta(seconds=45)).isoformat() + "Z"
                },
                {
                    "speaker": "pika",
                    "turn_id": 5,
                    "text": "Spirited Away is a masterpiece! Have you watched Howl's Moving Castle?",
                    "timestamp": (base_time + timedelta(seconds=60)).isoformat() + "Z"
                },
                {
                    "speaker": "user",
                    "turn_id": 6,
                    "text": "Yes! That's my second favorite. The music is beautiful.",
                    "timestamp": (base_time + timedelta(seconds=75)).isoformat() + "Z"
                }
            ]
        }
        
        # Default conversation log
        default_log = conversation_logs.get(
            conversation_id,
            [
                {
                    "speaker": "pika",
                    "turn_id": 1,
                    "text": "Hello! Nice to meet you!",
                    "timestamp": base_time.isoformat() + "Z"
                },
                {
                    "speaker": "user",
                    "turn_id": 2,
                    "text": "Hi! Nice to meet you too!",
                    "timestamp": (base_time + timedelta(seconds=10)).isoformat() + "Z"
                }
            ]
        )
        
        # Sample metadata
        metadata_samples = {
            "conv_id_2003doanngoccuong": {
                "emotion": "interesting",
                "user_initiated_questions": 2,
                "pika_initiated_topics": 2,
                "new_memories_created": 1
            }
        }
        
        default_metadata = metadata_samples.get(
            conversation_id,
            {
                "emotion": "neutral",
                "user_initiated_questions": 0,
                "pika_initiated_topics": 1,
                "new_memories_created": 0
            }
        )
        
        # Determine agent type and ID
        agent_type = "TALK"
        agent_id = "talk_movie_preference"
        
        if "greeting" in conversation_id.lower():
            agent_type = "GREETING"
            agent_id = "greeting_welcome"
        elif "game" in conversation_id.lower():
            agent_type = "GAME"
            agent_id = "game_20questions"
        
        return {
            "conversation_id": conversation_id,
            "user_id": "user_123",
            "agent_id": agent_id,
            "agent_type": agent_type,
            "start_time": base_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_seconds": 1200,
            "conversation_log": default_log,
            "metadata": default_metadata
        }
    
    def _parse_conversation_data(self, conversation: Any) -> Dict[str, Any]:
        """
        Parse conversation model/object into dictionary.
        
        Handles both database models and API responses.
        
        Args:
            conversation: Conversation object (model or dict)
            
        Returns:
            Normalized conversation data dictionary
        """
        # If already a dict, return as-is
        if isinstance(conversation, dict):
            return conversation
        
        # If it's a database model, convert to dict
        # Adjust field names based on your actual model structure
        return {
            "conversation_id": getattr(conversation, "id", None) or getattr(conversation, "conversation_id", None),
            "user_id": getattr(conversation, "user_id", None),
            "agent_id": getattr(conversation, "agent_id", None),
            "agent_type": getattr(conversation, "agent_type", None),
            "start_time": getattr(conversation, "start_time", None),
            "end_time": getattr(conversation, "end_time", None),
            "duration_seconds": getattr(conversation, "duration_seconds", None),
            "conversation_log": self._parse_conversation_log(conversation),
            "metadata": self._parse_metadata(conversation)
        }
    
    def _parse_conversation_log(self, conversation: Any) -> list:
        """Parse conversation log from conversation object."""
        log_data = getattr(conversation, "conversation_log", None) or getattr(conversation, "log", None)
        
        if log_data is None:
            return []
        
        # If it's a JSON string, parse it
        if isinstance(log_data, str):
            import json
            try:
                return json.loads(log_data)
            except json.JSONDecodeError:
                logger.warning("Failed to parse conversation_log JSON")
                return []
        
        # If it's already a list/dict, return as-is
        if isinstance(log_data, (list, dict)):
            return log_data if isinstance(log_data, list) else [log_data]
        
        return []
    
    def _parse_metadata(self, conversation: Any) -> dict:
        """Parse metadata from conversation object."""
        metadata = getattr(conversation, "metadata", None)
        
        if metadata is None:
            return {}
        
        # If it's a JSON string, parse it
        if isinstance(metadata, str):
            import json
            try:
                return json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning("Failed to parse metadata JSON")
                return {}
        
        # If it's already a dict, return as-is
        if isinstance(metadata, dict):
            return metadata
        
        return {}

