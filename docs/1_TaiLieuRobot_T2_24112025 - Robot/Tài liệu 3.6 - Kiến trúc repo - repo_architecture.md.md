
Cấu trúc thư mục chính (comment giải thích vai trò của file, folder) trên cấu trúc 
Các file chính và vai trò của chúng
Mối quan hệ giữa các module
Luồng dữ liệu giữa các thành phần


Sử dụng python
DB thì postgres hoặc mongoDB 

Chuẩn best practices trong thiết kế repo 

_ ...
____...
_____...

Vẽ dạng markdown như này nè 


---


# Kiến trúc Repository Chung: Context Handling (Friendlyship + Talk/Agent Management)

**Version:** 1.0  
**Date:** 25/11/2025  
**Technology Stack:** Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy ORM, Alembic

---

## 1. Tổng quan

Repository này là một **monorepo** chứa hai modules chính hoạt động cùng nhau trong hệ thống **Context Handling** của Pika:

1.  **Friendlyship Management Module:** Quản lý trạng thái tình bạn, tính toán điểm, lưu trữ ký ức.
2.  **Talk/Agent Management Module:** Quản lý kho Agent và logic lựa chọn Agent dựa trên trạng thái tình bạn.

Cả hai modules chia sẻ cùng một CSDL PostgreSQL nhưng có các API endpoints riêng biệt, cho phép chúng có thể được triển khai độc lập nếu cần.

---

## 2. Cấu trúc Thư mục Chung

