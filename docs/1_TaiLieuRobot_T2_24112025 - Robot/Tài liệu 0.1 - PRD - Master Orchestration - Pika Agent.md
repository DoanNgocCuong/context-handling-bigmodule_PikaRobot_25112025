'''

# PRD: Master Orchestration

**Version:** 1.0 **Date:** 24/11/2025

---

## 1. Introduction

### 1.1. Problem Statement

Trải nghiệm học tập hiện tại của Pika đang đi theo một lộ trình tương đối cố định, thiếu khả năng thích ứng sâu với nhu cầu, cảm xúc, và tiến độ học tập riêng của từng trẻ. Điều này dẫn đến nguy cơ trẻ cảm thấy nhàm chán (nếu nội dung quá dễ), nản lòng (nếu nội dung quá khó), hoặc mất kết nối (nếu các hoạt động không phù hợp với sở thích). Chúng ta cần một "bộ não" thông minh hơn để hoạch định một kế hoạch học tập hàng ngày thực sự được cá nhân hóa, giúp tối ưu hóa sự hứng thú và hiệu quả học tập.

### 1.2. Proposed Solution: Master Orchestration

**Master Orchestration** là một LLM-based Agent, đóng vai trò là bộ não hoạch định chiến lược của toàn bộ hệ thống. Nhiệm vụ chính của nó là xây dựng một **kế hoạch hoạt động hàng ngày (Daily Activities List)** được cá nhân hóa cho mỗi người dùng vào đầu mỗi ngày. Bằng cách phân tích đa dạng các nguồn dữ liệu (tiến độ học tập, mức độ thân thiết, sở thích cá nhân), Master Orchestration sẽ tạo ra một chuỗi các hoạt động học tập (Learn), vui chơi (Game), và trò chuyện (Talk) tối ưu nhất cho từng trẻ, trong ngày hôm đó.

## 2. Goals and Objectives

| Goal | Objective | Metrics (KPIs) |
| --- | --- | --- |
| **Tăng cường sự hứng thú (Engagement)** | Xây dựng một lộ trình hàng ngày cân bằng giữa học và chơi, phù hợp với sở thích của trẻ. | - Tăng thời gian trung bình của phiên học (Session Duration).
- Tăng tỷ lệ hoàn thành các hoạt động trong Daily Activities List. |
| **Tối ưu hóa hiệu quả học tập (Learning Efficacy)** | Tự động điều chỉnh độ khó và nội dung học tập dựa trên hiệu suất của trẻ. | - Tăng tỷ lệ trả lời đúng trong các Learn Agent.
- Giảm thời gian cần thiết để hoàn thành một cấp độ học (Level Completion Time). |
| **Cá nhân hóa trải nghiệm ở quy mô lớn (Personalization at Scale)** | Cung cấp một kế hoạch học tập độc nhất cho mỗi trẻ, mỗi ngày. | - Tăng điểm hài lòng của người dùng (User Satisfaction Score).
- Giảm tỷ lệ người dùng rời bỏ (Churn Rate). |

## 3. Scope

### 3.1. In Scope

- Logic thu thập và xử lý dữ liệu đầu vào (Learning-Status, Buddy-Status, User Profile).

- Logic của LLM-based Agent (Reasoning Engine) để đưa ra quyết định dựa trên Guiding Principles.

- Logic xây dựng và cấu trúc của Daily Activities List (output).

- Định nghĩa các loại activity có thể được đưa vào danh sách (`LearnWorkflow`, `LearnAgent`, `TalkAgent`, `GameAgent`).

- Logic cho Version 1 (xây dựng danh sách dựa trên quy tắc cứng).

### 3.2. Out of Scope

- **Cơ chế thực thi** Daily Activities List (thuộc về **Orchestration Agent**).

- **Cơ chế xử lý trigger** trong thời gian thực (thuộc về **Trigger Agent**).

- Chi tiết triển khai của các Agent/Workflow cụ thể (ví dụ: nội dung của một `LearnAgent`).



## 4. System Overview and User Flow

Master Orchestration là component khởi đầu của chuỗi điều phối, hoạt động trước khi người dùng bắt đầu phiên học. Nó không tương tác trực tiếp với người dùng mà cung cấp "kế hoạch tác chiến" cho Orchestration Agent.

### 4.1. High-Level Architecture

```mermaid
flowchart TD
    subgraph Master Orchestration
        direction LR
        A[Context Provider] --> B{Reasoning Engine  
(LLM-based Agent)};
        B --> C[Daily Activity List Builder];
    end

    subgraph Data Sources
        D[Learning-Status DB];
        E[Buddy-Status DB];
        F[User Profile  
(Mem0)];
    end

    subgraph Orchestration Agent
        G[Queue Management];
    end

    D --> A;
    E --> A;
    F --> A;
    C --> G;
```

**Luồng dữ liệu cấp cao:**

1. **Context Provider** thu thập dữ liệu từ các nguồn khác nhau.

2. **Reasoning Engine** nhận dữ liệu này, áp dụng các **Guiding Principles** để đưa ra một kế hoạch chiến lược.

3. **Daily Activity List Builder** nhận kế hoạch và định dạng nó thành một cấu trúc dữ liệu chuẩn.

4. Danh sách này được chuyển cho **Queue Management** (thuộc Orchestration Agent) để bắt đầu quá trình thực thi.

### 4.2. User Flow

Từ góc độ người dùng, họ không thấy Master Orchestration hoạt động. Họ chỉ trải nghiệm kết quả của nó thông qua một lộ trình học tập được cá nhân hóa mỗi ngày.

*Sơ đồ User Flow chi tiết sẽ được trình bày ở mục 6.* '''

