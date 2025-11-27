# Requirements Document

## Introduction

This document specifies the requirements for the Context Handling - PHRASE3_PHASE3_PHASE3_FRIENDship Management module for the Pika Robot system. The module manages PHRASE3_PHASE3_PHASE3_FRIENDship status between users and the Pika AI companion, tracks interaction metrics, and provides personalized activity recommendations (Greeting, Talk, and Game agents) based on the evolving relationship.

## Glossary

- **Context Handling Service**: The backend service responsible for managing PHRASE3_PHASE3_PHASE3_FRIENDship status, interaction metrics, and activity selection logic
- **PHRASE3_PHASE3_PHASE3_FRIENDship Status**: A data structure tracking the relationship state between a user and Pika, including score, level, streak, and topic metrics
- **PHRASE3_PHASE3_PHASE3_FRIENDship Score**: A numerical value (0+) representing the strength of the relationship
- **PHRASE3_PHASE3_PHASE3_FRIENDship Level**: A categorical classification (PHASE1_STRANGER, PHASE2_ACQUAINTANCE, PHRASE3_PHASE3_PHASE3_FRIEND) based on PHRASE3_PHASE3_PHASE3_FRIENDship score thresholds
- **Agent**: A conversational AI component that handles specific interaction types (Greeting, Talk, Game)
- **Topic Metrics**: JSONB data tracking user engagement with different conversation topics
- **Streak Day**: Consecutive days of user interaction with Pika
- **Conversation Log**: A record of turn-by-turn dialogue between user and Pika
- **Backend Service**: The main application backend that interfaces with the Context Handling Service
- **AI Scoring Service**: The component that analyzes conversations and calculates PHRASE3_PHASE3_PHASE3_FRIENDship score changes
- **Message Queue**: An asynchronous messaging system (RabbitMQ/Kafka) for event-driven processing

## Requirements

### Requirement 1: Database Schema Management

**User Story:** As a system administrator, I want a well-structured database schema for PHRASE3_PHASE3_PHASE3_FRIENDship data, so that the system can efficiently store and query user relationship information.

#### Acceptance Criteria

1. WHEN the system initializes, THE Context Handling Service SHALL create a PHRASE3_PHASE3_PHASE3_FRIENDship_status table with columns for user_id (primary key), PHRASE3_PHASE3_PHASE3_FRIENDship_score (float, default 0.0), PHRASE3_PHASE3_PHASE3_FRIENDship_level (enum: PHASE1_STRANGER/PHASE2_ACQUAINTANCE/PHRASE3_PHASE3_PHASE3_FRIEND), last_interaction_date (timestamp), streak_day (integer, default 0), topic_metrics (JSONB), created_at (timestamp), and updated_at (timestamp)

2. WHEN the system initializes, THE Context Handling Service SHALL create a PHRASE3_PHASE3_PHASE3_FRIENDship_agent_mapping table with columns for id (primary key), PHRASE3_PHASE3_PHASE3_FRIENDship_level (enum), agent_type (enum: GREETING/TALK/GAME), agent_id (string), agent_name (string), agent_description (text), weight (float, default 1.0), is_active (boolean, default true), created_at (timestamp), and updated_at (timestamp)

3. WHEN querying PHRASE3_PHASE3_PHASE3_FRIENDship data, THE Context Handling Service SHALL utilize indexes on PHRASE3_PHASE3_PHASE3_FRIENDship_level and last_interaction_date columns to optimize query performance

4. WHEN inserting agent mappings, THE Context Handling Service SHALL enforce a unique constraint on the combination of PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, and agent_id

5. WHEN managing database schema changes, THE Context Handling Service SHALL use Alembic migration files to version control all schema modifications

### Requirement 2: Conversation End Event Processing

**User Story:** As a backend developer, I want to notify the system when a conversation ends, so that PHRASE3_PHASE3_PHASE3_FRIENDship metrics can be updated asynchronously without blocking the user experience.

#### Acceptance Criteria

1. WHEN a conversation ends, THE Backend Service SHALL send a POST request to the /conversations/end endpoint with user_id and conversation_id

2. WHEN receiving a conversation end notification, THE Context Handling Service SHALL enqueue the event to a message queue and return a 202 Accepted response within 100 milliseconds

3. WHEN the conversation end event is queued, THE Context Handling Service SHALL include a processing_id in the response for tracking purposes

4. IF the message queue is unavailable, THEN THE Context Handling Service SHALL return a 503 Service Unavailable error with retry-after header

5. WHEN processing fails, THE Context Handling Service SHALL implement exponential backoff retry logic with a maximum of 3 retry attempts

