
# Thiết Kế Database Cập Nhật - Với Prompt Templates

## Context Handling Module - Friendlyship Management

**Phiên bản:** 2.0
**Ngày:** 27/11/2025
**Trạng thái:** Cập nhật thiết kế DB + Logic chọn Agent

---

## 📋 THAY ĐỔI CHÍNH

### Cũ (v1)

```
Bảng 1: friendship_status
  - user_id, friendship_score, friendship_level
  - topic_metrics (JSONB)

Bảng 2: friendship_agent_mapping
  - friendship_level → agent_id
```

### Mới (v2)

```
Bảng 1: friendship_status
  - user_id, friendship_score, friendship_level
  - topic_metric (JSONB - chi tiết hơn)
  - last_emotion, last_followup_topic

Bảng 2: prompt_template_for_level_friendship
  - friendship_level
  - context_style_guideline (prompt template)
  - user_profile (prompt template)

Bảng 3: prompt_template_for_level_friendship
  - topic_id, agent_id
  - talking_agenda (prompt template)
  - friendship_level
  - agent_type

Bảng 4: conversation_events
  - (giữ nguyên từ trước)
```

---

## 1️⃣ BẢNG 1: friendship_status

### Schema

```sql
CREATE TABLE friendship_status (
    user_id VARCHAR(255) PRIMARY KEY,
    friendship_score FLOAT NOT NULL DEFAULT 0.0,
    friendship_level VARCHAR(50) NOT NULL DEFAULT 'PHASE1_STRANGER'
        CHECK (friendship_level IN ('PHASE1_STRANGER', 'PHASE2_ACQUAINTANCE', 'PHASE3_FRIEND')),
  
    -- Topic metrics (JSONB - chi tiết hơn)
    topic_metric JSONB NOT NULL DEFAULT '{}'::jsonb,
  
    -- Thêm trường mới
    last_emotion VARCHAR(50),  -- 'interesting', 'boring', 'neutral', 'angry', 'happy', 'sad'
    last_followup_topic VARCHAR(255),  -- Topic cuối cùng user follow up
  
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_interaction_date TIMESTAMP,
  
    -- Metadata
    streak_day INTEGER DEFAULT 0,
    total_turns INTEGER DEFAULT 0
);

-- Indexes
CREATE INDEX idx_friendship_status_phase ON friendship_status(friendship_level);
CREATE INDEX idx_friendship_status_score ON friendship_status(friendship_score);
CREATE INDEX idx_friendship_status_updated_at ON friendship_status(updated_at);
```

### Ví Dụ Dữ Liệu

```json
{
  "user_id": "user_1234",
  "friendship_score": 20.0,
  "friendship_level": "STRANGER",
  "topic_metric": {
    "toy": {
      "score": 0,
      "turns": 0,
      "friendship_level": "STRANGER",
      "last_date": "2025-11-24T17:20:00Z"
    },
    "movie": {
      "score": 120.0,
      "turns": 150,
      "friendship_level": "ACQUAINTANCE",
      "last_date": "2025-11-25T18:00:00Z"
    },
    "school": {
      "score": 40.0,
      "turns": 30,
      "friendship_level": "FRIEND",
      "last_date": "2025-11-23T08:10:00Z"
    }
  },
  "last_emotion": "interesting",
  "last_followup_topic": "movie",
  "created_at": "2025-11-20T10:00:00Z",
  "updated_at": "2025-11-25T18:00:00Z",
  "last_interaction_date": "2025-11-25T18:00:00Z",
  "streak_day": 5,
  "total_turns": 180
}
```

### Giải Thích Chi Tiết

**topic_metric (JSONB):**

```
Mỗi topic có:
- score: Điểm tích lũy cho topic này
- turns: Số lượt hội thoại về topic này
- friendship_level: Phase tình bạn hiện tại cho topic này
  (có thể khác với friendship_level chung)
- last_date: Lần cuối cùng nói về topic này
```

**Ví dụ:**

