# Design Document

## Overview

The Context Handling - PHRASE3_PHASE3_PHASE3_FRIENDship Management module is a FastAPI-based microservice that manages the relationship state between users and the Pika AI companion. The system uses an event-driven architecture with asynchronous processing to handle conversation analysis, PHRASE3_PHASE3_PHASE3_FRIENDship scoring, and personalized activity recommendations without blocking user interactions.

### Key Design Principles

- **Event-Driven Architecture**: Conversation end events are processed asynchronously via message queue
- **Pre-computed Candidates**: Activity suggestions are calculated ahead of time and cached for fast retrieval
- **SOLID Principles**: Clean separation of concerns with repository, service, and API layers
- **PostgreSQL + JSONB**: Relational database with NoSQL-style flexibility for topic metrics
- **Redis Caching**: 6-hour TTL cache for pre-computed activity candidates
- **Weighted Selection**: Probabilistic agent selection based on configurable weights

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYSTEM ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Frontend   │────────▶│  Backend Service │────────▶│   Context    │
│     App      │         │   (Main API)     │         │   Handling   │
└──────────────┘         └──────────────────┘         │   Service    │
                                  │                    └──────────────┘
                                  │                           │
                                  ▼                           ▼
                         ┌──────────────────┐       ┌──────────────┐
                         │  Message Queue   │       │  PostgreSQL  │
                         │ (RabbitMQ/Kafka) │       │   Database   │
                         └──────────────────┘       └──────────────┘
                                  │                           │
                                  ▼                           ▼
                         ┌──────────────────┐       ┌──────────────┐
                         │   AI Scoring     │       │    Redis     │
                         │    Service       │       │    Cache     │
                         └──────────────────┘       └──────────────┘
```

### Event Flow

```
PHASE 1: CONVERSATION END (Non-blocking)
═══════════════════════════════════════════════════════════════
1. User finishes conversation
2. Backend → POST /conversations/end (user_id, conversation_id)
3. Context Service → Enqueue to Message Queue
4. Context Service → Return 202 Accepted (< 100ms)
5. User continues using app (no waiting)

PHASE 2: ASYNC PROCESSING (Background)
═══════════════════════════════════════════════════════════════
6. AI Scoring Service → Consume event from queue
7. AI Scoring Service → GET /conversations/{id} from Backend
8. AI Scoring Service → Calculate PHRASE3_PHASE3_PHASE3_FRIENDship_score_change
9. AI Scoring Service → Calculate topic_metrics_update
10. AI Scoring Service → POST /PHRASE3_PHASE3_PHASE3_FRIENDship/update to Context Service
11. Context Service → Update PostgreSQL database
12. Context Service → Invalidate cache if PHRASE3_PHASE3_PHASE3_FRIENDship_level changed
13. Context Service → Compute new candidates
14. Context Service → Cache candidates in Redis (6h TTL)

PHASE 3: ACTIVITY SUGGESTION (Fast retrieval)
═══════════════════════════════════════════════════════════════
15. User opens app next time
16. Backend → POST /activities/suggest (user_id)
17. Context Service → Check Redis cache
18. Context Service → Return cached candidates (< 100ms)
19. Frontend → Display greeting + 4 activities
```

## Components and Interfaces

### 1. API Layer

#### Endpoints

**Conversation Management**
- `POST /v1/conversations/end` - Notify conversation end (202 Accepted)
- `GET /v1/conversations/{conversation_id}` - Retrieve conversation data (Backend only)

**PHRASE3_PHASE3_PHASE3_FRIENDship Management**
- `POST /v1/PHRASE3_PHASE3_PHASE3_FRIENDship/status` - Get current PHRASE3_PHASE3_PHASE3_FRIENDship status
- `POST /v1/PHRASE3_PHASE3_PHASE3_FRIENDship/update` - Update PHRASE3_PHASE3_PHASE3_FRIENDship status (AI Service only)

**Activity Suggestion**
- `POST /v1/activities/suggest` - Get pre-computed activity suggestions

**Agent Mapping Management**
- `GET /v1/agent-mappings` - List agent mappings (with filters)
- `POST /v1/agent-mappings` - Create new agent mapping
- `PUT /v1/agent-mappings/{id}` - Update agent mapping
- `DELETE /v1/agent-mappings/{id}` - Soft delete agent mapping

**Health Check**
- `GET /v1/health` - Service health status

#### Request/Response Schemas

```python
# Conversation End
class ConversationEndRequest(BaseModel):
    user_id: str
    conversation_id: str
    session_metadata: Optional[Dict] = None

class ConversationEndResponse(BaseModel):
    status: str = "accepted"
    message: str
    user_id: str
    conversation_id: str
    processing_id: str

