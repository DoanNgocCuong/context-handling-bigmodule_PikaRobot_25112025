```
# 1. Install dependencies
cd src
pip install -r requirements.txt

# 2. Setup environment (optional)
cp .env.example .env

# 3. Run server
uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020

# 4. Test health check
curl http://localhost:8000/v1/health

# Or use test script
python test_health.py
```


----

###1. Health check
```
curl -X 'GET' \
  'http://localhost:30020/v1/health' \
  -H 'accept: application/json'
```
### 2. From conversation_id -> calculate score -> update friendship_status:
```
###### 2.1 Test GET conversation
curl -X GET "http://localhost:8000/v1/conversations/conv_id_2003doanngoccuong" \
  -H "Content-Type: application/json"

###### 2.2 Test POST calculate score
curl -X POST "http://localhost:8000/v1/friendship_status/calculate-score/conv_id_2003doanngoccuong" \
  -H "Content-Type: application/json"

###### 2.3 Test POST update friendship_status
curl -X POST "http://localhost:8000/v1/friendship_status/calculate-score-and-update" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_doanngoccuong",
    "conversation_id": "conv_id_2003doanngoccuong"
  }'
```




### 3. From user_id -> get suggested activities:
```
curl -X POST "http://localhost:8000/v1/activities/suggest" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_doanngoccuong"
  }'
```

### 4. Trigger conversation_events:
```
curl -X 'POST' \
  'http://localhost:30022/v1/conversations/end' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "bot_id": "talk_movie_preference",
  "bot_name": "Movie Preference Talk",
  "bot_type": "TALK",
  "conversation_id": "conv_20251126_001",
  "conversation_log": [
    {
      "speaker": "pika",
      "text": "Hello! Ready to talk about movies?",
      "timestamp": "2025-11-26T10:00:00Z",
      "turn_id": 1
    }
  ],
  "end_time": "2025-11-26T10:20:00Z",
  "start_time": "2025-11-26T10:00:00Z",
  "status": "PENDING",
  "user_id": "user_doanngoccuong"
}'
```


```
{
  "success": true,
  "message": "Conversation event accepted for processing",
  "data": {
    "id": 1,
    "conversation_id": "conv_20251126_001",
    "user_id": "user_doanngoccuong",
    "bot_type": "TALK",
    "bot_id": "talk_movie_preference",
    "bot_name": "Movie Preference Talk",
    "start_time": "2025-11-26T10:00:00",
    "end_time": "2025-11-26T10:20:00",
    "duration_seconds": 1200,
    "conversation_log": [
      {
        "speaker": "pika",
        "turn_id": 1,
        "text": "Hello! Ready to talk about movies?",
        "timestamp": "2025-11-26T10:00:00Z"
      }
    ],
    "status": "PENDING",
    "attempt_count": 0,
    "created_at": "2025-11-26T10:34:25.329741",
    "next_attempt_at": "2025-11-26T16:34:28.039026",
    "processed_at": null,
    "error_code": null,
    "error_details": null,
    "friendship_score_change": null,
    "new_friendship_level": null,
    "updated_at": "2025-11-26T10:34:25.329741"
  }
}

```


```
curl -X 'POST' \
  'http://localhost:30022/v1/conversations/end' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{

  "conversation_id": "conv_20251126_005",
  "user_id": "user_doanngoccuong",
  "bot_id": "talk_movie_preference",
  "bot_name": "Movie Preference Talk",
  "bot_type": "TALK",
  "conversation_log": [
   
  ],
  "end_time": "2025-11-26T10:20:00Z",
  "start_time": "2025-11-26T10:00:00Z"
}'

```

```

curl -X 'POST' \
  'http://localhost:30022/v1/conversations/end' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{

  "conversation_id": "conv_20251126_005",
  "user_id": "user_doanngoccuong",
  "bot_id": "talk_movie_preference",
  "bot_name": "Movie Preference Talk",
  "bot_type": "TALK",
  "conversation_log": [
   
  ],
  "end_time": "2025-11-26T10:20:00Z",
  "start_time": "2025-11-26T10:00:00Z", 
  "status": "PENDING"
}'