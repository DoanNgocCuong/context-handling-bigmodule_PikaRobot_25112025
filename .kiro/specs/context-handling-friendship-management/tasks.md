# Implementation Plan

- [ ] 1. Set up project structure and core configuration
  - Create FastAPI application structure following SOLID principles with app/core, app/models, app/schemas, app/repositories, app/services, app/api directories
  - Configure environment variables in .env.example for DATABASE_URL, REDIS_URL, RABBITMQ_URL, API settings
  - Set up logging configuration with structured JSON logging for production
  - Create core/config.py with Pydantic Settings for environment management
  - Create core/constants.py with PHRASE3_PHASE3_PHASE3_FRIENDshipLevel and AgentType enums and score thresholds
  - Create core/exceptions.py with custom exception classes
  - _Requirements: 1.1, 1.2, 14.1, 14.5_

- [ ] 2. Implement database models and migrations
  - [ ] 2.1 Create SQLAlchemy base model with created_at and updated_at timestamps
    - Write app/models/base.py with BaseModel class
    - _Requirements: 1.1_
  
  - [ ] 2.2 Create PHRASE3_PHASE3_PHASE3_FRIENDshipStatus model
    - Write app/models/PHRASE3_PHASE3_PHASE3_FRIENDship.py with user_id, PHRASE3_PHASE3_PHASE3_FRIENDship_score, PHRASE3_PHASE3_PHASE3_FRIENDship_level, last_interaction_date, streak_day, topic_metrics (JSONB) columns
    - Add CHECK constraints for PHRASE3_PHASE3_PHASE3_FRIENDship_score >= 0 and valid PHRASE3_PHASE3_PHASE3_FRIENDship_level values
    - _Requirements: 1.1, 1.3_
  
  - [ ] 2.3 Create PHRASE3_PHASE3_PHASE3_FRIENDshipAgentMapping model
    - Write app/models/agent.py with id, PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active columns
    - Add CHECK constraints for valid enum values and weight > 0
    - Add unique constraint on (PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, agent_id)
    - _Requirements: 1.2, 1.4_
  
  - [ ] 2.4 Set up Alembic migrations
    - Initialize Alembic with alembic init migrations
    - Create migration 001_create_PHRASE3_PHASE3_PHASE3_FRIENDship_status_table.py with indexes on PHRASE3_PHASE3_PHASE3_FRIENDship_level and last_interaction_date
    - Create migration 002_create_PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping_table.py with indexes on PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, is_active
    - Test upgrade and downgrade commands
    - _Requirements: 1.5_

- [ ] 3. Create Pydantic schemas for request/response validation
  - Write app/schemas/common.py with base schemas and error response models
  - Write app/schemas/PHRASE3_PHASE3_PHASE3_FRIENDship.py with PHRASE3_PHASE3_PHASE3_FRIENDshipStatusRequest, PHRASE3_PHASE3_PHASE3_FRIENDshipStatusResponse, TopicMetric schemas
  - Write app/schemas/agent.py with AgentDetail, ActivitySuggestionRequest, ActivitySuggestionResponse schemas
  - Write app/schemas/conversation.py with ConversationEndRequest, ConversationEndResponse schemas
  - Add field validators for user_id minimum length of 3 characters
  - _Requirements: 2.1, 2.3, 6.1, 7.1, 8.1, 14.4_

- [ ] 4. Implement database connection and repository layer
  - [ ] 4.1 Set up database connection
    - Write app/db/database.py with SQLAlchemy engine, SessionLocal, and connection pooling
    - Configure connection pool size and max overflow from environment variables
    - _Requirements: 1.1, 15.1_
  
  - [ ] 4.2 Create base repository pattern
    - Write app/db/base_repository.py with generic CRUD operations
    - _Requirements: 1.1_
  
  - [ ] 4.3 Implement PHRASE3_PHASE3_PHASE3_FRIENDshipRepository
    - Write app/repositories/PHRASE3_PHASE3_PHASE3_FRIENDship_repository.py with get_by_user_id, create_or_update, update_score, update_topic_metrics methods
    - Implement JSONB merge logic for topic_metrics updates
    - _Requirements: 6.2, 6.7, 7.2_
  
  - [ ] 4.4 Implement AgentRepository
    - Write app/repositories/agent_repository.py with get_by_level_and_type, get_all_active, soft_delete, bulk_create methods
    - Implement filtering by PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, and is_active status
    - _Requirements: 8.5, 13.1, 13.4_