### Requirement 3: Conversation Data Retrieval

**User Story:** As an AI scoring service, I want to retrieve complete conversation data by conversation_id, so that I can analyze the interaction and calculate PHRASE3_PHASE3_PHASE3_FRIENDship score changes.

#### Acceptance Criteria

1. WHEN the AI Scoring Service requests conversation data, THE Backend Service SHALL provide a GET /conversations/{conversation_id} endpoint that returns the complete conversation log, metadata, and timing information

2. WHEN a valid conversation_id is provided, THE Backend Service SHALL return conversation data including conversation_log array, user_id, agent_id, agent_type, start_time, end_time, duration_seconds, and metadata object

3. WHEN an invalid conversation_id is provided, THE Backend Service SHALL return a 404 Not Found error with a descriptive message

4. WHEN retrieving conversation data, THE Backend Service SHALL include metadata fields for emotion, user_initiated_questions, pika_initiated_topics, and new_memories_created

5. WHEN the conversation data request times out after 30 seconds, THE Backend Service SHALL return a 504 Gateway Timeout error

### Requirement 4: PHRASE3_PHASE3_PHASE3_FRIENDship Score Calculation

**User Story:** As an AI scoring service, I want to calculate PHRASE3_PHASE3_PHASE3_FRIENDship score changes based on conversation quality, so that the system accurately reflects the relationship strength.

#### Acceptance Criteria

1. WHEN calculating PHRASE3_PHASE3_PHASE3_FRIENDship score change, THE AI Scoring Service SHALL compute base_score as total_turns multiplied by 0.5

2. WHEN calculating PHRASE3_PHASE3_PHASE3_FRIENDship score change, THE AI Scoring Service SHALL compute engagement_bonus as user_initiated_questions multiplied by 3

3. WHEN calculating PHRASE3_PHASE3_PHASE3_FRIENDship score change, THE AI Scoring Service SHALL apply emotion_bonus of +15 for interesting emotion, -15 for boring emotion, +10 for happy emotion, -5 for sad emotion, and 0 for neutral emotion

4. WHEN calculating PHRASE3_PHASE3_PHASE3_FRIENDship score change, THE AI Scoring Service SHALL compute memory_bonus as new_memories_count multiplied by 5

5. WHEN calculating PHRASE3_PHASE3_PHASE3_FRIENDship score change, THE AI Scoring Service SHALL return the sum of base_score, engagement_bonus, emotion_bonus, and memory_bonus, with a minimum value of 0

### Requirement 5: Topic Metrics Update

**User Story:** As an AI scoring service, I want to update topic-specific engagement metrics, so that the system can recommend relevant conversation topics.

#### Acceptance Criteria

1. WHEN updating topic metrics for an agent, THE AI Scoring Service SHALL calculate score_change as (total_turns multiplied by 0.5) plus (user_questions multiplied by 3)

2. WHEN updating topic metrics, THE AI Scoring Service SHALL increment the total_turns counter by the number of turns in the current conversation

3. WHEN updating topic metrics, THE AI Scoring Service SHALL set last_date to the current timestamp in ISO 8601 format

4. WHEN a conversation involves multiple topics, THE AI Scoring Service SHALL update metrics for each relevant topic independently

5. WHEN topic metrics do not exist for an agent, THE AI Scoring Service SHALL initialize a new topic entry with score, total_turns, and last_date fields

### Requirement 6: PHRASE3_PHASE3_PHASE3_FRIENDship Status Update

**User Story:** As a backend developer, I want to update user PHRASE3_PHASE3_PHASE3_FRIENDship status after conversation analysis, so that the relationship state reflects recent interactions.

#### Acceptance Criteria

1. WHEN updating PHRASE3_PHASE3_PHASE3_FRIENDship status, THE Context Handling Service SHALL provide a POST /PHRASE3_PHASE3_PHASE3_FRIENDship/update endpoint that accepts user_id, PHRASE3_PHASE3_PHASE3_FRIENDship_score_change, and topic_metrics_update

2. WHEN PHRASE3_PHASE3_PHASE3_FRIENDship_score_change is applied, THE Context Handling Service SHALL increment the existing PHRASE3_PHASE3_PHASE3_FRIENDship_score by the change amount

3. WHEN PHRASE3_PHASE3_PHASE3_FRIENDship_score crosses a threshold, THE Context Handling Service SHALL update PHRASE3_PHASE3_PHASE3_FRIENDship_level to PHASE1_STRANGER (0-100), PHASE2_ACQUAINTANCE (100-500), or PHRASE3_PHASE3_PHASE3_FRIEND (500+)

