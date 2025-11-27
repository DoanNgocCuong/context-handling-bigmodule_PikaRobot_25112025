# API Examples - Context Handling Service (v2)

**Version:** 2.0  
**Date:** 25/11/2025  
**Base URL:** `http://localhost:8000/v1` (Development)  
**Production URL:** `https://api.pika.app/v1` (Production)

---

## 📋 Mục lục

1. [Luồng Dữ liệu Tổng thể](#luồng-dữ-liệu-tổng-thể)
2. [Health Check](#health-check)
3. [API 1: Tính toán Điểm (BE → AI)](#api-1-tính-toán-điểm-be--ai)
4. [API 2: Cập nhật Trạng thái (AI → BE)](#api-2-cập-nhật-trạng-thái-ai--be)
5. [API 3: Lấy Trạng thái (BE → Context Service)](#api-3-lấy-trạng-thái-be--context-service)
6. [API 4: Lấy Agents Đề xuất (BE → Context Service)](#api-4-lấy-agents-đề-xuất-be--context-service)
7. [API 5-8: Agent Mapping Management](#api-5-8-agent-mapping-management)
8. [Error Handling](#error-handling)

---

## Luồng Dữ liệu Tổng thể

```
┌──────────────────────────────────────────────────────────────────┐
│ FLOW 1: Cập nhật Friendship Score (Real-time)                   │
└──────────────────────────────────────────────────────────────────┘

1. Frontend/Main App
   └─> User kết thúc cuộc trò chuyện
   
2. Backend Service
   └─> API 1: POST /scoring/calculate-friendship
       (Body: user_id + conversation_log)
   
3. AI Scoring Service
   └─> Tính toán score change
   └─> Trả về friendship_score_change, topic_updates, new_memories
   
4. AI Scoring Service
   └─> API 2: POST /friendship/update
       (Body: user_id + score_change + topic_updates + memories)
   
5. Context Handling Service
   └─> Cập nhật friendship_status trong DB
   └─> Tự động tính friendship_level
   └─> Trả về updated status


┌──────────────────────────────────────────────────────────────────┐
│ FLOW 2: Lấy Agents Được Đề xuất (Khi User Mở App)               │
└──────────────────────────────────────────────────────────────────┘

1. Frontend/Main App
   └─> User mở app
   
2. Backend Service
   └─> API 3: POST /friendship/status
       (Body: user_id)
   └─> Lấy friendship_status hiện tại
   
3. Backend Service
   └─> API 4: POST /activities/suggest
       (Body: user_id)
   └─> Lấy danh sách agents được cá nhân hóa
   
4. Frontend/Main App
   └─> Hiển thị greeting + 4 agents cho user
```

---

## Health Check

### Endpoint

```
GET /health
```

### Description

Kiểm tra trạng thái của service và database connection.

### cURL Example

```bash
curl -X GET http://localhost:8000/v1/health
```

### Response (200 OK)

```json
{
  "status": "ok",
  "timestamp": "2025-11-25T18:30:00Z",
  "database": "connected"
}
```

---

## API 1: Tính toán Điểm (BE → AI)

### Endpoint

```
POST /scoring/calculate-friendship
```

### Description

**Gọi bởi:** Backend Service  
**Gọi tới:** AI Scoring Service  
**Mục đích:** Tính toán điểm tình bạn thay đổi từ log hội thoại

Sau khi user kết thúc một cuộc hội thoại, Backend gửi log đến AI để tính toán các thay đổi về điểm tình bạn, topic metrics, và ký ức mới.

### Request Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "user_id": "user_123",
  "conversation_id":"conv_123456"
```

Phía BE chỉ cần gửi user_id và conversation_id đến phía AI
### Request Fields - Phía AI tự xử lý để từ .
### cURL Example

```bash
curl -X POST http://localhost:8000/v1/scoring/calculate-friendship \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "conversation_id"
  }'
```

### Response (200 OK)

```json
{
  "user_id": "user_123",
  "": oke đã gửi dữ liệu thành công, phía AI sẽ lưu trữ và tính toán dynamic memory và friendlyship_score. 
}
```

### Response Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `user_id` | String | ID của user (echo lại) |
| `friendship_score_change` | Float | Mức độ thay đổi điểm tình bạn (có thể âm) |
| `topic_metrics_update` | Array | Danh sách cập nhật cho các topic |
| `topic_metrics_update[].topic_id` | String | ID của topic (ví dụ: "agent_movie") |
| `topic_metrics_update[].score_change` | Float | Mức độ thay đổi điểm topic |
| `topic_metrics_update[].turns_increment` | Integer | Số lượt tương tác tăng thêm |
| `new_memories` | Array | Danh sách ký ức mới được tạo |
| `new_memories[].memory_id` | String | ID duy nhất của ký ức |
| `new_memories[].content` | String | Nội dung ký ức |
| `new_memories[].related_topic` | String | Topic liên quan |
| `new_memories[].timestamp` | DateTime | Thời điểm tạo ký ức |

---

## API 2: Cập nhật Trạng thái (AI → BE)

### Endpoint

```
POST /friendship/update
```

### Description

**Gọi bởi:** AI Scoring Service  
**Gọi tới:** Context Handling Service  
**Mục đích:** Cập nhật trạng thái tình bạn vào database

Sau khi AI tính toán xong điểm, nó gửi các thay đổi này đến Context Service để cập nhật vào database. Service sẽ tự động tính toán `friendship_level` dựa trên `friendship_score`.

### Request Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "user_id": "user_123",
  "friendship_score_change": 35.5,
  "topic_metrics_update": [
    {
      "topic_id": "agent_movie",
      "score_change": 7.0,
      "turns_increment": 2
    }
  ],
  "new_memories": [
    {
      "memory_id": "mem_001",
      "content": "Thích xem phim Spirited Away của Hayao Miyazaki",
      "related_topic": "agent_movie",
      "timestamp": "2025-11-25T18:30:00Z"
    }
  ]
}
```

### Request Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | String | Yes | ID duy nhất của user |
| `friendship_score_change` | Float | Yes | Mức độ thay đổi điểm |
| `topic_metrics_update` | Array | No | Cập nhật topic metrics |
| `new_memories` | Array | No | Ký ức mới được tạo |

### cURL Example

```bash
curl -X POST http://localhost:8000/v1/friendship/update \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "friendship_score_change": 35.5,
    "topic_metrics_update": [
      {
        "topic_id": "agent_movie",
        "score_change": 7.0,
        "turns_increment": 2
      }
    ],
    "new_memories": [
      {
        "memory_id": "mem_001",
        "content": "Thích xem phim Spirited Away",
        "related_topic": "agent_movie",
        "timestamp": "2025-11-25T18:30:00Z"
      }
    ]
  }'
```

### Response (200 OK)

```json
{
  "success": true,
  "user_id": "user_123",
  "data": {
    "user_id": "user_123",
    "friendship_score": 835.5,
    "friendship_level": "PHASE2_ACQUAINTANCE",
    "last_interaction_date": "2025-11-25T18:30:00Z",
    "streak_day": 6,
    "topic_metrics": {
      "agent_movie": {
        "score": 59.0,
        "turns": 67,
        "last_date": "2025-11-25T18:30:00Z"
      },
      "agent_animal": {
        "score": 28.5,
        "turns": 32,
        "last_date": "2025-11-24T14:10:00Z"
      }
    }
  }
}
```

### Response Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `success` | Boolean | Có cập nhật thành công hay không |
| `user_id` | String | ID của user (echo lại) |
| `data` | Object | Friendship status sau khi cập nhật |
| `data.user_id` | String | ID của user |
| `data.friendship_score` | Float | Điểm tình bạn hiện tại |
| `data.friendship_level` | String | PHASE1_STRANGER / PHASE2_ACQUAINTANCE / PHASE3_FRIEND |
| `data.last_interaction_date` | DateTime | Lần tương tác cuối cùng |
| `data.streak_day` | Integer | Số ngày tương tác liên tiếp |
| `data.topic_metrics` | Object | Điểm và lịch sử cho mỗi topic |

---

## API 3: Lấy Trạng thái (BE → Context Service)

### Endpoint

```
POST /friendship/status
```

### Description

**Gọi bởi:** Backend Service  
**Gọi tới:** Context Handling Service  
**Mục đích:** Lấy trạng thái tình bạn hiện tại của user

Khi user mở app hoặc cần lấy thông tin tình bạn, Backend gửi request này để lấy toàn bộ thông tin tình bạn của user.

### Request Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "user_id": "user_123"
}
```

### Request Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | String | Yes | ID duy nhất của user |

### cURL Example

```bash
curl -X POST http://localhost:8000/v1/friendship/status \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

### Response (200 OK)

```json
{
  "user_id": "user_123",
  "friendship_score": 835.5,
  "friendship_level": "PHASE2_ACQUAINTANCE",
  "last_interaction_date": "2025-11-25T18:30:00Z",
  "streak_day": 6,
  "topic_metrics": {
    "agent_movie": {
      "score": 59.0,
      "turns": 67,
      "last_date": "2025-11-25T18:30:00Z"
    },
    "agent_animal": {
      "score": 28.5,
      "turns": 32,
      "last_date": "2025-11-24T14:10:00Z"
    },
    "agent_school": {
      "score": 15.0,
      "turns": 10,
      "last_date": "2025-11-23T09:15:00Z"
    }
  }
}
```

### Response (404 Not Found)

```json
{
  "error": "User not found",
  "user_id": "user_123"
}
```

---

## API 4: Lấy Agents Đề xuất (BE → Context Service)

### Endpoint

```
POST /activities/suggest
```

### Description

**Gọi bởi:** Backend Service  
**Gọi tới:** Context Handling Service  
**Mục đích:** Lấy danh sách Agent được đề xuất cho user

Dựa trên trạng thái tình bạn hiện tại, trả về 1 Greeting Agent + danh sách Talk/Game Agents được cá nhân hóa.

### Request Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "user_id": "user_123"
}
```

### Request Fields

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | String | Yes | ID duy nhất của user |

### cURL Example

```bash
curl -X POST http://localhost:8000/v1/activities/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

### Response (200 OK) - User ở PHASE2_ACQUAINTANCE Level

```json
{
  "user_id": "user_123",
  "friendship_level": "PHASE2_ACQUAINTANCE",
  "greeting_agent": {
    "id": 8,
    "friendship_level": "PHASE2_ACQUAINTANCE",
    "agent_type": "GREETING",
    "agent_id": "greeting_memory_recall",
    "agent_name": "Memory Recall",
    "agent_description": "Nhắc lại ký ức chung với user",
    "weight": 2.0,
    "is_active": true
  },
  "talk_agents": [
    {
      "id": 10,
      "friendship_level": "PHASE2_ACQUAINTANCE",
      "agent_type": "TALK",
      "agent_id": "talk_movie_preference",
      "agent_name": "Movie Preference",
      "agent_description": "Nói về phim yêu thích",
      "weight": 1.2,
      "is_active": true
    },
    {
      "id": 11,
      "friendship_level": "PHASE2_ACQUAINTANCE",
      "agent_type": "TALK",
      "agent_id": "talk_dreams",
      "agent_name": "Dreams Talk",
      "agent_description": "Nói về ước mơ",
      "weight": 1.0,
      "is_active": true
    }
  ],
  "game_agents": [
    {
      "id": 12,
      "friendship_level": "PHASE2_ACQUAINTANCE",
      "agent_type": "GAME_ACTIVITY",
      "agent_id": "game_20questions",
      "agent_name": "20 Questions",
      "agent_description": "Trò chơi 20 câu hỏi",
      "weight": 1.0,
      "is_active": true
    },
    {
      "id": 13,
      "friendship_level": "PHASE2_ACQUAINTANCE",
      "agent_type": "GAME_ACTIVITY",
      "agent_id": "game_story_building",
      "agent_name": "Story Building",
      "agent_description": "Xây dựng câu chuyện chung",
      "weight": 1.5,
      "is_active": true
    }
  ]
}
```

### Response (200 OK) - User ở PHASE1_STRANGER Level

```json
{
  "user_id": "user_123",
  "friendship_level": "PHASE1_STRANGER",
  "greeting_agent": {
    "id": 1,
    "friendship_level": "PHASE1_STRANGER",
    "agent_type": "GREETING",
    "agent_id": "greeting_welcome",
    "agent_name": "Welcome Greeting",
    "agent_description": "Chào mừng người dùng mới",
    "weight": 1.0,
    "is_active": true
  },
  "talk_agents": [
    {
      "id": 3,
      "friendship_level": "PHASE1_STRANGER",
      "agent_type": "TALK",
      "agent_id": "talk_hobbies",
      "agent_name": "Hobbies Talk",
      "agent_description": "Nói về sở thích",
      "weight": 1.0,
      "is_active": true
    },
    {
      "id": 4,
      "friendship_level": "PHASE1_STRANGER",
      "agent_type": "TALK",
      "agent_id": "talk_school",
      "agent_name": "School Life Talk",
      "agent_description": "Nói về học tập",
      "weight": 1.0,
      "is_active": true
    }
  ],
  "game_agents": [
    {
      "id": 6,
      "friendship_level": "PHASE1_STRANGER",
      "agent_type": "GAME_ACTIVITY",
      "agent_id": "game_drawing",
      "agent_name": "Drawing Game",
      "agent_description": "Trò chơi vẽ",
      "weight": 1.0,
      "is_active": true
    },
    {
      "id": 7,
      "friendship_level": "PHASE1_STRANGER",
      "agent_type": "GAME_ACTIVITY",
      "agent_id": "game_riddle",
      "agent_name": "Riddle Game",
      "agent_description": "Trò chơi đố",
      "weight": 0.9,
      "is_active": true
    }
  ]
}
```

---

## API 5-8: Agent Mapping Management

### API 5: List Agent Mappings

#### Endpoint

```
GET /agent-mappings
```

#### Query Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `friendship_level` | String | No | Lọc theo level: PHASE1_STRANGER, PHASE2_ACQUAINTANCE, PHASE3_FRIEND |
| `agent_type` | String | No | Lọc theo loại: GREETING, TALK, GAME_ACTIVITY |

#### cURL Examples

```bash
# Lấy tất cả mappings
curl -X GET http://localhost:8000/v1/agent-mappings

# Lấy mappings cho PHASE1_STRANGER level
curl -X GET "http://localhost:8000/v1/agent-mappings?friendship_level=PHASE1_STRANGER"

# Lấy Greeting agents cho PHASE2_ACQUAINTANCE level
curl -X GET "http://localhost:8000/v1/agent-mappings?friendship_level=PHASE2_ACQUAINTANCE&agent_type=GREETING"
```

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "friendship_level": "PHASE1_STRANGER",
    "agent_type": "GREETING",
    "agent_id": "greeting_welcome",
    "agent_name": "Welcome Greeting",
    "agent_description": "Chào mừng người dùng mới",
    "weight": 1.0,
    "is_active": true
  },
  {
    "id": 2,
    "friendship_level": "PHASE1_STRANGER",
    "agent_type": "GREETING",
    "agent_id": "greeting_intro",
    "agent_name": "Introduce Pika",
    "agent_description": "Giới thiệu về Pika",
    "weight": 1.5,
    "is_active": true
  }
]
```

---

### API 6: Create Agent Mapping

#### Endpoint

```
POST /agent-mappings
```

#### Request Body

```json
{
  "friendship_level": "PHASE3_FRIEND",
  "agent_type": "GREETING",
  "agent_id": "greeting_special_moment",
  "agent_name": "Special Moment",
  "agent_description": "Khoảnh khắc đặc biệt",
  "weight": 2.0
}
```

#### cURL Example

```bash
curl -X POST http://localhost:8000/v1/agent-mappings \
  -H "Content-Type: application/json" \
  -d '{
    "friendship_level": "PHASE3_FRIEND",
    "agent_type": "GREETING",
    "agent_id": "greeting_special_moment",
    "agent_name": "Special Moment",
    "agent_description": "Khoảnh khắc đặc biệt",
    "weight": 2.0
  }'
```

#### Response (201 Created)

```json
{
  "id": 20,
  "friendship_level": "PHASE3_FRIEND",
  "agent_type": "GREETING",
  "agent_id": "greeting_special_moment",
  "agent_name": "Special Moment",
  "agent_description": "Khoảnh khắc đặc biệt",
  "weight": 2.0,
  "is_active": true
}
```

---

### API 7: Update Agent Mapping

#### Endpoint

```
PUT /agent-mappings/{mapping_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mapping_id` | Integer | Yes | ID của agent mapping |

#### Request Body

```json
{
  "weight": 2.5,
  "is_active": true
}
```

#### cURL Example

```bash
curl -X PUT http://localhost:8000/v1/agent-mappings/20 \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 2.5,
    "is_active": true
  }'
```

#### Response (200 OK)

```json
{
  "id": 20,
  "friendship_level": "PHASE3_FRIEND",
  "agent_type": "GREETING",
  "agent_id": "greeting_special_moment",
  "agent_name": "Special Moment",
  "agent_description": "Khoảnh khắc đặc biệt",
  "weight": 2.5,
  "is_active": true
}
```

---

### API 8: Delete Agent Mapping

#### Endpoint

```
DELETE /agent-mappings/{mapping_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `mapping_id` | Integer | Yes | ID của agent mapping |

#### cURL Example

```bash
curl -X DELETE http://localhost:8000/v1/agent-mappings/20
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Agent mapping deleted successfully"
}
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request

```json
{
  "detail": [
    {
      "loc": ["body", "friendship_score_change"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 404 Not Found

```json
{
  "error": "User not found",
  "user_id": "user_999"
}
```

#### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "Failed to update friendship status",
  "request_id": "req_abc123xyz"
}
```

### Error Status Codes

| Status Code | Meaning | Example |
| :--- | :--- | :--- |
| 200 | OK | Request thành công |
| 201 | Created | Resource được tạo thành công |
| 400 | Bad Request | Request body không hợp lệ |
| 404 | Not Found | Resource không tìm thấy |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

---

## Complete Integration Example

### Scenario: User Hoàn thành một cuộc hội thoại và mở app lần tiếp theo

```bash
# ========== STEP 1: User kết thúc cuộc hội thoại ==========
# Backend gửi log đến AI để tính toán điểm

curl -X POST http://localhost:8000/v1/scoring/calculate-friendship \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "conversation_log": [
      {"speaker": "user", "turn_id": 1, "text": "Hi Pika!"},
      {"speaker": "pika", "turn_id": 2, "text": "Hello!"}
    ],
    "session_emotion": "interesting"
  }'

# Response: friendship_score_change = 35.5


# ========== STEP 2: AI cập nhật trạng thái vào DB ==========

curl -X POST http://localhost:8000/v1/friendship/update \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "friendship_score_change": 35.5,
    "topic_metrics_update": [],
    "new_memories": []
  }'

# Response: friendship_score = 835.5, friendship_level = PHASE2_ACQUAINTANCE


# ========== STEP 3: Lần tiếp theo, user mở app ==========
# Backend lấy trạng thái hiện tại

curl -X POST http://localhost:8000/v1/friendship/status \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'

# Response: Trạng thái tình bạn hiện tại


# ========== STEP 4: Backend lấy agents được đề xuất ==========

curl -X POST http://localhost:8000/v1/activities/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'

# Response: 1 greeting agent + 4 talk/game agents phù hợp với PHASE2_ACQUAINTANCE level
```

---

## Best Practices for Integration

### 1. Error Handling

Luôn check HTTP status code và handle errors:

```bash
response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/v1/scoring/calculate-friendship \
  -H "Content-Type: application/json" \
  -d '...')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" -eq 200 ]; then
  echo "Success: $body"
else
  echo "Error: HTTP $http_code"
  echo "$body"
fi
```

### 2. Timeout Configuration

Luôn set timeout cho requests:

```bash
curl --max-time 30 \
  -X POST http://localhost:8000/v1/scoring/calculate-friendship \
  -H "Content-Type: application/json" \
  -d '...'
```

### 3. Retry Logic

Implement retry logic cho transient errors:

```bash
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
  response=$(curl -s -X POST http://localhost:8000/v1/scoring/calculate-friendship \
    -H "Content-Type: application/json" \
    -d '...')
  
  if [ $? -eq 0 ]; then
    echo "$response"
    break
  fi
  
  retry_count=$((retry_count + 1))
  sleep 2
done
```

### 4. Logging

Log tất cả requests/responses:

```bash
curl -v -X POST http://localhost:8000/v1/scoring/calculate-friendship \
  -H "Content-Type: application/json" \
  -d '...' 2>&1 | tee request.log
```

---

## Testing Checklist

- [ ] Health check endpoint hoạt động
- [ ] API 1: Scoring API tính toán điểm chính xác
- [ ] API 2: Update API cập nhật DB thành công
- [ ] API 3: Get status API trả về dữ liệu đúng
- [ ] API 4: Suggested activities API trả về agents đúng level
- [ ] API 5-8: Agent mapping CRUD hoạt động
- [ ] Error handling hoạt động đúng
- [ ] Timeout handling hoạt động
- [ ] Logging hoạt động
- [ ] user_id trong body được xử lý đúng

---

## Summary: API Endpoints

| # | Endpoint | Method | Gọi bởi | Mục đích |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `/scoring/calculate-friendship` | POST | BE | Tính toán điểm |
| 2 | `/friendship/update` | POST | AI | Cập nhật trạng thái |
| 3 | `/friendship/status` | POST | BE | Lấy trạng thái |
| 4 | `/activities/suggest` | POST | BE | Lấy agents đề xuất |
| 5 | `/agent-mappings` | GET | Admin | Lấy danh sách mappings |
| 6 | `/agent-mappings` | POST | Admin | Tạo mapping mới |
| 7 | `/agent-mappings/{id}` | PUT | Admin | Cập nhật mapping |
| 8 | `/agent-mappings/{id}` | DELETE | Admin | Xóa mapping |

---

## Support & Troubleshooting

### Common Issues

**Q: API trả về 404 Not Found**  
A: Kiểm tra user_id có tồn tại không. Nếu không, hãy tạo user mới bằng cách gọi update-friendship API.

**Q: API timeout**  
A: Tăng timeout, hoặc kiểm tra database connection.

**Q: Friendship score không cập nhật**  
A: Kiểm tra xem AI Scoring Service có hoạt động không, và check logs.

### Contact

- **API Support:** api-support@pika.app
- **Documentation:** https://docs.pika.app/api
- **Status Page:** https://status.pika.app