```
context-handling-service/
│
├── README.md                          # Tài liệu giới thiệu project
├── LICENSE
├── .gitignore
├── .env.example                       # Ví dụ file biến môi trường
├── pyproject.toml                     # Cấu hình project Python
├── requirements.txt                   # Dependencies
├── Dockerfile                         # Dockerfile cho toàn bộ service
├── docker-compose.yml                 # Docker Compose cho local dev
│
├── src/                               # Mã nguồn chính
│   │
│   ├── main.py                        # Entry point chính của FastAPI app
│   │
│   ├── config/                        # Cấu hình ứng dụng (shared)
│   │   ├── __init__.py
│   │   ├── settings.py                # Cấu hình chính (DB, logging, etc.)
│   │   └── database.py                # Cấu hình kết nối PostgreSQL
│   │
│   ├── models/                        # ORM Models (SQLAlchemy) - shared
│   │   ├── __init__.py
│   │   ├── base.py                    # Base model class
│   │   ├── friendship_status.py       # Friendlyship module
│   │   ├── topic_metrics.py           # Friendlyship module
│   │   ├── dynamic_memory.py          # Friendlyship module
│   │   ├── interaction_history.py     # Friendlyship module
│   │   ├── agent_pool.py              # Talk/Agent module
│   │   ├── agent_selection_rules.py   # Talk/Agent module
│   │   └── schemas.py                 # Pydantic Schemas (shared)
│   │
│   ├── api/                           # API Routes (shared)
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py              # GET /health
│   │   │   │
│   │   │   ├── friendlyship/          # Routes cho Friendlyship module
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scoring.py         # POST /v1/scoring/calculate-friendship
│   │   │   │   └── status.py          # POST /v1/users/{user_id}/update-friendship
│   │   │   │                           # GET /v1/users/{user_id}/status
│   │   │   │
│   │   │   └── talk_agent/            # Routes cho Talk/Agent module
│   │   │       ├── __init__.py
│   │   │       ├── activities.py      # GET /v1/users/{user_id}/suggested-activities
│   │   │       ├── agents.py          # CRUD /v1/agents
│   │   │       └── rules.py           # CRUD /v1/selection-rules
│   │   │
│   │   └── dependencies.py            # Dependency injection (shared)
│   │
│   ├── services/                      # Business Logic (shared)
│   │   ├── __init__.py
│   │   │
│   │   ├── friendlyship/              # Services cho Friendlyship module
│   │   │   ├── __init__.py
│   │   │   ├── scoring_service.py     # Tính toán điểm từ log
│   │   │   ├── friendship_service.py  # Cập nhật status, level, streak
│   │   │   ├── topic_service.py       # Quản lý topic metrics
│   │   │   └── memory_service.py      # Quản lý ký ức
│   │   │
│   │   └── talk_agent/                # Services cho Talk/Agent module
│   │       ├── __init__.py
│   │       ├── selection_service.py   # Logic chính chọn Agent
│   │       ├── agent_service.py       # CRUD agents
│   │       ├── rule_service.py        # CRUD selection rules
│   │       └── external/
│   │           └── friendlyship_api.py # HTTP client gọi Friendlyship API
│   │
│   ├── repositories/                  # Data Access Layer (shared)
│   │   ├── __init__.py
│   │   ├── base_repository.py         # Base class
│   │   │
│   │   ├── friendlyship/              # Repositories cho Friendlyship module
│   │   │   ├── __init__.py
│   │   │   ├── friendship_repository.py
│   │   │   ├── topic_repository.py
│   │   │   ├── memory_repository.py
│   │   │   └── interaction_repository.py
│   │   │
│   │   └── talk_agent/                # Repositories cho Talk/Agent module
│   │       ├── __init__.py
│   │       ├── agent_repository.py
│   │       └── rule_repository.py
│   │
│   ├── utils/                         # Utility functions (shared)
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── converters.py
│   │   ├── constants.py
│   │   ├── enums.py                   # Enums: FriendshipPhase, Phase, AgentType, etc.
│   │   └── helpers.py
│   │
│   ├── exceptions/                    # Custom Exceptions (shared)
│   │   ├── __init__.py
│   │   ├── base_exceptions.py
│   │   ├── friendship_exceptions.py
│   │   └── validation_exceptions.py
│   │
│   └── middleware/                    # Middleware (shared)
│       ├── __init__.py
│       ├── error_handler.py
│       └── logging_middleware.py
│
├── tests/                             # Tests (shared)
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── friendlyship/
│   │   │   ├── test_scoring_service.py
│   │   │   └── test_friendship_service.py
│   │   └── talk_agent/
│   │       └── test_selection_service.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── friendlyship/
│   │   │   ├── test_scoring_api.py
│   │   │   └── test_status_api.py
│   │   └── talk_agent/
│   │       ├── test_activities_api.py
│   │       └── test_agents_api.py
│   │
│   └── fixtures/
│       ├── __init__.py
│       ├── friendship_fixtures.py
│       ├── agent_fixtures.py
│       └── conversation_fixtures.py
│
├── migrations/                        # Alembic migrations (shared)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_create_friendship_status_table.py
│       ├── 002_create_topic_metrics_table.py
│       ├── 003_create_dynamic_memory_table.py
│       ├── 004_create_interaction_history_table.py
│       ├── 005_create_agents_table.py
│       └── 006_create_agent_selection_rules_table.py
│
├── scripts/                           # Utility scripts
│   ├── __init__.py
│   ├── init_db.py                     # Khởi tạo database
│   ├── seed_agents.py                 # Seed dữ liệu agent pool
│   └── cleanup.py                     # Dọn dẹp dữ liệu
│
├── docs/                              # Tài liệu
│   ├── API.md                         # API documentation
│   ├── DATABASE.md                    # Database schema documentation
│   ├── ARCHITECTURE.md                # Architecture documentation
│   ├── DEPLOYMENT.md                  # Deployment guide
│   └── CONTRIBUTING.md                # Contribution guidelines
│
└── logs/                              # Logs directory
    └── .gitkeep

```

---

## 3. Mô tả Chi tiết từng Thư mục

### 3.1. Friendlyship Module

**Vị trí:** `src/services/friendlyship/`, `src/repositories/friendlyship/`, `src/api/routes/friendlyship/`

**Trách nhiệm:**
- Tính toán điểm tình bạn từ log hội thoại.
- Lưu trữ và cập nhật trạng thái tình bạn vào CSDL.
- Cung cấp API để các module khác truy vấn trạng thái.

