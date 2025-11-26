# Breakdown Tasks Delivery - Context Handling Service

**Version:** 1.0**Date:** 25/11/2025**Project:** Pika - Context Handling Module**Target Delivery:** MVP v1

---

## 📋 Tổng quan Delivery

Dự án được chia thành **3 phần chính** và **8 sub-tasks**:

```
┌─────────────────────────────────────────────────────────────────┐
│ DELIVERY 1: Implement DB - Friendship & Agent                  │
│ ├─ Task 1.1: Design & Create friendship_status table           │
│ ├─ Task 1.2: Design & Create friendship_agent_mapping table    │
│ ├─ Task 1.3: Create migration files (Alembic)                  │
│ └─ Task 1.4: Seed initial agent data                           │
├─────────────────────────────────────────────────────────────────┤
│ DELIVERY 2: Implement Logic - Calculate Score Friendship       │
│ ├─ Task 2.1: Implement conversation_id lookup logic            │
│ ├─ Task 2.2: Implement score calculation algorithm             │
│ ├─ Task 2.3: Implement topic_metrics update logic              │
│ └─ Task 2.4: Implement async processing (background job)       │
├─────────────────────────────────────────────────────────────────┤
│ DELIVERY 3: Implement API - Suggest Agents (for Hưng)          │
│ ├─ Task 3.1: Implement GET /activities/suggest endpoint        │
│ ├─ Task 3.2: Implement agent selection algorithm               │
│ ├─ Task 3.3: Implement caching mechanism                       │
│ └─ Task 3.4: Add error handling & validation                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## DELIVERY 1: Implement DB - Friendship & Agent

### Task 1.1: Design & Create `friendship_status` Table

**Objective:** Tạo bảng lưu trữ trạng thái tình bạn của mỗi user

**Deliverables:**

- [x] Table schema định nghĩa rõ ràng

- [x] Columns: `user_id`, `friendship_score`, `friendship_level`, `last_interaction_date`, `streak_day`, `topic_metrics` (JSONB)

- [x] Primary key: `user_id`

- [x] Indexes: `friendship_level`, `last_interaction_date` (for queries)

- [x] Constraints: NOT NULL, CHECK constraints cho `friendship_score` >= 0

- [x] Timestamps: `created_at`, `updated_at`

**SQL Schema:**

```sql
CREATE TABLE friendship_status (
    user_id VARCHAR(255) PRIMARY KEY,
    friendship_score FLOAT NOT NULL DEFAULT 0.0 CHECK (friendship_score >= 0),
    friendship_level VARCHAR(50) NOT NULL DEFAULT 'STRANGER' CHECK (friendship_level IN ('STRANGER', 'ACQUAINTANCE', 'FRIEND')),
    last_interaction_date TIMESTAMP,
    streak_day INTEGER NOT NULL DEFAULT 0,
    topic_metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_friendship_level ON friendship_status(friendship_level);
CREATE INDEX idx_last_interaction_date ON friendship_status(last_interaction_date);
```

**Acceptance Criteria:**

- [x] Table được tạo thành công

- [x] Có thể insert/update/delete records

- [x] Indexes hoạt động đúng

- [x] JSONB column hỗ trợ nested queries

---

### Task 1.2: Design & Create `friendship_agent_mapping` Table

**Objective:** Tạo bảng mapping giữa friendship_level và các agents (Greeting, Talk, Game)

**Deliverables:**

- [x] Table schema định nghĩa rõ ràng

- [x] Columns: `id`, `friendship_level`, `agent_type`, `agent_id`, `agent_name`, `agent_description`, `weight`, `is_active`

- [x] Primary key: `id` (auto-increment)

- [x] Unique constraint: `(friendship_level, agent_type, agent_id)`

- [x] Indexes: `friendship_level`, `agent_type`, `is_active`

- [x] Timestamps: `created_at`, `updated_at`

**SQL Schema:**

```sql
CREATE TABLE friendship_agent_mapping (
    id SERIAL PRIMARY KEY,
    friendship_level VARCHAR(50) NOT NULL CHECK (friendship_level IN ('STRANGER', 'ACQUAINTANCE', 'FRIEND')),
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('GREETING', 'TALK', 'GAME_ACTIVITY')),
    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_description TEXT,
    weight FLOAT NOT NULL DEFAULT 1.0 CHECK (weight > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (friendship_level, agent_type, agent_id)
);

CREATE INDEX idx_friendship_level ON friendship_agent_mapping(friendship_level);
CREATE INDEX idx_agent_type ON friendship_agent_mapping(agent_type);
CREATE INDEX idx_is_active ON friendship_agent_mapping(is_active);
```

**Acceptance Criteria:**

- [x] Table được tạo thành công

- [x] Unique constraint hoạt động

- [x] Có thể query agents theo friendship_level + agent_type

- [x] Weight column hỗ trợ weighted selection

---

### Task 1.3: Create Migration Files (Alembic)

**Objective:** Tạo migration files để version control database schema

**Deliverables:**

- [ ] Alembic initialized

- [ ] Migration file: `001_create_friendship_status_table.py`

- [ ] Migration file: `002_create_friendship_agent_mapping_table.py`

- [ ] Upgrade & downgrade functions hoạt động

- [ ] Có thể rollback nếu cần

**File Structure:**

```
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_create_friendship_status_table.py
    └── 002_create_friendship_agent_mapping_table.py
```

**Acceptance Criteria:**

- [ ] `alembic upgrade head` chạy thành công

- [ ] `alembic downgrade -1` chạy thành công

- [ ] Tables được tạo đúng schema

- [ ] Có thể track schema changes

---

### Task 1.4: Seed Initial Agent Data

**Objective:** Populate bảng `friendship_agent_mapping` với initial agents

**Deliverables:**

- [ ] Script: `scripts/seed_agents.py`

- [ ] Seed data cho STRANGER level (5-10 agents)

- [ ] Seed data cho ACQUAINTANCE level (8-12 agents)

- [ ] Seed data cho FRIEND level (10-15 agents)

- [ ] Mỗi level có: 2-3 Greeting agents, 3-5 Talk agents, 2-3 Game agents

**Sample Data:**

```python
AGENTS_DATA = [
    # STRANGER Level - Greeting
    {"friendship_level": "STRANGER", "agent_type": "GREETING", "agent_id": "greeting_welcome", "agent_name": "Welcome", "weight": 1.0},
    {"friendship_level": "STRANGER", "agent_type": "GREETING", "agent_id": "greeting_intro", "agent_name": "Introduce", "weight": 1.5},
    
    # STRANGER Level - Talk
    {"friendship_level": "STRANGER", "agent_type": "TALK", "agent_id": "talk_hobbies", "agent_name": "Hobbies", "weight": 1.0},
    {"friendship_level": "STRANGER", "agent_type": "TALK", "agent_id": "talk_school", "agent_name": "School", "weight": 1.0},
    
    # STRANGER Level - Game
    {"friendship_level": "STRANGER", "agent_type": "GAME_ACTIVITY", "agent_id": "game_drawing", "agent_name": "Drawing", "weight": 1.0},
    {"friendship_level": "STRANGER", "agent_type": "GAME_ACTIVITY", "agent_id": "game_riddle", "agent_name": "Riddle", "weight": 0.9},
    
    # ... more agents for ACQUAINTANCE and FRIEND levels
]
```

**Acceptance Criteria:**

- [ ] Script chạy thành công

- [ ] Tất cả agents được insert vào DB

- [ ] Có ít nhất 3 agents cho mỗi (level, type) combination

- [ ] Weights được set hợp lý (1.0 - 2.0)

- [ ] Có thể query agents theo level & type

---

## DELIVERY 2: Implement Logic - Calculate Score Friendship

### Task 2.1: Implement Conversation ID Lookup Logic

**Objective:** Implement logic để lấy conversation data từ conversation_id

**Deliverables:**

- [ ] API endpoint: `GET /conversations/{conversation_id}` (call từ AI service)

- [ ] Repository method: `get_conversation_by_id(conversation_id)`

- [ ] Service method: `fetch_conversation_data(conversation_id)`

- [ ] Error handling: 404 Not Found, 500 Server Error

- [ ] Logging: Log tất cả lookups

**Code Structure:**

```python
# app/repositories/conversation_repository.py
class ConversationRepository:
    def get_by_id(self, conversation_id: str):
        """Lấy conversation data từ DB"""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

# app/services/conversation_service.py
class ConversationService:
    def fetch_conversation_data(self, conversation_id: str):
        """Fetch conversation data và parse"""
        conv = self.repository.get_by_id(conversation_id)
        if not conv:
            raise ConversationNotFoundError(conversation_id)
        return {
            "conversation_id": conv.id,
            "user_id": conv.user_id,
            "conversation_log": json.loads(conv.log),
            "metadata": json.loads(conv.metadata)
        }

# app/api/v1/endpoints/conversations.py
@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, service: ConversationService = Depends()):
    return service.fetch_conversation_data(conversation_id)
