"""
Schemas for activity suggestion API.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentDetail(BaseModel):
    """Detail information for a selected agent."""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Display name of agent")
    agent_type: str = Field(..., description="Type: GREETING, TALK, GAME_ACTIVITY")
    reason: Optional[str] = Field(None, description="Why this agent was selected")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional info (topic score, etc.)")


class ActivitySuggestionData(BaseModel):
    """Data payload for activity suggestion result."""
    user_id: str = Field(..., description="User ID")
    friendship_level: str = Field(..., description="Current friendship level")
    greeting_agent: AgentDetail = Field(..., description="Selected greeting agent")
    talk_agents: List[AgentDetail] = Field(..., description="List of talk agents", min_items=0)
    game_agents: List[AgentDetail] = Field(..., description="List of game agents", min_items=0)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_doanngoccuong",
                "friendship_level": "ACQUAINTANCE",
                "greeting_agent": {
                    "agent_id": "greeting_memory_recall",
                    "agent_name": "Memory Recall Greeting",
                    "agent_type": "GREETING",
                    "reason": "Streak >= 5 days, recalling shared memory"
                },
                "talk_agents": [
                    {
                        "agent_id": "talk_movie_preference",
                        "agent_name": "Movie Talk",
                        "agent_type": "TALK",
                        "reason": "High topic score",
                        "metadata": {
                            "topic_score": 52.0,
                            "total_turns": 65
                        }
                    },
                    {
                        "agent_id": "talk_dreams",
                        "agent_name": "Dreams Talk",
                        "agent_type": "TALK",
                        "reason": "Exploration candidate",
                        "metadata": {
                            "topic_score": 10.0,
                            "total_turns": 5
                        }
                    }
                ],
                "game_agents": [
                    {
                        "agent_id": "game_20questions",
                        "agent_name": "20 Questions",
                        "agent_type": "GAME_ACTIVITY",
                        "reason": "Weighted random selection"
                    },
                    {
                        "agent_id": "game_story_building",
                        "agent_name": "Story Building",
                        "agent_type": "GAME_ACTIVITY",
                        "reason": "Weighted random selection"
                    }
                ]
            }
        }


class ActivitySuggestionResponse(BaseModel):
    """API response schema."""
    success: bool = Field(True, description="Operation status")
    data: ActivitySuggestionData = Field(..., description="Suggestion payload")
    message: str = Field(..., description="Response message")

