# Kiến Trúc Code Hiện Tại - Context Handling Service

## 📋 Tổng Quan

Context Handling Service là một FastAPI application xử lý conversation events từ Backend, tính toán friendship score, và quản lý topic metrics.

---

## 🏗️ Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (External)                               │
│                    POST /v1/conversations/end                            │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FastAPI Application Layer                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  API Endpoints (v1/)                                             │   │
│  │  - POST /conversations/end                                        │   │
│  │  - GET /conversations/{id}                                        │   │
│  │  - POST /friendship/calculate-score/{conversation_id}            │   │
│  │  - GET /friendship/status/{user_id}                              │   │
│  │  - GET /activities/suggest/{user_id}                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│                               ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Dependency Injection (dependency_injection.py)                    │   │
│  │  - get_db()                                                       │   │
│  │  - get_conversation_event_service()                               │   │
│  │  - get_friendship_score_calculation_service()                     │   │
│  │  - get_friendship_status_update_service()                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Service Layer (Business Logic)                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ConversationEventService                                         │   │
│  │  - create_event() → Store event + Trigger immediate processing    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│                               ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ConversationEventProcessingService                               │   │
│  │  - process_single_event()                                        │   │
│  │  - process_due_events()                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│         ┌─────────────────────┴─────────────────────┐                   │
│         ▼                                             ▼                   │
│  ┌──────────────────────┐              ┌──────────────────────────┐      │
│  │ FriendshipScore      │              │ FriendshipStatus         │      │
│  │ CalculationService   │              │ UpdateService            │      │
│  │                      │              │                          │      │
│  │ - calculate_score_   │              │ - apply_score_change()   │      │
│  │   from_conversation_ │              │ - update_topic_metrics() │      │
│  │   id()               │              │ - get_status()           │      │
│  │                      │              │                          │      │
│  │ - calculate_          │              │                          │      │
│  │   friendship_score_  │              │                          │      │
│  │   change()            │              │                          │      │
│  │                      │              │                          │      │
│  │ - _count_complete_    │              │                          │      │
│  │   turns()             │              │                          │      │
│  │                      │              │                          │      │
│  │ - _get_calculation_   │              │                          │      │
│  │   breakdown()         │              │                          │      │
│  └──────────────────────┘              └──────────────────────────┘      │
│         │                                             │                   │
│         └─────────────────────┬───────────────────────┘                   │
│                               ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ConversationDataFetchService                                     │   │
│  │  - fetch_by_id() → Get conversation from DB or mock              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Repository Layer (Data Access)                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ConversationEventRepository                                      │   │
│  │  - create()                                                       │   │
│  │  - get_by_conversation_id()                                      │   │
│  │  - mark_processing()                                             │   │
│  │  - mark_processed()                                               │   │
│  │  - mark_failed()                                                 │   │
│  │  - fetch_due_events()                                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  FriendshipStatusRepository                                       │   │
│  │  - get_by_user_id()                                              │   │
│  │  - create_default()                                              │   │
│  │  - update_topic_metrics()                                        │   │
│  │  - _determine_topic_level()                                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  PromptTemplateRepository                                        │   │
│  │  - get_topic_id_by_agent_id()                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Database Layer (PostgreSQL)                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  conversation_events                                             │   │
│  │  - id, conversation_id, user_id, bot_id, bot_type                │   │
│  │  - conversation_log (JSONB), raw_conversation_log (JSONB)         │   │
│  │  - status, attempt_count, next_attempt_at                        │   │
│  │  - friendship_score_change, new_friendship_level                 │   │
│  │  - score_calculation_details (JSONB) ← NEW                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  friendship_status                                                │   │
│  │  - user_id, friendship_score, friendship_level                   │   │
│  │  - topic_metrics (JSONB)                                         │   │
│  │  - last_interaction_date, streak_day                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  agenda_agent_prompting                                           │   │
│  │  - topic_id, agent_id, friendship_level                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    Background Processing (Async)                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ConversationEventScheduler                                      │   │
│  │  - start_background_jobs()                                       │   │
│  │  - Background thread: process_due_events() every 30s            │   │
│  │  - Retry failed events                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Luồng Xử Lý Hiện Tại

### 1. **API Request Flow (POST /v1/conversations/end)**