```

**Acceptance Criteria:**

- [ ] API endpoint hoạt động

- [ ] Có thể lấy conversation data từ conversation_id

- [ ] Error handling hoạt động

- [ ] Logging hoạt động

- [ ] Response format đúng

---

### Task 2.2: Implement Score Calculation Algorithm

**Objective:** Implement logic tính toán friendship_score_change từ conversation data

**Deliverables:**

- [ ] Algorithm: `calculate_friendship_score_change(conversation_log, metadata)`

- [ ] Tính `base_score` từ `total_turns`

- [ ] Tính `engagement_bonus` từ `user_initiated_questions`

- [ ] Tính `emotion_bonus` từ `session_emotion`

- [ ] Tính `memory_bonus` từ `new_memories_count`

- [ ] Return: `friendship_score_change` (float)

**Algorithm:**

```python
def calculate_friendship_score_change(conversation_log: list, metadata: dict) -> float:
    """
    Tính toán friendship_score_change từ conversation log
    
    Formula:
    - base_score = total_turns * 0.5
    - engagement_bonus = user_initiated_questions * 3
    - emotion_bonus = +15 (interesting), -15 (boring), 0 (neutral)
    - memory_bonus = new_memories_count * 5
    - friendship_score_change = base_score + engagement_bonus + emotion_bonus + memory_bonus
    """
    
    total_turns = len(conversation_log)
    user_initiated = sum(1 for msg in conversation_log if msg.speaker == "user")
    emotion = metadata.get("session_emotion", "neutral")
    new_memories = metadata.get("new_memories_count", 0)
    
    base_score = total_turns * 0.5
    engagement_bonus = user_initiated * 3
    
    emotion_bonus = {
        "interesting": 15,
        "boring": -15,
        "happy": 10,
        "sad": -5,
        "neutral": 0
    }.get(emotion, 0)
    
    memory_bonus = new_memories * 5
    
    friendship_score_change = base_score + engagement_bonus + emotion_bonus + memory_bonus
    
    return max(0, friendship_score_change)  # Không âm
