# Sơ Đồ Chi Tiết: Talk/Game Management & Context Handling

## 1. Talk/Game Management - Flowchart Chi Tiết

```mermaid
flowchart TD
    Start([Request từ Master Orchestration/Trigger Agent]) --> Input[Input: user_id + context]
    
    Input --> GetData[Lấy dữ liệu từ Context Handling]
    GetData --> FriendshipData[friendship_status:<br/>- friendship_score<br/>- friendship_level]
    GetData --> TopicData[topic_metrics:<br/>- topic scores]
    GetData --> MemoryData[dynamic_memory:<br/>- shared experiences]
    
    FriendshipData --> DeterminePhase{Xác định Phase}
    DeterminePhase -->|score < 50| Stranger[Phase: PHASE1_STRANGER]
    DeterminePhase -->|50 ≤ score < 150| Acquaintance[Phase: PHASE2_ACQUAINTANCE]
    DeterminePhase -->|score ≥ 150| Friend[Phase: PHASE3_FRIEND]
    
    Stranger --> QueryPool1[Query activity_pools]
    Acquaintance --> QueryPool2[Query activity_pools]
    Friend --> QueryPool3[Query activity_pools]
    
    QueryPool1 --> FilterPhase[Lọc agents theo Phase]
    QueryPool2 --> FilterPhase
    QueryPool3 --> FilterPhase
    
    FilterPhase --> BuildCandidates[Xây dựng danh sách ứng viên]
    
    BuildCandidates --> TopicMatch[Topic Matching:<br/>So sánh với topic_metrics]
    BuildCandidates --> MemoryMatch[Memory Matching:<br/>Kiểm tra dynamic_memory]
    BuildCandidates --> AntiDup[Anti-Duplication:<br/>Loại bỏ agents đã dùng gần đây]
    
    TopicMatch --> Scoring[Tính điểm cho từng agent]
    MemoryMatch --> Scoring
    AntiDup --> Scoring
    
    Scoring --> WeightedCalc[agent_score =<br/>topic_match * 0.6 +<br/>recency_penalty * 0.2 +<br/>variety_bonus * 0.2]
    
    WeightedCalc --> SelectBest{Chọn agent<br/>điểm cao nhất}
    
    SelectBest -->|Có agent phù hợp| ReturnAgent[Return agent_id]
    SelectBest -->|Không có agent| Fallback[Fallback:<br/>Chọn agent mặc định]
    
    ReturnAgent --> End([Trả về agent_id])
    Fallback --> End
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style DeterminePhase fill:#fff4e6
    style SelectBest fill:#fff4e6
    style Scoring fill:#f3e5f5
    style WeightedCalc fill:#f3e5f5
```

## 2. Talk/Game Management - Sequence Diagram

```mermaid
sequenceDiagram
    participant MO as Master Orchestration
    participant TGM as Talk/Game Management
    participant CH as Context Handling
    participant DB as MongoDB (activity_pools)
    
    MO->>TGM: Request agent (user_id, context)
    
    TGM->>CH: GET /context/friendship-status?user_id=...
    CH-->>TGM: friendship_score, friendship_level
    
    TGM->>CH: GET /context/topic-metrics?user_id=...
    CH-->>TGM: topic_metrics (dinosaurs: 45, space: 22)
    
    TGM->>CH: GET /context/memory?user_id=...
    CH-->>TGM: dynamic_memory (shared experiences)
    
    TGM->>TGM: Xác định Phase dựa trên friendship_score
    
    TGM->>DB: Query agents (required_phase, topic)
    DB-->>TGM: List of candidate agents
    
    TGM->>TGM: Tính điểm cho từng agent<br/>(topic match + memory + recency)
    
    TGM->>TGM: Weighted selection
    
    TGM-->>MO: Return agent_id
```

## 3. Context Handling - Architecture Diagram

