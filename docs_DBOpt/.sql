
--- friendship_status

CREATE TABLE friendship_status (
    user_id VARCHAR(255) PRIMARY KEY,
    friendship_score FLOAT DEFAULT 0.0 NOT NULL,
    friendship_level VARCHAR(50) DEFAULT 'STRANGER' NOT NULL,
    -- STRANGER (0-99), ACQUAINTANCE (100-499), FRIEND (500+)
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
    -- STRANGER, ACQUAINTANCE, FRIEND
    agent_type VARCHAR(50) NOT NULL,
    -- GREETING, TALK, GAME_ACTIVITY
    agent_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_description TEXT,
    weight FLOAT DEFAULT 1.0,
    -- Trọng số ưu tiên (cao hơn = được chọn nhiều hơn)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(friendship_level, agent_type, agent_id)
);

-- Indexes
CREATE INDEX idx_mapping_level_type ON friendship_agent_mapping(friendship_level, agent_type);
CREATE INDEX idx_mapping_active ON friendship_agent_mapping(is_active);