## 5. Component Deep Dive

### 5.1. Context Provider

**Chức năng:** Thu thập và tổng hợp tất cả dữ liệu cần thiết từ các nguồn khác nhau để cung cấp một bức tranh toàn cảnh về người dùng cho Reasoning Engine.

**Input:** `user_id`

**Logic Xử Lý:**

1. **Query Learning-Status DB:** Lấy thông tin về tiến độ học tập của `user_id`.
  - `current_lesson_id`: ID của bài học gần nhất mà trẻ đã học.
  - `last_session_performance`: Một bản tóm tắt về hiệu suất của phiên học trước (ví dụ: `{accuracy: 0.75, common_mistakes: ["past_tense"], time_spent: 25}`).

1. **Query Friendship-Status DB:** Lấy toàn bộ bản ghi `friendship_status` của `user_id`. Đây là nguồn dữ liệu cốt lõi về mối quan hệ và sở thích của trẻ.
  - `friendship_score`: Điểm số tổng thể đo lường mức độ thân thiết.
  - `friendship_level`: Cấp độ tình bạn (`STRANGER`, `ACQUAINTANCE`, `FRIEND`).
  - `last_interaction_date`: Dấu thời gian của lần tương tác cuối cùng.
  - `streak_day`: Số ngày tương tác liên tiếp.
  - `topic_metrics`: Điểm và lịch sử tương tác cho từng chủ đề.
  - `dynamic_memory`: Danh sách các "ký ức chung" giữa Pika và người dùng.

1. **Query User Profile (Mem0):** Lấy các thông tin cá nhân hóa dài hạn.
  - `preferences`: Sở thích của trẻ (ví dụ: `{topics: ["animals", "space"], activity_types: ["games", "stories"]}`).
  - `strengths`: Các điểm mạnh (ví dụ: `["vocabulary"]`).
  - `weaknesses`: Các điểm yếu cần cải thiện (ví dụ: `["pronunciation_s_sound"]`).
  - `emotional_state`: Trạng thái cảm xúc được ghi nhận gần đây (ví dụ: `"happy"`).

**Output:** Một đối tượng JSON (JSON object) duy nhất chứa tất cả thông tin trên, sẵn sàng để đưa vào prompt của LLM.

**Ví dụ Output của Context Provider:**

```json
{
  "learning_status": {
    "current_lesson_id": "L1_U2_A3",
    "last_session_performance": {
      "accuracy": 0.6,
      "common_mistakes": ["present_perfect_tense"],
      "time_spent": 22
    }
  },{
  "friendship_status": {
    "user_id": "user_123",
    "friendship_score": 750.5,
    "friendship_level": "ACQUAINTANCE",
    "last_interaction_date": "2025-11-23T15:00:00Z",
    "streak_day": 5,
    "topic_metrics": {
      "agent_movie": { "topic_score": 45.0, "last_talked_date": "2025-11-24T10:20:00Z" },
      "agent_animal": { "topic_score": 22.5, "last_talked_date": "2025-11-20T09:00:00Z" }
    },
    "dynamic_memory": [
      { "memory_id": "mem_01", "content": "Hứa sẽ cùng nhau xem phim 'Vùng Đất Linh Hồn'." },
      { "memory_id": "mem_02", "content": "Kể rằng thú cưng của bạn ấy là một chú chó tên là 'Milu'." }
    ]
  },  "user_profile": {
    "preferences": {
      "topics": ["dinosaurs", "music"],
      "activity_types": ["games"]
    },
    "strengths": ["listening_comprehension"],
    "weaknesses": ["irregular_verbs"],
    "emotional_state": "neutral"
  }
}
```

