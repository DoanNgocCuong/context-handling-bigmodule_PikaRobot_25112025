## 8. Define Folder Structure SOLID (Đơn giản nhưng Mạnh)

### 8.1. Cấu trúc Tổng thể

```
context-handling-service/
│
├── README.md                                    # Tài liệu chính của project
├── .env.example                                 # Template environment variables
├── .gitignore                                   # Git ignore file
├── requirements.txt                             # Python dependencies
├── pyproject.toml                               # Project configuration
├── Dockerfile                                   # Docker image definition
├── docker-compose.yml                           # Docker compose for local dev
│
├── app/                                         # Main application package
│   ├── __init__.py
│   │
│   ├── core/                                    # Core configuration & constants
│   │   ├── __init__.py
│   │   ├── config_settings.py                   # ✅ Settings & environment variables
│   │   ├── constants_enums.py                   # ✅ Constants & enums (FriendshipLevel, AgentType, etc.)
│   │   ├── exceptions_custom.py                 # ✅ Custom exceptions (FriendshipNotFoundError, etc.)
│   │   └── status_codes.py                      # ✅ HTTP status codes & error messages
│   │
│   ├── models/                                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base_model.py                        # ✅ Base model class with common fields
│   │   ├── friendship_status_model.py           # ✅ FriendshipStatus table model
│   │   ├── friendship_agent_mapping_model.py    # ✅ FriendshipAgentMapping table model
│   │   └── conversation_model.py                # ✅ Conversation table model (if needed)
│   │
│   ├── schemas/                                 # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── friendship_status_schemas.py         # ✅ FriendshipStatus request/response
│   │   ├── friendship_agent_mapping_schemas.py  # ✅ AgentMapping request/response
│   │   ├── activity_suggestion_schemas.py       # ✅ Activity suggestion request/response
│   │   ├── conversation_end_schemas.py          # ✅ Conversation end event schema
│   │   └── common_schemas.py                    # ✅ Common schemas (error responses, etc.)
│   │
│   ├── db/                                      # Database layer
│   │   ├── __init__.py
│   │   ├── database_connection.py               # ✅ Database connection & SessionLocal
│   │   ├── base_repository.py                   # ✅ Base repository class (generic CRUD)
│   │   └── database_migrations.py               # ✅ Migration utilities
│   │
│   ├── repositories/                            # Data access layer (Repository pattern)
│   │   ├── __init__.py
│   │   ├── friendship_status_repository.py      # ✅ FriendshipStatus CRUD operations
│   │   ├── friendship_agent_mapping_repository.py # ✅ AgentMapping CRUD operations
│   │   └── conversation_repository.py           # ✅ Conversation lookup operations
│   │
│   ├── services/                                # Business logic layer
│   │   ├── __init__.py
│   │   ├── friendship_score_calculation_service.py  # ✅ Calculate friendship score change
│   │   ├── friendship_status_update_service.py      # ✅ Update friendship status in DB
│   │   ├── topic_metrics_update_service.py          # ✅ Update topic metrics
│   │   ├── agent_selection_algorithm_service.py     # ✅ Select agents (greeting, talk, game)
│   │   ├── activity_suggestion_service.py           # ✅ Suggest activities for user
│   │   └── conversation_data_fetch_service.py       # ✅ Fetch conversation data by ID
│   │
│   ├── tasks/                                   # Background tasks & async jobs
│   │   ├── __init__.py
│   │   ├── process_conversation_end_task.py     # ✅ Background task: process conversation end
│   │   ├── batch_recompute_candidates_task.py   # ✅ Scheduled task: batch recompute (6h)
│   │   └── retry_failed_processing_task.py      # ✅ Retry mechanism for failed tasks
│   │
│   ├── cache/                                   # Caching layer
│   │   ├── __init__.py
│   │   ├── redis_cache_manager.py               # ✅ Redis cache operations
│   │   ├── cache_keys_builder.py                # ✅ Build cache keys (candidates:{user_id})
│   │   └── cache_invalidation_handler.py        # ✅ Invalidate cache when needed
│   │
│   ├── api/                                     # API routes & endpoints
│   │   ├── __init__.py
│   │   ├── dependency_injection.py              # ✅ Dependency injection setup
│   │   │
│   │   └── v1/                                  # API v1
│   │       ├── __init__.py
│   │       ├── router_v1_main.py                # ✅ Main router for v1
│   │       │
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── endpoint_conversations_end.py        # ✅ POST /conversations/end
│   │           ├── endpoint_conversations_get.py        # ✅ GET /conversations/{id}
│   │           ├── endpoint_friendship_status.py        # ✅ POST /friendship/status
│   │           ├── endpoint_friendship_update.py        # ✅ POST /friendship/update
│   │           ├── endpoint_activities_suggest.py       # ✅ POST /activities/suggest
│   │           ├── endpoint_agent_mappings_list.py      # ✅ GET /agent-mappings
│   │           ├── endpoint_agent_mappings_create.py    # ✅ POST /agent-mappings
│   │           ├── endpoint_agent_mappings_update.py    # ✅ PUT /agent-mappings/{id}
│   │           ├── endpoint_agent_mappings_delete.py    # ✅ DELETE /agent-mappings/{id}
│   │           └── endpoint_health_check.py             # ✅ GET /health
│   │
│   ├── utils/                                   # Utility functions & helpers
│   │   ├── __init__.py
│   │   ├── logger_setup.py                      # ✅ Logging configuration & setup
│   │   ├── input_validators.py                  # ✅ Input validation functions
│   │   ├── helper_functions.py                  # ✅ General helper functions
│   │   ├── weighted_random_selection.py         # ✅ Weighted random selection algorithm
│   │   └── datetime_utilities.py                # ✅ DateTime utilities
│   │
│   └── main_app.py                              # ✅ FastAPI app entry point
│
├── migrations/                                  # Alembic database migrations
│   ├── env.py                                   # ✅ Alembic environment config
│   ├── script.py.mako                           # ✅ Migration template
│   │
│   └── versions/
│       ├── __init__.py
│       ├── 001_create_friendship_status_table.py        # ✅ Migration: Create friendship_status
│       ├── 002_create_friendship_agent_mapping_table.py # ✅ Migration: Create agent_mapping
│       └── 003_add_indexes_and_constraints.py           # ✅ Migration: Add indexes
│
├── scripts/                                     # Utility scripts
│   ├── __init__.py
│   ├── script_seed_agent_data.py                # ✅ Seed initial agent data
│   ├── script_initialize_database.py            # ✅ Initialize database (create tables, seed)
│   ├── script_reset_database.py                 # ✅ Reset database (drop all tables)
│   └── script_generate_sample_data.py           # ✅ Generate sample data for testing
│
├── tests/                                       # Test suite
│   ├── __init__.py
│   ├── conftest_pytest_config.py                # ✅ Pytest configuration & fixtures
│   │
│   ├── unit/                                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_friendship_score_calculation.py # ✅ Test score calculation algorithm
│   │   ├── test_topic_metrics_update.py         # ✅ Test topic metrics update
│   │   ├── test_agent_selection_algorithm.py    # ✅ Test agent selection algorithm
│   │   ├── test_friendship_status_repository.py # ✅ Test repository methods
│   │   └── test_input_validators.py             # ✅ Test input validation
│   │
│   ├── integration/                             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_api_conversations_end.py        # ✅ Test POST /conversations/end
│   │   ├── test_api_friendship_status.py        # ✅ Test POST /friendship/status
│   │   ├── test_api_activities_suggest.py       # ✅ Test POST /activities/suggest
│   │   ├── test_api_agent_mappings_crud.py      # ✅ Test agent mappings CRUD
│   │   └── test_end_to_end_flow.py              # ✅ Test complete flow
│   │
│   └── fixtures/                                # Test fixtures & sample data
│       ├── __init__.py
│       ├── fixture_friendship_data.py           # ✅ Friendship test data
│       ├── fixture_agent_data.py                # ✅ Agent test data
│       └── fixture_conversation_data.py         # ✅ Conversation test data
│
├── logs/                                        # Application logs
│   └── .gitkeep
│
├── docs/                                        # Documentation
│   ├── API_SPECIFICATION.md                     # ✅ API specification
│   ├── DATABASE_SCHEMA.md                       # ✅ Database schema documentation
│   ├── ARCHITECTURE.md                          # ✅ Architecture documentation
│   ├── SETUP_GUIDE.md                           # ✅ Setup & installation guide
│   └── DEPLOYMENT_GUIDE.md                      # ✅ Deployment guide
│
└── config/                                      # Configuration files
    ├── logging_config.yaml                      # ✅ Logging configuration
    ├── database_config.yaml                     # ✅ Database configuration
    └── cache_config.yaml                        # ✅ Cache configuration
```

