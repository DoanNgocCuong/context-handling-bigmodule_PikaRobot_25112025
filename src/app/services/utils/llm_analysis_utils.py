"""
LLM Analysis Utilities for Conversation Analysis.

This module provides utilities for analyzing conversations using Groq LLM
with Langfuse observability integration and Memory API (Mem0).

Functions:
- analyze_user_initiated_questions: Count user-initiated questions via LLM
- analyze_session_emotion: Detect session emotion via LLM
- extract_memories_from_api: Extract memories using Mem0 API
- format_conversation_for_llm: Format conversation log for LLM input
- format_conversation_for_memory_api: Format conversation log for Memory API
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
from groq import Groq
from langfuse import Langfuse
from langfuse.decorators import observe
from app.core.config_settings import settings
from app.utils.logger_setup import get_logger
from app.core.exceptions_custom import InvalidScoreError

logger = get_logger(__name__)

# Valid emotions for session emotion analysis
VALID_EMOTIONS = ["interesting", "boring", "neutral", "angry", "happy", "sad"]


class LLMAnalysisClient:
    """
    Client for LLM analysis using Groq with Langfuse observability.
    
    This class handles:
    - Groq client initialization
    - Langfuse observability setup
    - LLM prompt execution with error handling
    """
    
    def __init__(self):
        """Initialize Groq client and Langfuse."""
        # Initialize Langfuse for observability (only if enabled and keys provided)
        if settings.LANGFUSE_ENABLED and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            try:
                self.langfuse = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
                logger.info("✅ Langfuse initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize Langfuse: {e}, continuing without it")
                self.langfuse = None
        else:
            self.langfuse = None
        
        # Initialize Groq client
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                self.model = settings.GROQ_MODEL or "openai/gpt-oss-20b"
                self.enabled = settings.LLM_ANALYSIS_ENABLED
                logger.info(f"✅ Groq client initialized | model={self.model} | enabled={self.enabled}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq client: {e}")
                self.client = None
                self.enabled = False
        else:
            self.client = None
            self.enabled = False
            logger.warning("⚠️  GROQ_API_KEY not provided. LLM analysis will be disabled.")
    
    def is_enabled(self) -> bool:
        """Check if LLM analysis is enabled and client is available."""
        return self.enabled and self.client is not None
    
    @observe(name="llm_analyze_user_questions")
    def analyze_user_questions(
        self,
        formatted_conversation: str,
        conversation_id: Optional[str] = None
    ) -> int:
        """
        Analyze user-initiated questions via LLM.
        
        Args:
            formatted_conversation: Formatted conversation text
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Count of user-initiated questions (>= 0)
        """
        if not self.is_enabled():
            logger.debug("LLM analysis disabled, returning 0 for user_initiated_questions")
            return 0
        
        system_prompt = (
            "You are an engagement analyst. Count how many times the USER actively asked a question."
        )
        user_prompt = f"""
Conversation:
{formatted_conversation}

Return JSON:
{{
    "user_initiated_questions": <integer count of questions the USER initiated (>=0)>
}}