### 5.2. Reasoning Engine (LLM-based Agent)

**Chức năng:** Là trái tim của Master Orchestration, sử dụng LLM để "suy nghĩ" và đưa ra một kế hoạch hoạt động chiến lược dựa trên dữ liệu từ Context Provider và các nguyên tắc sư phạm.

**Input:** Đối tượng JSON từ Context Provider.

**Logic Xử Lý:**

1. **Prompt Construction:** Xây dựng một prompt chi tiết cho LLM.
  - **Phần 1: Bối cảnh (Context):** Chèn toàn bộ đối tượng JSON từ Context Provider vào prompt.
  - **Phần 2: Nguyên tắc chỉ đạo (Guiding Principles):** Chèn "10 Nguyên Tắc Vàng của Master Orchestration" (đã định nghĩa ở mục 4.2.1 trong tài liệu kiến trúc) vào prompt.
  - **Phần 3: Yêu cầu (Instruction):** Ra lệnh cho LLM tạo ra một kế hoạch hoạt động cho ngày hôm nay dưới dạng một danh sách có lý do đi kèm.

**Ví dụ một phần của Prompt:**

```
Here is the user's current context:
{{CONTEXT_JSON}}

Based on this context and the following 10 Guiding Principles, create a strategic daily plan of activities. For each activity, provide the type and a brief rationale.

Guiding Principles:
1. Prioritize core learning goals...
...
2. Optimize for a 20-25 minute session.

Output your plan as a JSON array of objects, where each object has "activity_type" and "rationale".
```

1. **LLM Inference:** Gửi prompt đến LLM và nhận lại kết quả.

**Output:** Một danh sách các hoạt động ở mức cao, kèm theo lý do tại sao LLM chọn chúng.

**Ví dụ Output của Reasoning Engine:**

```json
[
  {
    "activity_type": "GreetingAgent",
    "rationale": "Standard start for every session."
  },
  {
    "activity_type": "LearnAgent",
    "rationale": "User struggled with irregular verbs last session. This activity will focus on reviewing them."
  },
  {
    "activity_type": "GameAgent",
    "rationale": "User loves games and dinosaurs. A dinosaur-themed game will boost engagement after a learning session."
  },
  {
    "activity_type": "LearnWorkflow",
    "rationale": "Continue the main curriculum path after the review."
  },
  {
    "activity_type": "TalkAgent",
    "rationale": "End the session with a light conversation to strengthen the buddy relationship."
  }
]
```

### 5.3. Daily Activity List Builder

**Chức năng:** Chuyển đổi kế hoạch chiến lược từ Reasoning Engine thành một danh sách các hoạt động cụ thể, có thể thực thi được, với đầy đủ ID và priority.

**Input:** Mảng JSON từ Reasoning Engine.

**Logic Xử Lý:**

1. **Iterate through the plan:** Lặp qua từng hoạt động trong kế hoạch của LLM.

2. **Resolve Activity ID:** Với mỗi `activity_type`, tìm `activity_id` cụ thể.
  - Nếu `activity_type` là `LearnWorkflow` hoặc `LearnAgent` liên quan đến lộ trình chính: Gọi API của Backend (`/getNextLesson`) để lấy `lesson_id`.
  - Nếu `activity_type` là `LearnAgent` để ôn tập: Gọi API của Backend (`/getReviewLesson?topic=irregular_verbs`) để lấy `lesson_id` phù hợp.
  - Nếu `activity_type` là `TalkAgent` hoặc `GameAgent`: Gọi **Talk/Game Management Module** với context (ví dụ: `topic: "dinosaurs"`) để module này chọn ra `agent_id` phù hợp nhất.

1. **Assign Priority:** Gán một mức độ ưu tiên (priority) cho mỗi hoạt động. Trong V1, logic này là cố định theo thứ tự.

2. **Build Final List:** Tạo ra danh sách cuối cùng.

**Logic Xử Lý (Version 1 - Quy tắc cứng):**