# PHRASE3_PHASE3_PHASE3_FRIENDship Status
class PHRASE3_PHASE3_PHASE3_FRIENDshipStatusRequest(BaseModel):
    user_id: str

class PHRASE3_PHASE3_PHASE3_FRIENDshipStatusResponse(BaseModel):
    user_id: str
    PHRASE3_PHASE3_PHASE3_FRIENDship_score: float
    PHRASE3_PHASE3_PHASE3_FRIENDship_level: str
    last_interaction_date: Optional[datetime]
    streak_day: int
    total_turns: int
    topic_metrics: Dict[str, TopicMetric]

class TopicMetric(BaseModel):
    score: float
    total_turns: int
    last_date: datetime

# Activity Suggestion
class ActivitySuggestionRequest(BaseModel):
    user_id: str

class ActivitySuggestionResponse(BaseModel):
    user_id: str
    PHRASE3_PHASE3_PHASE3_FRIENDship_level: str
    computed_at: datetime
    greeting_agent: AgentDetail
    talk_agents: List[AgentDetail]
    game_agents: List[AgentDetail]

class AgentDetail(BaseModel):
    id: int
    PHRASE3_PHASE3_PHASE3_FRIENDship_level: str
    agent_type: str
    agent_id: str
    agent_name: str
    agent_description: str
    weight: float
    is_active: bool
    reason: str
    topic_score: Optional[float] = None
    total_turns: Optional[int] = None
```

### 2. Service Layer

#### PHRASE3_PHASE3_PHASE3_FRIENDshipService

**Responsibilities:**
- Calculate PHRASE3_PHASE3_PHASE3_FRIENDship score changes from conversation data
- Update PHRASE3_PHASE3_PHASE3_FRIENDship status in database
- Manage PHRASE3_PHASE3_PHASE3_FRIENDship level transitions
- Update streak day logic

**Key Methods:**
```python
class PHRASE3_PHASE3_PHASE3_FRIENDshipService:
    def calculate_score_change(
        self, 
        conversation_log: List[Message], 
        metadata: Dict
    ) -> float:
        """
        Calculate PHRASE3_PHASE3_PHASE3_FRIENDship score change using formula:
        base_score + engagement_bonus + emotion_bonus + memory_bonus
        """
        
    def update_PHRASE3_PHASE3_PHASE3_FRIENDship_status(
        self,
        user_id: str,
        score_change: float,
        topic_metrics_update: Dict
    ) -> PHRASE3_PHASE3_PHASE3_FRIENDshipStatus:
        """
        Update PHRASE3_PHASE3_PHASE3_FRIENDship status and handle level transitions
        """
        
    def calculate_topic_metrics_update(
        self,
        conversation_log: List[Message],
        agent_type: str
    ) -> Dict:
        """
        Calculate topic-specific metric updates
        """
        
    def update_streak_day(
        self,
        user_id: str,
        last_interaction_date: datetime
    ) -> int:
        """
        Update streak day based on interaction pattern
        """
```

#### SelectionService

**Responsibilities:**
- Select greeting agent based on priority rules
- Select talk agents based on preferences and exploration
- Select game agents using weighted random selection
- Compute and cache activity candidates

**Key Methods:**
```python
class SelectionService:
    def compute_candidates(
        self,
        user_id: str
    ) -> ActivitySuggestionResponse:
        """
        Compute complete set of activity candidates
        """
        
    def select_greeting_agent(
        self,
        user_id: str,
        PHRASE3_PHASE3_PHASE3_FRIENDship_level: str,
        PHRASE3_PHASE3_PHASE3_FRIENDship_status: PHRASE3_PHASE3_PHASE3_FRIENDshipStatus
    ) -> AgentDetail:
        """
        Select greeting agent with priority logic:
        1. Birthday greeting (if today is birthday)
        2. Returning user (if streak > 3)
        3. Emotion-based (if last emotion was strong)
        4. Memory recall (if PHASE2_ACQUAINTANCE+)
        5. Weighted random from pool
        """
        
    def select_talk_agents(
        self,
        user_id: str,
        PHRASE3_PHASE3_PHASE3_FRIENDship_level: str,
        topic_metrics: Dict,
        count: int = 2
    ) -> List[AgentDetail]:
        """
        Select talk agents using scoring formula:
        selection_score = (topic_score * 0.7) + ((100 - total_turns) * 0.3)
        
        Strategy:
        - First agent: Highest topic_score (preference)
        - Second agent: Low total_turns (exploration)
        """
        
    def select_game_agents(
        self,
        PHRASE3_PHASE3_PHASE3_FRIENDship_level: str,
        count: int = 2
    ) -> List[AgentDetail]:
        """
        Select game agents using weighted random selection
        """
        
    def weighted_random_choice(
        self,
        agents: List[AgentMapping],
        weight_field: str = "weight"
    ) -> AgentMapping:
        """
        Perform weighted random selection
        """
