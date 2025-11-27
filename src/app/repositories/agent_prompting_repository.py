"""
Repository cho bảng agent_prompting.

Repository này cung cấp các phương thức để truy vấn dữ liệu từ bảng agent_prompting,
bao gồm việc lấy prompt theo agent_id để enrich thông tin agent khi suggest cho user.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.agent_prompting_model import AgentPrompting


class AgentPromptingRepository:
    """
    Repository cho việc truy cập dữ liệu agent_prompting.
    
    Repository này cung cấp các phương thức để:
    - Lấy thông tin prompt của agent theo agent_id
    - Hỗ trợ việc enrich agent data với prompt khi suggest activities
    
    Attributes:
        db: SQLAlchemy database session
        model: AgentPrompting model class
    """

    def __init__(self, db: Session):
        """
        Khởi tạo repository.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.model = AgentPrompting

    def get_by_agent_id(self, agent_id: str) -> Optional[AgentPrompting]:
        """
        Lấy thông tin prompt của agent theo agent_id.
        
        Phương thức này được sử dụng để lấy final_prompt của agent
        khi cần enrich thông tin agent trong response của API suggest activities.
        
        Args:
            agent_id: ID duy nhất của agent cần lấy prompt
            
        Returns:
            AgentPrompting object nếu tìm thấy, None nếu không tìm thấy
            
        Example:
            >>> repository = AgentPromptingRepository(db)
            >>> prompting = repository.get_by_agent_id("talk_movie_preference")
            >>> if prompting:
            ...     print(prompting.final_prompt)
        """
        return (
            self.db.query(self.model)
            .filter(self.model.agent_id == agent_id)
            .first()
        )