- Bỏ qua output của Reasoning Engine.

- **Bước 1:** Lấy `GreetingAgent` (P:10).

- **Bước 2:** Gọi API Backend (`/getNextLesson`) để lấy `LearnWorkflow` (P:9).

- **Bước 3:** Gọi Talk/Game Management để lấy `TalkAgent` hoặc `GameAgent` (P:8).

- **Bước 4:** Gọi API Backend (`/getNextLesson`) để lấy `LearnWorkflow` tiếp theo (P:7).

- **Bước 5:** Gọi Talk/Game Management để lấy `TalkAgent` hoặc `GameAgent` (P:6).

**Output:** Mảng JSON cuối cùng của `Daily Activities List`.

**Ví dụ Output của Daily Activity List Builder:**

```json
[
  {
    "activity_type": "GreetingAgent",
    "activity_id": "agent_greeting_v2",
    "priority": 10
  },
  {
    "activity_type": "LearnAgent",
    "activity_id": "lesson_review_irregular_verbs_01",
    "priority": 9
  },
  {
    "activity_type": "GameAgent",
    "activity_id": "game_dino_quiz_4",
    "priority": 8
  },
  {
    "activity_type": "LearnWorkflow",
    "activity_id": "L1_U2_A4",
    "priority": 7
  },
  {
    "activity_type": "TalkAgent",
    "activity_id": "agent_daily_chat_music_topic",
    "priority": 6
  }
]
```

## 6. User Flow and Data Flow

### 6.1. Data Flow Diagram

Sơ đồ dưới đây minh họa luồng dữ liệu chi tiết qua các components của Master Orchestration, từ khi nhận trigger "ngày mới" cho đến khi tạo ra Daily Activities List.

![Data Flow Diagram](master_orch_dataflow.png)

**Giải thích các bước chính:**

1. **Context Provider** thu thập dữ liệu từ ba nguồn: Learning-Status DB, Buddy-Status DB, và User Profile (Mem0).

2. Dữ liệu được tổng hợp thành một Context JSON duy nhất.

3. **Reasoning Engine** nhận Context JSON, xây dựng prompt với Guiding Principles, và gọi LLM API.

4. LLM trả về một kế hoạch chiến lược (Strategic Plan) với lý do đi kèm.

5. **Daily Activity List Builder** nhận kế hoạch. Trong Version 1, nó áp dụng logic cứng và bỏ qua chi tiết từ LLM.

6. Builder gọi Backend API để lấy `lesson_id` và gọi Talk/Game Management để lấy `agent_id`.

7. Builder xây dựng danh sách cuối cùng với đầy đủ ID và priority.

8. Danh sách được gửi đến **Queue Management** để sẵn sàng thực thi.

### 6.2. User Flow (Sequence Diagram)

Sơ đồ tuần tự dưới đây minh họa cách các components tương tác với nhau theo thời gian, từ góc độ hệ thống.

![User Flow Sequence Diagram](master_orch_userflow.png)

**Các bước chính trong Sequence:**

1. **System Scheduler** kích hoạt Master Orchestration vào đầu ngày (00:00 AM).

2. Master Orchestration yêu cầu Context Provider thu thập dữ liệu.

3. Context Provider truy vấn tuần tự từng database và tổng hợp kết quả.

4. Reasoning Engine nhận Context JSON, xây dựng prompt, và gọi LLM.

5. LLM phân tích và trả về một kế hoạch chiến lược.

6. Daily Activity List Builder áp dụng logic Version 1, gọi Backend API và Talk/Game Management để lấy ID cụ thể.

7. Builder xây dựng danh sách cuối cùng và gửi đến Queue Management.

8. Master Orchestration thông báo cho System rằng kế hoạch đã được tạo thành công.

## 7. Examples and Use Cases

### 7.1. Example 1: Trẻ Có Hiệu Suất Học Tập Tốt

**Context Input:**

```json
{
  "learning_status": {
    "current_lesson_id": "L2_U1_A5",
    "last_session_performance": {
      "accuracy": 0.9,
      "common_mistakes": [],
      "time_spent": 18
    }
  },
  "buddy_status": {
    "buddy_level": 7,
    "last_interaction_timestamp": "2025-11-23T16:00:00Z"
  },
  "user_profile": {
    "preferences": {
      "topics": ["space", "robots"],
      "activity_types": ["stories", "games"]
    },
    "strengths": ["vocabulary", "pronunciation"],
    "weaknesses": [],
    "emotional_state": "excited"
  }
}
```