```

**Acceptance Criteria:**

- [ ] Algorithm tính toán chính xác

- [ ] Base score = total_turns * 0.5

- [ ] Engagement bonus = user_questions * 3

- [ ] Emotion bonus áp dụng đúng

- [ ] Memory bonus = new_memories * 5

- [ ] Result >= 0 (không âm)

- [ ] Unit tests pass

---

### Task 2.3: Implement Topic Metrics Update Logic

**Objective:** Implement logic cập nhật topic_metrics cho mỗi topic

**Deliverables:**

- [ ] Algorithm: `calculate_topic_metrics_update(conversation_log, current_topic_metrics)`

- [ ] Tính `score_change` cho mỗi topic

- [ ] Tính `turns_increment` cho mỗi topic

- [ ] Update `last_date` cho mỗi topic

- [ ] Return: `topic_metrics_update` (dict)

**Algorithm:**

```python
def calculate_topic_metrics_update(conversation_log: list, agent_type: str) -> dict:
    """
    Tính toán topic_metrics_update
    
    Formula:
    - score_change = (total_turns * 0.5) + (user_questions * 3)
    - turns_increment = total_turns
    - last_date = current_timestamp
    """
    
    total_turns = len(conversation_log)
    user_questions = sum(1 for msg in conversation_log if msg.speaker == "user")
    
    score_change = (total_turns * 0.5) + (user_questions * 3)
    turns_increment = total_turns
    
    return {
        "agent_type": agent_type,
        "score_change": score_change,
        "turns_increment": turns_increment,
        "last_date": datetime.utcnow().isoformat()
    }
