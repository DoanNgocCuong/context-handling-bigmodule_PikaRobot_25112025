```mermaid
flowchart TD

    A[Input: user_id, context] --> B[Load friendship_status]

    B --> C{Determine Phase<br/>(from friendship_score)}
    C -->|<500| C1[Phase 1: STRANGER]
    C -->|500-3000| C2[Phase 2: ACQUAINTANCE]
    C -->|>3000| C3[Phase 3: FRIEND]

    C1 --> D[Filter Activity Pools<br/>by Phase]
    C2 --> D
    C3 --> D

    D --> E{Greeting Selection<br/>(Priority-Based Rules)}

    E -->|Birthday| E1[Greeting: Birthday]
    E -->|Absent >7 days| E2[Greeting: Returning]
    E -->|Sad yesterday| E3[Greeting: Emotion-based]
    E -->|Follow-up topic| E4[Greeting: Topic Follow-up]
    E -->|Else| E5[Greeting: Random (anti-duplicate)]

    %% Candidate List
    E1 --> F[Build Candidate List]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F

    F --> F1[Add top-2 topics<br/>(topic_metrics)]
    F --> F2[Add exploration topic<br/>(lowest total_turns)]
    F --> F3[Add dynamic memory topics]
    F --> F4[Add emotion-based candidates]
    F --> F5[Add context topic<br/>(from LLM)]

    F1 --> G[Merge Candidate List]
    F2 --> G
    F3 --> G
    F4 --> G
    F5 --> G

    %% Weighted selection
    G --> H[Weighted Selection<br/>Score & Sort]
    H --> H1[Apply Talk:Game ratio<br/>by Phase]
    H1 --> H2[Anti-duplicate filter]

    H2 --> I[Select Final 4 Activities]

    I --> J[Output:<br/>greeting_id + 4 activity_id]

```