```
User "user_1234" có:
- Tổng friendship_score: 20.0 (STRANGER)
- Nhưng topic "movie": score=120.0 (ACQUAINTANCE)
- Nhưng topic "school": score=40.0 (FRIEND)

Điều này có nghĩa:
- User chưa quen biết chung chung (STRANGER)
- Nhưng biết rất nhiều về phim (ACQUAINTANCE)
- Và biết rất rất nhiều về trường học (FRIEND)
```

---

## 2️⃣ BẢNG 2: prompt_template_for_level_friendship

### Schema

```sql
CREATE TABLE prompt_template_for_level_friendship (
    id SERIAL PRIMARY KEY,
    friendship_level VARCHAR(50) NOT NULL UNIQUE
        CHECK (friendship_level IN ('PHASE1_STRANGER', 'PHASE2_ACQUAINTANCE', 'PHASE3_FRIEND')),
  
    -- Prompt templates
    context_style_guideline TEXT NOT NULL,  -- Hướng dẫn cách nói
    user_profile TEXT NOT NULL,  -- Template lấy thông tin user
  
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_prompt_template_phase ON prompt_template_for_level_friendship(friendship_level);
```

### Ví Dụ Dữ Liệu

```json
{
  "id": 1,
  "friendship_level": "STRANGER",
  "context_style_guideline": "Every exchange in this convo must be less than 30 word count, gonna be back and forth exchange to get the goals done\n\n1. CONTEXT\n\nBạn là Pika: đến từ \"Hành tinh Popa\". Còn tôi là Trúc 10 tuổi, bạn thân của Pika\nBối cảnh: Pika khám phá Trái Đất, giúp các bạn nhỏ nói tiếng Anh, rồi kể lại cho Hành tinh Popa.\n...",
  "user_profile": "6. USER PROFILE\nTên trẻ: {{name}}\nTuổi: {{age}}\nBộ phim yêu thích: {{favorite_movie}}"
}
```

### Giải Thích

**context_style_guideline:**

- Hướng dẫn cách Pika nên nói chuyện ở mỗi phase
- Ví dụ:
  - STRANGER: Ngắn gọn, < 30 từ, từng bước một
  - ACQUAINTANCE: Bình thường, có thể dài hơn
  - FRIEND: Thân thiết, có thể trò chuyện tự do

**user_profile:**

- Template lấy thông tin user
- Ví dụ: {{name}}, {{age}}, {{favorite_movie}}
- Sẽ được thay thế bằng dữ liệu thực tế

---

## 3️⃣ BẢNG 3: prompt_template_for_level_friendship

### Schema

```sql
CREATE TABLE prompt_template_for_level_friendship (
    id SERIAL PRIMARY KEY,
    topic_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
  
    -- Prompt template
    talking_agenda TEXT NOT NULL,  -- Nội dung hội thoại
  
    -- Điều kiện sử dụng
    friendship_level VARCHAR(50) NOT NULL
        CHECK (friendship_level IN ('PHASE1_STRANGER', 'PHASE2_ACQUAINTANCE', 'PHASE3_FRIEND')),
    agent_type VARCHAR(50) NOT NULL
        CHECK (agent_type IN ('GREETING', 'TALK', 'GAME')),
  
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_prompt_guide_topic ON prompt_template_for_level_friendship(topic_id);
CREATE INDEX idx_prompt_guide_agent ON prompt_template_for_level_friendship(agent_id);
CREATE INDEX idx_prompt_guide_phase ON prompt_template_for_level_friendship(friendship_level);
CREATE UNIQUE INDEX idx_prompt_guide_unique ON prompt_template_for_level_friendship(topic_id, agent_id, friendship_level);
```

### Ví Dụ Dữ Liệu

```json
{
  "id": 1,
  "topic_id": "toy",
  "agent_id": "agent_toy_1",
  "talking_agenda": "4. EXTRA INFORMATION\n\nDate: {{current_date_time}}\n\n5. TODAY'S Talking agenda:\n\nNói về ngày hôm nay của tôi. Hướng dần về A → B → C.\n\nGoal A – Explore\nTrigger: Pika mở đầu bằng câu hỏi về ngày của Trúc.\nAction:\nKhuyến khích Trúc kể bằng tiếng Việt (tối đa 1–2 câu/lượt).\n...",
  "friendship_level": "STRANGER",
  "agent_type": "TALK"
}
```