**Reasoning Engine Output (Ví dụ từ LLM):**

```json
[
  {
    "activity_type": "GreetingAgent",
    "rationale": "Standard greeting to start the session."
  },
  {
    "activity_type": "LearnWorkflow",
    "rationale": "User is performing well. Continue with the next lesson in the main curriculum."
  },
  {
    "activity_type": "GameAgent",
    "rationale": "User loves games and is excited. A space-themed game will maintain high engagement."
  },
  {
    "activity_type": "LearnWorkflow",
    "rationale": "User can handle more learning content. Introduce a new topic."
  },
  {
    "activity_type": "TalkAgent",
    "rationale": "End with a conversation about robots to align with user's interests and strengthen buddy relationship."
  }
]
```

**Daily Activities List Output (Version 1):**

```json
[
  {"activity_type": "GreetingAgent", "activity_id": "agent_greeting_v2", "priority": 10},
  {"activity_type": "LearnWorkflow", "activity_id": "L2_U1_A6", "priority": 9},
  {"activity_type": "GameAgent", "activity_id": "game_space_explorer_2", "priority": 8},
  {"activity_type": "LearnWorkflow", "activity_id": "L2_U1_A7", "priority": 7},
  {"activity_type": "TalkAgent", "activity_id": "agent_daily_chat_robots_topic", "priority": 6}
]
```

### 7.2. Example 2: Trẻ Gặp Khó Khăn Trong Học Tập

**Context Input:**

```json
{
  "learning_status": {
    "current_lesson_id": "L1_U3_A2",
    "last_session_performance": {
      "accuracy": 0.4,
      "common_mistakes": ["pronunciation_th_sound", "vocabulary_confusion"],
      "time_spent": 30
    }
  },
  "buddy_status": {
    "buddy_level": 3,
    "last_interaction_timestamp": "2025-11-22T09:00:00Z"
  },
  "user_profile": {
    "preferences": {
      "topics": ["animals"],
      "activity_types": ["games"]
    },
    "strengths": [],
    "weaknesses": ["pronunciation_th_sound"],
    "emotional_state": "frustrated"
  }
}
```

**Reasoning Engine Output (Ví dụ từ LLM):**

```json
[
  {
    "activity_type": "GreetingAgent",
    "rationale": "Start with a warm greeting to lift the mood."
  },
  {
    "activity_type": "LearnAgent",
    "rationale": "User struggled with pronunciation. A focused review session on 'th' sound is needed."
  },
  {
    "activity_type": "GameAgent",
    "rationale": "User is frustrated. An animal-themed game will help reduce stress and re-engage."
  },
  {
    "activity_type": "LearnWorkflow",
    "rationale": "After the review and game, user should be ready to continue with a lighter lesson."
  },
  {
    "activity_type": "TalkAgent",
    "rationale": "End with a supportive conversation to rebuild confidence and strengthen the buddy bond."
  }
]
```

**Daily Activities List Output (Version 1):**

```json
[
  {"activity_type": "GreetingAgent", "activity_id": "agent_greeting_v2", "priority": 10},
  {"activity_type": "LearnAgent", "activity_id": "lesson_review_pronunciation_th", "priority": 9},
  {"activity_type": "GameAgent", "activity_id": "game_animal_sounds_3", "priority": 8},
  {"activity_type": "LearnWorkflow", "activity_id": "L1_U3_A3", "priority": 7},
  {"activity_type": "TalkAgent", "activity_id": "agent_encouragement_chat", "priority": 6}
]
```

### 7.3. Example 3: Trẻ Không Vào Học Trong 3 Ngày

**Context Input:**

```json
{
  "learning_status": {
    "current_lesson_id": "L1_U2_A8",
    "last_session_performance": {
      "accuracy": 0.7,
      "common_mistakes": ["simple_past_tense"],
      "time_spent": 20
    }
  },
  "buddy_status": {
    "buddy_level": 5,
    "last_interaction_timestamp": "2025-11-20T10:00:00Z"
  },
  "user_profile": {
    "preferences": {
      "topics": ["sports", "food"],
      "activity_types": ["games", "stories"]
    },
    "strengths": ["listening_comprehension"],
    "weaknesses": ["simple_past_tense"],
    "emotional_state": "neutral"
  }
}
```

**Reasoning Engine Output (Ví dụ từ LLM):**