Rules:
- Only count USER messages that introduce a question (end with '?' or interrogative structure)
- Do not count answers to Pika's questions
- If unsure, err on the side of under-counting
- Count only questions that the USER initiated, not responses to Pika's questions
"""
        try:
            response = self._invoke_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                conversation_id=conversation_id,
                metric_label="user_initiated_questions"
            )
            data = self._parse_json_response(response)
            
            # Log parsed JSON data
            logger.info(
                f"🔍 LLM 'user_initiated_questions' PARSED JSON: {data}"
            )
            
            count = int(data.get("user_initiated_questions", 0))
            result = max(0, count)
            logger.info(f"✅ LLM user_initiated_questions: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ LLM analysis failed for user_initiated_questions: {e}")
            return 0
    
    @observe(name="llm_analyze_session_emotion")
    def analyze_session_emotion(
        self,
        formatted_conversation: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Analyze session emotion via LLM.
        
        Args:
            formatted_conversation: Formatted conversation text
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Session emotion string (one of: interesting, boring, neutral, angry, happy, sad)
        """
        if not self.is_enabled():
            logger.debug("LLM analysis disabled, returning 'neutral' for session_emotion")
            return "neutral"
        
        system_prompt = (
            "You are an emotion analyst. Determine the overall emotion of the conversation session."
        )
        user_prompt = f"""
Conversation:
{formatted_conversation}

Return JSON:
{{
    "session_emotion": "<one of: interesting, boring, neutral, angry, happy, sad>"
}}

Rules:
- Consider the overall tone/feeling of the entire session
- Choose exactly one value from the allowed list
- 'interesting': User is engaged, asking questions, showing curiosity
- 'boring': User seems disinterested, giving short responses, not engaging
- 'neutral': Standard conversation, no strong emotion
- 'angry': User shows frustration, negative tone, complaints
- 'happy': User shows positive emotion, excitement, joy
- 'sad': User shows sadness, disappointment, negative feelings
"""
        try:
            response = self._invoke_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                conversation_id=conversation_id,
                metric_label="session_emotion"
            )
            data = self._parse_json_response(response)
            
            # Log parsed JSON data
            logger.info(
                f"🔍 LLM 'session_emotion' PARSED JSON: {data}"
            )
            
            emotion = str(data.get("session_emotion", "neutral")).lower()
            
            # Validate emotion
            if emotion not in VALID_EMOTIONS:
                logger.warning(f"⚠️  Invalid session_emotion '{emotion}', defaulting to 'neutral'")
                emotion = "neutral"
            
            logger.info(f"✅ LLM session_emotion: {emotion}")
            return emotion
        except Exception as e:
            logger.error(f"❌ LLM analysis failed for session_emotion: {e}")
            return "neutral"
    
    def _invoke_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_id: Optional[str],
        metric_label: str
    ) -> str:
        """
        Invoke Groq LLM with provided prompts.
        
        Args:
            system_prompt: System prompt for LLM
            user_prompt: User prompt with conversation data
            conversation_id: Optional conversation ID for tracking
            metric_label: Label for logging (e.g., "user_initiated_questions")
            
        Returns:
            LLM response text
            
        Raises:
            InvalidScoreError: If LLM client is not initialized
        """
        if not self.client:
            raise InvalidScoreError("LLM client not initialized")
        
        logger.info(
            f"🤖 LLM subtask '{metric_label}' started | "
            f"conversation_id={conversation_id} | model={self.model}"
        )
        
        # Log prompts for debugging
        logger.debug(
            f"📋 LLM '{metric_label}' SYSTEM PROMPT:\n{system_prompt}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=10000,  # Groq uses max_tokens, not max_completion_tokens
                top_p=1,
                stream=False
            )
            result_text = response.choices[0].message.content.strip()
            
            # Log full raw response for debugging
            logger.info(
                f"📝 LLM '{metric_label}' RAW RESPONSE (full):\n"
                f"{result_text}"
            )
            
            # Log prompt preview (first 500 chars)
            prompt_preview = user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt
            logger.debug(
                f"📋 LLM '{metric_label}' PROMPT PREVIEW:\n"
                f"{prompt_preview}"
            )
            
            return result_text
        except Exception as e:
            logger.error(f"❌ LLM API call failed for '{metric_label}': {e}")
            raise
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM.
        
        Args:
            response_text: Raw response text from LLM
            
        Returns:
            Parsed JSON dictionary (empty dict if parsing fails)
        """
        try:
            # Try to extract JSON from response (in case LLM adds extra text)
            # Look for JSON object in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                logger.debug(f"📦 Extracted JSON text: {json_text}")
                parsed = json.loads(json_text)
                logger.debug(f"✅ Successfully parsed JSON: {parsed}")
                return parsed
            else:
                # Try parsing entire response
                logger.debug(f"📦 Attempting to parse entire response as JSON")
                parsed = json.loads(response_text)
                logger.debug(f"✅ Successfully parsed JSON: {parsed}")
                return parsed
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse LLM response as JSON: {e}")
            logger.error(f"   Full response text: {response_text}")
            logger.error(f"   Response length: {len(response_text)} chars")
            return {}


def format_conversation_for_llm(conversation_log: List[Dict[str, Any]]) -> str:
    """
    Format conversation log for LLM input.
    
    Args:
        conversation_log: List of conversation messages with 'speaker' and 'text' keys
        
    Returns:
        Formatted conversation string
    """
    formatted_lines = []
    for idx, msg in enumerate(conversation_log, 1):
        speaker = msg.get("speaker", "unknown")
        text = msg.get("text", "")
        formatted_lines.append(f"{idx}. [{speaker.upper()}]: {text}")
    
    return "\n".join(formatted_lines)


def format_conversation_for_memory_api(
    conversation_log: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Format conversation log for Memory API (Mem0).
    
    Memory API expects format:
    [
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "..."}
    ]
    
    Supports both formats:
    1. Standardized format: {"speaker": "pika"/"user", "text": "..."}
    2. API format: {"character": "BOT_RESPONSE_CONVERSATION"/"USER", "content": "..."}
    
    Args:
        conversation_log: List of conversation messages
        
    Returns:
        Formatted conversation list for Memory API
    """
    formatted_conversation = []
    skipped_count = 0
    
    for idx, msg in enumerate(conversation_log):
        role = None
        content = None
        
        # Try standardized format first (speaker/text)
        if "speaker" in msg and "text" in msg:
            speaker = msg.get("speaker", "").lower()
            text = msg.get("text", "").strip()
            
            # Map speaker to role
            if speaker == "pika":
                role = "assistant"
                content = text
            elif speaker == "user":
                role = "user"
                content = text
            else:
                logger.debug(
                    f"⚠️  Unknown speaker '{speaker}' in message {idx}, skipping"
                )
                skipped_count += 1
                continue
        
        # Try API format (character/content)
        elif "character" in msg and "content" in msg:
            character = msg.get("character", "").strip()
            text = msg.get("content", "").strip()
            
            # Map character to role
            character_upper = character.upper()
            if "BOT" in character_upper or "PIKA" in character_upper:
                role = "assistant"
                content = text
            elif "USER" in character_upper:
                role = "user"
                content = text
            else:
                logger.debug(
                    f"⚠️  Unknown character '{character}' in message {idx}, skipping"
                )
                skipped_count += 1
                continue
        
        # Unknown format
        else:
            logger.debug(
                f"⚠️  Unknown message format at index {idx}, keys: {list(msg.keys())}, skipping"
            )
            skipped_count += 1
            continue
        
        # Skip empty content
        if not content:
            logger.debug(f"⏭️  Skipping empty message at index {idx}")
            skipped_count += 1
            continue
        
        formatted_conversation.append({
            "role": role,
            "content": content
        })
    
    if skipped_count > 0:
        logger.warning(
            f"⚠️  Skipped {skipped_count} messages when formatting for Memory API"
        )
    
    logger.debug(
        f"📋 Formatted {len(formatted_conversation)} messages for Memory API | "
        f"skipped={skipped_count}"
    )
    
    return formatted_conversation