```
Backend
  │
  │ POST /v1/conversations/end
  │ {
  │   "conversation_id": "conv_xxx",
  │   "user_id": "user_xxx",
  │   "bot_id": "agent_pet",
  │   "conversation_logs": [...]
  │ }
  │
  ▼
FastAPI Endpoint (endpoint_conversation_events.py)
  │
  │ @router.post("/conversations/end")
  │
  ▼
ConversationEventService.create_event()
  │
  │ 1. Validate request
  │ 2. Transform conversation_logs (API format → Standard format)
  │ 3. Store raw_conversation_log
  │ 4. Save to DB (conversation_events table)
  │ 5. **IMMEDIATELY** trigger processing (synchronous)
  │
  ▼
ConversationEventProcessingService.process_single_event()
  │
  │ 1. Mark event as PROCESSING
  │ 2. Calculate friendship score
  │ 3. Get topic_id from agenda_agent_prompting
  │ 4. Update topic_metrics (if topic_id found)
  │ 5. Update friendship_status
  │ 6. Mark event as PROCESSED
  │
  ▼
Response: 202 Accepted
  {
    "success": true,
    "data": {
      "id": 125,
      "status": "PROCESSED",  ← Processed immediately!
      "friendship_score_change": 0.5,
      "score_calculation_details": {...}
    }
  }
```

### 2. **Score Calculation Flow**

```
ConversationEventProcessingService
  │
  │ calc_result = score_service.calculate_score_from_conversation_id()
  │
  ▼
FriendshipScoreCalculationService
  │
  │ 1. Fetch conversation data
  │    └─> ConversationDataFetchService.fetch_by_id()
  │        └─> ConversationEventRepository.get_by_conversation_id()
  │
  │ 2. Extract metrics:
  │    - total_turns = _count_complete_turns()  ← Count (pika+user) pairs
  │    - user_initiated_questions (from metadata or LLM)
  │    - session_emotion (from metadata or LLM)
  │    - new_memories_count (from metadata)
  │
  │ 3. Calculate components:
  │    - base_score = total_turns * 0.5
  │    - engagement_bonus = user_initiated_questions * 3
  │    - emotion_bonus = mapping (interesting: +15, boring: -15, ...)
  │    - memory_bonus = new_memories_count * 5
  │
  │ 4. Total: base_score + engagement_bonus + emotion_bonus + memory_bonus
  │
  │ 5. Return: {
  │      "friendship_score_change": float,
  │      "calculation_details": {...}  ← Detailed breakdown
  │    }
  │
  ▼
Back to ConversationEventProcessingService
  │
  │ - Save calculation_details to score_calculation_details (JSONB)
  │ - Update friendship_status
```

### 3. **Topic Metrics Update Flow**

```
ConversationEventProcessingService
  │
  │ 1. Get user's friendship_level
  │    └─> FriendshipStatusRepository.get_by_user_id()
  │
  │ 2. Get topic_id from agent_id
  │    └─> PromptTemplateRepository.get_topic_id_by_agent_id()
  │        └─> Query agenda_agent_prompting table
  │
  │ 3. Calculate turns_change
  │    └─> _count_complete_turns(conversation_log)
  │
  │ 4. Update topic_metrics
  │    └─> FriendshipStatusRepository.update_topic_metrics()
  │        │
  │        ├─> Update topic_score += score_change
  │        ├─> Update topic_turns += turns_change
  │        ├─> Update last_date
  │        ├─> Add bot_id to agents_used
  │        ├─> Determine topic_level (PHASE1/2/3)
  │        └─> Update overall friendship_score
  │
  ▼
Database: friendship_status.topic_metrics (JSONB)
```

### 4. **Background Scheduler Flow**

```
Application Startup
  │
  │ @app.on_event("startup")
  │
  ▼
ConversationEventScheduler.start_background_jobs()
  │
  │ Start background thread:
  │   - Every 30 seconds
  │   - Fetch due events (status=PENDING or FAILED)
  │   - Process in batch (max 25 events)
  │   - Retry failed events
  │
  ▼
ConversationEventProcessingService.process_due_events()
  │
  │ For each event:
  │   1. Mark as PROCESSING
  │   2. Calculate score
  │   3. Update friendship_status
  │   4. Mark as PROCESSED or FAILED
  │
  ▼
Continuous monitoring
```

---

## 📁 Cấu Trúc Thư Mục

