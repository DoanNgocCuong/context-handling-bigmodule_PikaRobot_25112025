# 1. Cách tính `total_turns` hiện tại

### Code hiện tại

```155:155:src/app/services/friendship_score_calculation_service.py
            total_turns = len(conversation_log)
```

**Cách tính:**

- `total_turns = len(conversation_log)`
- Đếm số phần tử trong list `conversation_log` của 1 conversation
- Mỗi phần tử = 1 turn/message (của pika hoặc user)

### So sánh với tài liệu

**Tài liệu cũ (đã thay đổi):**

- `total_turns`: "Tổng số lượt trò chuyện trong ngày" (daily aggregate)
- Tính từ `daily_metrics` (tổng hợp nhiều conversations trong ngày)

**Tài liệu mới (hiện tại - Tài liệu 3.100):**

- `total_turns`: "Tổng số lượt trò chuyện trong phiên" (per session/conversation)
- Tính từ `conversation_log` của 1 conversation cụ thể
- Xử lý real-time sau mỗi conversation, không đợi cuối ngày

### Ví dụ

**Conversation 1:**

```json
[
  {"speaker": "pika", "turn_id": 1, "text": "Hello!"},
  {"speaker": "user", "turn_id": 2, "text": "Hi!"},
  {"speaker": "pika", "turn_id": 3, "text": "How are you?"}
]
```

→ `total_turns = 3` (cho conversation này)

**Conversation 2:**

```json
[
  {"speaker": "pika", "turn_id": 1, "text": "What's your favorite movie?"},
  {"speaker": "user", "turn_id": 2, "text": "I love action movies!"}
]
```

→ `total_turns = 2` (cho conversation này)

### Kết luận

- Code hiện tại đúng với tài liệu mới: tính `total_turns` per conversation (real-time)
- Không còn tính daily aggregate như tài liệu cũ
- Mỗi conversation được xử lý riêng và cộng dồn điểm vào `friendship_score` ngay sau khi kết thúc

Cần giải thích thêm phần nào không?
