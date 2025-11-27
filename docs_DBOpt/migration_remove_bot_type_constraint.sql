-- Migration: Remove bot_type CHECK constraint from conversation_events table
-- Date: 2025-11-27
-- Description: Remove CHECK constraint to allow any bot_type value (not limited to GREETING, TALK, GAME_ACTIVITY)

-- Drop the existing CHECK constraint
ALTER TABLE conversation_events 
DROP CONSTRAINT IF EXISTS conversation_events_bot_type_check;

-- Verify the constraint has been removed
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'conversation_events'::regclass
AND conname = 'conversation_events_bot_type_check';
-- Expected: No rows returned (constraint removed)

