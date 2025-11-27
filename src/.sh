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

### 1. Health check

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

```
{
  "success": true,
  "data": {
    "user_id": "user_doanngoccuong",
    "friendship_level": "PHASE1_STRANGER",
    "greeting_agent": {
      "agent_id": "general_greeting",
      "agent_name": "General Greeting",
      "agent_type": "GREETING",
      "agent_description": "{{CURRENT_EVENT}}",
      "final_prompt": "",
      "reason": "Phase default greeting",
      "metadata": {
        "topic_id": "general_greeting"
      }
    },
    "talk_agents": [
      {
        "agent_id": "agent_daily_routine",
        "agent_name": "Agent Daily Routine",
        "agent_type": "TALK",
        "agent_description": "\"4. OPENING GUIDE (DAILY ROUTINE)",
        "final_prompt": "",
        "reason": "Phase fallback",
        "metadata": {
          "topic_id": "Daily_Routine "
        }
      },
      {
        "agent_id": "agent_game",
        "agent_name": "Agent Game",
        "agent_type": "TALK",
        "agent_description": "4. OPENING GUIDE (HOBBY)",
        "final_prompt": "",
        "reason": "Phase fallback",
        "metadata": {
          "topic_id": "Game"
        }
      },
      {
        "agent_id": "agent_hobby_general ",
        "agent_name": "Agent Hobby General ",
        "agent_type": "TALK",
        "agent_description": "4. OPENING GUIDE (HOBBY)",
        "final_prompt": "",
        "reason": "Phase fallback",
        "metadata": {
          "topic_id": "Hobby General"
        }
      }
    ],
    "game_agents": [
      {
        "agent_id": "agent_story_telling",
        "agent_name": "Agent Story Telling",
        "agent_type": "GAME",
        "agent_description": "4. LỘ TRÌNH TRÒ CHUYỆN HÔM NAY (TODAY'S TALKING AGENDA): GAME \"CÙNG NHAU SÁNG TẠO CÂU CHUYỆN\"",
        "final_prompt": "",
        "reason": "Phase activity",
        "metadata": {
          "topic_id": "story"
        }
      },
      {
        "agent_id": "agent_play_game",
        "agent_name": "Agent Play Game",
        "agent_type": "GAME",
        "agent_description": "4. TODAY'S TALKING AGENDA): GAME \"ĐỐ BIẾT TỪ GÌ\"",
        "final_prompt": "",
        "reason": "Phase activity",
        "metadata": {
          "topic_id": "trò đố từ"
        }
      }
    ]
  },
  "message": "Activities suggested successfully"
}
```
### 4. Trigger conversation_events:

```bash
curl --location 'http://localhost:30080/v1/conversations/end' \
--header 'accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
  "conversation_id": "convc_1cxxcc23__",
  "user_id": "user_doanngoccuong",      
  "bot_id": "agent_pet",
  "bot_name": "Movie Preference Talk",
  "bot_type": "dd",
  "conversation_logs": [
    {
      "character": "BOT_RESPONSE_CONVERSATION",
      "content": ""
    },
    {
      "character": "BOT_RESPONSE_CONVERSATION",
      "content": "BEEP BEEP! Đã đến Trái Đất!"
    },
    {
      "character": "BOT_RESPONSE_CONVERSATION",
      "content": ""
    },
    {
      "character": "BOT_RESPONSE_CONVERSATION",
      "content": "Quả là một hành trình thú vị từ sao Hỏa."
    }
  ],
  "end_time": "2025-11-26T10:20:00Z",
  "start_time": "2025-11-26T10:00:00Z",
  "status": "PENDING"
}'
```

```bash
{

    "success": true,

    "message": "Conversation event accepted for processing",

    "data": {

        "id": 117,

        "conversation_id": "convc_1cxxcc23__",

        "user_id": "user_doanngoccuong",

        "bot_type": "dd",

        "bot_id": "agent_pet",

        "bot_name": "Movie Preference Talk",

        "start_time": "2025-11-26T10:00:00",

        "end_time": "2025-11-26T10:20:00",

        "duration_seconds": 1200,

        "conversation_log": [

            {

                "text": "BEEP BEEP! Đã đến Trái Đất!",

                "speaker": "pika",

                "turn_id": 1,

                "timestamp": "2025-11-26T10:05:00+00:00Z"

            },

            {

                "text": "Quả là một hành trình thú vị từ sao Hỏa.",

                "speaker": "pika",

                "turn_id": 2,

                "timestamp": "2025-11-26T10:15:00+00:00Z"

            }

        ],

        "raw_conversation_log": [

            {

                "content": "",

                "character": "BOT_RESPONSE_CONVERSATION"

            },

            {

                "content": "BEEP BEEP! Đã đến Trái Đất!",

                "character": "BOT_RESPONSE_CONVERSATION"

            },

            {

                "content": "",

                "character": "BOT_RESPONSE_CONVERSATION"

            },

            {

                "content": "Quả là một hành trình thú vị từ sao Hỏa.",

                "character": "BOT_RESPONSE_CONVERSATION"

            }

        ],

        "status": "PROCESSED",

        "attempt_count": 1,

        "created_at": "2025-11-27T17:22:15.224609",

        "next_attempt_at": "2025-11-27T17:22:17.488880",

        "processed_at": "2025-11-27T17:22:17.488880",

        "error_code": null,

        "error_details": null,

        "friendship_score_change": 0.5,

        "new_friendship_level": "PHASE1_STRANGER",

        "updated_at": "2025-11-27T17:22:17.488880"

    }

}
```