@observe(name="memory_api_extract_facts")
def extract_memories_from_api(
    conversation_log: List[Dict[str, Any]],
    user_id: str,
    conversation_id: Optional[str] = None
) -> int:
    """
    Extract memories from conversation using Mem0 API.
    
    Args:
        conversation_log: List of conversation messages
        user_id: User ID for the conversation
        conversation_id: Optional conversation ID for tracking
        
    Returns:
        Count of new memories extracted (>= 0)
    """
    if not settings.MEMORY_API_ENABLED:
        logger.warning(
            f"⚠️  Memory API disabled | "
            f"MEMORY_API_ENABLED={settings.MEMORY_API_ENABLED} | "
            f"Returning 0 for new_memories_count"
        )
        return 0
    
    if not settings.MEMORY_API_URL:
        logger.warning(
            f"⚠️  Memory API URL not set | "
            f"MEMORY_API_URL={'not set' if not settings.MEMORY_API_URL else 'set'} | "
            f"Returning 0 for new_memories_count"
        )
        return 0
    
    try:
        logger.info(
            f"🔍 Starting Memory API extraction | "
            f"conversation_id={conversation_id} | user_id={user_id}"
        )
        
        # Format conversation for Memory API
        formatted_conversation = format_conversation_for_memory_api(conversation_log)
        
        if not formatted_conversation:
            logger.warning("⚠️  No valid conversation messages to extract memories")
            return 0
        
        # Prepare request payload
        payload = {
            "user_id": user_id,
            "conversation_id": conversation_id or "unknown",
            "conversation": formatted_conversation
        }
        
        # Log full payload for debugging
        logger.info(
            f"📤 Memory API request payload:\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )
        
        # Call Memory API
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{settings.MEMORY_API_URL}/extract_facts",
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            result = response.json()
        
        # Log full response for debugging
        logger.info(
            f"📥 Memory API response (full):\n"
            f"{json.dumps(result, ensure_ascii=False, indent=2)}"
        )
        
        # Extract count from response
        count = result.get("count", 0)
        facts = result.get("facts", [])
        status = result.get("status", "unknown")
        
        logger.info(
            f"✅ Memory API extraction completed | "
            f"conversation_id={conversation_id} | "
            f"status={status} | "
            f"new_memories_count={count}"
        )
        
        if count > 0:
            logger.info(f"📝 Extracted {count} memories:")
            for i, fact in enumerate(facts[:5], 1):  # Log first 5 facts
                fact_value = fact.get("fact_value", "")
                fact_id = fact.get("id", "unknown")
                logger.info(f"   {i}. [{fact_id}] {fact_value}")
        
        return max(0, int(count))
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Memory API HTTP error: {e}")
        return 0
    except Exception as e:
        logger.error(f"❌ Memory API extraction failed: {e}", exc_info=True)
        return 0


def analyze_conversation_with_llm(
    conversation_log: List[Dict[str, Any]],
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    llm_client: Optional[LLMAnalysisClient] = None
) -> Dict[str, Any]:
    """
    Analyze conversation using LLM and Memory API to extract metrics.
    
    This function runs 3 analyses in parallel:
    1. user_initiated_questions: Count of questions user actively asked (LLM)
    2. session_emotion: Overall emotion of the conversation session (LLM)
    3. new_memories_count: Number of new memories extracted (Memory API)
    
    Args:
        conversation_log: List of conversation messages
        conversation_id: Optional conversation ID for tracking
        user_id: User ID for Memory API call
        llm_client: Optional LLM client instance (creates new one if not provided)
        
    Returns:
        Dictionary with:
        - user_initiated_questions: int
        - session_emotion: str
        - new_memories_count: int
    """
    # Initialize LLM client if not provided
    if llm_client is None:
        llm_client = LLMAnalysisClient()
    
    # Initialize analysis result
    analysis = {
        "user_initiated_questions": 0,
        "session_emotion": "neutral",
        "new_memories_count": 0
    }
    
    # Check if LLM is enabled
    llm_enabled = llm_client.is_enabled()
    if not llm_enabled:
        logger.warning(
            f"⚠️  LLM analysis disabled | "
            f"LLM_ANALYSIS_ENABLED={settings.LLM_ANALYSIS_ENABLED} | "
            f"GROQ_API_KEY={'set' if settings.GROQ_API_KEY else 'not set'}"
        )
    
    try:
        logger.info(
            f"🔍 Starting parallel analysis (2 LLMs + 1 Memory API) | "
            f"conversation_id={conversation_id} | user_id={user_id}"
        )
        
        # Format conversation for LLM
        formatted_conversation = format_conversation_for_llm(conversation_log)
        logger.debug(f"Formatted conversation length: {len(formatted_conversation)} chars")
        
        # Prepare tasks: 2 LLMs + 1 Memory API
        tasks = []
        
        # Task 1: LLM - user_initiated_questions
        if llm_enabled:
            tasks.append((
                "user_initiated_questions",
                lambda: llm_client.analyze_user_questions(formatted_conversation, conversation_id)
            ))
        else:
            tasks.append(("user_initiated_questions", lambda: 0))
        
        # Task 2: LLM - session_emotion
        if llm_enabled:
            tasks.append((
                "session_emotion",
                lambda: llm_client.analyze_session_emotion(formatted_conversation, conversation_id)
            ))
        else:
            tasks.append(("session_emotion", lambda: "neutral"))
        
        # Task 3: Memory API - new_memories_count
        if user_id:
            if settings.MEMORY_API_ENABLED and settings.MEMORY_API_URL:
                logger.info(
                    f"🔍 Memory API task added | "
                    f"conversation_id={conversation_id} | user_id={user_id} | "
                    f"url={settings.MEMORY_API_URL}"
                )
                tasks.append((
                    "new_memories_count",
                    lambda: extract_memories_from_api(conversation_log, user_id, conversation_id)
                ))
            else:
                logger.warning(
                    f"⚠️  Memory API not enabled or URL not set, skipping | "
                    f"MEMORY_API_ENABLED={settings.MEMORY_API_ENABLED} | "
                    f"MEMORY_API_URL={'set' if settings.MEMORY_API_URL else 'not set'}"
                )
                tasks.append(("new_memories_count", lambda: 0))
        else:
            logger.warning("⚠️  user_id not provided, skipping Memory API extraction")
            tasks.append(("new_memories_count", lambda: 0))
        
        # Run all 3 tasks in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {
                executor.submit(task): metric
                for metric, task in tasks
            }
            
            for future in as_completed(future_map):
                metric = future_map[future]
                try:
                    value = future.result()
                    analysis[metric] = value
                    logger.info(f"✅ Analysis subtask '{metric}' completed with value={value}")
                except Exception as e:
                    logger.error(f"❌ Analysis subtask '{metric}' failed: {e}", exc_info=True)
        
        logger.info(
            f"📊 Parallel analysis completed for conversation_id={conversation_id}:\n"
            f"   - user_initiated_questions: {analysis.get('user_initiated_questions')}\n"
            f"   - session_emotion: {analysis.get('session_emotion')}\n"
            f"   - new_memories_count: {analysis.get('new_memories_count')}"
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Parallel analysis failed: {e}", exc_info=True)
        return {
            "user_initiated_questions": 0,
            "session_emotion": "neutral",
            "new_memories_count": 0
        }

