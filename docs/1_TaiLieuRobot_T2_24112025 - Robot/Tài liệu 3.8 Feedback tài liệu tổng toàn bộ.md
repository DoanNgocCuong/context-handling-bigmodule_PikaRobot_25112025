
```
Đọc chính xác tài liệu cập nhật sau. 
1. Check xem tài liệu này có vấn đề gì ko 
2. Define repo-architech folder (cấu trúc thư mục) để đảm bảo đơn giản, SOLID và ko quá phức tạp. 

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
│   ├── models.py                      # SQLAlchemy models (2 bảng)
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
├── scripts/
│   └── seed_agents.py                 # Seed dữ liệu agent mapping
│
├── tests/
│   ├── test_api.py
│   └── test_services.py
│
└── logs/
    └── .gitkeep
```

Đơn giản như này, nhưng SOLID cần chia rõ các cục nhỏ chính, và vẫn đảm bảo SOLID nhưng ko quá rườm rà
```



---


# Phân tích Tài liệu & Define Folder Structure SOLID

**Version:** 1.0  
**Date:** 25/11/2025

---

## 1. Check Vấn đề trong Tài liệu Hiện tại

### ✅ Điểm Tốt

1. **Schema rõ ràng:** 2 bảng chính (`friendship_status`, `friendship_agent_mapping`) rất sạch sẽ
2. **API endpoints định nghĩa tốt:** 3 endpoints chính được mô tả chi tiết
3. **Logic xử lý rõ ràng:** Scoring logic và Selection logic được giải thích kỹ
4. **Visualization tốt:** Mermaid diagrams giúp hiểu flow

### ⚠️ Vấn đề Cần Giải quyết

| Vấn đề | Chi tiết | Tác động |
| :--- | :--- | :--- |
| **1. Folder structure quá đơn giản** | Tất cả code trong 1 file (`services.py`, `routes.py`) → khó bảo trì khi phát triển | Violation of Single Responsibility Principle |
| **2. Không có layer abstraction** | Không có interface/abstract class → khó test, khó mock | Violation of Dependency Inversion |
| **3. Không có error handling** | Không định nghĩa custom exceptions | Khó debug, khó maintain |
| **4. Không có config management** | Hardcoded values trong code | Khó deploy, khó scale |
| **5. Không có logging** | Không có structured logging | Khó monitor, khó troubleshoot |
| **6. Không có validation** | Không validate input/output | Dễ bị lỗi, dễ bị attack |
| **7. Database migration chưa rõ** | Chỉ nói Alembic nhưng không có migration file cụ thể | Khó setup lần đầu |
| **8. Seed data chưa hoàn thiện** | Chỉ có script nhưng không có dữ liệu mẫu đầy đủ | Khó test |

---

## 2. Define Folder Structure SOLID (Đơn giản nhưng Mạnh)

### 2.1. Cấu trúc Tổng thể

```
context-handling-service/
│
├── README.md
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                          # Cấu hình, constants, exceptions
│   │   ├── __init__.py
│   │   ├── config.py                  # Settings, environment variables
│   │   ├── constants.py               # Constants, enums
│   │   └── exceptions.py              # Custom exceptions
│   │
│   ├── models/                        # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── base.py                    # Base model class
│   │   ├── friendship.py              # FriendshipStatus model
│   │   └── agent.py                   # FriendshipAgentMapping model
│   │
│   ├── schemas/                       # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── friendship.py              # Friendship schemas
│   │   ├── agent.py                   # Agent schemas
│   │   └── common.py                  # Common schemas
│   │
│   ├── db/                            # Database layer
│   │   ├── __init__.py
│   │   ├── database.py                # Database connection, session
│   │   └── base_repository.py         # Base repository class
│   │
│   ├── repositories/                  # Data access layer (Repository pattern)
│   │   ├── __init__.py
│   │   ├── friendship_repository.py   # Friendship data access
│   │   └── agent_repository.py        # Agent mapping data access
│   │
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── friendship_service.py      # Friendship logic
│   │   └── selection_service.py       # Agent selection logic
│   │
│   ├── api/                           # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                    # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── friendship.py      # Friendship endpoints
│   │       │   ├── agents.py          # Agent endpoints
│   │       │   └── health.py          # Health check
│   │       └── router.py              # API router
│   │
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py                  # Logging setup
│   │   ├── validators.py              # Input validators
│   │   └── helpers.py                 # Helper functions
│   │
│   └── main.py                        # FastAPI app entry point
│
├── migrations/                        # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_create_friendship_status_table.py
│       └── 002_create_friendship_agent_mapping_table.py
│
├── scripts/                           # Utility scripts
│   ├── __init__.py
│   ├── seed_agents.py                 # Seed agent data
│   └── init_db.py                     # Initialize database
│
├── tests/                             # Tests
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_friendship_service.py
│   │   └── test_selection_service.py
│   └── integration/
│       ├── __init__.py
│       ├── test_friendship_api.py
│       └── test_agent_api.py
│
└── logs/
    └── .gitkeep
```

### 2.2. Giải thích Chi tiết

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

## 3. SOLID Principles Áp dụng

| Principle | Cách Áp dụng | Lợi ích |
| :--- | :--- | :--- |
| **S - Single Responsibility** | Mỗi file có 1 trách nhiệm duy nhất (models, schemas, services, repositories) | Dễ test, dễ bảo trì |
| **O - Open/Closed** | Dùng BaseRepository, BaseModel → dễ extend | Dễ thêm feature mới |
| **L - Liskov Substitution** | Repository, Service có interface rõ ràng | Dễ mock, dễ test |
| **I - Interface Segregation** | Tách schemas, models theo domain | Không phụ thuộc vào những gì không cần |
| **D - Dependency Inversion** | Dùng dependency injection (get_db, services) | Loose coupling, dễ test |

---

## 4. So sánh: Cũ vs Mới

| Aspect | Cũ | Mới |
| :--- | :--- | :--- |
| **Số file** | 8 file lớn | 25+ file nhỏ |
| **Responsibility** | Nhiều trách nhiệm/file | 1 trách nhiệm/file |
| **Testability** | Khó mock, khó test | Dễ mock, dễ test |
| **Maintainability** | Khó tìm code, khó sửa | Dễ tìm code, dễ sửa |
| **Scalability** | Khó mở rộng | Dễ mở rộng |
| **Error Handling** | Không có | Custom exceptions |
| **Logging** | Không có | Structured logging |
| **Configuration** | Hardcoded | Environment-based |

---

## 5. Quy trình Triển khai với Folder Structure Mới

```bash
# 1. Setup
git clone <repo-url>
cd context-handling-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Cấu hình
cp .env.example .env
# Edit .env với database URL

# 3. Database
docker-compose up -d db
alembic upgrade head

# 4. Seed dữ liệu
python scripts/seed_agents.py

# 5. Chạy ứng dụng
uvicorn app.main:app --reload

# 6. Test
pytest tests/
```

---

## 6. Kết luận

Folder structure mới này:

✅ **Đơn giản:** Dễ hiểu, dễ navigate  
✅ **SOLID:** Tuân theo tất cả 5 principles  
✅ **Scalable:** Dễ thêm features, dễ refactor  
✅ **Testable:** Dễ viết unit tests, integration tests  
✅ **Maintainable:** Dễ debug, dễ bảo trì  

Không quá rườm rà nhưng đủ mạnh để phát triển thành một hệ thống lớn.

