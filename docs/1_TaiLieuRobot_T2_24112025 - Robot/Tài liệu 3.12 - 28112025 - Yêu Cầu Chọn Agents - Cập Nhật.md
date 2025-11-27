# Yêu Cầu Chọn Agents - Cập Nhật
## Context Handling Module - Agent Selection Logic

**Phiên bản:** 2.0  
**Ngày:** 27/11/2025  
**Trạng thái:** Cập nhật requirements lấy 1 GREETING + 3 TALK + 2 GAME

---

## 📋 THAY ĐỔI CHÍNH

### Cũ (v1)
```
Lấy: 1 GREETING + 4 Talk/Game (không rõ tỷ lệ)
```

### Mới (v2)
```
Lấy: 1 GREETING + 3 TALK + 2 GAME
     (Tổng cộng 6 agents)
```

---

## 🎯 REQUIREMENTS CHI TIẾT

### 1️⃣ GREETING AGENT (1 cái)

**Mục đích:** Chào hỏi user khi mở app

**Quy trình chọn (Priority-Based):**

```
BƯỚC 1: Check điều kiện đặc biệt
  ├─ Hôm nay là sinh nhật? → Chọn GREETING_BIRTHDAY
  ├─ Lâu không tương tác (> 7 ngày)? → Chọn GREETING_RETURNING
  ├─ Cảm xúc hôm qua tiêu cực? → Chọn GREETING_EMOTION_CHECK
  └─ Có topic chưa follow up? → Chọn GREETING_TOPIC_FOLLOWUP

BƯỚC 2: Nếu không có điều kiện nào
  └─ Chọn ngẫu nhiên từ kho GREETING của phase hiện tại
     (Ưu tiên: chưa dùng gần đây)

BƯỚC 3: Đảm bảo phù hợp với friendship_level
  └─ PHASE1_STRANGER: Chỉ dùng greeting đơn giản
  └─ PHASE2_ACQUAINTANCE: Greeting bình thường
  └─ PHASE3_FRIEND: Greeting thân thiết
```

**Ví dụ:**
```
User: user_1234
Friendship_level: PHASE2_ACQUAINTANCE
Last_interaction: 2 ngày trước
Last_emotion: neutral
Last_followup_topic: movie

Kết quả: GREETING_NORMAL (không có điều kiện đặc biệt)
```

---

### 2️⃣ TALK AGENTS (3 cái)

**Mục đích:** Nói chuyện với user về các topics

**Quy trình chọn:**

```
BƯỚC 1: Tạo danh sách ứng viên (Candidate List)
  
  ├─ Ứng viên sở thích (Preference)
  │  └─ Lấy 2 agents có topic_score cao nhất
  │     (Từ topic_metric của user)
  │
  ├─ Ứng viên khám phá (Exploration)
  │  └─ Lấy 1 agent ngẫu nhiên từ kho TALK
  │     (Mà user ít tương tác - turns thấp)
  │
  └─ Ứng viên cảm xúc (Emotion-Based)
     └─ Nếu last_emotion = tiêu cực
        → Thêm TALK agents vui vẻ, hài hước

BƯỚC 2: Chọn 3 agents từ danh sách ứng viên
  ├─ Ưu tiên: Sở thích (2 agents)
  ├─ Tiếp theo: Khám phá (1 agent)
  └─ Nếu cảm xúc tiêu cực: Thay 1 cái bằng emotion-based

BƯỚC 3: Đảm bảo phù hợp với friendship_level
  └─ Chỉ lấy agents có friendship_level <= user's friendship_level

BƯỚC 4: Chống lặp nội dung
  └─ Không chọn 2 agents cùng topic
  └─ Không chọn 2 agents cùng hỏi cảm xúc
  └─ Không chọn 2 agents cùng loại hỏi
```

**Ví dụ:**
```
User: user_1234
Friendship_level: PHASE2_ACQUAINTANCE
Topic_metric: {
  "movie": {score: 120, turns: 150},
  "toy": {score: 0, turns: 0},
  "school": {score: 40, turns: 30}
}
Last_emotion: neutral

Ứng viên sở thích:
  - agent_movie_talk_1 (score: 120)
  - agent_school_talk_1 (score: 40)

Ứng viên khám phá:
  - agent_toy_talk_1 (turns: 0)

Chọn 3 TALK agents:
  1. agent_movie_talk_1 (sở thích)
  2. agent_school_talk_1 (sở thích)
  3. agent_toy_talk_1 (khám phá)
```