### Giải Thích

**Cấu trúc:**

- Mỗi topic có nhiều agent (agent_toy_1, agent_toy_2, agent_toy_3, ...)
- Mỗi agent có prompt guide khác nhau cho mỗi friendship_level
- Ví dụ:
  - topic="toy" + agent="agent_toy_1" + phase="STRANGER" → talking_agenda A
  - topic="toy" + agent="agent_toy_2" + phase="ACQUAINTANCE" → talking_agenda B
  - topic="toy" + agent="agent_toy_3" + phase="FRIEND" → talking_agenda C

**Ví dụ:**

```
Topic: toy
├── agent_toy_1 (STRANGER) → Ngắn gọn, đơn giản
├── agent_toy_2 (ACQUAINTANCE) → Bình thường
└── agent_toy_3 (FRIEND) → Chi tiết, tự do

Topic: movie
├── agent_movie_1 (STRANGER)
├── agent_movie_2 (ACQUAINTANCE)
└── agent_movie_3 (FRIEND)

Topic: school
├── agent_school_1 (ACQUAINTANCE)
└── agent_school_2 (FRIEND)
```

---

## 4️⃣ BẢNG 4: conversation_events (Giữ Nguyên)

```sql
CREATE TABLE conversation_events (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
  
    -- Bot information
    bot_type VARCHAR(50) NOT NULL,
    bot_id VARCHAR(255) NOT NULL,
    bot_name VARCHAR(255) NOT NULL,
  
    -- Conversation timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time))::INTEGER
    ) STORED,
  
    -- Conversation data
    conversation_log JSONB NOT NULL,
  
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED')),
  
    -- Processing metadata
    attempt_count INTEGER NOT NULL DEFAULT 0,
  
    -- Timing
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    next_attempt_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP + INTERVAL '6 hours',
    processed_at TIMESTAMP,
  
    -- Error tracking
    error_code VARCHAR(50),
    error_details TEXT,
  
    -- Processing results
    friendship_score_change FLOAT,
    new_friendship_level VARCHAR(50),
  
    -- Timestamps
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_conversation_events_status ON conversation_events(status);
CREATE INDEX idx_conversation_events_next_attempt ON conversation_events(next_attempt_at);
CREATE INDEX idx_conversation_events_user_id ON conversation_events(user_id);
CREATE INDEX idx_conversation_events_created_at ON conversation_events(created_at);
```

---

## 2️⃣ LOGIC CHỌN AGENT - CẬP NHẬT

### Luồng Chọn Agent (Mới)

```
BƯỚC 1: Lấy friendship_status của user
  ↓
BƯỚC 2: Xác định friendship_level chung
  (PHASE1_STRANGER / PHASE2_ACQUAINTANCE / PHASE3_FRIEND)
  ↓
BƯỚC 3: Lấy context_style_guideline từ prompt_template_for_level_friendship
  (Hướng dẫn cách nói ở phase này)
  ↓
BƯỚC 4: Lấy user_profile từ prompt_template_for_level_friendship
  (Thông tin user: tên, tuổi, sở thích, ...)
  ↓
BƯỚC 5: Chọn topic dựa trên topic_metric
  - Ưu tiên: score cao, lâu không nói, random
  - Lấy topic_id
  ↓
BƯỚC 6: Check topic_metric[topic_id].friendship_level
  - Nếu < friendship_level chung → Dùng friendship_level của topic
  - Nếu >= friendship_level chung → Dùng friendship_level chung
  ↓
BƯỚC 7: Lấy prompt_template_for_level_friendship
  - WHERE topic_id = [topic chọn]
  - AND friendship_level = [phase từ bước 6]
  ↓
BƯỚC 8: Lấy talking_agenda (prompt template)
  ↓
BƯỚC 9: Ghép prompt cuối cùng
  - context_style_guideline (từ bước 3)
  + user_profile (từ bước 4)
  + talking_agenda (từ bước 8)
  ↓
✅ XONG! Có prompt cuối cùng để gửi cho AI
```