```

**Acceptance Criteria:**

- [ ] Topic metrics được tính chính xác

- [ ] Score change = (turns * 0.5) + (questions * 3)

- [ ] Turns increment = total turns

- [ ] Last date được update

- [ ] Có thể handle multiple topics

- [ ] Unit tests pass

---

### Task 2.4: Implement Async Processing (Background Job)

**Objective:** Implement async processing để xử lý conversation end event ở background

**Deliverables:**

- [ ] Message Queue setup (RabbitMQ hoặc Kafka)

- [ ] Background worker: consume "conversation.ended" events

- [ ] Async task: `process_conversation_end(user_id, conversation_id)`

- [ ] Retry mechanism: 3 retries với exponential backoff

- [ ] Error handling & logging

- [ ] Health check endpoint

**Code Structure:**

```python
# app/tasks/conversation_tasks.py
@app.task(bind=True, max_retries=3)
def process_conversation_end(self, user_id: str, conversation_id: str):
    """
    Background task để xử lý conversation end event
    """
    try:
        # Step 1: Lấy conversation data
        conv_service = ConversationService(db)
        conv_data = conv_service.fetch_conversation_data(conversation_id)
        
        # Step 2: Tính toán score
        score_change = calculate_friendship_score_change(
            conv_data["conversation_log"],
            conv_data["metadata"]
        )
        
        # Step 3: Update friendship status
        friendship_service = FriendshipService(db)
        friendship_service.update_score(user_id, score_change)
        
        # Step 4: Compute candidates
        candidates = compute_candidates(user_id)
        cache_candidates(user_id, candidates)
        
        logger.info(f"Processed conversation {conversation_id} for user {user_id}")
        
    except Exception as exc:
        logger.error(f"Error processing conversation: {exc}")
        # Retry với exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# app/api/v1/endpoints/conversations.py
@router.post("/conversations/end")
def notify_conversation_end(request: ConversationEndRequest):
    """
    Notify conversation end - enqueue event
    """
    # Enqueue task
    process_conversation_end.delay(request.user_id, request.conversation_id)
    
    return {
        "status": "accepted",
        "message": "Conversation end event received and queued",
        "user_id": request.user_id,
        "conversation_id": request.conversation_id
    }
```

**Acceptance Criteria:**

- [ ] Message queue hoạt động

- [ ] Background worker consume events

- [ ] Async task xử lý đúng

- [ ] Retry mechanism hoạt động

- [ ] Error handling hoạt động

- [ ] Logging hoạt động

- [ ] Health check endpoint hoạt động

---

## DELIVERY 3: Implement API - Suggest Agents (for Hưng)

### Task 3.1: Implement GET `/activities/suggest` Endpoint

**Objective:** Implement API endpoint để lấy suggested agents cho user

**Deliverables:**

- [ ] Endpoint: `POST /activities/suggest`

- [ ] Request body: `{"user_id": "user_123"}`

- [ ] Response: Greeting agent + Talk agents + Game agents

- [ ] Error handling: 404 Not Found, 500 Server Error

- [ ] Validation: user_id required, valid format

**Code Structure:**

```python
# app/schemas/activity.py
class SuggestActivitiesRequest(BaseModel):
    user_id: str

class SuggestActivitiesResponse(BaseModel):
    user_id: str
    friendship_level: str
    computed_at: datetime
    greeting_agent: dict
    talk_agents: list
    game_agents: list

# app/api/v1/endpoints/activities.py
@router.post("/activities/suggest", response_model=SuggestActivitiesResponse)
def suggest_activities(
    request: SuggestActivitiesRequest,
    service: ActivitySelectionService = Depends()
):
    """Lấy suggested agents cho user"""
    return service.get_suggested_activities(request.user_id)
```

**Acceptance Criteria:**

- [ ] Endpoint hoạt động

- [ ] Request validation hoạt động

- [ ] Response format đúng

- [ ] Error handling hoạt động

- [ ] Có thể lấy agents cho user

---

### Task 3.2: Implement Agent Selection Algorithm

**Objective:** Implement logic chọn agents phù hợp nhất dựa trên friendship_level

**Deliverables:**

- [ ] Algorithm: `select_greeting_agent(user_id, friendship_level)`

- [ ] Algorithm: `select_talk_agents(user_id, friendship_level, count=2)`

- [ ] Algorithm: `select_game_agents(user_id, friendship_level, count=2)`

- [ ] Weighted selection dựa trên `weight` column

- [ ] Avoid duplicates

- [ ] Prioritize by topic_score & total_turns

**Algorithm:**

```python
def select_greeting_agent(user_id: str, friendship_level: str) -> dict:
    """
    Chọn 1 greeting agent dựa trên friendship_level
    Priority: Birthday > Returning > Emotion > Follow-up > Random
    """
    # Query agents từ DB
    agents = db.query(FriendshipAgentMapping).filter(
        FriendshipAgentMapping.friendship_level == friendship_level,
        FriendshipAgentMapping.agent_type == "GREETING",
        FriendshipAgentMapping.is_active == True
    ).all()
    
    # Weighted random selection
    selected = weighted_random_choice(agents, weight_field="weight")
    return selected

