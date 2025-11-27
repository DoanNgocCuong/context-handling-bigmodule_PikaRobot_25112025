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
            "friendship_level": guide.friendship_level,
            "agent_description": description,
            "final_prompt": final_prompt,
            "reason": reason,
        }
        # Thêm topic_id vào top level (ưu tiên từ parameter, nếu không có thì dùng từ guide)
        if topic_id:
            payload["topic_id"] = topic_id
        elif guide.topic_id:
            payload["topic_id"] = guide.topic_id
        else:
            payload["topic_id"] = None
        
        if metadata:
            payload["metadata"] = metadata.copy()
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
        Chọn talk agents dựa trên topic metrics và topic_level mapping.
        
        Logic mới:
        - 2 Talk sở thích: Lấy 2 topic có topic_score cao nhất → check topic_level → mapping agent_id
        - 1 Talk khám phá: Lấy 1 topic có total_turns thấp nhất → check topic_level → mapping agent_id
        """
        persona = self._get_persona(friendship_level)
        topic_metrics = self._get_topic_metrics(status)
        
        selected: List[Dict[str, Any]] = []
        used_agent_ids = set()
        used_topic_ids = set()

        # 1. Chọn 2 Talk sở thích (topic_score cao nhất)
        preference_topics = self._get_topics_by_score(topic_metrics, top_n=2, exclude_topic_ids=used_topic_ids)
        for topic_id, topic_data in preference_topics:
            if len(selected) >= 2:
                break
            
            topic_level = self._resolve_topic_level(
                topic_level=topic_data.get("friendship_level"),
                fallback=friendship_level,
            )
            guides = self.prompt_repo.get_guides(
                friendship_level=topic_level,
                agent_type=AgentType.TALK.value,
                topic_id=topic_id,
            )
            guides = [g for g in guides if g.agent_id not in used_agent_ids]
            if not guides:
                continue

            guide = choice(guides)
            used_agent_ids.add(guide.agent_id)
            used_topic_ids.add(topic_id)

            topic_score = topic_data.get("score", 0.0)
            total_turns = topic_data.get("turns") or topic_data.get("total_turns") or 0

            payload = self._build_agent_payload(
                guide=guide,
                persona=persona,
                reason="Topic preference",
                metadata={
                    "topic_score": topic_score,
                    "total_turns": total_turns,
                },
                topic_id=topic_id,
            )
            selected.append(payload)

        # 2. Chọn 1 Talk khám phá (total_turns thấp nhất)
        exploration_topics = self._get_topics_by_turns(topic_metrics, top_n=1, exclude_topic_ids=used_topic_ids)
        for topic_id, topic_data in exploration_topics:
            if len(selected) >= count:
                break

            topic_level = self._resolve_topic_level(
                topic_level=topic_data.get("friendship_level"),
                fallback=friendship_level,
            )
            guides = self.prompt_repo.get_guides(
                friendship_level=topic_level,
                agent_type=AgentType.TALK.value,
                topic_id=topic_id,
            )
            guides = [g for g in guides if g.agent_id not in used_agent_ids]
            if not guides:
                continue

            guide = choice(guides)
            used_agent_ids.add(guide.agent_id)
            used_topic_ids.add(topic_id)

            topic_score = topic_data.get("score", 0.0)
            total_turns = topic_data.get("turns") or topic_data.get("total_turns") or 0

            payload = self._build_agent_payload(
                guide=guide,
                persona=persona,
                reason="Exploration candidate",
                metadata={
                    "topic_score": topic_score,
                    "total_turns": total_turns,
                },
                topic_id=topic_id,
            )
            selected.append(payload)

        # 3. Fallback: nếu chưa đủ, random từ các topic còn lại hoặc guides chung
        if len(selected) < count:
            remaining_topics = [
                (tid, tdata) for tid, tdata in topic_metrics.items()
                if tid not in used_topic_ids
            ]
            for topic_id, topic_data in remaining_topics:
                if len(selected) >= count:
                    break

                topic_level = self._resolve_topic_level(
                    topic_level=topic_data.get("friendship_level"),
                    fallback=friendship_level,
                )
                guides = self.prompt_repo.get_guides(
                    friendship_level=topic_level,
                    agent_type=AgentType.TALK.value,
                    topic_id=topic_id,
                )
                guides = [g for g in guides if g.agent_id not in used_agent_ids]
                if not guides:
                    continue

                guide = choice(guides)
                used_agent_ids.add(guide.agent_id)
                used_topic_ids.add(topic_id)

                payload = self._build_agent_payload(
                    guide=guide,
                    persona=persona,
                    reason="Random topic",
                    metadata={
                        "topic_score": topic_data.get("score", 0.0),
                        "total_turns": topic_data.get("turns") or topic_data.get("total_turns") or 0,
                    },
                    topic_id=topic_id,
                )
                selected.append(payload)

        # 4. Final fallback: lấy guides từ PHASE1_STRANGER cho topics chưa học
        # Logic: Topics chưa có trong topic_metrics phải dùng PHASE1_STRANGER
        if len(selected) < count:
            # Ưu tiên query PHASE1_STRANGER cho topics chưa học
            phase1_guides = self.prompt_repo.get_guides(
                friendship_level=FriendshipLevel.PHASE1_STRANGER.value,
                agent_type=AgentType.TALK.value,
            )
            phase1_iter = [
                g for g in phase1_guides 
                if g.agent_id not in used_agent_ids 
                and g.topic_id not in used_topic_ids
            ]
            
            idx = 0
            while len(selected) < count and phase1_iter:
                guide = phase1_iter[idx % len(phase1_iter)]
                selected.append(
                    self._build_agent_payload(
                        guide=guide,
                        persona=persona,
                        reason="New topic exploration (PHASE1)",
                        topic_id=guide.topic_id,
                    )
                )
                used_agent_ids.add(guide.agent_id)
                used_topic_ids.add(guide.topic_id)
                idx += 1

        return selected

    def select_game_agents(self, friendship_level: FriendshipLevel, status, count: int = 2) -> List[Dict[str, Any]]:
        """
        Chọn game agents dựa trên topic metrics và topic_level mapping.
        
        Logic mới:
        - 1 Game sở thích: Lấy 1 topic có topic_score cao nhất → check topic_level → mapping agent_id
        - 1 Game khám phá: Lấy 1 topic có total_turns thấp nhất → check topic_level → mapping agent_id
        """
        persona = self._get_persona(friendship_level)
        topic_metrics = self._get_topic_metrics(status)
        
        selected: List[Dict[str, Any]] = []
        used_agent_ids = set()
        used_topic_ids = set()

        # 1. Chọn 1 Game sở thích (topic_score cao nhất)
        preference_topics = self._get_topics_by_score(topic_metrics, top_n=1, exclude_topic_ids=used_topic_ids)
        for topic_id, topic_data in preference_topics:
            if len(selected) >= 1:
                break

            topic_level = self._resolve_topic_level(
                topic_level=topic_data.get("friendship_level"),
                fallback=friendship_level,
            )
            guides = self.prompt_repo.get_guides(
                friendship_level=topic_level,
                agent_type=AgentType.GAME.value,
                topic_id=topic_id,
            )
            guides = [g for g in guides if g.agent_id not in used_agent_ids]
            if not guides:
                continue

            guide = choice(guides)
            used_agent_ids.add(guide.agent_id)
            used_topic_ids.add(topic_id)

            topic_score = topic_data.get("score", 0.0)
            total_turns = topic_data.get("turns") or topic_data.get("total_turns") or 0

            payload = self._build_agent_payload(
                guide=guide,
                persona=persona,
                reason="Game preference",
                metadata={
                    "topic_score": topic_score,
                    "total_turns": total_turns,
                },
                topic_id=topic_id,
            )
            selected.append(payload)

        # 2. Chọn 1 Game khám phá (total_turns thấp nhất)
        exploration_topics = self._get_topics_by_turns(topic_metrics, top_n=1, exclude_topic_ids=used_topic_ids)
        for topic_id, topic_data in exploration_topics:
            if len(selected) >= count:
                break

            topic_level = self._resolve_topic_level(
                topic_level=topic_data.get("friendship_level"),
                fallback=friendship_level,
            )
            guides = self.prompt_repo.get_guides(
                friendship_level=topic_level,
                agent_type=AgentType.GAME.value,
                topic_id=topic_id,
            )
            guides = [g for g in guides if g.agent_id not in used_agent_ids]
            if not guides:
                continue

            guide = choice(guides)
            used_agent_ids.add(guide.agent_id)
            used_topic_ids.add(topic_id)

            topic_score = topic_data.get("score", 0.0)
            total_turns = topic_data.get("turns") or topic_data.get("total_turns") or 0

            payload = self._build_agent_payload(
                guide=guide,
                persona=persona,
                reason="Game exploration",
                metadata={
                    "topic_score": topic_score,
                    "total_turns": total_turns,
                },
                topic_id=topic_id,
            )
            selected.append(payload)

        # 3. Fallback: nếu chưa đủ, random từ các topic còn lại hoặc guides chung
        if len(selected) < count:
            remaining_topics = [
                (tid, tdata) for tid, tdata in topic_metrics.items()
                if tid not in used_topic_ids
            ]
            for topic_id, topic_data in remaining_topics:
                if len(selected) >= count:
                    break

                topic_level = self._resolve_topic_level(
                    topic_level=topic_data.get("friendship_level"),
                    fallback=friendship_level,
                )
                guides = self.prompt_repo.get_guides(
                    friendship_level=topic_level,
                    agent_type=AgentType.GAME.value,
                    topic_id=topic_id,
                )
                guides = [g for g in guides if g.agent_id not in used_agent_ids]
                if not guides:
                    continue

                guide = choice(guides)
                used_agent_ids.add(guide.agent_id)
                used_topic_ids.add(topic_id)

                payload = self._build_agent_payload(
                    guide=guide,
                    persona=persona,
                    reason="Random game",
                    metadata={
                        "topic_score": topic_data.get("score", 0.0),
                        "total_turns": topic_data.get("turns") or topic_data.get("total_turns") or 0,
                    },
                    topic_id=topic_id,
                )
                selected.append(payload)

        # 4. Final fallback: lấy guides từ PHASE1_STRANGER cho topics chưa học
        # Logic: Topics chưa có trong topic_metrics phải dùng PHASE1_STRANGER
        if len(selected) < count:
            # Ưu tiên query PHASE1_STRANGER cho topics chưa học
            phase1_guides = self.prompt_repo.get_guides(
                friendship_level=FriendshipLevel.PHASE1_STRANGER.value,
                agent_type=AgentType.GAME.value,
            )
            if not phase1_guides:
                raise AgentSelectionError(f"No game guides configured for PHASE1_STRANGER")
            
            phase1_iter = [
                g for g in phase1_guides 
                if g.agent_id not in used_agent_ids 
                and g.topic_id not in used_topic_ids
            ]
            
            idx = 0
            while len(selected) < count and phase1_iter:
                guide = phase1_iter[idx % len(phase1_iter)]
                selected.append(
                    self._build_agent_payload(
                        guide=guide,
                        persona=persona,
                        reason="New topic exploration (PHASE1)",
                        topic_id=guide.topic_id,
                    )
                )
                used_agent_ids.add(guide.agent_id)
                used_topic_ids.add(guide.topic_id)
                idx += 1

        return selected

    def compute_candidates(self, user_id: str) -> Dict[str, Any]:
        """
        Tính toán và trả về danh sách candidates đầy đủ cho user.
        
        Phương thức này thực hiện các bước:
        1. Lấy friendship_status của user
        2. Xác định friendship_level dựa trên score
        3. Chọn greeting agent
        4. Chọn talk agents (3 agents: 2 sở thích + 1 khám phá) dựa trên topic_level
        5. Chọn game agents (2 agents: 1 sở thích + 1 khám phá) dựa trên topic_level
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
            - talk_agents: List các talk agents đã được enrich (3 agents: 2 sở thích + 1 khám phá)
            - game_agents: List các game agents đã được enrich (2 agents: 1 sở thích + 1 khám phá)
            
        Raises:
            FriendshipNotFoundError: Nếu không tìm thấy friendship_status của user
            AgentSelectionError: Nếu không có talk/game agents cho level này
            
        Example:
            >>> service = AgentSelectionService(db)
            >>> candidates = service.compute_candidates("user_123")
            >>> print(candidates["friendship_level"])  # "PHASE2_ACQUAINTANCE"
            >>> print(len(candidates["talk_agents"]))  # 3
        """
        status = self.status_repo.get_by_user_id(user_id)
        if not status:
            logger.info("Friendship status missing for %s, creating default", user_id)
            status = self.status_repo.create_default(user_id)

        level = self.determine_level(status.friendship_score or 0.0)

        greeting_agent = self.select_greeting_agent(level, status)
        talk_agents = self.select_talk_agents(level, status, count=3)
        if not talk_agents:
            raise AgentSelectionError(f"No talk agents available for level {level.value}")

        game_agents = self.select_game_agents(level, status, count=2)
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
        if persona and persona.context_style_guideline:
            blocks.append(persona.context_style_guideline.strip())
        if talking_agenda:
            blocks.append(talking_agenda.strip())
        if persona and persona.user_profile:
            blocks.append(persona.user_profile.strip())
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
        """
        Resolve topic level từ string hoặc fallback.
        
        Logic: Nếu topic không có level (chưa học), mặc định PHASE1_STRANGER
        thay vì dùng user_level làm fallback.
        """
        if not topic_level:
            # Topic chưa học → mặc định PHASE1_STRANGER
            return FriendshipLevel.PHASE1_STRANGER.value
        normalized = topic_level.upper()
        alias_map = {
            "STRANGER": FriendshipLevel.PHASE1_STRANGER.value,
            "PHASE1_STRANGER": FriendshipLevel.PHASE1_STRANGER.value,
            "ACQUAINTANCE": FriendshipLevel.PHASE2_ACQUAINTANCE.value,
            "PHASE2_ACQUAINTANCE": FriendshipLevel.PHASE2_ACQUAINTANCE.value,
            "FRIEND": FriendshipLevel.PHASE3_FRIEND.value,
            "PHASE3_FRIEND": FriendshipLevel.PHASE3_FRIEND.value,
        }
        return alias_map.get(normalized, FriendshipLevel.PHASE1_STRANGER.value)

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

    def _get_topics_by_score(
        self, 
        topic_metrics: Dict[str, Any], 
        top_n: int = 2,
        exclude_topic_ids: Optional[set] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Lấy top N topics có topic_score cao nhất.
        
        Args:
            topic_metrics: Dictionary chứa topic metrics
            top_n: Số lượng topics cần lấy
            exclude_topic_ids: Set các topic_id cần loại trừ
            
        Returns:
            List các tuple (topic_id, topic_data) đã sắp xếp theo score giảm dần
        """
        if not topic_metrics:
            return []
        
        exclude = exclude_topic_ids or set()
        candidates = [
            (topic_id, topic_data)
            for topic_id, topic_data in topic_metrics.items()
            if topic_id not in exclude
        ]
        
        # Sắp xếp theo score giảm dần
        candidates.sort(
            key=lambda item: -(item[1].get("score", 0.0) or 0.0)
        )
        
        return candidates[:top_n]

    def _get_topics_by_turns(
        self, 
        topic_metrics: Dict[str, Any], 
        top_n: int = 1,
        exclude_topic_ids: Optional[set] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Lấy top N topics có total_turns thấp nhất (khám phá).
        
        Args:
            topic_metrics: Dictionary chứa topic metrics
            top_n: Số lượng topics cần lấy
            exclude_topic_ids: Set các topic_id cần loại trừ
            
        Returns:
            List các tuple (topic_id, topic_data) đã sắp xếp theo turns tăng dần
        """
        if not topic_metrics:
            return []
        
        exclude = exclude_topic_ids or set()
        candidates = [
            (topic_id, topic_data)
            for topic_id, topic_data in topic_metrics.items()
            if topic_id not in exclude
        ]
        
        # Sắp xếp theo turns tăng dần (thấp nhất trước)
        candidates.sort(
            key=lambda item: (item[1].get("turns") or item[1].get("total_turns") or 0)
        )
        
        return candidates[:top_n]

