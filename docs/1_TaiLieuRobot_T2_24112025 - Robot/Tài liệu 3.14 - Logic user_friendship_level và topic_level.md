So sánh logic tăng `user_friendship_level` và `topic_level`:

[3 tools called]

So sánh logic tăng `user_friendship_level` và `topic_level`:

## So sánh logic

### 1. User Friendship Level (friendship_level)

File: `src/app/repositories/friendship_status_repository.py` - `_determine_level()`

Logic: chỉ dựa trên `friendship_score` tổng

```python
def _determine_level(score: float) -> FriendshipLevel:
    if score >= 3000:
        return PHASE3_FRIEND
    if score >= 500:
        return PHASE2_ACQUAINTANCE
    return PHASE1_STRANGER
```

Điều kiện:

- PHASE1_STRANGER: `0 <= score < 500`
- PHASE2_ACQUAINTANCE: `500 <= score < 3000`
- PHASE3_FRIEND: `score >= 3000`

Chỉ cần 1 điều kiện: `friendship_score`

---

### 2. Topic Level (topic_metrics[topic_id]["friendship_level"])

File: `src/app/repositories/friendship_status_repository.py` - `_determine_topic_level()`

Logic: dựa trên `topic_score` và `user_friendship_level` (cần cả 2)

```python
def _determine_topic_level(topic_score, user_level, current_topic_level):
    # PHASE3: topic_score >= 150 AND user_level >= PHASE3
    if topic_score >= 150.0 and user_level >= PHASE3_FRIEND:
        return PHASE3_FRIEND
  
    # PHASE2: topic_score >= 50 AND user_level >= PHASE2
    if topic_score >= 50.0 and user_level >= PHASE2_ACQUAINTANCE:
        return PHASE2_ACQUAINTANCE
  
    # PHASE1: topic_score < 50
    if topic_score < 50.0:
        return PHASE1_STRANGER
  
    return current_topic_level  # Giữ nguyên
```

Điều kiện:

- PHASE1_STRANGER: `topic_score < 50`
- PHASE2_ACQUAINTANCE: `topic_score >= 50` và `user_level >= PHASE2`
- PHASE3_FRIEND: `topic_score >= 150` và `user_level >= PHASE3`

Cần 2 điều kiện: `topic_score` và `user_friendship_level`

---

## Bảng so sánh

| Tiêu chí                                 | User Friendship Level        | Topic Level                                         |
| ------------------------------------------ | ---------------------------- | --------------------------------------------------- |
| Dựa trên                                 | `friendship_score` (tổng) | `topic_score` + `user_friendship_level`         |
| Threshold PHASE2                           | `score >= 500`             | `topic_score >= 50` và `user_level >= PHASE2`  |
| Threshold PHASE3                           | `score >= 3000`            | `topic_score >= 150` và `user_level >= PHASE3` |
| Số điều kiện                           | 1 (chỉ score)               | 2 (score + user level)                              |
| Có thể lên PHASE2 khi user còn PHASE1? | Có (nếu score >= 500)      | Không (cần user >= PHASE2)                        |
| Có thể lên PHASE3 khi user còn PHASE2? | Có (nếu score >= 3000)     | Không (cần user >= PHASE3)                        |

---

## Ví dụ

### Ví dụ 1: User mới, topic_score cao

```
User:
  - friendship_score: 100 (PHASE1_STRANGER)
  - Topic "movie": topic_score: 60

Kết quả:
  - User level: PHASE1_STRANGER (vì 100 < 500)
  - Topic level: PHASE1_STRANGER (vì user chưa đạt PHASE2, dù topic_score = 60 >= 50)
```

### Ví dụ 2: User đạt PHASE2, topic_score đủ

```
User:
  - friendship_score: 600 (PHASE2_ACQUAINTANCE)
  - Topic "movie": topic_score: 55

Kết quả:
  - User level: PHASE2_ACQUAINTANCE ✅
  - Topic level: PHASE2_ACQUAINTANCE ✅ (vì topic_score >= 50 VÀ user >= PHASE2)
```

### Ví dụ 3: User PHASE3, topic_score cao

```
User:
  - friendship_score: 3500 (PHASE3_FRIEND)
  - Topic "movie": topic_score: 200

Kết quả:
  - User level: PHASE3_FRIEND ✅
  - Topic level: PHASE3_FRIEND ✅ (vì topic_score >= 150 VÀ user >= PHASE3)
```

---

## Tóm tắt

- User level: chỉ cần `friendship_score` đạt ngưỡng
- Topic level: cần cả `topic_score` đạt ngưỡng và `user_friendship_level` đủ điều kiện

Topic level phụ thuộc vào user level, nên topic không thể vượt quá user level.