---

### 3️⃣ GAME/ACTIVITY AGENTS (2 cái)

**Mục đích:** Chơi game hoặc hoạt động với user

**Quy trình chọn:**

```
BƯỚC 1: Lọc kho GAME theo friendship_level
  ├─ PHASE1_STRANGER: Game đơn giản
  ├─ PHASE2_ACQUAINTANCE: Game cá nhân hóa
  └─ PHASE3_FRIEND: Game dự án chung

BƯỚC 2: Tạo danh sách ứng viên
  ├─ Ứng viên phổ biến
  │  └─ Lấy 2 games có play_count cao nhất
  │
  ├─ Ứng viên chưa chơi
  │  └─ Lấy games chưa chơi (play_count = 0)
  │
  └─ Ứng viên cảm xúc
     └─ Nếu last_emotion = tiêu cực
        → Thêm games vui vẻ, hài hước

BƯỚC 3: Chọn 2 games từ danh sách ứng viên
  ├─ Ưu tiên: Phổ biến (1-2 games)
  └─ Tiếp theo: Chưa chơi (1 game)

BƯỚC 4: Đảm bảo đa dạng
  └─ Không chọn 2 games cùng loại
  └─ Không chọn 2 games cùng độ khó

BƯỚC 5: Chống lặp với TALK agents
  └─ Không chọn game về topic giống TALK agents
```

**Ví dụ:**
```
User: user_1234
Friendship_level: PHASE2_ACQUAINTANCE
Last_emotion: neutral

Kho GAME (PHASE2):
  - game_puzzle_1 (play_count: 50)
  - game_word_1 (play_count: 30)
  - game_drawing_1 (play_count: 0)
  - game_story_1 (play_count: 0)

Ứng viên phổ biến:
  - game_puzzle_1 (50)
  - game_word_1 (30)

Ứng viên chưa chơi:
  - game_drawing_1 (0)
  - game_story_1 (0)

Chọn 2 GAME agents:
  1. game_puzzle_1 (phổ biến)
  2. game_drawing_1 (chưa chơi)
```

---

## 🔄 COMPLETE WORKFLOW

### Input
```json
{
  "user_id": "user_1234"
}
```

### Process

```
STEP 1: Lấy friendship_status
  ├─ friendship_level: PHASE2_ACQUAINTANCE
  ├─ topic_metric: {...}
  ├─ last_emotion: neutral
  └─ last_followup_topic: movie

STEP 2: Chọn 1 GREETING
  └─ GREETING_NORMAL (không có điều kiện đặc biệt)

STEP 3: Chọn 3 TALK agents
  ├─ agent_movie_talk_1 (sở thích)
  ├─ agent_school_talk_1 (sở thích)
  └─ agent_toy_talk_1 (khám phá)

STEP 4: Chọn 2 GAME agents
  ├─ game_puzzle_1 (phổ biến)
  └─ game_drawing_1 (chưa chơi)

STEP 5: Chống lặp nội dung
  ├─ Kiểm tra không có 2 agents cùng topic
  ├─ Kiểm tra không có 2 agents cùng loại hỏi
  └─ Kiểm tra game không trùng topic TALK

STEP 6: Sắp xếp kết quả
  └─ [GREETING, TALK_1, TALK_2, TALK_3, GAME_1, GAME_2]
```

### Output
```json
{
  "user_id": "user_1234",
  "greeting_agent": {
    "agent_id": "greeting_normal_1",
    "agent_type": "GREETING",
    "agent_name": "Greeting Normal",
    "reason": "No special condition"
  },
  "talk_agents": [
    {
      "agent_id": "agent_movie_talk_1",
      "agent_type": "TALK",
      "agent_name": "Movie Talk 1",
      "topic_id": "movie",
      "reason": "High preference"
    },
    {
      "agent_id": "agent_school_talk_1",
      "agent_type": "TALK",
      "agent_name": "School Talk 1",
      "topic_id": "school",
      "reason": "High preference"
    },
    {
      "agent_id": "agent_toy_talk_1",
      "agent_type": "TALK",
      "agent_name": "Toy Talk 1",
      "topic_id": "toy",
      "reason": "Exploration (low turns)"
    }
  ],
  "game_agents": [
    {
      "agent_id": "game_puzzle_1",
      "agent_type": "GAME_ACTIVITY",
      "agent_name": "Puzzle Game",
      "reason": "Popular"
    },
    {
      "agent_id": "game_drawing_1",
      "agent_type": "GAME_ACTIVITY",
      "agent_name": "Drawing Game",
      "reason": "Not played yet"
    }
  ],
  "total_agents": 6,
  "selection_timestamp": "2025-11-27T10:00:00Z"
}
```