```
src/app/
├── api/                          # API Layer
│   ├── dependency_injection.py   # FastAPI dependency injection
│   └── v1/
│       ├── router_v1_main.py    # Main router
│       └── endpoints/
│           ├── endpoint_conversation_events.py      # POST /conversations/end
│           ├── endpoint_conversations_get.py        # GET /conversations/{id}
│           ├── endpoint_friendship_calculate_score.py
│           ├── endpoint_friendship_status.py
│           └── endpoint_activities_suggest.py
│
├── services/                      # Business Logic Layer
│   ├── conversation_event_service.py                # Orchestrates event creation
│   ├── conversation_event_processing_service.py      # Processes events
│   ├── friendship_score_calculation_service.py     # Calculates scores
│   ├── friendship_status_update_service.py          # Updates friendship status
│   ├── conversation_data_fetch_service.py           # Fetches conversation data
│   └── agent_selection_service.py                   # Agent selection logic
│
├── repositories/                  # Data Access Layer
│   ├── conversation_event_repository.py             # conversation_events table
│   ├── friendship_status_repository.py              # friendship_status table
│   └── prompt_template_repository.py                # agenda_agent_prompting table
│
├── models/                        # SQLAlchemy ORM Models
│   ├── conversation_event_model.py
│   ├── friendship_status_model.py
│   └── prompt_template_model.py
│
├── schemas/                       # Pydantic Schemas
│   ├── conversation_event_schemas.py
│   ├── conversation_schemas.py
│   └── activity_suggestion_schemas.py
│
├── utils/                         # Utilities
│   ├── conversation_log_transform.py    # Transform API format → Standard format
│   ├── topic_utils.py                   # Extract topic_id from agent_id
│   └── logger_setup.py
│
├── background/                    # Background Jobs
│   └── conversation_event_scheduler.py   # Scheduled processing
│
├── cache/                         # Caching (Redis)
│   └── redis_cache_manager.py
│
└── main_app.py                    # FastAPI app entry point
```

---

## 🔑 Các Component Chính

### 1. **API Endpoints**

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/v1/conversations/end` | POST | Nhận conversation event từ Backend, lưu vào DB và xử lý ngay (synchronous) |
| `/v1/conversations/{id}` | GET | Lấy thông tin conversation event |
| `/v1/friendship/calculate-score/{conversation_id}` | POST | Tính điểm friendship từ conversation_id |
| `/v1/friendship/status/{user_id}` | GET | Lấy friendship status của user |
| `/v1/activities/suggest/{user_id}` | GET | Gợi ý activities cho user |

### 2. **Services**

| Service | Trách nhiệm |
|---------|-------------|
| `ConversationEventService` | Validate và lưu conversation event, trigger immediate processing |
| `ConversationEventProcessingService` | Xử lý event: tính điểm, update friendship status |
| `FriendshipScoreCalculationService` | Tính toán friendship score từ conversation log |
| `FriendshipStatusUpdateService` | Cập nhật friendship_status và topic_metrics |
| `ConversationDataFetchService` | Lấy conversation data từ DB hoặc mock |

### 3. **Repositories**

| Repository | Trách nhiệm |
|------------|-------------|
| `ConversationEventRepository` | CRUD operations cho `conversation_events` table |
| `FriendshipStatusRepository` | CRUD operations cho `friendship_status` table, update topic_metrics |
| `PromptTemplateRepository` | Query `agenda_agent_prompting` để lấy topic_id từ agent_id |

### 4. **Database Tables**

| Table | Mục đích |
|-------|----------|
| `conversation_events` | Lưu conversation events từ Backend, kết quả xử lý |
| `friendship_status` | Lưu friendship score, level, topic_metrics của mỗi user |
| `agenda_agent_prompting` | Mapping agent_id → topic_id theo friendship_level |

---

## ⚠️ Vấn Đề Hiện Tại

### 1. **Synchronous Processing**
- **Vấn đề**: API `POST /conversations/end` xử lý ngay trong request handler
- **Hậu quả**: Response time chậm, không scalable
- **Cần**: Chuyển sang async với RabbitMQ queue

### 2. **score_calculation_details không hiển thị**
- **Vấn đề**: Log cho thấy đã lưu vào DB, nhưng API response trả về `null`
- **Nguyên nhân có thể**: Transaction isolation, response serialization
- **Cần**: Kiểm tra `_serialize()` method trong `ConversationEventService`

### 3. **Mock Data Usage**
- **Vấn đề**: `ConversationDataFetchService` đang dùng mock data thay vì real data
- **Cần**: Sửa dependency injection để dùng real repository

---

## 🚀 Hướng Cải Thiện (Chuẩn Bị cho RabbitMQ)

### Kiến Trúc Mới (Proposed)

```
Backend
  │
  │ POST /v1/conversations/end
  │
  ▼