```

### 3. Repository Layer

#### PHRASE3_PHASE3_PHASE3_FRIENDshipRepository

**Responsibilities:**
- CRUD operations for PHRASE3_PHASE3_PHASE3_FRIENDship_status table
- Query optimization using indexes
- JSONB field manipulation for topic_metrics

**Key Methods:**
```python
class PHRASE3_PHASE3_PHASE3_FRIENDshipRepository(BaseRepository[PHRASE3_PHASE3_PHASE3_FRIENDshipStatus]):
    def get_by_user_id(self, user_id: str) -> Optional[PHRASE3_PHASE3_PHASE3_FRIENDshipStatus]
    
    def create_or_update(
        self,
        user_id: str,
        score_change: float,
        topic_metrics_update: Dict
    ) -> PHRASE3_PHASE3_PHASE3_FRIENDshipStatus
    
    def update_score(
        self,
        user_id: str,
        score_change: float
    ) -> PHRASE3_PHASE3_PHASE3_FRIENDshipStatus
    
    def update_topic_metrics(
        self,
        user_id: str,
        topic_id: str,
        metrics_update: Dict
    ) -> PHRASE3_PHASE3_PHASE3_FRIENDshipStatus
    
    def get_users_by_level(
        self,
        PHRASE3_PHASE3_PHASE3_FRIENDship_level: str
    ) -> List[PHRASE3_PHASE3_PHASE3_FRIENDshipStatus]
```

#### AgentRepository

**Responsibilities:**
- CRUD operations for PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping table
- Filter agents by level and type
- Manage agent activation status

**Key Methods:**
```python
class AgentRepository(BaseRepository[PHRASE3_PHASE3_PHASE3_FRIENDshipAgentMapping]):
    def get_by_level_and_type(
        self,
        PHRASE3_PHASE3_PHASE3_FRIENDship_level: str,
        agent_type: str,
        active_only: bool = True
    ) -> List[PHRASE3_PHASE3_PHASE3_FRIENDshipAgentMapping]
    
    def get_all_active(self) -> List[PHRASE3_PHASE3_PHASE3_FRIENDshipAgentMapping]
    
    def soft_delete(self, mapping_id: int) -> bool
    
    def bulk_create(
        self,
        mappings: List[AgentMappingCreate]
    ) -> List[PHRASE3_PHASE3_PHASE3_FRIENDshipAgentMapping]
```

### 4. Cache Layer

#### CacheManager

**Responsibilities:**
- Manage Redis cache for pre-computed candidates
- Handle cache invalidation
- Monitor cache hit/miss rates

**Key Methods:**
```python
class CacheManager:
    def get_candidates(
        self,
        user_id: str
    ) -> Optional[ActivitySuggestionResponse]:
        """
        Retrieve cached candidates
        Key format: "candidates:{user_id}"
        """
        
    def set_candidates(
        self,
        user_id: str,
        candidates: ActivitySuggestionResponse,
        ttl: int = 21600  # 6 hours
    ) -> bool:
        """
        Cache candidates with TTL
        """
        
    def invalidate_candidates(
        self,
        user_id: str
    ) -> bool:
        """
        Invalidate cache when PHRASE3_PHASE3_PHASE3_FRIENDship_level changes
        """
        
    def get_cache_stats(self) -> Dict:
        """
        Return cache hit/miss statistics
        """
```

### 5. Message Queue Integration

#### Event Producer (Context Service)

```python
class EventProducer:
    def publish_conversation_end(
        self,
        user_id: str,
        conversation_id: str,
        metadata: Dict
    ) -> str:
        """
        Publish conversation.ended event to queue
        Returns: processing_id for tracking
        """
```

#### Event Consumer (AI Scoring Service)

```python
class ConversationEndConsumer:
    def consume_conversation_end_events(self):
        """
        Consume conversation.ended events from queue
        Process with retry logic (max 3 attempts, exponential backoff)
        """
        
    async def process_conversation_end(
        self,
        user_id: str,
        conversation_id: str
    ):
        """
        1. Fetch conversation data from Backend
        2. Calculate PHRASE3_PHASE3_PHASE3_FRIENDship score change
        3. Calculate topic metrics update
        4. Update PHRASE3_PHASE3_PHASE3_FRIENDship status via Context Service API
        5. Trigger candidate recomputation
        """