---

## 📊 COMPARISON: Old vs New

| Aspect | Cũ (v1) | Mới (v2) |
| :--- | :--- | :--- |
| **GREETING** | 1 | 1 |
| **TALK** | Không rõ | 3 |
| **GAME** | Không rõ | 2 |
| **Total** | 5 (1+4) | 6 (1+3+2) |
| **Tỷ lệ Talk:Game** | Không rõ | 3:2 (60:40) |

---

## 🛠️ IMPLEMENTATION CHECKLIST

### Phase 1: Database
- [ ] Thêm cột `play_count` vào bảng agents
- [ ] Thêm cột `agent_difficulty` vào bảng agents
- [ ] Thêm cột `agent_category` vào bảng agents

### Phase 2: Service Layer
- [ ] Implement `select_greeting_agent(user_id)`
- [ ] Implement `select_talk_agents(user_id, count=3)`
- [ ] Implement `select_game_agents(user_id, count=2)`
- [ ] Implement `validate_no_duplicate_content(agents)`
- [ ] Implement `suggest_activities(user_id)` - main function

### Phase 3: API
- [ ] Endpoint: `POST /v1/activities/suggest`
  - Input: `{user_id}`
  - Output: `{greeting_agent, talk_agents, game_agents}`

### Phase 4: Testing
- [ ] Unit tests cho mỗi selection function
- [ ] Integration tests cho complete workflow
- [ ] Edge case tests (user mới, user cũ, etc.)

---

## 💾 SQL SCHEMA UPDATES

### Thêm cột vào agents table

```sql
ALTER TABLE prompt_template_for_level_friendship ADD COLUMN (
    play_count INTEGER DEFAULT 0,
    agent_difficulty VARCHAR(50) DEFAULT 'MEDIUM',
    agent_category VARCHAR(50),
    last_played_at TIMESTAMP,
    success_rate FLOAT DEFAULT 0.0
);

-- Indexes
CREATE INDEX idx_agent_play_count ON prompt_template_for_level_friendship(play_count);
CREATE INDEX idx_agent_difficulty ON prompt_template_for_level_friendship(agent_difficulty);
CREATE INDEX idx_agent_category ON prompt_template_for_level_friendship(agent_category);
```

---

## 🔍 VALIDATION RULES

### Chống Lặp Nội Dung

```python
def validate_no_duplicate_content(agents):
    """
    Kiểm tra:
    1. Không có 2 agents cùng topic
    2. Không có 2 agents cùng loại hỏi
    3. Không có 2 agents cùng difficulty
    """
    
    topics = [a.topic_id for a in agents]
    if len(topics) != len(set(topics)):
        raise DuplicateTopicError()
    
    question_types = [a.question_type for a in agents]
    if len(question_types) != len(set(question_types)):
        raise DuplicateQuestionTypeError()
    
    return True
```

---

## 📈 METRICS TO TRACK

```
- Greeting selection rate (by type)
- Talk agent selection rate (by topic)
- Game agent selection rate (by difficulty)
- User engagement by agent type
- Agent popularity (play_count)
- Success rate by agent
```

---

## 🎯 SUMMARY

| Item | Requirement |
| :--- | :--- |
| **GREETING** | 1 agent (priority-based selection) |
| **TALK** | 3 agents (2 preference + 1 exploration) |
| **GAME** | 2 agents (1 popular + 1 new) |
| **Total** | 6 agents |
| **Validation** | No duplicate content |
| **Caching** | 12h TTL |
| **Update** | Real-time (after each conversation) |

---

**Tài liệu requirements cập nhật sẵn sàng!** 🚀
