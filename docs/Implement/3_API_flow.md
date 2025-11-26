```

# ========== STEP 1: User kết thúc cuộc hội thoại ==========
# Backend gửi conversation_id (không gửi toàn bộ log)

curl -X POST http://localhost:8000/v1/conversations/end \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "conversation_id": "conv_doanngoccuong",
    "session_metadata": {
      "duration_seconds": 1200,
      "agent_type": "talk"
    }
  }'

# Response: 202 Accepted (không cần đợi)


# ========== STEP 2: AI Service xử lý async (background) ==========
# 1. Consume event từ queue
# 2. Call API 2 để lấy conversation data
# 3. Tính toán score
# 4. Update friendship_status
# 5. Compute & cache candidates
# (Tất cả diễn ra ở background, BE không cần biết)


# ========== STEP 3: Lần tiếp theo, user mở app ==========
# Backend lấy trạng thái hiện tại

curl -X POST http://localhost:8000/v1/friendship/status \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'

# Response: Trạng thái tình bạn hiện tại (từ cache/DB)


# ========== STEP 4: Backend lấy agents được đề xuất ==========
# Dữ liệu đã được pre-computed, response rất nhanh!

curl -X POST http://localhost:8000/v1/activities/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'

# Response: 1 greeting agent + 4 talk/game agents (từ cache)
# Không cần đợi AI tính toán!
```
