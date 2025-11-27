
--- friendship_status

CREATE TABLE friendship_status (
    user_id VARCHAR(255) PRIMARY KEY,
    friendship_score FLOAT DEFAULT 0.0 NOT NULL,
    friendship_level VARCHAR(50) DEFAULT 'PHASE1_STRANGER' NOT NULL,
    -- PHASE1_STRANGER (0-99), PHASE2_ACQUAINTANCE (100-499), PHASE3_FRIEND (500+)
    last_interaction_date TIMESTAMP WITH TIME ZONE,
    streak_day INTEGER DEFAULT 0 NOT NULL,
    topic_metrics JSONB DEFAULT '{}' NOT NULL,
    -- {
    --   "agent_movie": { "score": 52.0, "turns": 65, "last_date": "..." },
    --   "agent_animal": { "score": 28.5, "turns": 32, "last_date": "..." }
    -- }
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_friendship_score ON friendship_status(friendship_score);
CREATE INDEX idx_friendship_level ON friendship_status(friendship_level);
CREATE INDEX idx_updated_at ON friendship_status(updated_at DESC);




--- friendship_agent_mapping
CREATE TABLE friendship_agent_mapping (
    id SERIAL PRIMARY KEY,
    friendship_level VARCHAR(50) NOT NULL,
    -- PHASE1_STRANGER, PHASE2_ACQUAINTANCE, PHASE3_FRIEND

    agent_type VARCHAR(50) NOT NULL,
    -- GREETING, TALK, GAME_ACTIVITY

    topic VARCHAR(100),
    -- Chủ đề gắn với agent: ví dụ 'pets', 'school', 'movie'

    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_description TEXT,

    weight FLOAT DEFAULT 1.0,
    -- Trọng số ưu tiên (cao hơn = được chọn nhiều hơn)

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (friendship_level, agent_type, agent_id)
);

CREATE INDEX idx_mapping_level_type
ON friendship_agent_mapping(friendship_level, agent_type);

CREATE INDEX idx_mapping_active
ON friendship_agent_mapping(is_active);

CREATE INDEX idx_mapping_topic
ON friendship_agent_mapping(topic);



--- agent_prompting table

CREATE TABLE agent_prompting (
    id SERIAL PRIMARY KEY,

    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,

    goal TEXT NOT NULL,
    -- Mục tiêu sư phạm / hành vi của agent

    prompt_template TEXT NOT NULL,
    -- Prompt "thô" có placeholder, ví dụ: {{user_name}}, {{topic}}

    final_prompt TEXT,
    -- Prompt đã compile / cache sẵn (optional, có thể null)

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (agent_id)
);

CREATE INDEX idx_agent_prompting_agent_id
ON agent_prompting(agent_id);



--- conversation_events table
CREATE TABLE conversation_events (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Identifiers
    conversation_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    
    -- Bot Information
    bot_type VARCHAR(50) NOT NULL,
    bot_id VARCHAR(255) NOT NULL,
    bot_name VARCHAR(255) NOT NULL,
    
    -- Conversation Timing
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_seconds INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (end_time - start_time))::INTEGER
    ) STORED,
    
    -- Conversation Data
    conversation_log JSONB NOT NULL DEFAULT '[]',
    
    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED')),
    attempt_count INTEGER NOT NULL DEFAULT 0,
    
    -- Timing for processing
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    next_attempt_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP + INTERVAL '6 hours',
    processed_at TIMESTAMP,
    
    -- Error tracking (only when FAILED)
    error_code VARCHAR(50),
    error_details TEXT,
    
    -- Processing results
    friendship_score_change FLOAT,
    new_friendship_level VARCHAR(50),
    
    -- Timestamps
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX idx_conversation_events_status ON conversation_events(status);
CREATE INDEX idx_conversation_events_next_attempt ON conversation_events(next_attempt_at);
CREATE INDEX idx_conversation_events_user_id ON conversation_events(user_id);
CREATE INDEX idx_conversation_events_created_at ON conversation_events(created_at);
CREATE INDEX idx_conversation_events_bot_type ON conversation_events(bot_type);
CREATE INDEX idx_conversation_events_bot_id ON conversation_events(bot_id);

-- Composite index for common queries
CREATE INDEX idx_conversation_events_status_next_attempt 
    ON conversation_events(status, next_attempt_at);

-- GIN index for JSONB queries
CREATE INDEX idx_conversation_events_log_gin 
    ON conversation_events USING GIN (conversation_log);
