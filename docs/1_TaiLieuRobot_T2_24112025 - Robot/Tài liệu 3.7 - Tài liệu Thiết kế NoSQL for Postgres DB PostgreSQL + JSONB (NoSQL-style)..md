# Kiến trúc Repository: Context Handling Service (PostgreSQL + JSONB)

**Version:** 1.0  
**Date:** 25/11/2025  
**Technology Stack:** Python 3.11+, FastAPI, PostgreSQL (JSONB), SQLAlchemy

---

Bảng friendship of user : user_id, friendship_score, friendship_level, last_interaction_date, streak_day, topic_metrics

Bảng friendship map with agent (3 loại: Gretting, Talk, Game/ACtivitity, )

---

## 1. Khái niệm: PostgreSQL + JSONB (NoSQL-style)

Thay vì tách dữ liệu thành nhiều bảng quan hệ, chúng ta sẽ sử dụng **PostgreSQL JSONB columns** để lưu trữ dữ liệu dạng JSON. Điều này cho phép:

- **Linh hoạt:** Dễ thêm/xóa fields mà không cần migration
- **Đơn giản:** Ít bảng, ít relationships
- **Hiệu suất:** PostgreSQL JSONB có indexing và querying tốt
- **NoSQL-like:** Cảm giác giống MongoDB nhưng với sức mạnh của PostgreSQL

---

## 2. Cấu trúc Thư mục

```
context-handling-service/
│
├── README.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app entry point
│   │
│   ├── models.py                      # SQLAlchemy models (chỉ 3 bảng)
│   ├── schemas.py                     # Pydantic schemas
│   ├── database.py                    # Database configuration
│   │
│   ├── routes.py                      # Tất cả API routes
│   ├── services.py                    # Tất cả business logic
│   ├── repository.py                  # Tất cả database queries
│   │
│   └── utils.py                       # Helper functions, enums, constants
│
├── migrations/                        # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── tests/
│   ├── test_api.py
│   └── test_services.py
│
└── logs/
    └── .gitkeep
```

---

## 3. Database Schema (Chỉ 3 bảng)

### 3.1. Bảng `users`