### 8.2. Giải thích Chi tiết

#### **`app/core/`** - Cấu hình & Constants

Tập trung tất cả cấu hình, constants, exceptions.

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
  
    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# app/core/constants.py
from enum import Enum

class FriendshipLevel(str, Enum):
    STRANGER = "STRANGER"
    ACQUAINTANCE = "ACQUAINTANCE"
    FRIEND = "FRIEND"

class AgentType(str, Enum):
    GREETING = "GREETING"
    TALK = "TALK"
    GAME_ACTIVITY = "GAME_ACTIVITY"

# Score thresholds
FRIENDSHIP_SCORE_THRESHOLDS = {
    FriendshipLevel.STRANGER: (0, 100),
    FriendshipLevel.ACQUAINTANCE: (100, 500),
    FriendshipLevel.FRIEND: (500, float('inf'))
}
```

```python
# app/core/exceptions.py
class AppException(Exception):
    """Base exception"""
    pass

class FriendshipNotFoundError(AppException):
    """Raised when friendship status not found"""
    pass

class InvalidScoreError(AppException):
    """Raised when score calculation fails"""
    pass

class AgentSelectionError(AppException):
    """Raised when agent selection fails"""
    pass
```

#### **`app/models/`** - ORM Models

Tách models thành các file nhỏ theo domain.

```python
# app/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

```python
# app/models/friendship.py
from sqlalchemy import Column, String, Float, Integer, DateTime, JSONB
from app.models.base import BaseModel

class FriendshipStatus(BaseModel):
    __tablename__ = "friendship_status"
    user_id = Column(String, primary_key=True)
    friendship_score = Column(Float, default=0.0, nullable=False)
    friendship_level = Column(String, default="STRANGER", nullable=False)
    last_interaction_date = Column(DateTime, nullable=True)
    streak_day = Column(Integer, default=0, nullable=False)
    topic_metrics = Column(JSONB, default={}, nullable=False)
```

#### **`app/schemas/`** - Pydantic Schemas

Tách schemas theo domain.