```mermaid
graph TB
    subgraph Container3[Container 3: Context Handling]
        subgraph MemoryModule[Memory Module - Mem0]
            StoreMemory[Store Memory<br/>LLM auto-detect important info]
            StructureMemory[Structure Memory<br/>Schema-based storage]
            RetrieveMemory[Retrieve Memory<br/>Context-aware search]
            
            StoreMemory --> StructureMemory
            StructureMemory --> RetrieveMemory
        end
        
        subgraph FriendshipModule[Friendship Status Management]
            DailyCollector[Daily Metrics Collector<br/>Thu thập: total_turns,<br/>user_questions, emotion]
            FriendshipCalc[Friendship Score Calculator<br/>Tính daily_change_score]
            TopicTracker[Topic Metrics Tracker<br/>Cập nhật topic_score]
            DynamicMemory[Dynamic Memory Manager<br/>Quản lý ký ức chung]
            
            DailyCollector --> FriendshipCalc
            DailyCollector --> TopicTracker
            DailyCollector --> DynamicMemory
        end
        
        subgraph BackgroundJob[Daily Background Job - 23:59]
            Trigger[Scheduler Trigger]
            Calculate[Calculate daily_change_score<br/>từ daily_metrics]
            Update[Update friendship_score,<br/>topic_metrics, dynamic_memory]
            Cleanup[Reset daily_metrics = empty]
            
            Trigger --> Calculate
            Calculate --> Update
            Update --> Cleanup
        end
    end
    
    subgraph Database[(MongoDB)]
        FS[friendship_status collection]
        TM[topic_metrics collection]
        MEM[memories collection]
    end
    
    ConvAgent[Conversational Agent<br/>Container 2] -->|Send metrics| DailyCollector
    
    FriendshipCalc --> FS
    TopicTracker --> TM
    StoreMemory --> MEM
    
    Calculate --> FS
    Calculate --> TM
    
    Orchestration[Orchestration System<br/>Container 1] -->|Request context| RetrieveMemory
    Orchestration -->|Request friendship data| FS
    
    style MemoryModule fill:#e8f5e9
    style FriendshipModule fill:#fff3e0
    style BackgroundJob fill:#fce4ec
    style Database fill:#e3f2fd
```

## 4. Context Handling - Daily Metrics Collection Flow

```mermaid
flowchart LR
    subgraph Session[Phiên Tương Tác]
        User[User tương tác với Pika]
        Agent[Conversational Agent]
        
        User -->|Voice/Text| Agent
        Agent -->|Response| User
    end
    
    subgraph Tracking[Theo Dõi Metrics]
        CountTurns[Đếm total_turns]
        CountQuestions[Đếm user_initiated_questions]
        DetectEmotion[Phát hiện session_emotion]
        TrackTopic[Theo dõi topics discussed]
        
        Agent --> CountTurns
        Agent --> CountQuestions
        Agent --> DetectEmotion
        Agent --> TrackTopic
    end
    
    subgraph Collection[Thu Thập & Lưu Trữ]
        API[POST /context/metrics/collect]
        Aggregate[Cộng dồn metrics trong ngày]
        Store[Lưu vào daily_metrics]
        
        CountTurns --> API
        CountQuestions --> API
        DetectEmotion --> API
        TrackTopic --> API
        
        API --> Aggregate
        Aggregate --> Store
    end
    
    subgraph EndOfDay[Cuối Ngày - 23:59]
        BGJob[Background Job]
        Calculate[Tính daily_change_score]
        UpdateScore[Cập nhật friendship_score]
        Reset[Reset daily_metrics]
        
        Store -.->|Đọc dữ liệu| BGJob
        BGJob --> Calculate
        Calculate --> UpdateScore
        UpdateScore --> Reset
    end
    
    style Session fill:#e3f2fd
    style Tracking fill:#fff3e0
    style Collection fill:#e8f5e9
    style EndOfDay fill:#fce4ec
```

## 5. Context Handling - Friendship Score Calculation