- [ ] 5. Implement Redis cache manager
  - Write app/utils/cache.py with CacheManager class
  - Implement get_candidates method with key format "candidates:{user_id}"
  - Implement set_candidates method with 6-hour TTL (21600 seconds)
  - Implement invalidate_candidates method for cache invalidation
  - Implement get_cache_stats method for monitoring cache hit/miss rates
  - Add logging for cache hits and misses
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 6. Implement PHRASE3_PHASE3_PHASE3_FRIENDship scoring service
  - [ ] 6.1 Create score calculation algorithm
    - Write app/services/PHRASE3_PHASE3_PHASE3_FRIENDship_service.py with calculate_score_change method
    - Implement base_score = total_turns * 0.5
    - Implement engagement_bonus = user_initiated_questions * 3
    - Implement emotion_bonus mapping (interesting: +15, boring: -15, happy: +10, sad: -5, neutral: 0)
    - Implement memory_bonus = new_memories_count * 5
    - Return sum with minimum value of 0
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ] 6.2 Create topic metrics calculation
    - Implement calculate_topic_metrics_update method
    - Calculate score_change as (total_turns * 0.5) + (user_questions * 3)
    - Calculate turns_increment as total_turns
    - Set last_date to current timestamp in ISO 8601 format
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [ ] 6.3 Implement PHRASE3_PHASE3_PHASE3_FRIENDship status update logic
    - Implement update_PHRASE3_PHASE3_PHASE3_FRIENDship_status method
    - Increment PHRASE3_PHASE3_PHASE3_FRIENDship_score by score_change
    - Update PHRASE3_PHASE3_PHASE3_FRIENDship_level based on thresholds (PHASE1_PHASE1_STRANGER: 0-100, PHASE2_PHASE2_ACQUAINTANCE: 100-500, PHRASE3_PHASE3_PHASE3_FRIEND: 500+)
    - Merge topic_metrics_update into existing JSONB field
    - _Requirements: 6.2, 6.3, 6.7_
  
  - [ ] 6.4 Implement streak day logic
    - Implement update_streak_day method
    - Maintain streak_day if same calendar day as last_interaction_date
    - Increment streak_day by 1 if consecutive calendar day
    - Reset streak_day to 1 if gap > 1 day
    - _Requirements: 6.4, 6.5, 6.6_

- [ ] 7. Implement agent selection service
  - [ ] 7.1 Create greeting agent selection
    - Write app/services/selection_service.py with select_greeting_agent method
    - Implement priority logic: birthday > returning user > emotion-based > memory recall > weighted random
    - Filter by PHRASE3_PHASE3_PHASE3_FRIENDship_level and is_active = true
    - Include reason field in response
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ] 7.2 Create talk agent selection
    - Implement select_talk_agents method
    - Calculate selection_score = (topic_score * 0.7) + ((100 - total_turns) * 0.3)
    - Sort by selection_score descending and select top 2
    - Ensure at least one exploration candidate (low total_turns)
    - Include topic_score, total_turns, and reason in response
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 7.3 Create game agent selection
    - Implement select_game_agents method
    - Use weighted random selection based on weight field
    - Ensure no duplicate agents
    - Filter by PHRASE3_PHASE3_PHASE3_FRIENDship_level and is_active = true
    - Include reason field in response
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ] 7.4 Implement weighted random selection utility
    - Implement weighted_random_choice method using random.choices with weights
    - Handle equal weights with uniform random selection
    - _Requirements: 9.2, 11.1_
  
  - [ ] 7.5 Create candidate computation and caching
    - Implement compute_candidates method that calls select_greeting_agent, select_talk_agents, select_game_agents
    - Integrate with CacheManager to cache results with 6-hour TTL
    - Invalidate cache when PHRASE3_PHASE3_PHASE3_FRIENDship_level changes
    - _Requirements: 8.2, 8.3, 12.2, 12.3_