```json
[
  {
    "activity_type": "GreetingAgent",
    "rationale": "Welcome the user back after a long absence."
  },
  {
    "activity_type": "TalkAgent",
    "rationale": "Start with a light conversation about sports to re-engage and rebuild the connection."
  },
  {
    "activity_type": "GameAgent",
    "rationale": "A fun food-themed game will help ease the user back into learning."
  },
  {
    "activity_type": "LearnWorkflow",
    "rationale": "After warming up, introduce a light review of the last lesson."
  },
  {
    "activity_type": "TalkAgent",
    "rationale": "End with an encouraging conversation to motivate the user to return tomorrow."
  }
]
```

**Daily Activities List Output (Version 1):**

```json
[
  {"activity_type": "GreetingAgent", "activity_id": "agent_greeting_welcome_back", "priority": 10},
  {"activity_type": "TalkAgent", "activity_id": "agent_daily_chat_sports_topic", "priority": 9},
  {"activity_type": "GameAgent", "activity_id": "game_food_quiz_1", "priority": 8},
  {"activity_type": "LearnWorkflow", "activity_id": "L1_U2_A8_review", "priority": 7},
  {"activity_type": "TalkAgent", "activity_id": "agent_encouragement_return", "priority": 6}
]
```

## 8. Edge Cases and Error Handling

### 8.1. Edge Case 1: Context Provider Không Lấy Được Dữ Liệu

**Scenario:** Một trong các database (Learning-Status, Buddy-Status, hoặc Mem0) không phản hồi hoặc trả về lỗi.

**Handling:**

- Context Provider sẽ sử dụng **giá trị mặc định (default values)** cho phần dữ liệu bị thiếu.

- Ví dụ: Nếu Mem0 không phản hồi, sử dụng `preferences: {topics: ["general"], activity_types: ["learn"]}`.

- Ghi log lỗi để team kỹ thuật điều tra.

- Master Orchestration vẫn tiếp tục tạo danh sách, nhưng sẽ thiên về một kế hoạch "an toàn" hơn (ít cá nhân hóa hơn).

### 8.2. Edge Case 2: LLM Trả Về Kết Quả Không Hợp Lệ

**Scenario:** Reasoning Engine gọi LLM, nhưng LLM trả về một JSON không đúng format hoặc chứa các `activity_type` không hợp lệ.

**Handling:**

- Daily Activity List Builder sẽ kiểm tra (validate) output của LLM.

- Nếu không hợp lệ, Builder sẽ **fallback về logic cứng của Version 1** và ghi log cảnh báo.

- Đảm bảo hệ thống luôn tạo ra một danh sách hợp lệ, ngay cả khi LLM thất bại.

### 8.3. Edge Case 3: Backend API Không Trả Về Lesson ID

**Scenario:** Khi Daily Activity List Builder gọi `/getNextLesson`, API trả về lỗi hoặc không có bài học tiếp theo (ví dụ: trẻ đã hoàn thành toàn bộ lộ trình).

**Handling:**

- Builder sẽ thay thế `LearnWorkflow` bằng một `ReviewAgent` (ôn tập các bài học trước).

- Hoặc, nếu không có bài ôn tập, thay thế bằng một `TalkAgent` hoặc `GameAgent` bổ sung.

- Ghi log để Product Team biết và lên kế hoạch mở rộng nội dung.

### 8.4. Edge Case 4: Talk/Game Management Không Trả Về Agent ID

**Scenario:** Module Talk/Game Management không tìm được agent phù hợp với sở thích của trẻ.

**Handling:**

- Module sẽ trả về một **agent mặc định** (ví dụ: `agent_daily_chat_general` hoặc `game_general_quiz`).

- Đảm bảo danh sách luôn có đủ hoạt động, ngay cả khi không tối ưu về cá nhân hóa.

## 9. Success Metrics and Acceptance Criteria

### 9.1. Success Metrics

| Metric | Target | Measurement Method |
| --- | --- | --- |
| **Daily Activities List Creation Success Rate** | > 99.5% | Tỷ lệ số lần Master Orchestration tạo thành công danh sách / tổng số lần được trigger. |
| **Average Latency** | < 3 giây | Thời gian từ khi nhận trigger đến khi gửi danh sách đến Queue Management. |
| **Personalization Score** | > 70% | Tỷ lệ các hoạt động trong danh sách phù hợp với `preferences` của user (đo bằng A/B test). |
| **User Engagement (Post-Launch)** | Tăng 15% | Tăng Session Duration và Activity Completion Rate so với baseline (trước khi có Master Orchestration). |