FastAPI Endpoint
  │
  │ 1. Validate request
  │ 2. Store event to DB (status=PENDING)
  │ 3. Publish message to RabbitMQ queue
  │ 4. Return 202 Accepted immediately
  │
  ▼
RabbitMQ Queue
  │
  │ Queue: "conversation_events_processing"
  │
  ▼
Worker Process (Celery/Background Task)
  │
  │ 1. Consume message from queue
  │ 2. Process event (calculate score, update status)
  │ 3. Mark event as PROCESSED
  │ 4. Retry on failure
  │
  ▼
Database: Updated friendship_status
```

### Các Thay Đổi Cần Thiết

1. **Thêm RabbitMQ Integration**
   - Install `pika` hoặc `celery`
   - Tạo queue `conversation_events_processing`
   - Publisher: Publish message sau khi lưu event
   - Consumer: Worker process xử lý messages

2. **Tách Immediate Processing**
   - Bỏ `processor.process_single_event()` khỏi `create_event()`
   - Chỉ lưu event và publish message

3. **Worker Process**
   - Tạo separate worker process hoặc Celery task
   - Consume messages từ queue
   - Gọi `ConversationEventProcessingService.process_single_event()`

4. **Error Handling & Retry**
   - Dead letter queue cho failed messages
   - Exponential backoff retry
   - Monitoring và alerting

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│   Backend   │
└──────┬──────┘
       │ POST /v1/conversations/end
       │ {conversation_id, user_id, bot_id, conversation_logs}
       ▼
┌─────────────────────────────────────┐
│  FastAPI Endpoint                   │
│  endpoint_conversation_events.py    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  ConversationEventService           │
│  - Validate request                  │
│  - Transform conversation_logs      │
│  - Store to DB (status=PENDING)     │
│  - [CURRENT] Process immediately     │
│  - [FUTURE] Publish to RabbitMQ     │
└──────┬──────────────────────────────┘
       │
       ├─────────────────────────────────┐
       │                                 │
       ▼                                 ▼
┌──────────────────────┐    ┌──────────────────────────┐
│  DB:                 │    │  [CURRENT]                │
│  conversation_events │    │  Immediate Processing     │
│  - status=PENDING    │    │  (Synchronous)           │
│  - conversation_log  │    │                          │
│  - raw_conversation_ │    │  [FUTURE]                │
│    log               │    │  RabbitMQ Queue          │
└──────────────────────┘    └──────────────────────────┘
       │                                 │
       │                                 ▼
       │                    ┌──────────────────────────┐
       │                    │  Worker Process         │
       │                    │  (Consumer)             │
       │                    └───────────┬────────────┘
       │                                │
       │                                ▼
       │                    ┌──────────────────────────┐
       │                    │  Process Event:         │
       │                    │  1. Calculate score     │
       │                    │  2. Update topic_metrics │
       │                    │  3. Update friendship_   │
       │                    │     status              │
       │                    └───────────┬────────────┘
       │                                │
       └────────────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  DB:                 │
         │  conversation_events │
         │  - status=PROCESSED   │
         │  - score_calculation_│
         │    details           │
         │                      │
         │  friendship_status   │
         │  - friendship_score  │
         │  - topic_metrics     │
         └──────────────────────┘
```

---

## 🔧 Dependencies

### External Services
- **PostgreSQL**: Database
- **Redis**: Caching (optional)
- **RabbitMQ**: Message Queue (planned)

### Python Packages
- `fastapi`: Web framework
- `sqlalchemy`: ORM
- `pydantic`: Data validation
- `structlog`: Logging
- `groq`: LLM API (for conversation analysis)
- `langfuse`: LLM observability

---

## 📝 Notes

1. **Current Architecture**: Synchronous processing trong request handler
2. **Future Architecture**: Async với RabbitMQ queue
3. **Background Scheduler**: Hiện tại chỉ retry failed events, không xử lý primary flow
4. **Score Calculation**: Chi tiết được lưu trong `score_calculation_details` JSONB field

---

**Tài liệu này mô tả kiến trúc hiện tại để chuẩn bị cho việc implement RabbitMQ queue.**

