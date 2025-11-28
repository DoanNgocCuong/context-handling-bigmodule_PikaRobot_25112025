"""
ConversationEvent ORM model mapping conversation_events table.
"""
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
    Computed,
)
from sqlalchemy.dialects.postgresql import JSONB

from app.core.constants_enums import ConversationEventStatus
from app.db.database_connection import Base


class ConversationEvent(Base):
    """
    SQLAlchemy model mapping `conversation_events`.

    Field summary:
    - `conversation_id`, `user_id`, bot info: identifiers for the finished session.
    - `start_time`, `end_time`: precise timestamps provided by BE.
    - `duration_seconds`: STORED computed column (Postgres) = EXTRACT(EPOCH FROM (end_time - start_time)).
       -> Không cần/không được set thủ công trong code; DB tự tính dựa trên start/end.
    - `conversation_log`: JSONB lưu trọn cuộc hội thoại BE gửi sang.
    - `status` + `attempt_count` + `next_attempt_at`: theo dõi process pipeline (PENDING / PROCESSING / PROCESSED / FAILED / SKIPPED).
    - `processed_at`, `error_code`, `error_details`: log kết quả xử lý (thành công hay lỗi).
    - `friendship_score_change`, `new_friendship_level`: kết quả cuối cùng đưa ra sau khi AI xử lý.
    - `created_at` / `updated_at`: timestamps chuẩn cho auditing.
    """

    __tablename__ = "conversation_events"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    bot_type = Column(String(50), nullable=False)
    bot_id = Column(String(255), nullable=False)
    bot_name = Column(String(255), nullable=False)
    agent_tag = Column(String(255), nullable=True)  # ADDED: Agent tag for topic mapping (replaces bot_id for topic lookup)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(
        Integer,
        Computed("(EXTRACT(EPOCH FROM (end_time - start_time))::INTEGER)", persisted=True),
        nullable=False,
    )
    conversation_log = Column(JSONB, nullable=False, default=list)
    raw_conversation_log = Column(JSONB, nullable=True, default=None)
    status = Column(String(50), nullable=False, default=ConversationEventStatus.PENDING.value)
    attempt_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    next_attempt_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(String(50), nullable=True)
    error_details = Column(Text, nullable=True)
    friendship_score_change = Column(Float, nullable=True)
    new_friendship_level = Column(String(50), nullable=True)
    score_calculation_details = Column(JSONB, nullable=True, default=None)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


