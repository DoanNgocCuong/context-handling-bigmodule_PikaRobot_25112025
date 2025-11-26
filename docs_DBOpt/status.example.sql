Quá chuẩn, schema nhìn rất ổn rồi. Giờ anh lên **example seed cho bảng `friendship_status`** nhé.

---

## 🔹 1. Nhắc lại cấu trúc `friendship_status`

```sql
CREATE TABLE friendship_status (
    user_id VARCHAR(255) PRIMARY KEY,
    friendship_score FLOAT DEFAULT 0.0 NOT NULL,
    friendship_level VARCHAR(50) DEFAULT 'STRANGER' NOT NULL,
    -- STRANGER (0-99), ACQUAINTANCE (100-499), FRIEND (500+)
    last_interaction_date TIMESTAMPTZ,
    streak_day INTEGER DEFAULT 0 NOT NULL,
    topic_metrics JSONB DEFAULT '{}' NOT NULL,
    -- {
    --   "agent_movie": { "score": 52.0, "turns": 65, "last_date": "..." },
    --   "agent_animal": { "score": 28.5, "turns": 32, "last_date": "..." }
    -- }
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔹 2. Ví dụ dữ liệu seed cho `friendship_status`

### ✅ Case 1: User mới – STRANGER (score thấp)

```sql
INSERT INTO friendship_status (
    user_id,
    friendship_score,
    friendship_level,
    last_interaction_date,
    streak_day,
    topic_metrics
) VALUES (
    'user_001',
    20.0,
    'STRANGER',
    '2025-11-25T09:05:00Z',
    1,
    '{}'::jsonb
);
```

---

### ✅ Case 2: User tương tác kha khá – ACQUAINTANCE

Có vài topic đã có tương tác, giống format trong tài liệu:

```sql
INSERT INTO friendship_status (
    user_id,
    friendship_score,
    friendship_level,
    last_interaction_date,
    streak_day,
    topic_metrics
) VALUES (
    'user_002',
    230.5,
    'ACQUAINTANCE',
    '2025-11-24T15:30:00Z',
    4,
    '{
      "agent_movie": {
        "score": 52.0,
        "turns": 65,
        "last_date": "2025-11-24T10:20:00Z"
      },
      "agent_animal": {
        "score": 28.5,
        "turns": 32,
        "last_date": "2025-11-23T09:00:00Z"
      }
    }'::jsonb
);
```

---

### ✅ Case 3: User thân – FRIEND (score cao, streak dài)

```sql
INSERT INTO friendship_status (
    user_id,
    friendship_score,
    friendship_level,
    last_interaction_date,
    streak_day,
    topic_metrics
) VALUES (
    'user_003',
    780.0,
    'FRIEND',
    '2025-11-25T18:45:00Z',
    12,
    '{
      "agent_movie": {
        "score": 120.0,
        "turns": 150,
        "last_date": "2025-11-25T18:00:00Z"
      },
      "agent_pets": {
        "score": 85.5,
        "turns": 90,
        "last_date": "2025-11-24T17:20:00Z"
      },
      "agent_school": {
        "score": 40.0,
        "turns": 30,
        "last_date": "2025-11-23T08:10:00Z"
      }
    }'::jsonb
);
```

---

### ✅ Case 4: User có streak nhưng ít topic – chuẩn cho kịch bản “đẩy khám phá chủ đề mới”

```sql
INSERT INTO friendship_status (
    user_id,
    friendship_score,
    friendship_level,
    last_interaction_date,
    streak_day,
    topic_metrics
) VALUES (
    'user_004',
    120.0,
    'ACQUAINTANCE',
    '2025-11-23T08:00:00Z',
    7,
    '{
      "agent_hobbies": {
        "score": 30.0,
        "turns": 25,
        "last_date": "2025-11-22T09:15:00Z"
      }
    }'::jsonb
);
```

---

Nếu anh muốn bước tiếp, mình có thể:

* Viết luôn **UPDATE logic** minh hoạ: từ `daily_metrics` → update `friendship_score`, `topic_metrics`.
* Hoặc mapping thẳng từ `topic` trong `friendship_agent_mapping` → key trong `topic_metrics` để team AI/BE nhìn thấy full vòng lặp dữ liệu.
