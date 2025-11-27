# Worker Flow - RabbitMQ Consumer

## 📋 Tổng quan

Worker là một process độc lập chạy liên tục, consume messages từ RabbitMQ queue và xử lý conversation events trong background.

## 🔄 Flow hoàn chỉnh

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Backend gửi POST /v1/conversations/end                      │
│    → API lưu event vào DB (status=PENDING)                     │
│    → Publish message vào RabbitMQ queue                         │
│    → Return 202 Accepted (ngay lập tức)                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. RabbitMQ Queue                                               │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐                          │
│    │ Msg 1   │ │ Msg 2   │ │ Msg 3   │  ...                     │
│    └─────────┘ └─────────┘ └─────────┘                          │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Worker (rabbitmq_consumer.py)                                │
│    - Chạy liên tục: python src/worker.py                        │
│    - Consume messages từ queue                                  │
│    - Gọi callback() cho mỗi message                             │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. Processing (conversation_event_processing_service.py)        │
│    a. Lấy event từ DB bằng conversation_id                       │
│    b. Fetch conversation data                                   │
│    c. Calculate friendship score                                │
│    d. Update friendship_status & topic_metrics                  │
│    e. Mark event as PROCESSED                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Acknowledge Message                                           │
│    - Nếu thành công: ch.basic_ack() → Message bị xóa khỏi queue │
│    - Nếu lỗi: ch.basic_nack(requeue=True) → Retry sau          │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 Chi tiết từng bước

### Bước 1: API nhận request

```python
# endpoint_conversation_events.py
POST /v1/conversations/end
  ↓
1. Validate request
2. Save to DB (status=PENDING)
3. Publish to RabbitMQ queue
4. Return 202 Accepted (< 100ms)
```

**Log:**
```
🌐 POST /v1/conversations/end | client_ip=127.0.0.1
📥 POST /conversations/end | conversation_id=testc_id | user_id=user_123
✅ Saved to DB | conversation_id=testc_id | event_id=129
✅ Published to queue | conversation_id=testc_id
✅ 202 Accepted | conversation_id=testc_id
```

### Bước 2: Worker consume message

```python
# rabbitmq_consumer.py
def callback(ch, method, properties, body):
    1. Parse JSON message → conversation_id
    2. Tạo DB session mới
    3. Lấy event từ DB
    4. Setup services
    5. Process event
    6. Acknowledge message
```

**Log:**
```
📥 Processing conversation from queue: testc_id
```

### Bước 3: Process event

```python
# conversation_event_processing_service.py
def process_single_event(event_id):
    1. Mark status=PROCESSING
    2. Fetch conversation data
    3. Calculate score
    4. Update friendship_status
    5. Update topic_metrics (nếu có topic_id)
    6. Mark status=PROCESSED
```

**Log:**
```
Processing single conversation event conversation_id=testc_id attempt=1
Calculating friendship score for conversation_id: testc_id
Found conversation in database: testc_id
Score calculation completed for conversation_id: testc_id, score_change: 0.0
✅ Successfully processed conversation: testc_id
```

## ⚠️ Tại sao Score = 0?

### Nguyên nhân

Từ log bạn cung cấp:
```json
{
  "total_turns": 0,
  "user_initiated_questions": 0,
  "session_emotion": "neutral",
  "new_memories_count": 0,
  "base_score": 0.0,
  "engagement_bonus": 0.0,
  "emotion_bonus": 0.0,
  "memory_bonus": 0.0,
  "final_score_change": 0.0
}
```

### Phân tích

1. **`total_turns = 0`** 
   - **Nguyên nhân:** Conversation log chỉ có 8 messages, **TẤT CẢ đều là "pika"** (BOT_RESPONSE_CONVERSATION)
   - **Logic:** `_count_complete_turns()` chỉ đếm **cặp (pika, user)** hoặc **(user, pika)**
   - **Kết quả:** Không có cặp nào → `total_turns = 0` → `base_score = 0 * 0.5 = 0`

2. **`user_initiated_questions = 0`**
   - **Nguyên nhân:** Không có user messages trong conversation_log
   - **Kết quả:** `engagement_bonus = 0 * 3 = 0`

3. **`session_emotion = "neutral"`**
   - **Kết quả:** `emotion_bonus = 0` (neutral không có bonus)

4. **`new_memories_count = 0`**
   - **Kết quả:** `memory_bonus = 0 * 5 = 0`

### Giải pháp

**Vấn đề:** Backend gửi conversation_log chỉ có BOT messages, không có USER messages.

**Cần kiểm tra:**
1. Backend có gửi đúng format không?
2. Có USER_RESPONSE_CONVERSATION trong conversation_logs không?
3. Transform có đúng không?

**Test với data đúng:**
```json
{
  "conversation_logs": [
    {"character": "BOT_RESPONSE_CONVERSATION", "content": "Hello!"},
    {"character": "USER_RESPONSE_CONVERSATION", "content": "Hi there!"},
    {"character": "BOT_RESPONSE_CONVERSATION", "content": "How are you?"},
    {"character": "USER_RESPONSE_CONVERSATION", "content": "I'm good!"}
  ]
}
```

→ Sẽ có `total_turns = 2` (2 cặp) → `base_score = 2 * 0.5 = 1.0`

## 🚀 Cách chạy Worker

### Local Development

**Terminal 1 - API:**
```bash
uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020
```

**Terminal 2 - Worker:**
```bash
python src/worker.py
```

### Docker Compose

```bash
docker-compose up -d
```

Worker sẽ tự động chạy trong container `rabbitmq_worker`.

## 📊 Monitoring

### RabbitMQ Management UI
- URL: http://localhost:15672
- Username: guest
- Password: guest
- Xem queue: `conversation_events_processing`
  - **Ready:** Messages đang chờ
  - **Unacked:** Messages đang được xử lý
  - **Total:** Tổng số messages

### Logs

**Worker logs:**
```
📥 Processing conversation from queue: testc_id
✅ Successfully processed conversation: testc_id
```

**API logs:**
```
🌐 POST /v1/conversations/end
✅ 202 Accepted
```

## 🔧 Troubleshooting

### Worker không chạy
- Kiểm tra RabbitMQ đang chạy: `docker ps | grep rabbitmq`
- Kiểm tra connection: `telnet localhost 5672`

### Messages đọng trong queue
- Worker không chạy hoặc bị crash
- Kiểm tra worker logs

### Score = 0
- Kiểm tra conversation_log có cả pika và user messages không
- Xem log breakdown để debug