### 9.2. Acceptance Criteria

- [ ] Context Provider có thể thu thập dữ liệu từ cả ba nguồn (Learning-Status, Buddy-Status, Mem0) trong < 1 giây.

- [ ] Reasoning Engine có thể gọi LLM và nhận kết quả trong < 2 giây.

- [ ] Daily Activity List Builder có thể xây dựng danh sách với đầy đủ ID và priority trong < 0.5 giây.

- [ ] Hệ thống có thể xử lý ít nhất 10,000 requests đồng thời (concurrent requests) mà không bị lỗi.

- [ ] Tất cả các edge cases đã được kiểm thử và có cơ chế fallback rõ ràng.

- [ ] Danh sách được tạo ra luôn có ít nhất 3 hoạt động (Greeting + 2 hoạt động khác).

## 10. Future Enhancements (Out of Scope for V1)

### 10.1. Dynamic LLM-Driven Planning (Version 2)

Trong Version 2, Daily Activity List Builder sẽ **không** sử dụng logic cứng mà sẽ phân tích chi tiết output của Reasoning Engine để xây dựng danh sách một cách linh hoạt hơn. Điều này cho phép LLM có quyền quyết định cao hơn về cấu trúc của ngày học.

### 10.2. Real-Time Re-Planning

Trong tương lai, Master Orchestration có thể được gọi lại **trong ngày** (không chỉ vào đầu ngày) để điều chỉnh kế hoạch dựa trên hiệu suất thực tế của trẻ trong các hoạt động đầu tiên.

### 10.3. Multi-Day Planning

Mở rộng khả năng hoạch định từ một ngày sang một tuần hoặc một tháng, giúp tạo ra một lộ trình học tập dài hạn có tính liên kết cao hơn.

### 10.4. A/B Testing Framework

Xây dựng một framework để A/B test các bộ Guiding Principles khác nhau, giúp tối ưu hóa logic của Reasoning Engine dựa trên dữ liệu thực tế.

## 11. Appendix

### 11.1. 10 Guiding Principles (Chi Tiết Đầy Đủ)

> 1. **Ưu tiên mục tiêu học tập cốt lõi:** Luôn đảm bảo có ít nhất một hoạt động học tập chính trong ngày.1. **Cân bằng giữa Học và Chơi:** Xen kẽ các hoạt động học tập (Learn) với các hoạt động giải trí (Talk, Game) để duy trì sự hứng thú.1. **Thích ứng với hiệu suất gần đây:** Nếu trẻ gặp khó khăn, hãy thêm các hoạt động ôn tập; nếu trẻ làm tốt, hãy đưa ra thử thách mới.1. **Củng cố các điểm yếu:** Chủ động chèn các hoạt động được thiết kế để khắc phục các lỗi sai từ những buổi học trước.1. **Tăng cường mối quan hệ bạn bè:** Dành thời gian cho các hoạt động trò chuyện (Talk Agent) để xây dựng tình bạn với Pika.1. **Tôn trọng trạng thái cảm xúc:** Dựa vào `emotional_state` từ Mem0 để đề xuất các hoạt động phù hợp (ví dụ: nếu trẻ buồn, hãy bắt đầu bằng một trò chơi vui nhộn).1. **Đa dạng hóa hoạt động:** Tránh lặp lại một cấu trúc hoạt động duy nhất mỗi ngày.1. **Xây dựng tính liên tục:** Bắt đầu buổi học bằng cách nhắc lại những gì đã học ở buổi trước.1. **Hướng tới mục tiêu dài hạn:** Đảm bảo các hoạt động hàng ngày phù hợp với lộ trình học tập tổng thể.1. **Tối ưu hóa thời lượng:** Giữ cho tổng thời lượng của các hoạt động trong khoảng 20-25 phút.

### 11.2. Glossary

| Thuật Ngữ | Định Nghĩa |
| --- | --- |
| **Master Orchestration** | LLM-based Agent chịu trách nhiệm xây dựng Daily Activities List. |
| **Context Provider** | Component thu thập dữ liệu từ các nguồn khác nhau. |
| **Reasoning Engine** | LLM-based Agent sử dụng Guiding Principles để đưa ra kế hoạch chiến lược. |
| **Daily Activity List Builder** | Component chuyển đổi kế hoạch chiến lược thành danh sách có thể thực thi. |
| **Daily Activities List** | Danh sách các hoạt động được sắp xếp theo priority, sẵn sàng để Orchestration Agent thực thi. |
| **Guiding Principles** | 10 nguyên tắc sư phạm để hướng dẫn LLM đưa ra quyết định. |