- [ ] 8. Implement message queue integration
  - [ ] 8.1 Set up RabbitMQ/Kafka connection
    - Write app/utils/queue.py with connection configuration
    - Configure queue name and consumer prefetch count from environment
    - _Requirements: 2.2_
  
  - [ ] 8.2 Create event producer
    - Implement EventProducer class with publish_conversation_end method
    - Generate processing_id for tracking
    - Publish event with user_id, conversation_id, and metadata
    - _Requirements: 2.2, 2.3_
  
  - [ ] 8.3 Create event consumer (AI Scoring Service)
    - Implement ConversationEndConsumer class with consume_conversation_end_events method
    - Implement process_conversation_end async method
    - Add retry logic with exponential backoff (max 3 attempts)
    - _Requirements: 2.5_

- [ ] 9. Implement API endpoints
  - [ ] 9.1 Create dependency injection
    - Write app/api/deps.py with get_db dependency for database sessions
    - Add get_cache_manager dependency for Redis cache
    - _Requirements: 1.1_
  
  - [ ] 9.2 Implement conversation end endpoint
    - Write app/api/v1/endpoints/conversations.py with POST /conversations/end
    - Validate request body with ConversationEndRequest schema
    - Enqueue event to message queue
    - Return 202 Accepted response within 100ms with processing_id
    - Handle queue unavailable error with 503 and retry-after header
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ] 9.3 Implement PHRASE3_PHASE3_PHASE3_FRIENDship status endpoint
    - Write app/api/v1/endpoints/PHRASE3_PHASE3_PHASE3_FRIENDship.py with POST /PHRASE3_PHASE3_PHASE3_FRIENDship/status
    - Validate user_id with minimum length 3 characters
    - Query PHRASE3_PHASE3_PHASE3_FRIENDshipRepository for user data
    - Return 404 if user not found
    - Return PHRASE3_PHASE3_PHASE3_FRIENDship_score, PHRASE3_PHASE3_PHASE3_FRIENDship_level, last_interaction_date, streak_day, total_turns, topic_metrics
    - Ensure response time < 200ms using database indexes
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 14.4_
  
  - [ ] 9.4 Implement PHRASE3_PHASE3_PHASE3_FRIENDship update endpoint (AI Service only)
    - Add POST /PHRASE3_PHASE3_PHASE3_FRIENDship/update endpoint in app/api/v1/endpoints/PHRASE3_PHASE3_PHASE3_FRIENDship.py
    - Accept user_id, PHRASE3_PHASE3_PHASE3_FRIENDship_score_change, topic_metrics_update
    - Call PHRASE3_PHASE3_PHASE3_FRIENDshipService.update_PHRASE3_PHASE3_PHASE3_FRIENDship_status
    - Invalidate cache if PHRASE3_PHASE3_PHASE3_FRIENDship_level changed
    - _Requirements: 6.1, 6.2, 6.3, 12.3_
  
  - [ ] 9.5 Implement activity suggestion endpoint
    - Write app/api/v1/endpoints/activities.py with POST /activities/suggest
    - Check Redis cache for pre-computed candidates
    - Return cached results within 100ms if cache hit
    - Compute candidates on-demand if cache miss and cache with 6-hour TTL
    - Return 1 greeting_agent, 2 talk_agents, 2 game_agents
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 12.4, 12.5_
  
  - [ ] 9.6 Implement agent mapping CRUD endpoints
    - Add GET /agent-mappings with query filters for PHRASE3_PHASE3_PHASE3_FRIENDship_level and agent_type
    - Add POST /agent-mappings for creating new mappings
    - Add PUT /agent-mappings/{id} for updating mappings
    - Add DELETE /agent-mappings/{id} for soft delete (set is_active = false)
    - Validate weight > 0 and valid enum values
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ] 9.7 Implement health check endpoint
    - Write app/api/v1/endpoints/health.py with GET /health
    - Check database connection status
    - Check Redis connection status
    - Check message queue connection status
    - Return 200 OK if all healthy, 503 if any component unhealthy
    - Respond within 5 seconds
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ] 9.8 Create API router and main application
    - Write app/api/v1/router.py to combine all endpoint routers
    - Write app/main.py with FastAPI application initialization
    - Configure CORS, middleware, and exception handlers
    - _Requirements: 1.1_