```python
# app/schemas/friendship.py
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class FriendshipStatusResponse(BaseModel):
    user_id: str
    friendship_score: float
    friendship_level: str
    last_interaction_date: Optional[datetime]
    streak_day: int
    topic_metrics: Dict

    class Config:
        from_attributes = True
```

#### **`app/repositories/`** - Data Access Layer

Repository pattern cho data access.

```python
# app/repositories/base_repository.py
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
  
    def get_by_id(self, id: any):
        return self.db.query(self.model).filter(self.model.id == id).first()
  
    def create(self, obj_in):
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
```

```python
# app/repositories/friendship_repository.py
from sqlalchemy.orm import Session
from app.models import FriendshipStatus
from app.repositories.base_repository import BaseRepository

class FriendshipRepository(BaseRepository[FriendshipStatus]):
    def __init__(self, db: Session):
        super().__init__(db, FriendshipStatus)
  
    def get_by_user_id(self, user_id: str):
        return self.db.query(FriendshipStatus).filter(
            FriendshipStatus.user_id == user_id
        ).first()
  
    def update_score(self, user_id: str, score_change: float):
        status = self.get_by_user_id(user_id)
        if status:
            status.friendship_score += score_change
            self.db.commit()
            self.db.refresh(status)
        return status
```

#### **`app/services/`** - Business Logic

Service layer chứa business logic.

```python
# app/services/friendship_service.py
from sqlalchemy.orm import Session
from app.repositories import FriendshipRepository
from app.schemas import CalculateFriendshipResponse
from app.core.exceptions import FriendshipNotFoundError

class FriendshipService:
    def __init__(self, db: Session):
        self.repository = FriendshipRepository(db)
  
    def calculate_score(self, request) -> CalculateFriendshipResponse:
        """Tính toán điểm từ log"""
        total_turns = len(request.conversation_log)
        user_initiated = sum(1 for msg in request.conversation_log if msg.speaker == "user")
    
        base_score = total_turns * 0.5
        engagement_bonus = user_initiated * 3
    
        return CalculateFriendshipResponse(
            friendship_score_change=base_score + engagement_bonus
        )
  
    def update_status(self, user_id: str, score_change: float):
        """Cập nhật trạng thái"""
        status = self.repository.update_score(user_id, score_change)
        if not status:
            raise FriendshipNotFoundError(f"User {user_id} not found")
        return status
```

#### **`app/api/v1/endpoints/`** - API Routes

Tách routes theo domain.

```python
# app/api/v1/endpoints/friendship.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import CalculateFriendshipRequest, CalculateFriendshipResponse
from app.services import FriendshipService

router = APIRouter(prefix="/scoring", tags=["friendship"])

@router.post("/calculate-friendship", response_model=CalculateFriendshipResponse)
def calculate_friendship(
    request: CalculateFriendshipRequest,
    db: Session = Depends(get_db)
):
    """Tính toán điểm tình bạn"""
    service = FriendshipService(db)
    return service.calculate_score(request)
```

#### **`app/api/deps.py`** - Dependency Injection

Centralized dependency injection.

```python
# app/api/deps.py
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### **`app/utils/logger.py`** - Logging

Structured logging setup.

```python
# app/utils/logger.py
import logging
import json
from app.core.config import settings

def get_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
  
    if settings.ENVIRONMENT == "production":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
  
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.LOG_LEVEL)
  
    return logger
```

---

### 8.3. SOLID Principles Áp dụng

| Principle                           | Cách Áp dụng                                                                   | Lợi ích                                      |
| :---------------------------------- | :-------------------------------------------------------------------------------- | :--------------------------------------------- |
| **S - Single Responsibility** | Mỗi file có 1 trách nhiệm duy nhất (models, schemas, services, repositories) | Dễ test, dễ bảo trì                        |
| **O - Open/Closed**           | Dùng BaseRepository, BaseModel → dễ extend                                     | Dễ thêm feature mới                         |
| **L - Liskov Substitution**   | Repository, Service có interface rõ ràng                                       | Dễ mock, dễ test                             |
| **I - Interface Segregation** | Tách schemas, models theo domain                                                 | Không phụ thuộc vào những gì không cần |
| **D - Dependency Inversion**  | Dùng dependency injection (get_db, services)                                     | Loose coupling, dễ test                       |

---

## 9. Chi tiết luồng đi của API

1. [Luồng Dữ liệu Tổng thể (v3)](#luồng-dữ-liệu-tổng-thể-v3)
2. [Health Check](#health-check)
3. [API 1: Notify Conversation End (BE → AI)](#api-1-notify-conversation-end-be--ai)
4. [API 2: Get Conversation Data (AI → BE)](#api-2-get-conversation-data-ai--be)
5. [API 3: Get Friendship Status (BE → Context Service)](#api-3-get-friendship-status-be--context-service)
6. [API 4: Get Suggested Activities (BE → Context Service)](#api-4-get-suggested-activities-be--context-service)
7. [API 5-8: Agent Mapping Management](#api-5-8-agent-mapping-management)
8. [Async Processing &amp; Scheduling](#async-processing--scheduling)
9. [Error Handling](#error-handling)

---

### Luồng Dữ liệu Tổng thể (v3)

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EVENT-DRIVEN ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

PHASE 1: REAL-TIME NOTIFICATION
═════════════════════════════════════════════════════════════════════════════

1. Frontend/Main App
   └─> User kết thúc cuộc trò chuyện
   
2. Backend Service
   └─> API 1: POST /conversations/end
       (Body: user_id + conversation_id)
       (Response: 202 Accepted - không cần đợi)
   
3. Message Queue (RabbitMQ / Kafka)
   └─> Enqueue event: "conversation.ended"
   └─> Payload: {user_id, conversation_id}


PHASE 2: ASYNC PROCESSING (AI Service)
═════════════════════════════════════════════════════════════════════════════

4. AI Scoring Service (Background Worker)
   └─> Consume event từ queue
   └─> API 2: GET /conversations/{conversation_id}
       (Call BE để lấy conversation data)
   
5. AI Service
   └─> Mổ xẻ conversation log
   └─> Tính toán: friendship_score_change, topic_metrics_update
   └─> Tính toán: new_memories, emotion analysis
   
6. AI Service
   └─> API 3: POST /friendship/update
       (Update friendship_status vào DB)
       (Update: friendship_score, friendship_level, streak_day, topic_metrics)
   
7. AI Service
   └─> API 4: POST /candidates/compute
       (Tính toán & cache candidates cho user)
       (Greeting, Talk, Game agents phù hợp nhất)
       (Có thể batch mỗi 6h hoặc real-time)


PHASE 3: SERVING CACHED DATA (BE Service)
═════════════════════════════════════════════════════════════════════════════

8. Backend Service (Lần tiếp theo user mở app)
   └─> API 5: POST /friendship/status
       (Lấy friendship_status - từ cache/DB)
   
9. Backend Service
   └─> API 6: POST /activities/suggest
       (Lấy pre-computed candidates - từ cache)
       (Response: Greeting + Talk + Game agents)
       (Không cần đợi, dữ liệu đã sẵn!)
   
10. Frontend/Main App
    └─> Hiển thị greeting + 4 agents cho user


PHASE 4: BATCH RECOMPUTATION (Optional - mỗi 6h)
═════════════════════════════════════════════════════════════════════════════

11. Scheduler (AI Service)
    └─> Mỗi 6 giờ, trigger batch job
    └─> Duyệt tất cả active users
    └─> Recompute candidates dựa trên friendship_level hiện tại
    └─> Update cache
```

