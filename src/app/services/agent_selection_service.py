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
from typing import Dict, Any, List
from random import choices
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.repositories.friendship_status_repository import FriendshipStatusRepository
from app.repositories.friendship_agent_mapping_repository import FriendshipAgentMappingRepository
from app.repositories.agent_prompting_repository import AgentPromptingRepository
from app.core.constants_enums import FriendshipLevel, AgentType, FRIENDSHIP_SCORE_THRESHOLDS
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
        self.agent_repo = FriendshipAgentMappingRepository(db)
        self.prompting_repo = AgentPromptingRepository(db)

    def determine_level(self, score: float) -> FriendshipLevel:
        """
        Xác định friendship level dựa trên friendship_score.
        
        Phương thức này sử dụng các ngưỡng điểm được định nghĩa trong
        FRIENDSHIP_SCORE_THRESHOLDS để xác định level:
        - STRANGER: score < 500
        - ACQUAINTANCE: 500 <= score <= 3000
        - FRIEND: score > 3000
        
        Args:
            score: Điểm friendship_score của user
            
        Returns:
            FriendshipLevel enum value tương ứng với score
            
        Example:
            >>> service = AgentSelectionService(db)
            >>> level = service.determine_level(850.5)
            >>> print(level)  # FriendshipLevel.ACQUAINTANCE
        """
        if score >= FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.FRIEND][0]:
            return FriendshipLevel.FRIEND
        if score >= FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.ACQUAINTANCE][0]:
            return FriendshipLevel.ACQUAINTANCE
        return FriendshipLevel.STRANGER

    def _enrich_agent_data(
        self, 
        agent_mapping, 
        reason: str = None, 
        metadata: dict = None
    ) -> Dict[str, Any]:
        """
        Enrich agent data với description và prompt từ database.
        
        Phương thức này lấy thêm thông tin từ các bảng:
        - agent_description từ friendship_agent_mapping
        - final_prompt từ agent_prompting
        
        Args:
            agent_mapping: FriendshipAgentMapping object từ database
            reason: Lý do agent được chọn (optional)
            metadata: Metadata bổ sung như topic_score, total_turns (optional)
            
        Returns:
            Dictionary chứa đầy đủ thông tin agent bao gồm:
            - agent_id, agent_name, agent_type
            - agent_description (từ mapping table)
            - final_prompt (từ prompting table, có thể None)
            - reason (nếu có)
            - metadata (nếu có)
            
        Example:
            >>> agent = agent_mapping_object
            >>> enriched = service._enrich_agent_data(
            ...     agent, 
            ...     reason="High topic score",
            ...     metadata={"topic_score": 52.0}
            ... )
        """
        result = {
            "agent_id": agent_mapping.agent_id,
            "agent_name": agent_mapping.agent_name,
            "agent_type": agent_mapping.agent_type,
            "agent_description": agent_mapping.agent_description,
            "reason": reason
        }
        
        # Lấy final_prompt từ agent_prompting table
        prompting = self.prompting_repo.get_by_agent_id(agent_mapping.agent_id)
        if prompting:
            result["final_prompt"] = prompting.final_prompt
        else:
            result["final_prompt"] = None
        
        if metadata:
            result["metadata"] = metadata
        
        return result

    def select_greeting_agent(self, friendship_level: FriendshipLevel, status) -> Dict[str, Any]:
        """
        Chọn greeting agent dựa trên priority logic.
        
        Logic ưu tiên:
        1. Nếu streak_day >= 5: Ưu tiên agent có "streak" trong agent_id
        2. Nếu days_since_last >= 7: Ưu tiên agent có "return" hoặc "welcome_back" trong agent_id
        3. Mặc định: Chọn ngẫu nhiên từ tất cả greeting agents của level
        
        Sau khi chọn, agent data sẽ được enrich với description và prompt.
        
        Args:
            friendship_level: Friendship level của user (STRANGER/ACQUAINTANCE/FRIEND)
            status: FriendshipStatus object chứa thông tin user
            
        Returns:
            Dictionary chứa thông tin greeting agent đã được enrich:
            - agent_id, agent_name, agent_type
            - agent_description, final_prompt
            - reason: Lý do được chọn
            
        Raises:
            ValueError: Nếu không có greeting agent nào được config cho level này
            
        Example:
            >>> level = FriendshipLevel.ACQUAINTANCE
            >>> status = friendship_status_object
            >>> greeting = service.select_greeting_agent(level, status)
            >>> print(greeting["agent_id"])  # "greeting_memory_recall"
        """
        agents = self.agent_repo.get_by_level_and_type(friendship_level.value, AgentType.GREETING.value)
        if not agents:
            raise ValueError("No greeting agents configured")

        now = datetime.now(timezone.utc)
        last_interaction = status.last_interaction_date or now
        if last_interaction.tzinfo is None:
            last_interaction = last_interaction.replace(tzinfo=timezone.utc)
        else:
            last_interaction = last_interaction.astimezone(timezone.utc)
        days_since_last = (now - last_interaction).days

        # Priority filters (simple heuristics aligned with docs)
        prioritized = []
        if status.streak_day and status.streak_day >= 5:
            prioritized = [a for a in agents if "streak" in a.agent_id.lower()]
        elif days_since_last >= 7:
            prioritized = [a for a in agents if "return" in a.agent_id.lower() or "welcome_back" in a.agent_id.lower()]

        pool = prioritized or agents
        selected = self._weighted_random(pool)
        reason = "Returning user" if prioritized and days_since_last >= 7 else "High streak" if prioritized else "Default greeting"

        # Sử dụng helper method để enrich data
        return self._enrich_agent_data(selected, reason=reason)

    def select_talk_agents(self, friendship_level: FriendshipLevel, status, count: int = 2) -> List[Dict[str, Any]]:
        """
        Chọn talk agents dựa trên topic metrics scoring.
        
        Algorithm:
        1. Lấy tất cả talk agents của friendship_level
        2. Với mỗi agent, tính selection_score:
           - selection_score = (topic_score * 0.7) + ((100 - min(total_turns, 100)) * 0.3)
           - topic_score cao hơn = ưu tiên hơn (70% weight)
           - total_turns thấp hơn = ưu tiên khám phá (30% weight)
        3. Sắp xếp theo selection_score giảm dần
        4. Chọn top N agents (mặc định 2)
        5. Enrich data với description và prompt
        
        Args:
            friendship_level: Friendship level của user
            status: FriendshipStatus object chứa topic_metrics
            count: Số lượng talk agents cần chọn (mặc định 2)
            
        Returns:
            List các dictionary chứa thông tin talk agents đã được enrich:
            - agent_id, agent_name, agent_type
            - agent_description, final_prompt
            - reason: "Topic preference" hoặc "Exploration candidate"
            - metadata: topic_score, total_turns, selection_score
            
        Example:
            >>> level = FriendshipLevel.ACQUAINTANCE
            >>> status = friendship_status_object
            >>> talk_agents = service.select_talk_agents(level, status, count=2)
            >>> print(len(talk_agents))  # 2
        """
        agents = self.agent_repo.get_by_level_and_type(friendship_level.value, AgentType.TALK.value)
        if not agents:
            return []

        topic_metrics = status.topic_metrics or {}
        scored = []
        for agent in agents:
            topic_id = self._extract_topic_id(agent.agent_id)
            topic_data = topic_metrics.get(topic_id, {})
            topic_score = topic_data.get("score", 0.0)
            total_turns = topic_data.get("turns", topic_data.get("total_turns", 0.0))

            selection_score = (topic_score * 0.7) + ((100 - min(total_turns, 100)) * 0.3)
            scored.append((agent, selection_score, topic_score, total_turns))

        scored.sort(key=lambda item: item[1], reverse=True)

        selected = []
        for agent, score, topic_score, total_turns in scored[:count]:
            metadata = {
                "topic_score": topic_score,
                "total_turns": total_turns,
                "selection_score": score
            }
            reason = "Topic preference" if topic_score > 0 else "Exploration candidate"
            
            # Sử dụng helper method để enrich data
            selected.append(self._enrich_agent_data(agent, reason=reason, metadata=metadata))

        return selected

    def select_game_agents(self, friendship_level: FriendshipLevel, count: int = 2) -> List[Dict[str, Any]]:
        """
        Chọn game agents dựa trên weighted random selection.
        
        Algorithm:
        1. Lấy tất cả game agents của friendship_level
        2. Chọn ngẫu nhiên dựa trên weight của từng agent
        3. Loại bỏ agent đã chọn khỏi pool để tránh trùng lặp
        4. Lặp lại cho đến khi đủ số lượng hoặc hết agents
        5. Enrich data với description và prompt
        
        Args:
            friendship_level: Friendship level của user
            count: Số lượng game agents cần chọn (mặc định 2)
            
        Returns:
            List các dictionary chứa thông tin game agents đã được enrich:
            - agent_id, agent_name, agent_type
            - agent_description, final_prompt
            - reason: "Weighted random selection"
            
        Raises:
            AgentSelectionError: Nếu không có game agent nào được config cho level này
            
        Example:
            >>> level = FriendshipLevel.ACQUAINTANCE
            >>> game_agents = service.select_game_agents(level, count=2)
            >>> print(len(game_agents))  # 2
        """
        agents = self.agent_repo.get_by_level_and_type(friendship_level.value, AgentType.GAME_ACTIVITY.value)
        if not agents:
            raise AgentSelectionError(f"No game agents configured for level {friendship_level.value}")

        pool = agents.copy()
        selected = []
        for _ in range(min(count, len(pool))):
            agent = self._weighted_random(pool)
            # Sử dụng helper method để enrich data
            selected.append(self._enrich_agent_data(agent, reason="Weighted random selection"))
            pool.remove(agent)
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
            - friendship_level: Level hiện tại (STRANGER/ACQUAINTANCE/FRIEND)
            - greeting_agent: 1 greeting agent đã được enrich
            - talk_agents: List các talk agents đã được enrich (thường 2)
            - game_agents: List các game agents đã được enrich (thường 2)
            
        Raises:
            FriendshipNotFoundError: Nếu không tìm thấy friendship_status của user
            AgentSelectionError: Nếu không có talk/game agents cho level này
            
        Example:
            >>> service = AgentSelectionService(db)
            >>> candidates = service.compute_candidates("user_123")
            >>> print(candidates["friendship_level"])  # "ACQUAINTANCE"
            >>> print(len(candidates["talk_agents"]))  # 2
        """
        status = self.status_repo.get_by_user_id(user_id)
        if not status:
            raise FriendshipNotFoundError(f"Friendship status not found for user {user_id}")

        level = self.determine_level(status.friendship_score or 0.0)

        greeting_agent = self.select_greeting_agent(level, status)
        talk_agents = self.select_talk_agents(level, status)
        if not talk_agents:
            raise AgentSelectionError(f"No talk agents available for level {level.value}")

        game_agents = self.select_game_agents(level)
        if not game_agents:
            raise AgentSelectionError(f"No game agents available for level {level.value}")

        return {
            "user_id": status.user_id,
            "friendship_level": level.value,
            "greeting_agent": greeting_agent,
            "talk_agents": talk_agents,
            "game_agents": game_agents
        }

    @staticmethod
    def _weighted_random(agent_list):
        """
        Chọn agent ngẫu nhiên dựa trên weight.
        
        Phương thức này sử dụng weighted random selection:
        - Agent có weight cao hơn sẽ có xác suất được chọn cao hơn
        - Weight tối thiểu là 0.1 để tránh lỗi khi weight = 0
        
        Args:
            agent_list: List các agent objects có thuộc tính weight
            
        Returns:
            Agent object được chọn ngẫu nhiên
            
        Example:
            >>> agents = [agent1, agent2, agent3]  # agent1.weight=2.0, agent2.weight=1.0
            >>> selected = AgentSelectionService._weighted_random(agents)
            >>> # agent1 có xác suất được chọn cao gấp đôi agent2
        """
        weights = [max(agent.weight, 0.1) for agent in agent_list]
        return choices(agent_list, weights=weights, k=1)[0]

    @staticmethod
    def _extract_topic_id(agent_id: str) -> str:
        """
        Trích xuất topic identifier từ agent_id.
        
        Format agent_id thường là: "{type}_{topic}"
        Ví dụ: "talk_movie_preference" -> "movie_preference"
        
        Args:
            agent_id: ID của agent (ví dụ: "talk_movie_preference")
            
        Returns:
            Topic identifier sau dấu underscore đầu tiên
            Nếu không có underscore, trả về toàn bộ agent_id
            
        Example:
            >>> topic = AgentSelectionService._extract_topic_id("talk_movie_preference")
            >>> print(topic)  # "movie_preference"
            >>> topic = AgentSelectionService._extract_topic_id("greeting_welcome")
            >>> print(topic)  # "welcome"
        """
        if "_" in agent_id:
            return agent_id.split("_", 1)[1]
        return agent_id

