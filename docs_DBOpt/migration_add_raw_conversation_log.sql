-- Migration: Add raw_conversation_log column to conversation_events table
-- Date: 2025-11-26
-- Description: Add column to store raw conversation logs in original API format

ALTER TABLE conversation_events
ADD COLUMN raw_conversation_log JSONB NULL DEFAULT NULL;

-- Add comment for documentation
COMMENT ON COLUMN conversation_events.raw_conversation_log IS 
    'Raw conversation log in original API format (before transformation). '
    'Stored separately from conversation_log which contains standardized format.';

-- Optional: Add GIN index for JSONB queries (if needed for searching raw logs)
-- CREATE INDEX idx_conversation_events_raw_log_gin 
--     ON conversation_events USING GIN (raw_conversation_log);