### Ví Dụ Chi Tiết

**Input:**

```
user_id = "user_1234"
```

**Bước 1-2: Lấy friendship_status**

```
friendship_score = 20.0
friendship_level = "STRANGER"
topic_metric = {
  "toy": {score: 0, turns: 0, friendship_level: "STRANGER"},
  "movie": {score: 120.0, turns: 150, friendship_level: "ACQUAINTANCE"},
  "school": {score: 40.0, turns: 30, friendship_level: "FRIEND"}
}
```

**Bước 3: Lấy context_style_guideline**

```
Query: SELECT context_style_guideline FROM prompt_template_for_level_friendship
       WHERE friendship_level = 'PHASE1_STRANGER'

Result:
"Every exchange in this convo must be less than 30 word count...
1. CONTEXT
Bạn là Pika: đến từ \"Hành tinh Popa\". Còn tôi là Trúc 10 tuổi...
..."
```

**Bước 4: Lấy user_profile**

```
Query: SELECT user_profile FROM prompt_template_for_level_friendship
       WHERE friendship_level = 'PHASE1_STRANGER'

Result:
"6. USER PROFILE
Tên trẻ: {{name}}
Tuổi: {{age}}
Bộ phim yêu thích: {{favorite_movie}}"

After replacement:
"6. USER PROFILE
Tên trẻ: Trúc
Tuổi: 10
Bộ phim yêu thích: Zootopia"
```

**Bước 5: Chọn topic**

```
Topics available:
- toy: score=0 (chưa nói)
- movie: score=120.0 (đã nói nhiều)
- school: score=40.0 (nói vừa phải)

Strategy: Ưu tiên topic chưa nói (toy)
Chọn: topic_id = "toy"
```

**Bước 6: Check topic friendship_level**

```
topic_metric["toy"].friendship_level = "STRANGER"
friendship_level chung = "STRANGER"

Kết quả: Dùng "STRANGER"
```

**Bước 7: Lấy prompt_template_for_level_friendship**

```
Query: SELECT talking_agenda FROM prompt_template_for_level_friendship
       WHERE topic_id = 'toy'
       AND friendship_level = 'PHASE1_STRANGER'

Result:
"4. EXTRA INFORMATION
Date: 2025-11-27T10:00:00Z

5. TODAY'S Talking agenda:
Nói về ngày hôm nay của tôi. Hướng dần về A → B → C.

Goal A – Explore
Trigger: Pika mở đầu bằng câu hỏi về ngày của Trúc.
Action:
Khuyến khích Trúc kể bằng tiếng Việt (tối đa 1–2 câu/lượt).
..."
```

**Bước 9: Ghép prompt cuối cùng**

```
FINAL PROMPT = 
  context_style_guideline (từ bước 3)
  + user_profile (từ bước 4)
  + talking_agenda (từ bước 8)

=

"Every exchange in this convo must be less than 30 word count...

1. CONTEXT
Bạn là Pika: đến từ \"Hành tinh Popa\". Còn tôi là Trúc 10 tuổi...

6. USER PROFILE
Tên trẻ: Trúc
Tuổi: 10
Bộ phim yêu thích: Zootopia

4. EXTRA INFORMATION
Date: 2025-11-27T10:00:00Z

5. TODAY'S Talking agenda:
Nói về ngày hôm nay của tôi. Hướng dần về A → B → C.

Goal A – Explore
Trigger: Pika mở đầu bằng câu hỏi về ngày của Trúc.
Action:
Khuyến khích Trúc kể bằng tiếng Việt (tối đa 1–2 câu/lượt).
..."
```

**Output:**

```
Prompt cuối cùng để gửi cho AI (Pika)
```

---

## 3️⃣ LOGIC CHỌN TOPIC - CHI TIẾT