---

### Health Check

#### Endpoint

```
GET /health
```

#### Description

Kiểm tra trạng thái của service và database connection.

#### cURL Example

```bash
curl -X GET http://localhost:8000/v1/health
```

#### Response (200 OK)

```json
{
  "status": "ok",
  "timestamp": "2025-11-25T18:30:00Z",
  "database": "connected",
  "cache": "connected",
  "queue": "connected"
}
```

---

### API 1: Notify Conversation End (BE → AI)

#### Endpoint

```
POST /conversations/end
```

#### Description

**Gọi bởi:** Backend Service
**Gọi tới:** AI Scoring Service (via Message Queue)
**Mục đích:** Thông báo rằng một cuộc hội thoại đã kết thúc

Backend chỉ gửi `conversation_id` (và `user_id` để tracking). AI Service sẽ consume event từ queue và tự động xử lý.

**Đặc điểm:**

- **Non-blocking:** Response 202 Accepted ngay, không cần đợi AI xử lý
- **Asynchronous:** AI xử lý ở background
- **Reliable:** Message được queue, đảm bảo không mất dữ liệu

#### Request Headers

```
Content-Type: application/json
```

#### Request Body

```json
{
  "user_id": "user_123",
  "conversation_id": "conv_doanngoccuong",
  "session_metadata": {
    "duration_seconds": 1200,
    "agent_type": "talk"
  }
}
```

#### Request Fields

| Field                | Type   | Required | Description                                      |
| :------------------- | :----- | :------- | :----------------------------------------------- |
| `user_id`          | String | Yes      | ID duy nhất của user                           |
| `conversation_id`  | String | Yes      | ID duy nhất của cuộc hội thoại              |
| `session_metadata` | Object | No       | Metadata về phiên (duration, agent_type, v.v.) |

#### cURL Example

```bash
curl -X POST http://localhost:8000/v1/conversations/end \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "conversation_id": "conv_doanngoccuong",
    "session_metadata": {
      "duration_seconds": 1200,
      "agent_type": "talk"
    }
  }'
```

#### Response (202 Accepted)

```json
{
  "status": "accepted",
  "message": "Conversation end event received and queued for processing",
  "user_id": "user_123",
  "conversation_id": "conv_doanngoccuong",
  "processing_id": "proc_xyz789abc"
}
```

#### Response Fields

| Field               | Type   | Description                           |
| :------------------ | :----- | :------------------------------------ |
| `status`          | String | "accepted" - event đã được queue |
| `message`         | String | Thông báo                           |
| `user_id`         | String | ID của user (echo lại)              |
| `conversation_id` | String | ID của conversation (echo lại)      |
| `processing_id`   | String | ID để tracking quá trình xử lý  |

---

### API 2: Get Conversation Data (AI → BE)

#### Endpoint

```
GET /conversations/{conversation_id}
```

#### Description

**Gọi bởi:** AI Scoring Service
**Gọi tới:** Backend Service
**Mục đích:** Lấy toàn bộ conversation data dựa trên conversation_id

AI Service gọi API này để lấy conversation log, metadata, v.v. để phân tích và tính điểm.

**Đặc điểm:**

- **Gọi bởi AI:** Chỉ AI Service gọi API này, không phải BE
- **Caching:** Kết quả có thể cache để tránh gọi lại
- **Timeout:** Nên có timeout hợp lý (ví dụ: 30s)

#### Path Parameters

| Parameter           | Type   | Required | Description                         |
| :------------------ | :----- | :------- | :---------------------------------- |
| `conversation_id` | String | Yes      | ID duy nhất của cuộc hội thoại |