**API Endpoints:**
- `POST /v1/scoring/calculate-friendship` - Tính toán điểm (không ghi DB).
- `POST /v1/users/{user_id}/update-friendship` - Cập nhật trạng thái vào DB.
- `GET /v1/users/{user_id}/status` - Lấy trạng thái hiện tại.
- `GET /v1/users/{user_id}/topic-metrics` - Lấy topic metrics.
- `GET /v1/users/{user_id}/memories` - Lấy ký ức.

**Database Tables:**
- `users`
- `friendship_status`
- `topic_metrics`
- `dynamic_memories`
- `interaction_history`

### 3.2. Talk/Agent Module

**Vị trí:** `src/services/talk_agent/`, `src/repositories/talk_agent/`, `src/api/routes/talk_agent/`

**Trách nhiệm:**
- Quản lý kho Agent (CRUD).
- Quản lý quy tắc lựa chọn Agent (CRUD).
- Lựa chọn Agent phù hợp cho người dùng dựa trên trạng thái tình bạn.

**API Endpoints:**
- `GET /v1/users/{user_id}/suggested-activities` - Lấy danh sách Agent đề xuất.
- `GET /v1/agents` - Lấy danh sách tất cả agents.
- `POST /v1/agents` - Tạo agent mới.
- `PUT /v1/agents/{agent_id}` - Cập nhật agent.
- `DELETE /v1/agents/{agent_id}` - Xóa agent.
- `GET /v1/selection-rules` - Lấy danh sách quy tắc.
- `POST /v1/selection-rules` - Tạo quy tắc mới.
- `PUT /v1/selection-rules/{rule_id}` - Cập nhật quy tắc.
- `DELETE /v1/selection-rules/{rule_id}` - Xóa quy tắc.

**Database Tables:**
- `agents`
- `agent_selection_rules`

---

## 4. Luồng Dữ liệu Tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Backend (Main App) - Kết thúc hội thoại                      │
│    POST /v1/scoring/calculate-friendship                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Friendlyship Module - Tính toán điểm                         │
│    scoring_service.calculate_friendship_score_change()          │
│    Trả về: {score_change, topic_updates, memories}             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Backend (Main App) - Cập nhật vào DB                         │
│    POST /v1/users/{user_id}/update-friendship                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Friendlyship Module - Ghi vào CSDL                           │
│    friendship_service.update_friendship_score()                 │
│    Cập nhật: friendship_status, topic_metrics, memories         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Backend (Main App) - Bắt đầu phiên mới                       │
│    GET /v1/users/{user_id}/suggested-activities                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Talk/Agent Module - Lựa chọn Agent                           │
│    selection_service.get_suggested_activities()                 │
│    6.1. Gọi Friendlyship API: GET /v1/users/{user_id}/status    │
│    6.2. Nhận dữ liệu: phase, friendship_score, topic_metrics    │
│    6.3. Truy vấn CSDL: agents, agent_selection_rules            │
│    6.4. Áp dụng thuật toán lựa chọn                             │
│    Trả về: [greeting_agent_id, talk_agent_id_1, ...]           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Backend (Main App) - Hiển thị cho người dùng                 │
│    Lấy nội dung chi tiết từ kho Agent                           │
│    Hiển thị Greeting Agent + 4 Talk/Game Agent                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Shared Components

### 5.1. Database Configuration

File `src/config/database.py` được chia sẻ bởi cả hai modules. Nó cung cấp:
- SQLAlchemy engine
- Session factory
- Connection pooling settings

### 5.2. ORM Models

Tất cả ORM models được định nghĩa trong `src/models/` và được import bởi cả hai modules.

### 5.3. Pydantic Schemas

File `src/models/schemas.py` chứa tất cả Pydantic schemas cho request/response validation.

### 5.4. Enums và Constants

File `src/utils/enums.py` chứa các enum được sử dụng bởi cả hai modules:
- `FriendshipPhase` (PHASE1_STRANGER, PHASE2_ACQUAINTANCE, PHASE3_FRIEND)
- `Phase` (PHASE_1, PHASE_2, PHASE_3)
- `AgentType` (GREETING, TALK, GAME)
- `Emotion` (interesting, boring, neutral, happy, sad)

### 5.5. Exception Classes

File `src/exceptions/` chứa các exception classes được sử dụng bởi cả hai modules.

---