def select_talk_agents(user_id: str, friendship_level: str, count: int = 2) -> list:
    """
    Chọn N talk agents dựa trên:
    1. Topic score cao nhất (sở thích)
    2. Ít tương tác (khám phá)
    3. Cảm xúc phiên trước
    """
    # Query agents
    agents = db.query(FriendshipAgentMapping).filter(
        FriendshipAgentMapping.friendship_level == friendship_level,
        FriendshipAgentMapping.agent_type == "TALK",
        FriendshipAgentMapping.is_active == True
    ).all()
    
    # Lấy friendship status
    status = db.query(FriendshipStatus).filter(
        FriendshipStatus.user_id == user_id
    ).first()
    
    # Score agents dựa trên topic_metrics
    scored_agents = []
    for agent in agents:
        topic_id = agent.agent_id.split("_")[1]  # Extract topic from agent_id
        topic_score = status.topic_metrics.get(topic_id, {}).get("score", 0)
        total_turns = status.topic_metrics.get(topic_id, {}).get("turns", 0)
        
        # Higher score = higher priority
        # Lower turns = exploration candidate
        score = (topic_score * 0.7) + ((100 - total_turns) * 0.3)
        scored_agents.append((agent, score))
    
    # Sort by score và select top N
    scored_agents.sort(key=lambda x: x[1], reverse=True)
    selected = [agent for agent, score in scored_agents[:count]]
    
    return selected

def select_game_agents(user_id: str, friendship_level: str, count: int = 2) -> list:
    """
    Chọn N game agents dựa trên weight
    """
    agents = db.query(FriendshipAgentMapping).filter(
        FriendshipAgentMapping.friendship_level == friendship_level,
        FriendshipAgentMapping.agent_type == "GAME_ACTIVITY",
        FriendshipAgentMapping.is_active == True
    ).all()
    
    # Weighted random selection
    selected = weighted_random_choices(agents, k=count, weight_field="weight")
    return selected
```

**Acceptance Criteria:**

- [ ] Greeting agent selection hoạt động

- [ ] Talk agent selection hoạt động

- [ ] Game agent selection hoạt động

- [ ] Weighted selection hoạt động

- [ ] Avoid duplicates

- [ ] Priority logic hoạt động

- [ ] Unit tests pass

---

### Task 3.3: Implement Caching Mechanism

**Objective:** Implement caching để lưu pre-computed candidates

**Deliverables:**

- [ ] Redis setup & configuration

- [ ] Cache key format: `candidates:{user_id}`

- [ ] Cache TTL: 6 hours (hoặc configurable)

- [ ] Cache invalidation: Khi friendship_level thay đổi

- [ ] Cache hit/miss logging

**Code Structure:**

```python
# app/utils/cache.py
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_candidates(self, user_id: str):
        """Lấy candidates từ cache"""
        key = f"candidates:{user_id}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set_candidates(self, user_id: str, candidates: dict, ttl: int = 21600):
        """Lưu candidates vào cache (6h TTL)"""
        key = f"candidates:{user_id}"
        self.redis.setex(key, ttl, json.dumps(candidates))
    
    def invalidate_candidates(self, user_id: str):
        """Xóa cache khi friendship_level thay đổi"""
        key = f"candidates:{user_id}"
        self.redis.delete(key)

# app/services/activity_selection_service.py
class ActivitySelectionService:
    def get_suggested_activities(self, user_id: str):
        """Lấy suggested activities từ cache hoặc compute"""
        # Thử lấy từ cache
        cached = self.cache_manager.get_candidates(user_id)
        if cached:
            logger.info(f"Cache hit for user {user_id}")
            return cached
        
        # Compute nếu cache miss
        logger.info(f"Cache miss for user {user_id}, computing...")
        candidates = self.compute_candidates(user_id)
        
        # Lưu vào cache
        self.cache_manager.set_candidates(user_id, candidates)
        
        return candidates