#### cURL Example

```bash
curl -X GET http://localhost:8000/v1/conversations/conv_doanngoccuong
```

#### Response (200 OK)

```json
{
  "conversation_id": "conv_doanngoccuong",
  "user_id": "user_123",
  "agent_id": "talk_movie_preference",
  "agent_type": "talk",
  "start_time": "2025-11-25T18:00:00Z",
  "end_time": "2025-11-25T18:20:00Z",
  "duration_seconds": 1200,
  "conversation_log": [
    {
      "speaker": "pika",
      "turn_id": 1,
      "text": "Hi! What's your favorite movie genre?",
      "timestamp": "2025-11-25T18:00:00Z"
    },
    {
      "speaker": "user",
      "turn_id": 2,
      "text": "I love animated movies, especially Miyazaki films!",
      "timestamp": "2025-11-25T18:00:15Z"
    },
    {
      "speaker": "pika",
      "turn_id": 3,
      "text": "Miyazaki is amazing! Which is your favorite?",
      "timestamp": "2025-11-25T18:00:30Z"
    },
    {
      "speaker": "user",
      "turn_id": 4,
      "text": "Spirited Away! The animation is incredible.",
      "timestamp": "2025-11-25T18:00:45Z"
    },
    {
      "speaker": "pika",
      "turn_id": 5,
      "text": "Spirited Away is a masterpiece! Have you watched Howl's Moving Castle?",
      "timestamp": "2025-11-25T18:01:00Z"
    },
    {
      "speaker": "user",
      "turn_id": 6,
      "text": "Yes! That's my second favorite. The music is beautiful.",
      "timestamp": "2025-11-25T18:01:15Z"
    }
  ],
  "metadata": {
    "emotion": "interesting",
    "user_initiated_questions": 2,
    "pika_initiated_topics": 2,
    "new_memories_created": 1
  }
}
```

#### Response Fields

| Field                | Type     | Description                                |
| :------------------- | :------- | :----------------------------------------- |
| `conversation_id`  | String   | ID của conversation                       |
| `user_id`          | String   | ID của user                               |
| `agent_id`         | String   | ID của agent được sử dụng            |
| `agent_type`       | String   | Loại agent: GREETING, TALK, GAME_ACTIVITY |
| `start_time`       | DateTime | Thời điểm bắt đầu                    |
| `end_time`         | DateTime | Thời điểm kết thúc                    |
| `duration_seconds` | Integer  | Thời lượng (giây)                      |
| `conversation_log` | Array    | Danh sách các lượt nói                |
| `metadata`         | Object   | Metadata về phiên                        |

### API Update Score: ngoài việc cho con rjob chạy ngầm, thì thêm 1 API để update friendship level of user_id

---

### API 3: Get Friendship Status (BE → Context Service)

#### Endpoint

```
POST /friendship/status
```

#### Description

**Gọi bởi:** Backend Service
**Gọi tới:** Context Handling Service
**Mục đích:** Lấy trạng thái tình bạn hiện tại của user

Khi user mở app hoặc cần lấy thông tin tình bạn, Backend gọi API này. Dữ liệu được lưu trong cache/DB, response nhanh.

#### Request Headers

```
Content-Type: application/json
```

#### Request Body

```json
{
  "user_id": "user_123"
}
```

#### Request Fields

| Field       | Type   | Required | Description            |
| :---------- | :----- | :------- | :--------------------- |
| `user_id` | String | Yes      | ID duy nhất của user |

#### cURL Example

```bash
curl -X POST http://localhost:8000/v1/friendship/status \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

#### Response (200 OK)

```json
{
  "user_id": "user_123",
  "friendship_score": 835.5,
  "friendship_level": "ACQUAINTANCE",
  "last_interaction_date": "2025-11-25T18:30:00Z",
  "streak_day": 6,
  "total_turns": 67,
  "topic_metrics": {
    "agent_movie": {
      "score": 59.0,
      "total_turns": 12,
      "last_date": "2025-11-25T18:30:00Z"
    },
    "agent_animal": {
      "score": 28.5,
      "total_turns": 8,
      "last_date": "2025-11-24T14:10:00Z"
    },
    "agent_school": {
      "score": 15.0,
      "total_turns": 5,
      "last_date": "2025-11-23T09:15:00Z"
    }
  }
}
```

#### Response (404 Not Found)

```json
{
  "error": "User not found",
  "user_id": "user_123"
}
```

---

### API 4: Get Suggested Activities (BE → Context Service)

#### Endpoint

```
POST /activities/suggest
```

#### Description

**Gọi bởi:** Backend Service
**Gọi tới:** Context Handling Service
**Mục đích:** Lấy danh sách Agent được đề xuất (pre-computed)

**Đặc điểm quan trọng:**

- **Pre-computed:** Dữ liệu đã được tính toán sẵn bởi AI Service (real-time hoặc batch)
- **Cached:** Response từ cache, rất nhanh (< 100ms)
- **No Waiting:** BE không cần đợi AI xử lý, dữ liệu đã sẵn

#### Request Headers

```
Content-Type: application/json
```

#### Request Body

```json
{
  "user_id": "user_123"
}
```

#### Request Fields

| Field       | Type   | Required | Description            |
| :---------- | :----- | :------- | :--------------------- |
| `user_id` | String | Yes      | ID duy nhất của user |

#### cURL Example

```bash
curl -X POST http://localhost:8000/v1/activities/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

