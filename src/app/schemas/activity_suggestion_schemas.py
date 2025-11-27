"""
Schemas cho API suggest activities.

Schemas này định nghĩa cấu trúc request/response cho API suggest activities,
bao gồm thông tin chi tiết về các agents được suggest cho user.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AgentDetail(BaseModel):
    """
    Schema cho thông tin chi tiết của một agent được suggest.
    
    AgentDetail chứa đầy đủ thông tin về agent bao gồm:
    - Thông tin cơ bản: agent_id, agent_name, agent_type
    - Thông tin friendship_level: friendship_level (từ agenda_agent_prompting)
    - Thông tin mô tả: agent_description (từ friendship_agent_mapping)
    - Thông tin prompt: final_prompt (từ agent_prompting, có thể None)
    - Lý do chọn: reason
    - Metadata bổ sung: metadata (topic_score, total_turns, etc.)
    """
    agent_id: str = Field(..., description="ID duy nhất của agent")
    agent_name: str = Field(..., description="Tên hiển thị của agent")
    agent_type: str = Field(..., description="Loại agent: GREETING, TALK, GAME")
    friendship_level: str = Field(..., description="Friendship level của agent từ bảng agenda_agent_prompting (PHASE1_STRANGER, PHASE2_ACQUAINTANCE, PHASE3_FRIEND)")
    topic_id: Optional[str] = Field(None, description="Topic ID mà agent này thuộc về (từ bảng agenda_agent_prompting)")
    agent_description: Optional[str] = Field(None, description="Mô tả agent từ bảng friendship_agent_mapping")
    final_prompt: Optional[str] = Field(None, description="Final prompt từ bảng agent_prompting (có thể None nếu chưa có)")
    reason: Optional[str] = Field(None, description="Lý do agent này được chọn")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata bổ sung (topic_score, total_turns, selection_score, etc.)")


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
                "friendship_level": "PHASE2_ACQUAINTANCE",
                "greeting_agent": {
                    "agent_id": "greeting_memory_recall",
                    "agent_name": "Memory Recall Greeting",
                    "agent_type": "GREETING",
                    "friendship_level": "PHASE2_ACQUAINTANCE",
                    "topic_id": "general_greeting",
                    "agent_description": "Nhắc lại ký ức chung với user",
                    "final_prompt": "You are Pika, a buddy who REMEMBERS...",
                    "reason": "Streak >= 5 days, recalling shared memory"
                },
                "talk_agents": [
                    {
                        "agent_id": "talk_movie_preference",
                        "agent_name": "Movie Talk",
                        "agent_type": "TALK",
                        "friendship_level": "PHASE2_ACQUAINTANCE",
                        "topic_id": "movie",
                        "agent_description": "Nói về phim yêu thích",
                        "final_prompt": "You are Pika, talking with a child about movies...",
                        "reason": "High topic score",
                        "metadata": {
                            "topic_score": 52.0,
                            "total_turns": 65,
                            "selection_score": 45.5
                        }
                    },
                    {
                        "agent_id": "talk_dreams",
                        "agent_name": "Dreams Talk",
                        "agent_type": "TALK",
                        "friendship_level": "PHASE1_STRANGER",
                        "topic_id": "dreams",
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
                        "agent_type": "GAME",
                        "friendship_level": "PHASE2_ACQUAINTANCE",
                        "topic_id": "game",
                        "reason": "Weighted random selection"
                    },
                    {
                        "agent_id": "game_story_building",
                        "agent_name": "Story Building",
                        "agent_type": "GAME",
                        "friendship_level": "PHASE2_ACQUAINTANCE",
                        "topic_id": "story",
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