### Chiến Lược Chọn Topic

```python
def select_topic(topic_metric, friendship_level):
    """
    Chọn topic dựa trên:
    1. Score cao (user thích nói về topic này)
    2. Lâu không nói (cần khám phá)
    3. Random (để đa dạng)
    """
  
    # Ưu tiên 1: Topic chưa nói (score = 0)
    untouched = [t for t, m in topic_metric.items() if m['score'] == 0]
    if untouched:
        return random.choice(untouched)
  
    # Ưu tiên 2: Topic score cao
    high_score = sorted(
        topic_metric.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    top_3 = high_score[:3]
  
    # Ưu tiên 3: Topic lâu không nói
    old_topics = sorted(
        top_3,
        key=lambda x: x[1]['last_date']
    )
  
    return old_topics[0][0]  # Chọn topic lâu nhất không nói
```

### Ví Dụ

```
topic_metric = {
  "toy": {score: 0, turns: 0, last_date: "2025-11-24"},
  "movie": {score: 120.0, turns: 150, last_date: "2025-11-25"},
  "school": {score: 40.0, turns: 30, last_date: "2025-11-23"}
}

Bước 1: Tìm topic chưa nói
  - "toy" có score=0 → Chọn "toy"

Kết quả: topic_id = "toy"
```

---

## 4️⃣ LOGIC CHỌN AGENT - CHI TIẾT

### Chiến Lược Chọn Agent

```python
def select_agent(topic_id, topic_metric, friendship_level):
    """
    Chọn agent dựa trên:
    1. Topic friendship_level
    2. Có sẵn agent cho phase đó
    """
  
    # Lấy topic friendship_level
    topic_phase = topic_metric[topic_id]['friendship_level']
  
    # Nếu topic phase < chung phase → Dùng topic phase
    # Nếu topic phase >= chung phase → Dùng chung phase
    if topic_phase < friendship_level:
        use_phase = topic_phase
    else:
        use_phase = friendship_level
  
    # Query agents cho topic + phase
    agents = db.query(PromptGuideByTopic).filter(
        PromptGuideByTopic.topic_id == topic_id,
        PromptGuideByTopic.friendship_level == use_phase
    ).all()
  
    # Chọn agent random
    return random.choice(agents)
```

### Ví Dụ

```
topic_id = "toy"
topic_metric["toy"].friendship_level = "STRANGER"
friendship_level = "STRANGER"

Bước 1: Compare phases
  - topic phase = "STRANGER"
  - chung phase = "STRANGER"
  - topic phase < chung phase? NO
  - Dùng chung phase = "STRANGER"

Bước 2: Query agents
  Query: SELECT * FROM prompt_template_for_level_friendship
         WHERE topic_id = 'toy'
         AND friendship_level = 'PHASE1_STRANGER'
  
  Result: agent_toy_1

Kết quả: agent_id = "agent_toy_1"
```

---

## 5️⃣ LOGIC GHÉP PROMPT - CHI TIẾT

### Công Thức Ghép Prompt

```
FINAL PROMPT = 
  persona_by_phase.context_style_guideline
  + persona_by_phase.user_profile
  + prompt_template_for_level_friendship.talking_agenda
```

### Code Implementation