#### Response (200 OK) - User ở ACQUAINTANCE Level

```json
{
  "user_id": "user_123",
  "friendship_level": "ACQUAINTANCE",
  "computed_at": "2025-11-25T18:30:00Z",
  "greeting_agent": {
    "id": 8,
    "friendship_level": "ACQUAINTANCE",
    "agent_type": "GREETING",
    "agent_id": "greeting_memory_recall",
    "agent_name": "Memory Recall",
    "agent_description": "Nhắc lại ký ức chung với user",
    "weight": 2.0,
    "is_active": true,
    "reason": "High affinity with past memories"
  },
  "talk_agents": [
    {
      "id": 10,
      "friendship_level": "ACQUAINTANCE",
      "agent_type": "TALK",
      "agent_id": "talk_movie_preference",
      "agent_name": "Movie Preference",
      "agent_description": "Nói về phim yêu thích",
      "weight": 1.2,
      "is_active": true,
      "reason": "Highest topic_score (59.0)",
      "topic_score": 59.0,
      "total_turns": 12
    },
    {
      "id": 11,
      "friendship_level": "ACQUAINTANCE",
      "agent_type": "TALK",
      "agent_id": "talk_dreams",
      "agent_name": "Dreams Talk",
      "agent_description": "Nói về ước mơ",
      "weight": 1.0,
      "is_active": true,
      "reason": "Exploration candidate - low interaction",
      "topic_score": 8.5,
      "total_turns": 2
    }
  ],
  "game_agents": [
    {
      "id": 12,
      "friendship_level": "ACQUAINTANCE",
      "agent_type": "GAME_ACTIVITY",
      "agent_id": "game_20questions",
      "agent_name": "20 Questions",
      "agent_description": "Trò chơi 20 câu hỏi",
      "weight": 1.0,
      "is_active": true,
      "reason": "Engagement booster"
    },
    {
      "id": 13,
      "friendship_level": "ACQUAINTANCE",
      "agent_type": "GAME_ACTIVITY",
      "agent_id": "game_story_building",
      "agent_name": "Story Building",
      "agent_description": "Xây dựng câu chuyện chung",
      "weight": 1.5,
      "is_active": true,
      "reason": "Creative engagement"
    }
  ]
}
```

#### Response Fields

| Field                | Type     | Description                         |
| :------------------- | :------- | :---------------------------------- |
| `user_id`          | String   | ID của user                        |
| `friendship_level` | String   | STRANGER / ACQUAINTANCE / FRIEND    |
| `computed_at`      | DateTime | Thời điểm tính toán candidates |
| `greeting_agent`   | Object   | 1 greeting agent được chọn      |
| `talk_agents`      | Array    | Danh sách talk agents (2-3 cái)   |
| `game_agents`      | Array    | Danh sách game agents (1-2 cái)   |
| `reason`           | String   | Lý do chọn agent này             |
| `topic_score`      | Float    | Điểm topic (nếu có)             |
| `total_turns`      | Integer  | Số lượt tương tác (nếu có)  |

---

### API 5-8: Agent Mapping Management

#### API 5: List Agent Mappings

###### Endpoint

```
GET /agent-mappings
```

###### Query Parameters

| Parameter            | Type   | Required | Description                                     |
| :------------------- | :----- | :------- | :---------------------------------------------- |
| `friendship_level` | String | No       | Lọc theo level: STRANGER, ACQUAINTANCE, FRIEND |
| `agent_type`       | String | No       | Lọc theo loại: GREETING, TALK, GAME_ACTIVITY  |

###### cURL Examples

```bash
# Lấy tất cả mappings
curl -X GET http://localhost:8000/v1/agent-mappings

# Lấy mappings cho STRANGER level
curl -X GET "http://localhost:8000/v1/agent-mappings?friendship_level=STRANGER"

# Lấy Greeting agents cho ACQUAINTANCE level
curl -X GET "http://localhost:8000/v1/agent-mappings?friendship_level=ACQUAINTANCE&agent_type=GREETING"
```

###### Response (200 OK)

```json
[
  {
    "id": 1,
    "friendship_level": "STRANGER",
    "agent_type": "GREETING",
    "agent_id": "greeting_welcome",
    "agent_name": "Welcome Greeting",
    "agent_description": "Chào mừng người dùng mới",
    "weight": 1.0,
    "is_active": true
  },
  {
    "id": 2,
    "friendship_level": "STRANGER",
    "agent_type": "GREETING",
    "agent_id": "greeting_intro",
    "agent_name": "Introduce Pika",
    "agent_description": "Giới thiệu về Pika",
    "weight": 1.5,
    "is_active": true
  }
]
```

---

#### API 6: Create Agent Mapping

###### Endpoint

```
POST /agent-mappings
```

###### Request Body

```json
{
  "friendship_level": "FRIEND",
  "agent_type": "GREETING",
  "agent_id": "greeting_special_moment",
  "agent_name": "Special Moment",
  "agent_description": "Khoảnh khắc đặc biệt",
  "weight": 2.0
}
```

###### cURL Example

```bash
curl -X POST http://localhost:8000/v1/agent-mappings \
  -H "Content-Type: application/json" \
  -d '{
    "friendship_level": "FRIEND",
    "agent_type": "GREETING",
    "agent_id": "greeting_special_moment",
    "agent_name": "Special Moment",
    "agent_description": "Khoảnh khắc đặc biệt",
    "weight": 2.0
  }'
```

###### Response (201 Created)