```

## Data Models

### Database Schema

#### PHRASE3_PHASE3_PHASE3_FRIENDship_status Table

```sql
CREATE TABLE PHRASE3_PHASE3_PHASE3_FRIENDship_status (
    user_id VARCHAR(255) PRIMARY KEY,
    PHRASE3_PHASE3_PHASE3_FRIENDship_score FLOAT NOT NULL DEFAULT 0.0 
        CHECK (PHRASE3_PHASE3_PHASE3_FRIENDship_score >= 0),
    PHRASE3_PHASE3_PHASE3_FRIENDship_level VARCHAR(50) NOT NULL DEFAULT 'PHASE1_STRANGER' 
        CHECK (PHRASE3_PHASE3_PHASE3_FRIENDship_level IN ('PHASE1_STRANGER', 'PHASE2_ACQUAINTANCE', 'PHRASE3_PHASE3_PHASE3_FRIEND')),
    last_interaction_date TIMESTAMP,
    streak_day INTEGER NOT NULL DEFAULT 0,
    topic_metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_PHRASE3_PHASE3_PHASE3_FRIENDship_level 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_status(PHRASE3_PHASE3_PHASE3_FRIENDship_level);
CREATE INDEX idx_last_interaction_date 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_status(last_interaction_date DESC);
CREATE INDEX idx_topic_metrics_gin 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_status USING GIN (topic_metrics);
```

#### PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping Table

```sql
CREATE TABLE PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping (
    id SERIAL PRIMARY KEY,
    PHRASE3_PHASE3_PHASE3_FRIENDship_level VARCHAR(50) NOT NULL 
        CHECK (PHRASE3_PHASE3_PHASE3_FRIENDship_level IN ('PHASE1_STRANGER', 'PHASE2_ACQUAINTANCE', 'PHRASE3_PHASE3_PHASE3_FRIEND')),
    agent_type VARCHAR(50) NOT NULL 
        CHECK (agent_type IN ('GREETING', 'TALK', 'GAME')),
    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_description TEXT,
    weight FLOAT NOT NULL DEFAULT 1.0 CHECK (weight > 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, agent_id)
);

CREATE INDEX idx_PHRASE3_PHASE3_PHASE3_FRIENDship_level 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping(PHRASE3_PHASE3_PHASE3_FRIENDship_level);
CREATE INDEX idx_agent_type 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping(agent_type);
CREATE INDEX idx_is_active 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping(is_active);
CREATE INDEX idx_level_type_active 
    ON PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping(PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, is_active);
```

### JSONB Structure for topic_metrics

```json
{
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
```

### PHRASE3_PHASE3_PHASE3_FRIENDship Level Thresholds

```python
PHRASE3_PHASE3_PHASE3_FRIENDSHIP_SCORE_THRESHOLDS = {
    "PHASE1_STRANGER": (0, 100),
    "PHASE2_ACQUAINTANCE": (100, 500),
    "PHRASE3_PHASE3_PHASE3_FRIEND": (500, float('inf'))
}
```

## Error Handling

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime
    request_id: str
```

### Error Scenarios

| Scenario | HTTP Status | Error Code | Handling Strategy |
|----------|-------------|------------|-------------------|
| Invalid user_id format | 400 | INVALID_USER_ID | Validate length >= 3 chars |
| User not found | 404 | USER_NOT_FOUND | Return descriptive message |
| Conversation not found | 404 | CONVERSATION_NOT_FOUND | Log and return error |
| Message queue unavailable | 503 | QUEUE_UNAVAILABLE | Return retry-after header |
| Database connection failed | 503 | DATABASE_UNAVAILABLE | Circuit breaker pattern |
| Redis connection failed | 503 | CACHE_UNAVAILABLE | Fallback to DB query |
| Internal processing error | 500 | INTERNAL_ERROR | Log full stack trace |
| Request timeout | 504 | TIMEOUT | Return after 30s |

### Retry Logic

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(TransientError)
)
async def process_with_retry(task):
    """
    Retry configuration:
    - Max attempts: 3
    - Wait time: 2s, 4s, 8s (exponential backoff)
    - Only retry on transient errors
    """
```

## Testing Strategy

### Unit Tests

**Coverage Target: 80%+**

- **Service Layer Tests**
  - `test_calculate_score_change()` - Test all formula components
  - `test_update_PHRASE3_PHASE3_PHASE3_FRIENDship_status()` - Test level transitions
  - `test_select_greeting_agent()` - Test priority logic
  - `test_select_talk_agents()` - Test scoring and selection
  - `test_select_game_agents()` - Test weighted random
  - `test_update_streak_day()` - Test streak logic

- **Repository Layer Tests**
  - `test_create_PHRASE3_PHASE3_PHASE3_FRIENDship_status()` - Test CRUD operations
  - `test_update_topic_metrics()` - Test JSONB updates
  - `test_get_by_level_and_type()` - Test filtering

- **Cache Layer Tests**
  - `test_cache_set_get()` - Test cache operations
  - `test_cache_invalidation()` - Test invalidation logic
  - `test_cache_ttl()` - Test expiration

### Integration Tests

- **API Endpoint Tests**
  - `test_conversation_end_flow()` - Test full async flow
  - `test_PHRASE3_PHASE3_PHASE3_FRIENDship_status_retrieval()` - Test status API
  - `test_activity_suggestion_cached()` - Test cache hit
  - `test_activity_suggestion_miss()` - Test cache miss
  - `test_agent_mapping_crud()` - Test CRUD operations

- **Database Tests**
  - `test_PHRASE3_PHASE3_PHASE3_FRIENDship_level_transition()` - Test threshold logic
  - `test_topic_metrics_merge()` - Test JSONB merge
  - `test_concurrent_updates()` - Test race conditions

### Performance Tests

- **Load Testing**
  - Target: 1000 requests/second for /activities/suggest
  - Target: < 100ms response time for cached requests
  - Target: < 500ms response time for cache miss

- **Stress Testing**
  - Test message queue backlog handling
  - Test database connection pool exhaustion
  - Test Redis memory limits

## Deployment Considerations

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/context_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10
CACHE_TTL_SECONDS=21600  # 6 hours

# Message Queue
RABBITMQ_URL=amqp://user:pass@localhost:5672/
QUEUE_NAME=conversation_events
CONSUMER_PREFETCH_COUNT=10

# API
API_HOST=0.0.0.0
API_PORT=30020
API_WORKERS=4
ENVIRONMENT=production
LOG_LEVEL=INFO

# Scoring Formula
BASE_SCORE_MULTIPLIER=0.5
ENGAGEMENT_BONUS_MULTIPLIER=3
MEMORY_BONUS_MULTIPLIER=5
```

### Docker Compose Setup

```yaml
version: '3.8'

services:
  context-service:
    build: .
    ports:
      - "30020:30020"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - RABBITMQ_URL=${RABBITMQ_URL}
    depends_on:
      - postgres
      - redis
      - rabbitmq
      
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=context_db
      - POSTGRES_USER=context_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
      
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      - RABBITMQ_DEFAULT_USER=context_user
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
    ports:
      - "15672:15672"  # Management UI
```

### Monitoring and Observability

**Metrics to Track:**
- API response times (p50, p95, p99)
- Cache hit rate (target: > 80%)
- Message queue lag
- Database query performance
- Error rates by endpoint
- PHRASE3_PHASE3_PHASE3_FRIENDship level distribution
- Agent selection distribution

**Logging Strategy:**
- Structured JSON logging in production
- Log levels: DEBUG (dev), INFO (staging), WARNING (prod)
- Include request_id in all logs for tracing
- Log all PHRASE3_PHASE3_PHASE3_FRIENDship level transitions
- Log all cache invalidations

**Alerting:**
- Alert if cache hit rate < 70%
- Alert if API p95 latency > 500ms
- Alert if message queue lag > 1000 messages
- Alert if error rate > 1%
- Alert if database connection pool exhausted

## Security Considerations

- **Input Validation**: Validate all user inputs using Pydantic schemas
- **SQL Injection Prevention**: Use SQLAlchemy ORM with parameterized queries
- **Rate Limiting**: Implement rate limiting on public endpoints
- **Authentication**: Require API keys for inter-service communication
- **Data Privacy**: Do not log sensitive user data (PII)
- **CORS**: Configure CORS for allowed origins only
- **HTTPS**: Enforce HTTPS in production
- **Secrets Management**: Use environment variables, never hardcode secrets

## Future Enhancements

1. **Machine Learning Integration**: Use ML models to predict optimal agent selection
2. **A/B Testing Framework**: Test different selection algorithms
3. **Real-time Analytics Dashboard**: Visualize PHRASE3_PHASE3_PHASE3_FRIENDship metrics and trends
4. **Multi-language Support**: Internationalize agent descriptions
5. **Advanced Caching**: Implement cache warming strategies
6. **GraphQL API**: Provide GraphQL interface for flexible queries
7. **Webhook Support**: Allow external systems to subscribe to PHRASE3_PHASE3_PHASE3_FRIENDship events
8. **Batch Processing**: Optimize bulk candidate recomputation
