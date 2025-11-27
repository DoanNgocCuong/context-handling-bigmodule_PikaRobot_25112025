"""
Service xử lý logic chọn lựa agent (greeting, talk, game).

Service này chịu trách nhiệm:
- Xác định friendship level dựa trên score
- Chọn greeting agent dựa trên priority logic (streak, returning user, etc.)
- Chọn talk agents dựa trên topic metrics scoring
- Chọn game agents dựa trên weighted random selection
- Enrich agent data với description và prompt từ các bảng liên quan
- Tính toán và trả về danh sách candidates đầy đủ cho user
"""
from typing import Dict, Any, List, Optional, Tuple
from random import choice
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.repositories.friendship_status_repository import FriendshipStatusRepository
from app.repositories.prompt_template_repository import PromptTemplateRepository
from app.core.constants_enums import FriendshipLevel, AgentType, PHASE3_FRIENDSHIP_SCORE_THRESHOLDS
from app.core.exceptions_custom import FriendshipNotFoundError, AgentSelectionError
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class AgentSelectionService:
    """
    Service xử lý logic chọn lựa agent cho user.
    
    Service này đóng gói toàn bộ logic chọn lựa agent bao gồm:
    - Chọn greeting agent dựa trên priority (streak, returning user, etc.)
    - Chọn talk agents dựa trên topic metrics và scoring algorithm
    - Chọn game agents dựa trên weighted random selection
    - Enrich agent data với description và prompt từ database
    
    Attributes:
        db: SQLAlchemy database session
        status_repo: Repository để truy cập friendship_status
        agent_repo: Repository để truy cập friendship_agent_mapping
        prompting_repo: Repository để truy cập agent_prompting
    """

    def __init__(self, db: Session):
        """
        Khởi tạo service với các repository cần thiết.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.status_repo = FriendshipStatusRepository(db)
        self.prompt_repo = PromptTemplateRepository(db)

    def determine_level(self, score: float) -> FriendshipLevel:
        """
        Xác định friendship level dựa trên friendship_score.
        
        Phương thức này sử dụng các ngưỡng điểm được định nghĩa trong
        PHASE3_FRIENDSHIP_SCORE_THRESHOLDS để xác định level:
        - PHASE1_STRANGER: score < 500
        - PHASE2_ACQUAINTANCE: 500 <= score <= 3000
        - PHASE3_FRIEND: score > 3000
        
        Args:
            score: Điểm friendship_score của user
            
        Returns:
            FriendshipLevel enum value tương ứng với score
            
        Example:
            >>> service = AgentSelectionService(db)
            >>> level = service.determine_level(850.5)
            >>> print(level)  # FriendshipLevel.PHASE2_ACQUAINTANCE
        """
        if score >= PHASE3_FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.PHASE3_FRIEND][0]:
            return FriendshipLevel.PHASE3_FRIEND
        if score >= PHASE3_FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.PHASE2_ACQUAINTANCE][0]:
            return FriendshipLevel.PHASE2_ACQUAINTANCE
        return FriendshipLevel.PHASE1_STRANGER

    def _build_agent_payload(
        self,
        *,
        guide,
        persona,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        topic_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compose agent payload by merging persona template, talking agenda,
        and metadata stored in agent_prompting.
        """
        agent_name = guide.agent_id.replace("_", " ").title()
        description = self._summarize_text(guide.talking_agenda)

        final_prompt = self._build_final_prompt(
            persona=persona,
            talking_agenda=guide.talking_agenda,
        )

        payload: Dict[str, Any] = {
            "agent_id": guide.agent_id,
            "agent_name": agent_name,
            "agent_type": guide.agent_type,
            "agent_description": description,
            "final_prompt": final_prompt,
            "reason": reason,
        }
        if metadata:
            payload["metadata"] = metadata.copy()
        if topic_id:
            payload.setdefault("metadata", {})["topic_id"] = topic_id
        return payload

    def select_greeting_agent(self, friendship_level: FriendshipLevel, status) -> Dict[str, Any]:
        """
        Chọn greeting agent dựa trên priority logic và prompt template mới.
        """
        guides = self.prompt_repo.get_guides(
            friendship_level=friendship_level.value,
            agent_type=AgentType.GREETING.value,
        )
        if not guides:
            raise AgentSelectionError(f"No greeting guides configured for {friendship_level.value}")

        persona = self._get_persona(friendship_level)

        now = datetime.now(timezone.utc)
        last_interaction = status.last_interaction_date or now
        if last_interaction.tzinfo is None:
            last_interaction = last_interaction.replace(tzinfo=timezone.utc)
        else:
            last_interaction = last_interaction.astimezone(timezone.utc)
        days_since_last = (now - last_interaction).days

        last_emotion = (getattr(status, "last_emotion", None) or "").lower()
        has_followup = bool(getattr(status, "last_followup_topic", None))

        heuristic_rules = [
            ("streak", status.streak_day and status.streak_day >= 5, "High streak celebration"),
            ("return", days_since_last >= 7, "Returning user greeting"),
            ("emotion", last_emotion in {"sad", "angry"}, "Emotion check-in"),
            ("follow", has_followup, "Follow-up topic greeting"),
        ]

        for keyword, condition, reason in heuristic_rules:
            if not condition:
                continue
            filtered = self._filter_guides_by_keyword(guides, keyword)
            if filtered:
                selected = choice(filtered)
                return self._build_agent_payload(
                    guide=selected,
                    persona=persona,
                    reason=reason,
                    topic_id=selected.topic_id,
                )

        selected = choice(guides)
        return self._build_agent_payload(
            guide=selected,
            persona=persona,
            reason="Phase default greeting",
            topic_id=selected.topic_id,
        )

    def select_talk_agents(self, friendship_level: FriendshipLevel, status, count: int = 3) -> List[Dict[str, Any]]:
        """
        Chọn talk agents dựa trên topic metrics và prompt template mới.
        """
        persona = self._get_persona(friendship_level)
        topic_metrics = self._get_topic_metrics(status)
        prioritized_topics = self._prioritize_topics(topic_metrics)

        selected: List[Dict[str, Any]] = []
        used_agent_ids = set()

        for topic_id, topic_data in prioritized_topics:
            if len(selected) >= count:
                break

            target_level = self._resolve_topic_level(
                topic_level=topic_data.get("friendship_level"),
                fallback=friendship_level,
            )
            guides = self.prompt_repo.get_guides(
                friendship_level=target_level,
                agent_type=AgentType.TALK.value,
                topic_id=topic_id,
            )
            guides = [g for g in guides if g.agent_id not in used_agent_ids]
            if not guides:
                continue

            guide = choice(guides)
            used_agent_ids.add(guide.agent_id)

            topic_score = topic_data.get("score", 0.0)
            total_turns = topic_data.get("turns") or topic_data.get("total_turns") or 0
            reason = "Topic preference" if topic_score > 0 else "Exploration candidate"

            payload = self._build_agent_payload(
                guide=guide,
                persona=persona,
                reason=reason,
                metadata={
                    "topic_score": topic_score,
                    "total_turns": total_turns,
                },
                topic_id=topic_id,
            )
            selected.append(payload)

        if len(selected) >= count:
            return selected

        # Fallback: lấy các guide chung của phase nếu chưa đủ số lượng
        fallback_guides = self.prompt_repo.get_guides(
            friendship_level=friendship_level.value,
            agent_type=AgentType.TALK.value,
        )
        fallback_iter = [g for g in fallback_guides if g.agent_id not in used_agent_ids]
        idx = 0
        while len(selected) < count and fallback_iter:
            guide = fallback_iter[idx % len(fallback_iter)]
            selected.append(
                self._build_agent_payload(
                    guide=guide,
                    persona=persona,
                    reason="Phase fallback",
                    topic_id=guide.topic_id,
                )
            )
            idx += 1

        return selected

    def select_game_agents(self, friendship_level: FriendshipLevel, count: int = 2) -> List[Dict[str, Any]]:
        """
        Chọn game agents dựa trên prompt template mới.
        """
        guides = self.prompt_repo.get_guides(
            friendship_level=friendship_level.value,
            agent_type=AgentType.GAME.value,
        )
        if not guides:
            raise AgentSelectionError(f"No game guides configured for {friendship_level.value}")

        persona = self._get_persona(friendship_level)
        pool = guides.copy()
        selected: List[Dict[str, Any]] = []

        idx = 0
        while pool and len(selected) < count:
            guide = pool[idx % len(pool)]
            selected.append(
                self._build_agent_payload(
                    guide=guide,
                    persona=persona,
                    reason="Phase activity",
                    topic_id=guide.topic_id,
                )
            )
            idx += 1

        return selected

    def compute_candidates(self, user_id: str) -> Dict[str, Any]:
        """
        Tính toán và trả về danh sách candidates đầy đủ cho user.
        
        Phương thức này thực hiện các bước:
        1. Lấy friendship_status của user
        2. Xác định friendship_level dựa trên score
        3. Chọn greeting agent
        4. Chọn talk agents (mặc định 2)
        5. Chọn game agents (mặc định 2)
        6. Trả về payload đầy đủ với tất cả agents đã được enrich
        
        Tất cả agents trong response đã được enrich với:
        - agent_description từ friendship_agent_mapping
        - final_prompt từ agent_prompting (nếu có)
        
        Args:
            user_id: ID của user cần tính toán candidates
            
        Returns:
            Dictionary chứa:
            - user_id: ID của user
            - friendship_level: Level hiện tại (PHASE1_STRANGER/PHASE2_ACQUAINTANCE/PHASE3_FRIEND)
            - greeting_agent: 1 greeting agent đã được enrich
            - talk_agents: List các talk agents đã được enrich (thường 2)
            - game_agents: List các game agents đã được enrich (thường 2)
            
        Raises:
            FriendshipNotFoundError: Nếu không tìm thấy friendship_status của user
            AgentSelectionError: Nếu không có talk/game agents cho level này
            
        Example:
            >>> service = AgentSelectionService(db)
            >>> candidates = service.compute_candidates("user_123")
            >>> print(candidates["friendship_level"])  # "PHASE2_ACQUAINTANCE"
            >>> print(len(candidates["talk_agents"]))  # 2
        """
        status = self.status_repo.get_by_user_id(user_id)
        if not status:
            raise FriendshipNotFoundError(f"Friendship status not found for user {user_id}")

        level = self.determine_level(status.friendship_score or 0.0)

        greeting_agent = self.select_greeting_agent(level, status)
        talk_agents = self.select_talk_agents(level, status, count=3)
        if not talk_agents:
            raise AgentSelectionError(f"No talk agents available for level {level.value}")

        game_agents = self.select_game_agents(level, count=2)
        if not game_agents:
            raise AgentSelectionError(f"No game agents available for level {level.value}")

        return {
            "user_id": status.user_id,
            "friendship_level": level.value,
            "greeting_agent": greeting_agent,
            "talk_agents": talk_agents,
            "game_agents": game_agents
        }

    def _get_persona(self, friendship_level: FriendshipLevel):
        persona = self.prompt_repo.get_persona_by_phase(friendship_level.value)
        if not persona:
            logger.warning("Persona template missing for level %s", friendship_level.value)
        return persona

    @staticmethod
    def _summarize_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        for line in text.strip().splitlines():
            clean_line = line.strip()
            if clean_line:
                return clean_line[:240]
        return text.strip()[:240]

    def _build_final_prompt(self, *, persona, talking_agenda: Optional[str]) -> Optional[str]:
        blocks: List[str] = []
        if persona:
            if persona.context_style_guideline:
                blocks.append(persona.context_style_guideline.strip())
            if persona.user_profile:
                blocks.append(persona.user_profile.strip())
        if talking_agenda:
            blocks.append(talking_agenda.strip())
        final_prompt = "\n\n".join(blocks).strip()
        return final_prompt or None

    @staticmethod
    def _get_topic_metrics(status) -> Dict[str, Any]:
        return getattr(status, "topic_metrics", None) or {}

    def _prioritize_topics(self, topic_metrics: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        if not topic_metrics:
            return []
        untouched = []
        others = []
        for topic_id, meta in topic_metrics.items():
            score = meta.get("score", 0.0)
            (untouched if score <= 0 else others).append((topic_id, meta))

        others.sort(
            key=lambda item: (
                -(item[1].get("score", 0.0) or 0.0),
                self._last_interaction_sort_key(item[1]),
            )
        )
        return untouched + others

    def _resolve_topic_level(self, topic_level: Optional[str], fallback: FriendshipLevel) -> str:
        if not topic_level:
            return fallback.value
        normalized = topic_level.upper()
        alias_map = {
            "STRANGER": FriendshipLevel.PHASE1_STRANGER.value,
            "PHASE1_STRANGER": FriendshipLevel.PHASE1_STRANGER.value,
            "ACQUAINTANCE": FriendshipLevel.PHASE2_ACQUAINTANCE.value,
            "PHASE2_ACQUAINTANCE": FriendshipLevel.PHASE2_ACQUAINTANCE.value,
            "FRIEND": FriendshipLevel.PHASE3_FRIEND.value,
            "PHASE3_FRIEND": FriendshipLevel.PHASE3_FRIEND.value,
        }
        return alias_map.get(normalized, fallback.value)

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _last_interaction_sort_key(self, meta: Dict[str, Any]) -> float:
        dt = self._parse_datetime(meta.get("last_date") or meta.get("last_talked_date"))
        if not dt:
            return float("inf")
        return dt.timestamp()

    @staticmethod
    def _filter_guides_by_keyword(guides, keyword: str):
        key = keyword.lower()
        return [
            guide
            for guide in guides
            if (guide.topic_id and key in guide.topic_id.lower())
            or (guide.agent_id and key in guide.agent_id.lower())
        ]