```sql
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2. Bảng `friendship_data` (JSONB)

Lưu **tất cả dữ liệu tình bạn** của một user trong một document JSONB duy nhất.

```sql
CREATE TABLE friendship_data (
    user_id VARCHAR(255) PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_friendship_data_score ON friendship_data USING GIN (data);
CREATE INDEX idx_friendship_data_level ON friendship_data ((data->>'friendship_level'));
CREATE INDEX idx_friendship_data_phase ON friendship_data ((data->>'phase'));
```

**Cấu trúc JSON bên trong `data` column:**

```json
{
  "friendship_score": 785.5,
  "friendship_level": "PHASE2_ACQUAINTANCE",
  "phase": "PHASE_2",
  "last_interaction_date": "2025-11-25T18:30:00Z",
  "streak_day": 6,
  
  "topic_metrics": {
    "agent_movie": {
      "topic_score": 52.0,
      "total_turns": 65,
      "last_talked_date": "2025-11-25T18:25:00Z"
    },
    "agent_animal": {
      "topic_score": 28.5,
      "total_turns": 32,
      "last_talked_date": "2025-11-24T14:10:00Z"
    }
  },
  
  "dynamic_memories": [
    {
      "memory_id": "mem_001",
      "content": "Thích xem phim của đạo diễn Hayao Miyazaki",
      "related_topic": "agent_movie",
      "timestamp": "2025-11-25T18:28:00Z"
    },
    {
      "memory_id": "mem_002",
      "content": "Có một con mèo tên Milu",
      "related_topic": "agent_animal",
      "timestamp": "2025-11-24T14:05:00Z"
    }
  ],
  
  "interaction_history": [
    {
      "interaction_id": "int_001",
      "session_start_time": "2025-11-25T18:00:00Z",
      "session_end_time": "2025-11-25T18:30:00Z",
      "total_turns": 15,
      "session_emotion": "interesting",
      "friendship_score_change": 35.0,
      "conversation_log": [
        {"speaker": "user", "turn_id": 1, "text": "Hello Pika!"},
        {"speaker": "pika", "turn_id": 2, "text": "Hi there! How are you?"}
      ]
    }
  ]
}
```

### 3.3. Bảng `agent_pool` (JSONB)

Lưu **tất cả dữ liệu Agent** trong một document JSONB duy nhất.

```sql
CREATE TABLE agent_pool (
    agent_id VARCHAR(255) PRIMARY KEY,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_agent_pool_type ON agent_pool ((data->>'agent_type'));
CREATE INDEX idx_agent_pool_active ON agent_pool ((data->>'is_active'));
```

**Cấu trúc JSON bên trong `data` column:**

```json
{
  "agent_id": "greeting_streak_milestone_5_days",
  "agent_name": "Greeting - 5 Day Streak",
  "agent_type": "GREETING",
  "description": "Chào mừng người dùng khi đạt 5 ngày tương tác liên tiếp",
  "is_active": true,
  "metadata": {
    "version": "1.0",
    "tags": ["greeting", "milestone", "streak"],
    "required_phase": "PHASE_2",
    "weight": 1.5
  }
}
```

---

## 4. Chi tiết từng File

### 4.1. `app/models.py` - ORM Models (Chỉ 3 bảng)

```python
from sqlalchemy import Column, String, DateTime, JSONB, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FriendshipData(Base):
    """Lưu tất cả dữ liệu tình bạn của user trong một JSONB document"""
    __tablename__ = "friendship_data"
    user_id = Column(String, primary_key=True)
    data = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentPool(Base):
    """Lưu tất cả dữ liệu Agent trong một JSONB document"""
    __tablename__ = "agent_pool"
    agent_id = Column(String, primary_key=True)
    data = Column(JSONB, default={}, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 4.2. `app/schemas.py` - Pydantic Schemas

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============ Friendlyship Schemas ============

class TopicMetricsSchema(BaseModel):
    topic_score: float
    total_turns: int
    last_talked_date: Optional[datetime] = None

class DynamicMemorySchema(BaseModel):
    memory_id: str
    content: str
    related_topic: Optional[str] = None
    timestamp: datetime

class InteractionLogSchema(BaseModel):
    speaker: str  # "user" or "pika"
    turn_id: int
    text: str

class InteractionHistorySchema(BaseModel):
    interaction_id: str
    session_start_time: datetime
    session_end_time: datetime
    total_turns: int
    session_emotion: Optional[str] = None
    friendship_score_change: float
    conversation_log: List[InteractionLogSchema]

class FriendshipDataSchema(BaseModel):
    friendship_score: float
    friendship_level: str  # PHASE1_STRANGER, PHASE2_ACQUAINTANCE, PHASE3_FRIEND
    phase: str  # PHASE_1, PHASE_2, PHASE_3
    last_interaction_date: Optional[datetime] = None
    streak_day: int = 0
    topic_metrics: Dict[str, TopicMetricsSchema] = {}
    dynamic_memories: List[DynamicMemorySchema] = []
    interaction_history: List[InteractionHistorySchema] = []

# ============ API Request/Response Schemas ============

class ConversationLogItem(BaseModel):
    speaker: str
    turn_id: int
    text: str

class CalculateFriendshipRequest(BaseModel):
    user_id: str
    conversation_log: List[ConversationLogItem]
    session_emotion: Optional[str] = None

class TopicMetricsUpdateSchema(BaseModel):
    score_change: float
    turns_increment: int

class CalculateFriendshipResponse(BaseModel):
    friendship_score_change: float
    topic_metrics_update: Dict[str, TopicMetricsUpdateSchema] = {}
    new_memories: List[Dict[str, Any]] = []

class UpdateFriendshipRequest(BaseModel):
    friendship_score_change: float
    topic_metrics_update: Dict[str, TopicMetricsUpdateSchema] = {}
    new_memories: List[Dict[str, Any]] = []

class FriendshipStatusResponse(BaseModel):
    user_id: str
    friendship_score: float
    friendship_level: str
    phase: str
    streak_day: int
    last_interaction_date: Optional[datetime]
    topic_metrics: Dict[str, TopicMetricsSchema]

# ============ Agent Schemas ============

class AgentMetadataSchema(BaseModel):
    version: str
    tags: List[str]
    required_phase: str
    weight: float

class AgentDataSchema(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str  # GREETING, TALK, GAME
    description: str
    is_active: bool
    metadata: Optional[AgentMetadataSchema] = None

class SuggestedActivitiesResponse(BaseModel):
    greeting_agent: Optional[AgentDataSchema]
    suggested_agents: List[AgentDataSchema]
```

### 4.3. `app/services.py` - Business Logic

```python
from sqlalchemy.orm import Session
from app.models import FriendshipData, AgentPool
from app.schemas import CalculateFriendshipRequest, CalculateFriendshipResponse, FriendshipDataSchema
from datetime import datetime
from typing import Dict, Any
import json

class FriendshipService:
    """Quản lý tính toán và cập nhật điểm tình bạn"""
    
    @staticmethod
    def calculate_friendship_score(request: CalculateFriendshipRequest) -> CalculateFriendshipResponse:
        """Tính toán thay đổi điểm từ log hội thoại"""
        
        # 1. Phân tích log
        total_turns = len(request.conversation_log)
        user_initiated = sum(1 for msg in request.conversation_log if msg.speaker == "user")
        
        # 2. Tính điểm cơ bản
        base_score = total_turns * 0.5
        engagement_bonus = user_initiated * 3
        emotion_bonus = 15 if request.session_emotion == "interesting" else -15 if request.session_emotion == "boring" else 0
        
        friendship_score_change = base_score + engagement_bonus + emotion_bonus
        
        # 3. Tính topic metrics (đơn giản hóa)
        topic_metrics_update = {}
        
        # 4. Trích ký ức (đơn giản hóa)
        new_memories = []
        
        return CalculateFriendshipResponse(
            friendship_score_change=friendship_score_change,
            topic_metrics_update=topic_metrics_update,
            new_memories=new_memories
        )
    
    @staticmethod
    def update_friendship_status(db: Session, user_id: str, score_change: float, topic_updates: Dict = None, new_memories: list = None):
        """Cập nhật trạng thái tình bạn vào DB (JSONB)"""
        
        # 1. Lấy hoặc tạo document
        friendship_doc = db.query(FriendshipData).filter(FriendshipData.user_id == user_id).first()
        
        if not friendship_doc:
            # Tạo document mới
            friendship_doc = FriendshipData(
                user_id=user_id,
                data={
                    "friendship_score": score_change,
                    "friendship_level": "PHASE1_STRANGER",
                    "phase": "PHASE_1",
                    "last_interaction_date": datetime.utcnow().isoformat(),
                    "streak_day": 1,
                    "topic_metrics": {},
                    "dynamic_memories": [],
                    "interaction_history": []
                }
            )
            db.add(friendship_doc)
        else:
            # Cập nhật document hiện tại
            data = friendship_doc.data
            
            # Cập nhật score
            data["friendship_score"] = data.get("friendship_score", 0) + score_change
            data["last_interaction_date"] = datetime.utcnow().isoformat()
            
            # Cập nhật level và phase dựa trên score
            score = data["friendship_score"]
            if score < 100:
                data["friendship_level"] = "PHASE1_STRANGER"
                data["phase"] = "PHASE_1"
            elif score < 500:
                data["friendship_level"] = "PHASE2_ACQUAINTANCE"
                data["phase"] = "PHASE_2"
            else:
                data["friendship_level"] = "PHASE3_FRIEND"
                data["phase"] = "PHASE_3"
            
            # Cập nhật topic metrics
            if topic_updates:
                if "topic_metrics" not in data:
                    data["topic_metrics"] = {}
                data["topic_metrics"].update(topic_updates)
            
            # Thêm ký ức mới
            if new_memories:
                if "dynamic_memories" not in data:
                    data["dynamic_memories"] = []
                data["dynamic_memories"].extend(new_memories)
            
            friendship_doc.data = data
        
        db.commit()
        return friendship_doc
    
    @staticmethod
    def get_friendship_status(db: Session, user_id: str) -> Dict[str, Any]:
        """Lấy trạng thái tình bạn hiện tại"""
        doc = db.query(FriendshipData).filter(FriendshipData.user_id == user_id).first()
        
        if not doc:
            return None
        
        return {
            "user_id": user_id,
            **doc.data
        }

class SelectionService:
    """Lựa chọn Agent phù hợp cho người dùng"""
    
    @staticmethod
    def get_suggested_activities(db: Session, user_id: str) -> Dict[str, Any]:
        """Lấy danh sách Agent đề xuất"""
        
        # 1. Lấy trạng thái tình bạn
        friendship_status = FriendshipService.get_friendship_status(db, user_id)
        
        if not friendship_status:
            # Tạo user mới nếu chưa tồn tại
            FriendshipService.update_friendship_status(db, user_id, 0)
            friendship_status = FriendshipService.get_friendship_status(db, user_id)
        
        phase = friendship_status.get("phase", "PHASE_1")
        
        # 2. Lấy tất cả agents từ agent_pool
        all_agents = db.query(AgentPool).filter(AgentPool.data["is_active"].astext == "true").all()
        
        # 3. Lọc agents theo phase
        suitable_agents = []
        for agent in all_agents:
            agent_data = agent.data
            required_phase = agent_data.get("metadata", {}).get("required_phase")
            
            if required_phase == phase or required_phase is None:
                suitable_agents.append(agent_data)
        
        # 4. Tách greeting agent và talk/game agents
        greeting_agents = [a for a in suitable_agents if a.get("agent_type") == "GREETING"]
        talk_game_agents = [a for a in suitable_agents if a.get("agent_type") in ["TALK", "GAME"]]
        
        return {
            "greeting_agent": greeting_agents[0] if greeting_agents else None,
            "suggested_agents": talk_game_agents[:4]
        }
```

### 4.4. `app/repository.py` - Database Queries

```python
from sqlalchemy.orm import Session
from app.models import FriendshipData, AgentPool
from typing import Dict, Any

class Repository:
    """Tập hợp tất cả database queries"""
    
    @staticmethod
    def get_friendship_data(db: Session, user_id: str) -> FriendshipData:
        """Lấy document tình bạn"""
        return db.query(FriendshipData).filter(FriendshipData.user_id == user_id).first()
    
    @staticmethod
    def update_friendship_data(db: Session, user_id: str, data: Dict[str, Any]) -> FriendshipData:
        """Cập nhật document tình bạn"""
        doc = db.query(FriendshipData).filter(FriendshipData.user_id == user_id).first()
        if doc:
            doc.data = data
            db.commit()
        return doc
    
    @staticmethod
    def get_all_agents(db: Session) -> list:
        """Lấy tất cả agents"""
        return db.query(AgentPool).all()
    
    @staticmethod
    def get_agent_by_id(db: Session, agent_id: str) -> AgentPool:
        """Lấy agent theo ID"""
        return db.query(AgentPool).filter(AgentPool.agent_id == agent_id).first()
    
    @staticmethod
    def create_agent(db: Session, agent_id: str, agent_data: Dict[str, Any]) -> AgentPool:
        """Tạo agent mới"""
        agent = AgentPool(agent_id=agent_id, data=agent_data)
        db.add(agent)
        db.commit()
        return agent
    
    @staticmethod
    def update_agent(db: Session, agent_id: str, agent_data: Dict[str, Any]) -> AgentPool:
        """Cập nhật agent"""
        agent = db.query(AgentPool).filter(AgentPool.agent_id == agent_id).first()
        if agent:
            agent.data = agent_data
            db.commit()
        return agent
    
    @staticmethod
    def delete_agent(db: Session, agent_id: str) -> bool:
        """Xóa agent"""
        agent = db.query(AgentPool).filter(AgentPool.agent_id == agent_id).first()
        if agent:
            db.delete(agent)
            db.commit()
            return True
        return False
```

### 4.5. `app/routes.py` - API Routes

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CalculateFriendshipRequest, UpdateFriendshipRequest, AgentDataSchema
from app.services import FriendshipService, SelectionService
from app.repository import Repository

router = APIRouter(prefix="/v1", tags=["api"])

# ============ Friendlyship Routes ============

@router.post("/scoring/calculate-friendship")
def calculate_friendship(request: CalculateFriendshipRequest, db: Session = Depends(get_db)):
    """Tính toán điểm tình bạn từ log hội thoại"""
    result = FriendshipService.calculate_friendship_score(request)
    return result

@router.post("/users/{user_id}/update-friendship")
def update_friendship(user_id: str, request: UpdateFriendshipRequest, db: Session = Depends(get_db)):
    """Cập nhật trạng thái tình bạn vào DB"""
    FriendshipService.update_friendship_status(
        db, 
        user_id, 
        request.friendship_score_change,
        request.topic_metrics_update,
        request.new_memories
    )
    status = FriendshipService.get_friendship_status(db, user_id)
    return {"success": True, "data": status}

@router.get("/users/{user_id}/status")
def get_friendship_status(user_id: str, db: Session = Depends(get_db)):
    """Lấy trạng thái tình bạn hiện tại"""
    status = FriendshipService.get_friendship_status(db, user_id)
    return status if status else {"error": "User not found"}

# ============ Talk/Agent Routes ============

@router.get("/users/{user_id}/suggested-activities")
def get_suggested_activities(user_id: str, db: Session = Depends(get_db)):
    """Lấy danh sách Agent đề xuất"""
    result = SelectionService.get_suggested_activities(db, user_id)
    return result

@router.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả agents"""
    agents = Repository.get_all_agents(db)
    return [{"agent_id": a.agent_id, **a.data} for a in agents]

@router.post("/agents")
def create_agent(agent_id: str, agent_data: dict, db: Session = Depends(get_db)):
    """Tạo agent mới"""
    agent = Repository.create_agent(db, agent_id, agent_data)
    return {"agent_id": agent.agent_id, **agent.data}

@router.put("/agents/{agent_id}")
def update_agent(agent_id: str, agent_data: dict, db: Session = Depends(get_db)):
    """Cập nhật agent"""
    agent = Repository.update_agent(db, agent_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"agent_id": agent.agent_id, **agent.data}

@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Xóa agent"""
    success = Repository.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True}
```

### 4.6. `app/database.py` - Database Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/context_handling_db")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4.7. `app/main.py` - FastAPI App

```python
from fastapi import FastAPI
from app.database import engine, Base
from app import routes

# Tạo tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Context Handling Service", version="1.0.0")

# Include routes
app.include_router(routes.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### 4.8. `app/utils.py` - Helpers

```python
from enum import Enum

class FriendshipPhase(str, Enum):
    PHASE1_STRANGER = "PHASE1_STRANGER"
    PHASE2_ACQUAINTANCE = "PHASE2_ACQUAINTANCE"
    PHASE3_FRIEND = "PHASE3_FRIEND"

class Phase(str, Enum):
    PHASE_1 = "PHASE_1"
    PHASE_2 = "PHASE_2"
    PHASE_3 = "PHASE_3"

class AgentType(str, Enum):
    GREETING = "GREETING"
    TALK = "TALK"
    GAME = "GAME"

class Emotion(str, Enum):
    INTERESTING = "interesting"
    BORING = "boring"
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
```

---

## 5. File Cấu hình

### 5.1. `requirements.txt`

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
alembic==1.13.0
pytest==7.4.3
```

### 5.2. `.env.example`

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/context_handling_db
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

### 5.3. `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.4. `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/context_handling_db
    depends_on:
      - db
    volumes:
      - ./app:/app/app

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: context_handling_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 6. Lợi ích của Cách tiếp cận PostgreSQL + JSONB

| Aspect | Lợi ích |
| :--- | :--- |
| **Linh hoạt Schema** | Thêm/xóa fields mà không cần migration |
| **Ít Bảng** | Chỉ 3 bảng thay vì 7 bảng |
| **Dễ Mở rộng** | Thêm dữ liệu mới vào JSON mà không ảnh hưởng cấu trúc |
| **Hiệu suất JSONB** | PostgreSQL JSONB có GIN indexing, querying nhanh |
| **NoSQL-like** | Cảm giác giống MongoDB nhưng với ACID compliance của PostgreSQL |
| **Tính Toàn vẹn** | Vẫn có referential integrity (FK) và transactions |
| **Đơn giản Code** | Ít models, ít repositories, ít migrations |

---

## 7. So sánh: Relational vs JSONB

| Aspect | Relational (7 bảng) | JSONB (3 bảng) |
| :--- | :--- | :--- |
| **Số bảng** | 7 | 3 |
| **Migrations** | Nhiều | Ít |
| **Flexibility** | Cứng nhắc | Linh hoạt |
| **Querying** | Joins phức tạp | Đơn giản (JSONB operators) |
| **Performance** | Tốt cho queries phức tạp | Tốt cho document-based queries |
| **Learning Curve** | Cao | Thấp |

---

## 8. Quy trình Triển khai

```bash
# 1. Setup
git clone <repo-url>
cd context-handling-service
pip install -r requirements.txt
cp .env.example .env

# 2. Khởi động database
docker-compose up -d db

# 3. Chạy migrations
alembic upgrade head

# 4. Seed dữ liệu
python scripts/seed_agents.py

# 5. Chạy ứng dụng
uvicorn app.main:app --reload
```

---

## 9. Ví dụ API Calls

### 9.1. Tính toán điểm

```bash
curl -X POST http://localhost:8000/v1/scoring/calculate-friendship \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "conversation_log": [
      {"speaker": "user", "turn_id": 1, "text": "Hi Pika!"},
      {"speaker": "pika", "turn_id": 2, "text": "Hello! How are you?"}
    ],
    "session_emotion": "interesting"
  }'
```

### 9.2. Cập nhật trạng thái

```bash
curl -X POST http://localhost:8000/v1/users/user_123/update-friendship \
  -H "Content-Type: application/json" \
  -d '{
    "friendship_score_change": 35.0,
    "topic_metrics_update": {},
    "new_memories": []
  }'
```

### 9.3. Lấy trạng thái

```bash
curl http://localhost:8000/v1/users/user_123/status
```

### 9.4. Lấy Agent đề xuất

```bash
curl http://localhost:8000/v1/users/user_123/suggested-activities
```

---

## 10. Kết luận

Cách tiếp cận **PostgreSQL + JSONB** kết hợp được:
- **Tính linh hoạt** của NoSQL (MongoDB-style)
- **Tính mạnh mẽ** của SQL (transactions, ACID)
- **Tính đơn giản** của cấu trúc (3 bảng, ít migrations)

Đây là lựa chọn tối ưu cho MVP và có thể dễ dàng mở rộng hoặc tách thành microservices sau.