## 6. Dependency Injection

File `src/api/dependencies.py` cung cấp các dependencies được sử dụng bởi tất cả routes:

```python
# Ví dụ
def get_db_session():
    """Trả về SQLAlchemy session"""
    
def get_friendship_service(db_session) -> FriendshipService:
    """Trả về FriendshipService instance"""
    
def get_selection_service(db_session) -> SelectionService:
    """Trả về SelectionService instance"""
```

---

## 7. Cấu hình Environment

File `.env.example`:

```bash
# Application
APP_NAME=context-handling-service
APP_VERSION=1.0.0
ENVIRONMENT=development

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@localhost:5432/context_handling_db

# SQLAlchemy
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=10

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Timeouts
REQUEST_TIMEOUT=30
DATABASE_TIMEOUT=10
```

---

## 8. Docker Compose

File `docker-compose.yml` khởi động:
- **PostgreSQL container** (port 5432)
- **FastAPI application container** (port 8000)

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/context_handling_db
    depends_on:
      - db
    volumes:
      - ./src:/app/src
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=context_handling_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 9. Quy trình Development

### 9.1. Setup Local Environment

```bash
# Clone repository
git clone <repo-url>
cd context-handling-service

# Tạo virtual environment
python -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình environment
cp .env.example .env

# Khởi tạo database
docker-compose up -d db
alembic upgrade head

# Seed dữ liệu
python scripts/seed_agents.py

# Chạy ứng dụng
uvicorn src.main:app --reload
```

### 9.2. Running Tests

```bash
# Tất cả tests
pytest

# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Với coverage
pytest --cov=src tests/
```

### 9.3. Database Migrations

```bash
# Tạo migration
alembic revision --autogenerate -m "description"

# Áp dụng
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 10. Deployment

### 10.1. Docker Image

```bash
# Build image
docker build -t context-handling-service:1.0.0 .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  context-handling-service:1.0.0
```

### 10.2. Kubernetes Deployment

Có thể sử dụng Kubernetes manifests để deploy:
- Deployment cho FastAPI app
- Service để expose API
- ConfigMap cho environment variables
- Secret cho sensitive data (DB password, API keys)

---

## 11. Monitoring và Logging

### 11.1. Structured Logging

Sử dụng Python logging module với structured format (JSON):

```python
logger.info("POST /v1/scoring/calculate-friendship", extra={
    "user_id": "user_123",
    "latency_ms": 125,
    "status_code": 200
})
```

### 11.2. Health Check

Endpoint `GET /health` để kiểm tra trạng thái ứng dụng và kết nối database.

### 11.3. Metrics

Có thể tích hợp Prometheus để thu thập metrics:
- Request count by endpoint
- Request latency
- Database query count
- Error count

---

## 12. Best Practices Áp dụng

| Aspect | Best Practice | Implementation |
| :--- | :--- | :--- |
| **Separation of Concerns** | Tách biệt logic từng module | Friendlyship và Talk/Agent modules độc lập |
| **Code Organization** | Layered architecture | API → Services → Repositories → Database |
| **Database Design** | Relational model với proper indexes | PostgreSQL với strategic indexes |
| **Error Handling** | Custom exceptions | `src/exceptions/` module |
| **Configuration** | Environment variables | `.env` file + `src/config/settings.py` |
| **Testing** | Unit + Integration tests | `tests/unit/` và `tests/integration/` |
| **Documentation** | Code comments + docstrings | Mỗi function có docstring |
| **Dependency Injection** | Loose coupling | `src/api/dependencies.py` |
| **Database Migrations** | Version control | Alembic migrations |
| **Logging** | Structured logging | JSON format logs |

---

## 13. Kết luận

Repository này cung cấp một cấu trúc rõ ràng, modular và dễ bảo trì cho module **Context Handling**. Việc gộp hai modules vào một repository chung cho phép chia sẻ các shared components (database, models, utils) trong khi vẫn duy trì sự độc lập của từng module thông qua cấu trúc thư mục rõ ràng. Cấu trúc này có thể dễ dàng mở rộng khi cần thêm các modules mới hoặc tính năng mới.
