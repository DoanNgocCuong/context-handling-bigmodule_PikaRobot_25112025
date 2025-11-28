-- Migration: Add agent_tag column to conversation_events table
-- Date: 2025-11-28
-- Description: Add agent_tag field for topic mapping (replaces bot_id for topic lookup)

-- Add agent_tag column (nullable for backward compatibility)
ALTER TABLE conversation_events
ADD COLUMN agent_tag VARCHAR(255) NULL;

-- Add comment
COMMENT ON COLUMN conversation_events.agent_tag IS 'Agent tag for topic mapping. Used instead of bot_id to query topic_id from agenda_agent_prompting table. Falls back to bot_id if not provided.';

-- Optional: Add index if needed for queries
-- CREATE INDEX idx_conversation_events_agent_tag ON conversation_events(agent_tag);