```python
def build_final_prompt(user_id, topic_id, agent_id):
    """
    Ghép prompt cuối cùng
    """
  
    # Bước 1: Lấy friendship_status
    friendship_status = db.query(FriendshipStatus).filter(
        FriendshipStatus.user_id == user_id
    ).first()
  
    friendship_level = friendship_status.friendship_level
  
    # Bước 2: Lấy context_style_guideline + user_profile
    persona = db.query(PromptTemplateForLevelFriend).filter(
        PromptTemplateForLevelFriend.friendship_level == friendship_level
    ).first()
  
    context_style = persona.context_style_guideline
    user_profile = persona.user_profile
  
    # Replace user_profile variables
    user_profile = user_profile.replace("{{name}}", friendship_status.user_name)
    user_profile = user_profile.replace("{{age}}", str(friendship_status.user_age))
    # ... more replacements
  
    # Bước 3: Lấy talking_agenda
    prompt_guide = db.query(PromptGuideByTopic).filter(
        PromptGuideByTopic.topic_id == topic_id,
        PromptGuideByTopic.agent_id == agent_id,
        PromptGuideByTopic.friendship_level == friendship_level
    ).first()
  
    talking_agenda = prompt_guide.talking_agenda
  
    # Replace talking_agenda variables
    talking_agenda = talking_agenda.replace(
        "{{current_date_time}}",
        datetime.now().isoformat()
    )
    # ... more replacements
  
    # Bước 4: Ghép prompt cuối cùng
    final_prompt = f"{context_style}\n\n{user_profile}\n\n{talking_agenda}"
  
    return final_prompt
```

---

## 6️⃣ MIGRATION SCRIPT

### Alembic Migration

```python
# migrations/versions/003_add_prompt_tables.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Thêm cột vào friendship_status
    op.add_column('friendship_status', 
        sa.Column('last_emotion', sa.String(50), nullable=True))
    op.add_column('friendship_status',
        sa.Column('last_followup_topic', sa.String(255), nullable=True))
  
    # Tạo bảng prompt_template_for_level_friendship
    op.create_table(
        'prompt_template_for_level_friendship',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('friendship_level', sa.String(50), nullable=False),
        sa.Column('context_style_guideline', sa.Text(), nullable=False),
        sa.Column('user_profile', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('friendship_level')
    )
  
    # Tạo bảng prompt_template_for_level_friendship
    op.create_table(
        'prompt_template_for_level_friendship',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.String(255), nullable=False),
        sa.Column('agent_id', sa.String(255), nullable=False),
        sa.Column('talking_agenda', sa.Text(), nullable=False),
        sa.Column('friendship_level', sa.String(50), nullable=False),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('topic_id', 'agent_id', 'friendship_level')
    )
  
    # Tạo indexes
    op.create_index('idx_prompt_template_phase', 'prompt_template_for_level_friendship', ['friendship_level'])
    op.create_index('idx_prompt_guide_topic', 'prompt_template_for_level_friendship', ['topic_id'])
    op.create_index('idx_prompt_guide_agent', 'prompt_template_for_level_friendship', ['agent_id'])
    op.create_index('idx_prompt_guide_phase', 'prompt_template_for_level_friendship', ['friendship_level'])
    op.create_index('idx_prompt_guide_unique', 'prompt_template_for_level_friendship', ['topic_id', 'agent_id', 'friendship_level'], unique=True)

def downgrade():
    op.drop_index('idx_prompt_guide_unique', 'prompt_template_for_level_friendship')
    op.drop_index('idx_prompt_guide_phase', 'prompt_template_for_level_friendship')
    op.drop_index('idx_prompt_guide_agent', 'prompt_template_for_level_friendship')
    op.drop_index('idx_prompt_guide_topic', 'prompt_template_for_level_friendship')
    op.drop_index('idx_prompt_template_phase', 'prompt_template_for_level_friendship')
    op.drop_table('prompt_template_for_level_friendship')
    op.drop_table('prompt_template_for_level_friendship')
    op.drop_column('friendship_status', 'last_followup_topic')
    op.drop_column('friendship_status', 'last_emotion')
```

---

## 7️⃣ SQLALCHEMY MODELS

### Models

