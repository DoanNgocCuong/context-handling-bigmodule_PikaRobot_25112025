"""
Agent selection logic for greeting, talk, and game agents.
"""
from typing import Dict, Any, List
from random import choices
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.repositories.friendship_status_repository import FriendshipStatusRepository
from app.repositories.friendship_agent_mapping_repository import FriendshipAgentMappingRepository
from app.core.constants_enums import FriendshipLevel, AgentType, FRIENDSHIP_SCORE_THRESHOLDS
from app.core.exceptions_custom import FriendshipNotFoundError, AgentSelectionError
from app.utils.logger_setup import get_logger

logger = get_logger(__name__)


class AgentSelectionService:
    """Encapsulates selection logic for greeting/talk/game agents."""

    def __init__(self, db: Session):
        self.db = db
        self.status_repo = FriendshipStatusRepository(db)
        self.agent_repo = FriendshipAgentMappingRepository(db)

    def determine_level(self, score: float) -> FriendshipLevel:
        """Determine friendship level based on score."""
        if score >= FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.FRIEND][0]:
            return FriendshipLevel.FRIEND
        if score >= FRIENDSHIP_SCORE_THRESHOLDS[FriendshipLevel.ACQUAINTANCE][0]:
            return FriendshipLevel.ACQUAINTANCE
        return FriendshipLevel.STRANGER

    def select_greeting_agent(self, friendship_level: FriendshipLevel, status) -> Dict[str, Any]:
        """Select greeting agent based on priority logic."""
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

        return {
            "agent_id": selected.agent_id,
            "agent_name": selected.agent_name,
            "agent_type": selected.agent_type,
            "reason": reason
        }

    def select_talk_agents(self, friendship_level: FriendshipLevel, status, count: int = 2) -> List[Dict[str, Any]]:
        """Select talk agents using topic metrics scoring."""
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
            selected.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "agent_type": agent.agent_type,
                "reason": "Topic preference" if topic_score > 0 else "Exploration candidate",
                "metadata": {
                    "topic_score": topic_score,
                    "total_turns": total_turns,
                    "selection_score": score
                }
            })

        return selected

    def select_game_agents(self, friendship_level: FriendshipLevel, count: int = 2) -> List[Dict[str, Any]]:
        """Select game agents via weighted random."""
        agents = self.agent_repo.get_by_level_and_type(friendship_level.value, AgentType.GAME_ACTIVITY.value)
        if not agents:
            raise AgentSelectionError(f"No game agents configured for level {friendship_level.value}")

        pool = agents.copy()
        selected = []
        for _ in range(min(count, len(pool))):
            agent = self._weighted_random(pool)
            selected.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "agent_type": agent.agent_type,
                "reason": "Weighted random selection"
            })
            pool.remove(agent)
        return selected

    def compute_candidates(self, user_id: str) -> Dict[str, Any]:
        """Compute full suggestion payload."""
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
        """Pick agent based on weight."""
        weights = [max(agent.weight, 0.1) for agent in agent_list]
        return choices(agent_list, weights=weights, k=1)[0]

    @staticmethod
    def _extract_topic_id(agent_id: str) -> str:
        """Extract topic identifier from agent_id (after first underscore)."""
        if "_" in agent_id:
            return agent_id.split("_", 1)[1]
        return agent_id