---

**End of Document**

## 5.4. Talk/Game Management Module

**Chức năng:** Module này chịu trách nhiệm chọn ra một `agent_id` (Talk hoặc Game) phù hợp nhất khi được Daily Activity List Builder yêu cầu. Nó hoạt động như một chuyên gia về sở thích và sự đa dạng, đảm bảo các hoạt động giải trí luôn mới mẻ và hấp dẫn.

**Input:**

- `user_id`: Để truy cập `friendship_status`.

- `context`: Một đối tượng chứa các gợi ý từ Reasoning Engine (ví dụ: `{topic: "dinosaurs"}`).

**Logic Xử Lý (Selection Algorithm):**

1. **Tải dữ liệu và Xác định Phase:** Tải bản ghi `friendship_status` của `user_id` và xác định `Phase` (Stranger, Acquaintance, Friend) dựa trên `friendship_score`.

2. **Lọc Kho Hoạt động (Pool Filtering):** Dựa vào `Phase`, giới hạn các kho Talk/Game được phép truy cập. Ví dụ, `Phase 3 (Friend)` có thể truy cập các game dự án chung hoặc các chủ đề trò chuyện sâu sắc hơn.

3. **Tạo Danh sách Ứng viên (Candidate List):**
  - **Ứng viên theo Context:** Nếu `context` có `topic`, tìm các agent liên quan đến topic đó.
  - **Ứng viên theo Sở thích:** Lấy 2 Agent có `topic_score` cao nhất từ `topic_metrics`.
  - **Ứng viên theo Ký ức:** Nếu có `dynamic_memory` liên quan đến một topic, thêm agent của topic đó vào danh sách.
  - **Ứng viên Khám phá:** Lấy 1 Agent ngẫu nhiên từ kho Talk của `Phase` mà người dùng ít tương tác nhất.

1. **Chọn Ứng viên Tốt nhất (Weighted Selection):**
  - Ưu tiên các ứng viên theo thứ tự: Context > Ký ức > Sở thích > Khám phá.
  - Áp dụng bộ lọc **chống lặp** để đảm bảo agent được chọn không trùng với các agent đã có trong Daily Activities List.
  - Chọn ra agent có trọng số cao nhất.

**Output:** Một `agent_id` duy nhất.

**Ví dụ:**

- **Input:** `user_id: "user_123"`, `context: {topic: "dinosaurs"}`

- **Logic:**
    1. Phase của user_123 là `ACQUAINTANCE`.
    2. Lọc các game trong kho của Phase Acquaintance.
    3. Tìm thấy ứng viên `game_dino_quiz_4` khớp với context `topic: "dinosaurs"`.
    4. Kiểm tra chống lặp, thấy chưa có trong list.

- **Output:** `"game_dino_quiz_4"`

## 12. Appendix B: Daily Update Logic for Friendship Status

Phần này mô tả quy trình cập nhật các biến trạng thái tình bạn vào cuối mỗi ngày, được thực hiện bởi một tác vụ nền (background job). Logic này không thuộc về Master Orchestration nhưng là một phần quan trọng để đảm bảo dữ liệu đầu vào cho Master Orchestration luôn chính xác và cập nhật.

**1. Trigger:** Tác vụ được kích hoạt tự động vào 23:59 mỗi ngày.

**2. Quy trình thực thi:**

- Hệ thống lấy tất cả các bản ghi người dùng có tương tác trong ngày (`daily_metrics` không rỗng).

- Với mỗi người dùng, tính toán `daily_change_score` dựa trên các chỉ số như `total_turns`, `user_initiated_questions`, `session_emotion`, `new_memories_count`.

- **Công thức ví dụ:** `daily_change_score = (total_turns * 0.5) + (user_initiated_questions * 3) + (emotion_bonus) + (new_memories_count * 5)`.

- Cập nhật các biến dài hạn:
  - `friendship_score` += `daily_change_score`.
  - Cập nhật `friendship_level` dựa trên `friendship_score` mới.
  - Cập nhật `topic_metrics` cho từng chủ đề đã thảo luận.
  - Cập nhật `streak_day` và `last_interaction_date`.

- Reset `daily_metrics` về rỗng.