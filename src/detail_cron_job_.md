# Conversation Event Cron Job

## Overview
The context-handling service persists every conversation termination in the `conversation_events` table.  
An APScheduler-based cron job (`ConversationEventProcessingService`) periodically scans for events that are ready to be processed (status `PENDING`/`FAILED` and `next_attempt_at <= now`) and executes the friendship-score workflow.

```
conversation_events (JSONB log, status tracking)
        │
APScheduler job (every 10s) ──> ConversationEventProcessingService
        │                              │
        │                              ├─ calculate score (FriendshipScoreCalculationService)
        │                              └─ update friendship status (FriendshipStatusUpdateService)
```

## Trigger & Scheduling
- Scheduler defined in `app/background/conversation_event_scheduler.py`.
- Uses `AsyncIOScheduler` with `IntervalTrigger(seconds=10)`.
- Job ID: `conversation_event_processor`.
- `CONVERSATION_EVENT_RETRY_HOURS` = `0`, so failed events are immediately eligible for the next cycle.
- Max simultaneous executions = 1 to avoid concurrent processing of the same rows.

## Processing Steps
1. `_run_conversation_event_job()` opens a DB session and resolves the services.
2. `ConversationEventProcessingService.process_due_events()`:
   - `fetch_due_events(batch_size=20)` loads a small batch ordered by `next_attempt_at`.
   - For each record:
     - Logs `Processing conversation event conversation_id=… attempt=…`.
     - Marks status ➜ `PROCESSING`, increments `attempt_count`.
     - Computes friendship score, updates friendship status.
     - On success: marks `PROCESSED`, stores score result, stamps `processed_at`.
     - On failure: marks `FAILED`, sets `error_code`, `error_details`, and recalculates `next_attempt_at`.
3. Final job log summarizes processed/failed counts.

## Database Impact
- Every 10 seconds the job issues **one SELECT** with `LIMIT 20` and indexed filters (`status`, `next_attempt_at`).  
  If no rows are returned, SQLAlchemy simply rolls back the idle transaction; this is expected and inexpensive.
- Because the query is bounded and only reads two small columns for filtering, the load is minimal for current traffic.  
  If future volume grows, we can:
  - Increase interval (e.g., 30s/60s) or use dynamic backoff.
  - Maintain a covering index (`status`, `next_attempt_at`) to keep scans fast.
  - Shard workload by running the job in a dedicated worker scaled via locks.

## Configuration & Overrides
| Setting | Location | Purpose |
| --- | --- | --- |
| `CONVERSATION_EVENT_RETRY_HOURS` | `app/core/constants_enums.py` | Delay before retry after failure (currently `0`) |
| Job interval | `conversation_event_scheduler.py` | `IntervalTrigger(seconds=10)` controls polling cadence |
| Batch size | `process_due_events(batch_size=20)` | Max events handled per iteration |

To change behaviour:
1. Update the constant/interval value.
2. Restart the FastAPI service (scheduler starts inside `app.main_app`).

## Operational Notes
- If you see repeated SELECT + ROLLBACK lines, it simply means no event met the criteria; not an error.
- When new events arrive, `next_attempt_at` is set immediately (0 delay), so they are picked up in the next cycle.
- Keep APScheduler running in the main app process; shutting down the FastAPI instance stops the cron job.