- [ ] 10. Implement error handling and logging
  - Create app/core/error_handlers.py with exception handlers for custom exceptions
  - Implement ErrorResponse schema with error, message, details, timestamp, request_id fields
  - Add request_id middleware for tracing
  - Configure logging to include request_id, user_id, endpoint, error message
  - Log all PHRASE3_PHASE3_PHASE3_FRIENDship level transitions
  - Log all cache invalidations
  - Return 400 for invalid input, 404 for not found, 500 for internal errors, 503 for service unavailable, 504 for timeout
  - _Requirements: 14.1, 14.2, 14.3, 14.5_

- [ ] 11. Create seed data script
  - Write scripts/seed_agents.py to populate PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping table
  - Add 5-10 agents for PHASE1_PHASE1_STRANGER level (2-3 Greeting, 3-5 Talk, 2-3 Game)
  - Add 8-12 agents for PHASE2_PHASE2_ACQUAINTANCE level (2-3 Greeting, 4-6 Talk, 2-3 Game)
  - Add 10-15 agents for PHRASE3_PHASE3_PHASE3_FRIEND level (3-4 Greeting, 5-8 Talk, 2-3 Game)
  - Set appropriate weights (1.0-2.0) for each agent
  - _Requirements: 1.2_

- [ ] 12. Create Docker and deployment configuration
  - Write Dockerfile with Python 3.11, FastAPI, and dependencies
  - Write docker-compose.yml with services for context-service, postgres, redis, rabbitmq
  - Configure environment variables for all services
  - Set up PostgreSQL with persistent volume
  - Set up Redis with maxmemory 2gb and allkeys-lru eviction policy
  - Set up RabbitMQ with management UI
  - _Requirements: 1.1, 15.1_

- [ ] 13. Write documentation
  - Create README.md with project overview, setup instructions, API documentation
  - Document environment variables in .env.example
  - Create API documentation using FastAPI's automatic OpenAPI generation
  - Document deployment process
  - _Requirements: 1.1_

- [ ]* 14. Write unit tests for core logic
  - Write tests/unit/test_PHRASE3_PHASE3_PHASE3_FRIENDship_service.py for score calculation, topic metrics, streak day logic
  - Write tests/unit/test_selection_service.py for greeting, talk, game agent selection
  - Write tests/unit/test_cache_manager.py for cache operations, invalidation, TTL
  - Write tests/unit/test_repositories.py for CRUD operations, JSONB updates
  - Achieve 80%+ code coverage
  - _Requirements: 4.1-4.5, 5.1-5.3, 6.2-6.6, 9.1-9.5, 10.1-10.5, 11.1-11.5, 12.1-12.5_

- [ ]* 15. Write integration tests for API endpoints
  - Write tests/integration/test_conversation_flow.py for full async conversation end flow
  - Write tests/integration/test_PHRASE3_PHASE3_PHASE3_FRIENDship_api.py for status retrieval and update
  - Write tests/integration/test_activity_api.py for cache hit and miss scenarios
  - Write tests/integration/test_agent_mapping_api.py for CRUD operations
  - Write tests/integration/test_database.py for PHRASE3_PHASE3_PHASE3_FRIENDship level transitions, JSONB merge, concurrent updates
  - _Requirements: 2.1-2.5, 6.1-6.7, 7.1-7.5, 8.1-8.5, 13.1-13.5_

- [ ]* 16. Perform load and performance testing
  - Use Locust or similar tool to test 1000 requests/second for /activities/suggest
  - Verify < 100ms response time for cached requests
  - Verify < 500ms response time for cache miss
  - Test message queue backlog handling
  - Test database connection pool under load
  - Test Redis memory limits
  - _Requirements: 8.2, 8.3_