```json
{
  "id": 20,
  "friendship_level": "FRIEND",
  "agent_type": "GREETING",
  "agent_id": "greeting_special_moment",
  "agent_name": "Special Moment",
  "agent_description": "Khoảnh khắc đặc biệt",
  "weight": 2.0,
  "is_active": true
}
```

---

#### API 7: Update Agent Mapping

###### Endpoint

```
PUT /agent-mappings/{mapping_id}
```

###### Path Parameters

| Parameter      | Type    | Required | Description           |
| :------------- | :------ | :------- | :-------------------- |
| `mapping_id` | Integer | Yes      | ID của agent mapping |

###### Request Body

```json
{
  "weight": 2.5,
  "is_active": true
}
```

###### cURL Example

```bash
curl -X PUT http://localhost:8000/v1/agent-mappings/20 \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 2.5,
    "is_active": true
  }'
```

###### Response (200 OK)

```json
{
  "id": 20,
  "friendship_level": "FRIEND",
  "agent_type": "GREETING",
  "agent_id": "greeting_special_moment",
  "agent_name": "Special Moment",
  "agent_description": "Khoảnh khắc đặc biệt",
  "weight": 2.5,
  "is_active": true
}
```

---

#### API 8: Delete Agent Mapping

###### Endpoint

```
DELETE /agent-mappings/{mapping_id}
```

###### Path Parameters

| Parameter      | Type    | Required | Description           |
| :------------- | :------ | :------- | :-------------------- |
| `mapping_id` | Integer | Yes      | ID của agent mapping |

###### cURL Example

```bash
curl -X DELETE http://localhost:8000/v1/agent-mappings/20
```

###### Response (200 OK)

```json
{
  "success": true,
  "message": "Agent mapping deleted successfully"
}
```

---

### Async Processing & Scheduling

#### Background Job: Process Conversation End Event

**Trigger:** Khi event "conversation.ended" được enqueue
**Worker:** AI Scoring Service (Background Worker)
**Processing Time:** Sớm nhất có thể (thường < 5 giây)

###### Pseudocode

```python
@app.on_event("startup")
async def start_background_tasks():
    """Khởi động background worker"""
    asyncio.create_task(consume_conversation_events())

async def consume_conversation_events():
    """Consume events từ message queue"""
    while True:
        event = queue.get()  # Blocking call
    
        user_id = event.user_id
        conversation_id = event.conversation_id
    
        try:
            # Step 1: Lấy conversation data từ BE
            conv_data = await get_conversation_data(conversation_id)
        
            # Step 2: Tính toán điểm
            score_change, topic_updates, memories = calculate_friendship_score(conv_data)
        
            # Step 3: Update friendship status
            await update_friendship_status(user_id, score_change, topic_updates, memories)
        
            # Step 4: Compute & cache candidates
            candidates = compute_candidates(user_id)
            await cache_candidates(user_id, candidates)
        
            logger.info(f"Processed conversation {conversation_id} for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error processing conversation {conversation_id}: {e}")
            queue.nack(event)  # Requeue for retry
```

---

#### Scheduled Job: Batch Recompute Candidates (Optional)

**Trigger:** Mỗi 6 giờ (hoặc theo cấu hình)
**Worker:** AI Scoring Service (Scheduler)
**Purpose:** Recompute candidates cho tất cả active users

###### Pseudocode

```python
@scheduler.scheduled_job('interval', hours=6)
async def batch_recompute_candidates():
    """Recompute candidates cho tất cả users mỗi 6 giờ"""
  
    logger.info("Starting batch recompute candidates job")
  
    # Lấy tất cả active users
    users = db.query(FriendshipStatus).filter(
        FriendshipStatus.last_interaction_date >= now() - timedelta(days=30)
    ).all()
  
    for user in users:
        try:
            # Compute candidates dựa trên friendship_level hiện tại
            candidates = compute_candidates(user.user_id)
        
            # Cache candidates
            await cache_candidates(user.user_id, candidates)
        
            logger.info(f"Recomputed candidates for user {user.user_id}")
        
        except Exception as e:
            logger.error(f"Error recomputing candidates for user {user.user_id}: {e}")
  
    logger.info("Batch recompute candidates job completed")
```

---

### Error Handling

#### Common Error Responses

###### 400 Bad Request

```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

###### 404 Not Found

```json
{
  "error": "Conversation not found",
  "conversation_id": "conv_invalid"
}
```

###### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "Failed to process conversation",
  "request_id": "req_abc123xyz"
}
```

#### Error Status Codes

| Status Code | Meaning               | Example                                |
| :---------- | :-------------------- | :------------------------------------- |
| 200         | OK                    | Request thành công                   |
| 201         | Created               | Resource được tạo thành công     |
| 202         | Accepted              | Event được queue, sẽ xử lý async |
| 400         | Bad Request           | Request body không hợp lệ           |
| 404         | Not Found             | Resource không tìm thấy             |
| 422         | Unprocessable Entity  | Validation error                       |
| 500         | Internal Server Error | Server error                           |

---

### Complete Integration Example (v3)

#### Scenario: User Hoàn thành hội thoại và mở app lần tiếp theo