```

**Acceptance Criteria:**

- [ ] Redis hoạt động

- [ ] Cache set/get hoạt động

- [ ] TTL hoạt động

- [ ] Cache invalidation hoạt động

- [ ] Logging hoạt động

- [ ] Cache hit rate > 80%

---

### Task 3.4: Add Error Handling & Validation

**Objective:** Implement comprehensive error handling & input validation

**Deliverables:**

- [ ] Input validation: user_id format, required fields

- [ ] Error responses: 400 Bad Request, 404 Not Found, 500 Server Error

- [ ] Custom exceptions: `UserNotFoundError`, `InvalidUserIdError`, `AgentSelectionError`

- [ ] Logging: Log tất cả errors

- [ ] Request/Response validation: Pydantic schemas

**Code Structure:**

```python
# app/core/exceptions.py
class UserNotFoundError(AppException):
    """Raised when user not found"""
    pass

class InvalidUserIdError(AppException):
    """Raised when user_id format invalid"""
    pass

class AgentSelectionError(AppException):
    """Raised when agent selection fails"""
    pass

# app/api/v1/endpoints/activities.py
@router.post("/activities/suggest", response_model=SuggestActivitiesResponse)
def suggest_activities(
    request: SuggestActivitiesRequest,
    service: ActivitySelectionService = Depends()
):
    """Lấy suggested activities cho user"""
    try:
        # Validate user_id
        if not request.user_id or len(request.user_id) < 3:
            raise InvalidUserIdError("user_id must be at least 3 characters")
        
        # Get activities
        result = service.get_suggested_activities(request.user_id)
        
        if not result:
            raise UserNotFoundError(f"User {request.user_id} not found")
        
        return result
        
    except UserNotFoundError as e:
        logger.error(f"User not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except InvalidUserIdError as e:
        logger.error(f"Invalid user_id: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Acceptance Criteria:**

- [ ] Input validation hoạt động

- [ ] Error responses hoạt động

- [ ] Custom exceptions hoạt động

- [ ] Logging hoạt động

- [ ] Pydantic validation hoạt động

---

## 📊 Checklist Tổng hợp

### DELIVERY 1: DB Implementation

- [ ] **Task 1.1:** friendship_status table

   - [ ] Schema defined

   - [ ] Columns correct

   - [ ] Indexes created

   - [ ] Constraints applied

   - [ ] Timestamps added

- [ ] **Task 1.2:** friendship_agent_mapping table

   - [ ] Schema defined

   - [ ] Columns correct

   - [ ] Unique constraints applied

   - [ ] Indexes created

   - [ ] Timestamps added

- [ ] **Task 1.3:** Alembic migrations

   - [ ] Alembic initialized

   - [ ] Migration 001 created

   - [ ] Migration 002 created

   - [ ] Upgrade works

   - [ ] Downgrade works

- [ ] **Task 1.4:** Seed agent data

   - [ ] Script created

   - [ ] STRANGER agents seeded (5-10)

   - [ ] ACQUAINTANCE agents seeded (8-12)

   - [ ] FRIEND agents seeded (10-15)

   - [ ] Data verified in DB

---

### DELIVERY 2: Score Calculation Logic

- [ ] **Task 2.1:** Conversation ID lookup

   - [ ] API endpoint created

   - [ ] Repository method created

   - [ ] Service method created

   - [ ] Error handling implemented

   - [ ] Logging implemented

   - [ ] Unit tests pass

- [ ] **Task 2.2:** Score calculation algorithm

   - [ ] Algorithm implemented

   - [ ] Base score = turns * 0.5

   - [ ] Engagement bonus = questions * 3

   - [ ] Emotion bonus implemented

   - [ ] Memory bonus = memories * 5

   - [ ] Result >= 0

   - [ ] Unit tests pass

- [ ] **Task 2.3:** Topic metrics update

   - [ ] Algorithm implemented

   - [ ] Score change calculated

   - [ ] Turns increment calculated

   - [ ] Last date updated

   - [ ] Multiple topics handled

   - [ ] Unit tests pass

- [ ] **Task 2.4:** Async processing

   - [ ] Message queue setup

   - [ ] Background worker created

   - [ ] Async task created

   - [ ] Retry mechanism implemented

   - [ ] Error handling implemented

   - [ ] Logging implemented

   - [ ] Health check endpoint created

---

### DELIVERY 3: Suggest Agents API

- [ ] **Task 3.1:** API endpoint

   - [ ] Endpoint created

   - [ ] Request validation implemented

   - [ ] Response format correct

   - [ ] Error handling implemented

   - [ ] Logging implemented

- [ ] **Task 3.2:** Agent selection algorithm

   - [ ] Greeting selection implemented

   - [ ] Talk selection implemented

   - [ ] Game selection implemented

   - [ ] Weighted selection implemented

   - [ ] Duplicates avoided

   - [ ] Priority logic implemented

   - [ ] Unit tests pass

- [ ] **Task 3.3:** Caching mechanism

   - [ ] Redis setup

   - [ ] Cache set/get implemented

   - [ ] TTL configured (6h)

   - [ ] Cache invalidation implemented

   - [ ] Logging implemented

   - [ ] Cache hit rate > 80%

- [ ] **Task 3.4:** Error handling & validation

   - [ ] Input validation implemented

   - [ ] Error responses implemented

   - [ ] Custom exceptions created

   - [ ] Logging implemented

   - [ ] Pydantic validation implemented

---

## 🚀 Quy trình Triển khai

### Phase 1: Setup & Database (Week 1)

1. Setup PostgreSQL, Alembic

1. Implement Task 1.1 & 1.2 (DB schema)

1. Implement Task 1.3 (Migrations)

1. Implement Task 1.4 (Seed data)

1. **Milestone:** DB ready

### Phase 2: Scoring Logic (Week 2)

1. Implement Task 2.1 (Conversation lookup)

1. Implement Task 2.2 (Score calculation)

1. Implement Task 2.3 (Topic metrics)

1. Implement Task 2.4 (Async processing)

1. **Milestone:** Scoring logic ready

### Phase 3: API & Caching (Week 3)

1. Implement Task 3.1 (API endpoint)

1. Implement Task 3.2 (Agent selection)

1. Implement Task 3.3 (Caching)

1. Implement Task 3.4 (Error handling)

1. **Milestone:** API ready for Hưng

### Phase 4: Testing & Deployment (Week 4)

1. Unit tests (all tasks)

1. Integration tests

1. Performance testing

1. Deployment to staging

1. UAT with Hưng

1. **Milestone:** Production ready

---

## ✅ Acceptance Criteria - Tổng hợp

**Tất cả tasks phải:**

- [ ] Có unit tests (coverage >= 80%)

- [ ] Có integration tests

- [ ] Có logging

- [ ] Có error handling

- [ ] Có documentation

- [ ] Code review passed

- [ ] Performance acceptable

- [ ] Security checked

---

## 📝 Ghi chú Quan trọng

### Điều cần chú ý:

1. **Database:**
  - JSONB column cho `topic_metrics` để linh hoạt
  - Indexes trên `friendship_level` & `last_interaction_date`
  - Constraints để đảm bảo data integrity

1. **Scoring Logic:**
  - Formula: base_score + engagement_bonus + emotion_bonus + memory_bonus
  - Tất cả scores >= 0
  - Unit tests cho tất cả edge cases

1. **API Endpoint:**
  - Response từ cache (< 100ms)
  - Pre-computed candidates
  - Comprehensive error handling

1. **Async Processing:**
  - Message queue để reliability
  - Retry mechanism với exponential backoff
  - Logging cho troubleshooting

1. **Caching:**
  - 6h TTL (hoặc configurable)
  - Invalidation khi friendship_level thay đổi
  - Cache hit rate monitoring

---

## 🎯 Deliverables Summary

| Delivery | Tasks | Status | Owner | ETA |
| --- | --- | --- | --- | --- |
| **DB Implementation** | 1.1, 1.2, 1.3, 1.4 | ⏳ | Backend | Week 1 |
| **Score Logic** | 2.1, 2.2, 2.3, 2.4 | ⏳ | AI/Backend | Week 2 |
| **Suggest API** | 3.1, 3.2, 3.3, 3.4 | ⏳ | Backend | Week 3 |
| **Testing & Deploy** | Tests, Docs, Deploy | ⏳ | QA/DevOps | Week 4 |

---

## 📞 Contact & Support

- **Backend Lead:** [Name]

- **AI Lead:** [Name]

- **QA Lead:** [Name]

- **DevOps Lead:** [Name]

**Questions?** Hãy liên hệ hoặc tạo issue trên project board.