```mermaid
flowchart TD
    Start([Background Job Trigger - 23:59]) --> Query[Query tất cả users<br/>có daily_metrics ≠ empty]
    
    Query --> Batch[Xử lý theo batch<br/>1000 users/lần]
    
    Batch --> ForEach{Với mỗi user}
    
    ForEach --> ReadMetrics[Đọc daily_metrics:<br/>- total_turns<br/>- user_initiated_questions<br/>- session_emotion]
    
    ReadMetrics --> CalcFormula[Áp dụng công thức:<br/>daily_change_score =<br/>total_turns * 0.5 +<br/>user_questions * 3 +<br/>emotion_bonus]
    
    CalcFormula --> UpdateFS[Cập nhật friendship_score:<br/>friendship_score += daily_change_score]
    
    UpdateFS --> CheckLevel{Kiểm tra ngưỡng}
    
    CheckLevel -->|score < 50| SetStranger[friendship_level = PHASE1_STRANGER]
    CheckLevel -->|50 ≤ score < 150| SetAcquaintance[friendship_level = PHASE2_ACQUAINTANCE]
    CheckLevel -->|score ≥ 150| SetFriend[friendship_level = PHASE3_FRIEND]
    
    SetStranger --> UpdateTopic[Cập nhật topic_metrics]
    SetAcquaintance --> UpdateTopic
    SetFriend --> UpdateTopic
    
    UpdateTopic --> UpdateMemory[Cập nhật dynamic_memory]
    
    UpdateMemory --> ResetDaily[Reset daily_metrics = empty]
    
    ResetDaily --> UpdateStreak[Cập nhật streak_day,<br/>last_interaction_date]
    
    UpdateStreak --> NextUser{Còn user nào?}
    
    NextUser -->|Có| ForEach
    NextUser -->|Không| End([Hoàn thành])
    
    style Start fill:#e1f5ff
    style End fill:#e1f5ff
    style CalcFormula fill:#fff4e6
    style CheckLevel fill:#f3e5f5
```

## 6. Data Flow Between Modules

```mermaid
graph LR
    subgraph ConvAgent[Container 2: Conversational Agent]
        Talk[Talk Agent]
        Learn[Learn Agent]
        Game[Game Agent]
    end
    
    subgraph Context[Container 3: Context Handling]
        Collector[Daily Metrics Collector]
        Memory[Memory Module]
        Friendship[Friendship Management]
    end
    
    subgraph Orchestration[Container 1: Orchestration]
        Master[Master Orchestration]
        TGM[Talk/Game Management]
        Queue[Queue Management]
    end
    
    Talk -->|Metrics| Collector
    Learn -->|Metrics| Collector
    Game -->|Metrics| Collector
    
    Talk -->|Important Info| Memory
    Learn -->|Important Info| Memory
    
    Collector --> Friendship
    
    Master -->|Request Context| Friendship
    Master -->|Request Memory| Memory
    
    TGM -->|Query Friendship Data| Friendship
    TGM -->|Query Topic Metrics| Friendship
    TGM -->|Query Memory| Memory
    
    Friendship -->|friendship_score,<br/>friendship_level| TGM
    Memory -->|Relevant memories| TGM
    
    TGM -->|agent_id| Master
    
    style ConvAgent fill:#e8f5e9
    style Context fill:#fff3e0
    style Orchestration fill:#e3f2fd
```

## 7. Database Schema Visualization

```mermaid
erDiagram
    PHASE3_FRIENDSHIP_STATUS {
        string user_id PK
        int friendship_score
        string friendship_level
        int streak_day
        date last_interaction_date
        object daily_metrics
        object topic_metrics
    }
    
    TOPIC_METRICS {
        string user_id FK
        string topic_name
        float topic_score
        int total_turns
        date last_discussed
    }
    
    MEMORIES {
        string memory_id PK
        string user_id FK
        string content
        string type
        date created_at
        object metadata
    }
    
    ACTIVITY_POOLS {
        string agent_id PK
        string type
        string required_phase
        string topic
        string difficulty
        timestamp last_used_timestamp
        int last_used_count
    }
    
    PHASE3_FRIENDSHIP_STATUS ||--o{ TOPIC_METRICS : has
    PHASE3_FRIENDSHIP_STATUS ||--o{ MEMORIES : has
```