4. WHEN updating on the same calendar day as last_interaction_date, THE Context Handling Service SHALL maintain the current streak_day value

5. WHEN updating on a consecutive calendar day after last_interaction_date, THE Context Handling Service SHALL increment streak_day by 1

6. WHEN updating after a gap of more than 1 day, THE Context Handling Service SHALL reset streak_day to 1

7. WHEN topic_metrics_update is provided, THE Context Handling Service SHALL merge the updates into the existing topic_metrics JSONB field

### Requirement 7: PHRASE3_PHASE3_PHASE3_FRIENDship Status Retrieval

**User Story:** As a backend developer, I want to retrieve current PHRASE3_PHASE3_PHASE3_FRIENDship status for a user, so that I can display relationship information in the application.

#### Acceptance Criteria

1. WHEN requesting PHRASE3_PHASE3_PHASE3_FRIENDship status, THE Backend Service SHALL call POST /PHRASE3_PHASE3_PHASE3_FRIENDship/status endpoint with user_id

2. WHEN a valid user_id is provided, THE Context Handling Service SHALL return PHRASE3_PHASE3_PHASE3_FRIENDship_score, PHRASE3_PHASE3_PHASE3_FRIENDship_level, last_interaction_date, streak_day, total_turns, and topic_metrics

3. WHEN an invalid user_id is provided, THE Context Handling Service SHALL return a 404 Not Found error

4. WHEN retrieving PHRASE3_PHASE3_PHASE3_FRIENDship status, THE Context Handling Service SHALL respond within 200 milliseconds by utilizing database indexes

5. WHEN topic_metrics contains data, THE Context Handling Service SHALL include score, total_turns, and last_date for each topic in the response

### Requirement 8: Activity Suggestion with Pre-computed Candidates

**User Story:** As a backend developer, I want to retrieve pre-computed activity suggestions for a user, so that I can present personalized content without waiting for real-time computation.

#### Acceptance Criteria

1. WHEN requesting activity suggestions, THE Backend Service SHALL call POST /activities/suggest endpoint with user_id

2. WHEN pre-computed candidates exist in cache, THE Context Handling Service SHALL return the cached results within 100 milliseconds

3. WHEN pre-computed candidates do not exist, THE Context Handling Service SHALL compute candidates on-demand and cache the results with a 6-hour TTL

4. WHEN returning activity suggestions, THE Context Handling Service SHALL include exactly 1 greeting_agent, 2 talk_agents, and 2 game_agents

5. WHEN selecting agents, THE Context Handling Service SHALL filter candidates by the user's current PHRASE3_PHASE3_PHASE3_FRIENDship_level and agent is_active status

### Requirement 9: Greeting Agent Selection Logic

**User Story:** As an AI orchestration service, I want to select the most appropriate greeting agent, so that users receive contextually relevant greetings.

#### Acceptance Criteria

1. WHEN selecting a greeting agent, THE Context Handling Service SHALL prioritize birthday greeting IF the current date matches the user's birthday

2. WHEN no special condition applies, THE Context Handling Service SHALL select a greeting agent using weighted random selection based on the weight field

3. WHEN multiple greeting agents have the same weight, THE Context Handling Service SHALL select randomly among them with equal probability

4. WHEN selecting a greeting agent, THE Context Handling Service SHALL only consider agents where PHRASE3_PHASE3_PHASE3_FRIENDship_level matches the user's current level and is_active is true

5. WHEN returning the selected greeting agent, THE Context Handling Service SHALL include a reason field explaining the selection logic

### Requirement 10: Talk Agent Selection Logic

**User Story:** As an AI orchestration service, I want to select talk agents based on user preferences and exploration needs, so that conversations remain engaging and diverse.

#### Acceptance Criteria

1. WHEN selecting talk agents, THE Context Handling Service SHALL prioritize agents with the highest topic_score from the user's topic_metrics

2. WHEN selecting talk agents, THE Context Handling Service SHALL include at least one exploration candidate with low total_turns to encourage topic diversity

3. WHEN calculating agent priority, THE Context Handling Service SHALL compute a selection score as (topic_score multiplied by 0.7) plus ((100 minus total_turns) multiplied by 0.3)

4. WHEN selecting 2 talk agents, THE Context Handling Service SHALL sort candidates by selection score in descending order and select the top 2

5. WHEN returning selected talk agents, THE Context Handling Service SHALL include topic_score, total_turns, and reason fields for each agent

