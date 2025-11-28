```bash
┌─────────────────────────────────────────────────────────────┐
│ 1. API Endpoint: POST /v1/conversations/end                  │
│    - Nhận request từ Backend                                 │
│    - Validate và lưu vào DB (status=PENDING)                │
│    - Publish message vào RabbitMQ queue                      │
│    - Return 202 Accepted (ngay lập tức, không chờ xử lý)    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. RabbitMQ Queue: conversation_events_processing           │
│    - Queue durable, persistent                              │
│    - TTL: 24 hours                                          │
│    - Max length: 100k messages                               │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Worker (rabbitmq_consumer.py)                            │
│    - Consume messages từ queue                              │
│    - QoS: prefetch_count=1 (xử lý 1 message tại một thời điểm)│
│    - Manual acknowledgment                                  │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Callback Handler (rabbitmq_consumer.py::callback)        │
│    a. Parse JSON message → conversation_id                   │
│    b. Tạo DB session MỚI cho mỗi message                    │
│    c. Lấy event từ DB bằng conversation_id                   │
│    d. Setup services:                                        │
│       - ConversationDataFetchService                        │
│       - FriendshipScoreCalculationService                   │
│       - FriendshipStatusUpdateService                       │
│    e. Gọi ConversationEventProcessingService                 │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Processing (conversation_event_processing_service.py)     │
│    a. Mark status=PROCESSING                                 │
│    b. Fetch conversation data                                │
│    c. Calculate friendship score                             │
│    d. Get topic_id từ agent_tag (hoặc bot_id)               │
│    e. Update topic_metrics (nếu có topic_id)                │
│    f. Update friendship_status                               │
│    g. Mark status=PROCESSED                                   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Acknowledge Message                                       │
│    - Thành công: ch.basic_ack() → Message bị xóa khỏi queue│
│    - Lỗi: ch.basic_nack(requeue=True) → Retry sau          │
│    - LUÔN close DB session trong finally                     │
└─────────────────────────────────────────────────────────────┘
```