```bash
# ========== STEP 1: User kết thúc cuộc hội thoại ==========
# Backend gửi conversation_id (không gửi toàn bộ log)

curl -X POST http://localhost:8000/v1/conversations/end \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "conversation_id": "conv_doanngoccuong",
    "session_metadata": {
      "duration_seconds": 1200,
      "agent_type": "talk"
    }
  }'

# Response: 202 Accepted (không cần đợi)


# ========== STEP 2: AI Service xử lý async (background) ==========
# 1. Consume event từ queue
# 2. Call API 2 để lấy conversation data
# 3. Tính toán score
# 4. Update friendship_status
# 5. Compute & cache candidates
# (Tất cả diễn ra ở background, BE không cần biết)


# ========== STEP 3: Lần tiếp theo, user mở app ==========
# Backend lấy trạng thái hiện tại

curl -X POST http://localhost:8000/v1/friendship/status \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'

# Response: Trạng thái tình bạn hiện tại (từ cache/DB)


# ========== STEP 4: Backend lấy agents được đề xuất ==========
# Dữ liệu đã được pre-computed, response rất nhanh!

curl -X POST http://localhost:8000/v1/activities/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'

# Response: 1 greeting agent + 4 talk/game agents (từ cache)
# Không cần đợi AI tính toán!
```

---

### Architecture Benefits (v3)

| Benefit                 | Giải thích                                                        |
| :---------------------- | :------------------------------------------------------------------ |
| **Non-blocking**  | BE không cần đợi AI xử lý, response ngay với 202 Accepted    |
| **Scalable**      | AI xử lý ở background, có thể scale workers độc lập         |
| **Reliable**      | Message queue đảm bảo không mất dữ liệu, có retry mechanism |
| **Fast Response** | Candidates đã pre-computed, BE lấy từ cache (< 100ms)           |
| **Flexible**      | Có thể xử lý real-time hoặc batch mỗi 6h                      |
| **Decoupled**     | BE và AI độc lập, có thể deploy riêng                        |

---

### Technology Stack (Recommended)

| Component                   | Technology           | Purpose                                |
| :-------------------------- | :------------------- | :------------------------------------- |
| **Message Queue**     | RabbitMQ / Kafka     | Enqueue conversation end events        |
| **Cache**             | Redis                | Cache pre-computed candidates          |
| **Database**          | PostgreSQL           | Lưu friendship_status, agent_mappings |
| **Background Worker** | Celery / APScheduler | Consume events, batch jobs             |
| **API Framework**     | FastAPI              | HTTP API endpoints                     |

---

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                              │
└─────────────────────────────────────────────────────────────────┘

Frontend/App
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Backend Service (FastAPI)                                       │
│ - API 1: POST /conversations/end                                │
│ - API 3: POST /friendship/status                                │
│ - API 4: POST /activities/suggest                               │
│ - API 2: GET /conversations/{id} (for AI)                       │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Message Queue (RabbitMQ / Kafka)                                │
│ - Queue: conversation.ended                                     │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ AI Scoring Service (FastAPI + Celery)                           │
│ - Background Worker (consume events)                            │
│ - Scheduler (batch jobs mỗi 6h)                                 │
└─────────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ Context Handling Service (FastAPI)                              │
│ - Database: PostgreSQL                                          │
│ - Cache: Redis                                                  │
│ - Tables: friendship_status, agent_mappings, candidates_cache   │
└─────────────────────────────────────────────────────────────────┘
```

---

### Summary: API Endpoints (v3)

| # | Endpoint                 | Method | Gọi bởi | Mục đích                  | Response     |
| :- | :----------------------- | :----- | :-------- | :--------------------------- | :----------- |
| 1 | `/conversations/end`   | POST   | BE        | Notify conversation end      | 202 Accepted |
| 2 | `/conversations/{id}`  | GET    | AI        | Lấy conversation data       | 200 OK       |
| 3 | `/friendship/status`   | POST   | BE        | Lấy friendship status       | 200 OK       |
| 4 | `/activities/suggest`  | POST   | BE        | Lấy pre-computed candidates | 200 OK       |
| 5 | `/agent-mappings`      | GET    | Admin     | Lấy danh sách mappings     | 200 OK       |
| 6 | `/agent-mappings`      | POST   | Admin     | Tạo mapping mới            | 201 Created  |
| 7 | `/agent-mappings/{id}` | PUT    | Admin     | Cập nhật mapping           | 200 OK       |
| 8 | `/agent-mappings/{id}` | DELETE | Admin     | Xóa mapping                 | 200 OK       |

---

### Key Differences: v2 vs v3

| Aspect                 | v2 (Synchronous)           | v3 (Event-Driven Async)   |
| :--------------------- | :------------------------- | :------------------------ |
| **BE gửi**      | Toàn bộ conversation log | Chỉ conversation_id      |
| **AI lấy data** | Từ request body           | Gọi API riêng           |
| **Processing**   | Synchronous (BE đợi)     | Asynchronous (background) |
| **Response**     | 200 OK sau khi xong        | 202 Accepted ngay         |
| **Candidates**   | Tính khi BE request       | Pre-computed, cached      |
| **Latency**      | Cao (phụ thuộc AI)       | Thấp (từ cache)         |
| **Scalability**  | Khó scale                 | Dễ scale                 |
| **Reliability**  | Có thể mất dữ liệu    | Queue đảm bảo          |

---

---

**Kết luận:** Tài liệu này cung cấp một kế hoạch triển khai kỹ thuật toàn diện cho module **Context Handling - Friendlyship Management**, chuyển đổi hệ thống sang mô hình cập nhật thời gian thực để tạo ra một trải nghiệm người dùng linh hoạt và cá nhân hóa hơn. Các API và cấu trúc dữ liệu được định nghĩa rõ ràng để đảm bảo sự phối hợp nhịp nhàng giữa Backend, AI và Database.