### Requirement 11: Game Agent Selection Logic

**User Story:** As an AI orchestration service, I want to select game agents to boost engagement, so that users have fun interactive experiences.

#### Acceptance Criteria

1. WHEN selecting game agents, THE Context Handling Service SHALL use weighted random selection based on the weight field

2. WHEN selecting 2 game agents, THE Context Handling Service SHALL ensure no duplicate agents are selected

3. WHEN selecting game agents, THE Context Handling Service SHALL only consider agents where PHRASE3_PHASE3_PHASE3_FRIENDship_level matches the user's current level and is_active is true

4. WHEN returning selected game agents, THE Context Handling Service SHALL include a reason field indicating the selection purpose (e.g., "Engagement booster")

5. WHEN insufficient game agents exist for the PHRASE3_PHASE3_PHASE3_FRIENDship_level, THE Context Handling Service SHALL return all available game agents without error

### Requirement 12: Candidate Caching Mechanism

**User Story:** As a system architect, I want to cache pre-computed activity candidates, so that activity suggestions can be served with minimal latency.

#### Acceptance Criteria

1. WHEN caching candidates, THE Context Handling Service SHALL use Redis with a key format of "candidates:{user_id}"

2. WHEN caching candidates, THE Context Handling Service SHALL set a TTL of 6 hours (21600 seconds) by default

3. WHEN PHRASE3_PHASE3_PHASE3_FRIENDship_level changes for a user, THE Context Handling Service SHALL invalidate the cached candidates for that user_id

4. WHEN a cache miss occurs, THE Context Handling Service SHALL log the event and compute candidates on-demand

5. WHEN a cache hit occurs, THE Context Handling Service SHALL log the event and return the cached data without recomputation

### Requirement 13: Agent Mapping Management

**User Story:** As a content manager, I want to manage agent mappings through APIs, so that I can add, update, and configure agents without database access.

#### Acceptance Criteria

1. WHEN listing agent mappings, THE Context Handling Service SHALL provide a GET /agent-mappings endpoint with optional query parameters for PHRASE3_PHASE3_PHASE3_FRIENDship_level and agent_type

2. WHEN creating an agent mapping, THE Context Handling Service SHALL provide a POST /agent-mappings endpoint that accepts PHRASE3_PHASE3_PHASE3_FRIENDship_level, agent_type, agent_id, agent_name, agent_description, and weight

3. WHEN updating an agent mapping, THE Context Handling Service SHALL provide a PUT /agent-mappings/{mapping_id} endpoint that allows modification of agent_name, agent_description, weight, and is_active fields

4. WHEN deleting an agent mapping, THE Context Handling Service SHALL provide a DELETE /agent-mappings/{mapping_id} endpoint that performs a soft delete by setting is_active to false

5. WHEN creating or updating agent mappings, THE Context Handling Service SHALL validate that weight is greater than 0 and PHRASE3_PHASE3_PHASE3_FRIENDship_level and agent_type are valid enum values

### Requirement 14: Error Handling and Validation

**User Story:** As a backend developer, I want comprehensive error handling and input validation, so that the system provides clear feedback and maintains data integrity.

#### Acceptance Criteria

1. WHEN receiving invalid input, THE Context Handling Service SHALL return a 400 Bad Request error with a descriptive message indicating which field is invalid

2. WHEN a requested resource does not exist, THE Context Handling Service SHALL return a 404 Not Found error with the resource type and identifier

3. WHEN an internal error occurs, THE Context Handling Service SHALL return a 500 Internal Server Error and log the full error details for debugging

4. WHEN validating user_id, THE Context Handling Service SHALL require a minimum length of 3 characters

5. WHEN an error occurs, THE Context Handling Service SHALL log the error with timestamp, request_id, user_id (if available), endpoint, and error message

### Requirement 15: Health Check and Monitoring

**User Story:** As a DevOps engineer, I want health check endpoints, so that I can monitor service availability and dependencies.

#### Acceptance Criteria

1. WHEN checking service health, THE Context Handling Service SHALL provide a GET /health endpoint that returns status, timestamp, database connection status, cache connection status, and queue connection status

2. WHEN all dependencies are healthy, THE Context Handling Service SHALL return a 200 OK response with status "ok"

3. WHEN any dependency is unhealthy, THE Context Handling Service SHALL return a 503 Service Unavailable response with status "degraded" and details of the failing component

4. WHEN the health check endpoint is called, THE Context Handling Service SHALL respond within 5 seconds

5. WHEN database connection fails, THE Context Handling Service SHALL report database status as "disconnected" in the health check response