```python
# app/models/friendship_status_model.py
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class FriendshipStatus(Base):
    __tablename__ = 'friendship_status'
  
    user_id = Column(String(255), primary_key=True)
    friendship_score = Column(Float, default=0.0)
    friendship_level = Column(String(50), default='PHASE1_STRANGER')
    topic_metric = Column(JSON, default={})
    last_emotion = Column(String(50), nullable=True)
    last_followup_topic = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction_date = Column(DateTime, nullable=True)
    streak_day = Column(Integer, default=0)
    total_turns = Column(Integer, default=0)

# app/models/prompt_template_model.py
class PromptTemplateForLevelFriend(Base):
    __tablename__ = 'prompt_template_for_level_friendship'
  
    id = Column(Integer, primary_key=True)
    friendship_level = Column(String(50), unique=True)
    context_style_guideline = Column(String)
    user_profile = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# app/models/prompt_guide_model.py
class PromptGuideByTopic(Base):
    __tablename__ = 'prompt_template_for_level_friendship'
  
    id = Column(Integer, primary_key=True)
    topic_id = Column(String(255))
    agent_id = Column(String(255))
    talking_agenda = Column(String)
    friendship_level = Column(String(50))
    agent_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 8️⃣ PYDANTIC SCHEMAS

### Request/Response Schemas

```python
# app/schemas/friendship_status_schema.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TopicMetricItem(BaseModel):
    score: float
    turns: int
    friendship_level: str
    last_date: datetime

class FriendshipStatusResponse(BaseModel):
    user_id: str
    friendship_score: float
    friendship_level: str
    topic_metric: Dict[str, TopicMetricItem]
    last_emotion: Optional[str]
    last_followup_topic: Optional[str]
    last_interaction_date: Optional[datetime]
    streak_day: int
    total_turns: int
  
    class Config:
        from_attributes = True

# app/schemas/prompt_schema.py
class PromptTemplateResponse(BaseModel):
    id: int
    friendship_level: str
    context_style_guideline: str
    user_profile: str
  
    class Config:
        from_attributes = True

class PromptGuideResponse(BaseModel):
    id: int
    topic_id: str
    agent_id: str
    talking_agenda: str
    friendship_level: str
    agent_type: str
  
    class Config:
        from_attributes = True

class FinalPromptResponse(BaseModel):
    user_id: str
    topic_id: str
    agent_id: str
    final_prompt: str
    friendship_level: str
```

---

## 9️⃣ REPOSITORY METHODS

### Repository Implementation

```python
# app/repositories/prompt_repository.py
from sqlalchemy.orm import Session
from app.models import PromptTemplateForLevelFriend, PromptGuideByTopic

class PromptRepository:
    def __init__(self, db: Session):
        self.db = db
  
    def get_template_by_phase(self, friendship_level: str):
        """Lấy template theo phase"""
        return self.db.query(PromptTemplateForLevelFriend).filter(
            PromptTemplateForLevelFriend.friendship_level == friendship_level
        ).first()
  
    def get_guide_by_topic_and_phase(self, topic_id: str, friendship_level: str):
        """Lấy guide theo topic và phase"""
        return self.db.query(PromptGuideByTopic).filter(
            PromptGuideByTopic.topic_id == topic_id,
            PromptGuideByTopic.friendship_level == friendship_level
        ).all()
  
    def get_guide_by_topic_agent_phase(self, topic_id: str, agent_id: str, friendship_level: str):
        """Lấy guide theo topic, agent và phase"""
        return self.db.query(PromptGuideByTopic).filter(
            PromptGuideByTopic.topic_id == topic_id,
            PromptGuideByTopic.agent_id == agent_id,
            PromptGuideByTopic.friendship_level == friendship_level
        ).first()
```

---

## 🔟 SUMMARY

### Thay Đổi Chính

| Aspect                | Cũ         | Mới                              |
| :-------------------- | :---------- | :-------------------------------- |
| **Bảng**       | 2           | 4                                 |
| **Logic chọn** | Đơn giản | Chi tiết (topic + phase)         |
| **Prompt**      | Không có  | Có 3 bảng template              |
| **Flexibility** | Thấp       | Cao (mỗi phase/topic khác nhau) |

### Lợi Ích

✅ **Linh hoạt:** Mỗi topic có agent khác nhau cho mỗi phase
✅ **Chi tiết:** Có prompt template cho mỗi trường hợp
✅ **Dễ quản lý:** Tách riêng template và logic chọn
✅ **Dễ mở rộng:** Thêm topic/agent/phase mà không cần code

---

**Tài liệu cập nhật sẵn sàng!** 🚀
