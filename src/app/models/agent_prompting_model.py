"""
Model ORM cho bảng agent_prompting.

Bảng này lưu trữ thông tin về prompt của các agent, bao gồm:
- prompt_template: Prompt template có placeholder (ví dụ: {{user_name}}, {{topic}})
- final_prompt: Prompt đã được compile/cache sẵn (optional, có thể null)
- goal: Mục tiêu sư phạm/hành vi của agent

Bảng này được sử dụng để giao tiếp với phía Academy Prompting Service,
cung cấp prompt đã được xử lý sẵn cho các agent khi được suggest cho user.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database_connection import Base


class AgentPrompting(Base):
    """
    SQLAlchemy model cho bảng agent_prompting.
    
    Bảng này lưu trữ thông tin prompt của từng agent, được sử dụng để:
    - Lưu prompt template (có placeholder)
    - Lưu final_prompt đã được compile sẵn (nếu có)
    - Cung cấp prompt cho Academy Prompting Service
    
    Attributes:
        id: Primary key, auto increment
        agent_id: ID duy nhất của agent (unique, indexed)
        agent_name: Tên hiển thị của agent
        goal: Mục tiêu sư phạm/hành vi của agent
        prompt_template: Prompt template có placeholder (ví dụ: {{user_name}})
        final_prompt: Prompt đã compile sẵn (optional, có thể null)
        created_at: Thời điểm tạo record
        updated_at: Thời điểm cập nhật cuối cùng
    """
    __tablename__ = "agent_prompting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(255), nullable=False, unique=True, index=True)
    agent_name = Column(String(255), nullable=False)
    goal = Column(Text, nullable=False)
    prompt_template = Column(Text, nullable=False)
    final_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

