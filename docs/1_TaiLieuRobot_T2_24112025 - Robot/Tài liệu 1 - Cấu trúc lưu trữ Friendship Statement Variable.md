# Tài liệu 1: Cấu trúc lưu trữ Friendship Statement Variable

**Mục đích:** Tài liệu này định nghĩa cấu trúc dữ liệu chi tiết để lưu trữ trạng thái tình bạn và các biến liên quan cho mỗi người dùng, phục vụ cho hệ thống Buddy Talk V2.

**1. Tổng quan**

Để quản lý trạng thái tình bạn một cách hiệu quả, mỗi người dùng sẽ có một bản ghi (record) riêng, được lưu dưới dạng một đối tượng JSON. Cấu trúc này cho phép truy cập, cập nhật và mở rộng dễ dàng. Dữ liệu này nên được lưu trong một cơ sở dữ liệu NoSQL (ví dụ: MongoDB, Firestore, DynamoDB) để tối ưu cho việc đọc/ghi các đối tượng phức tạp.

**2. Định dạng bản ghi (Record Format)**

Một bản ghi `friendship_status` cho một người dùng sẽ bao gồm các trường sau:

| Tên trường              | Kiểu dữ liệu       | Mô tả                                                                                                       | Rationale (Lý do tồn tại)                                                                                                   |
| :---------------------- | :----------------- | :---------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| `user_id`               | String             | (Primary Key) Mã định danh duy nhất của người dùng.                                                         | Bắt buộc để xác định dữ liệu thuộc về người dùng nào.                                                                       |
| `friendship_score`      | Float              | Điểm số tổng thể đo lường mức độ thân thiết. Đây là chỉ số cốt lõi, thay đổi hàng ngày.                     | Là "trí nhớ dài hạn" về lịch sử mối quan hệ, quyết định cấp độ tình bạn.                                                    |
| `friendship_level`      | String (Enum)      | Cấp độ tình bạn hiện tại, được suy ra từ `friendship_score`. Giá trị: `PHASE1_STRANGER`, `PHASE2_ACQUAINTANCE`, `PHASE3_FRIEND`. | Để hệ thống nhanh chóng xác định hành vi, giọng điệu của Pika mà không cần tính toán lại từ điểm số.                        |
| `last_interaction_date` | ISO 8601 Timestamp | Dấu thời gian của lần tương tác cuối cùng.                                                                  | Dùng để tính `streak_day` và xác định các kịch bản vắng mặt (returning after absence).                                      |
| `streak_day`            | Integer            | Số ngày tương tác liên tiếp.                                                                                | Ghi nhận sự cam kết của người dùng, dùng để kích hoạt các kịch bản Greeting đặc biệt (ví dụ: Streak Milestone).             |
| `daily_metrics`         | Object             | Một đối tượng tạm thời để thu thập các chỉ số trong ngày. Sẽ được xử lý và xóa sau khi cập nhật cuối ngày.  | Tách biệt dữ liệu thô hàng ngày khỏi dữ liệu tổng hợp dài hạn, giúp quy trình cập nhật cuối ngày rõ ràng và an toàn.        |
| `topic_metrics`         | Object / Map       | Lưu trữ điểm và lịch sử tương tác cho từng chủ đề (`topic_id`).                                             | Giúp Pika "lắng nghe" và xác định sở thích của trẻ, từ đó cá nhân hóa cuộc trò chuyện.                                      |
| `dynamic_memory`        | Array of Objects   | Danh sách các "ký ức chung" giữa Pika và người dùng.                                                        | Là "cuốn nhật ký chung", vũ khí tối thượng để tạo ra các khoảnh khắc "Aha! Pika nhớ thật này!", chống lại cảm giác máy móc. |

**3. Ví dụ về một bản ghi hoàn chỉnh**

Dưới đây là ví dụ về cấu trúc dữ liệu cho người dùng `user_123` sau một ngày tương tác, thể hiện rõ cách các biến được lưu trữ.

```json
{
  "user_id": "user_123",
  "friendship_score": 750.5,
  "friendship_level": "PHASE2_ACQUAINTANCE",
  "last_interaction_date": "2025-11-24T15:00:00Z",
  "streak_day": 5,
  "daily_metrics": {
    "total_turns": 25,
    "user_initiated_questions": 3,
    "new_memories_count": 2,
    "followup_topics_count": 1,
    "session_emotion": "interesting",
    "topic_details": {
        "agent_movie": { "turns": 15, "initiated_questions": 2 },
        "agent_animal": { "turns": 10, "initiated_questions": 1 }
    }
  },
  "topic_metrics": {
    "agent_movie": {
      "topic_score": 45.0,
      "total_turns": 50,
      "last_talked_date": "2025-11-24T10:20:00Z"
    },
    "agent_animal": {
      "topic_score": 22.5,
      "total_turns": 30,
      "last_talked_date": "2025-11-20T09:00:00Z"
    }
  },
  "dynamic_memory": [
    {
      "memory_id": "mem_01",
      "content": "Hứa sẽ cùng nhau xem phim 'Vùng Đất Linh Hồn'.",
      "related_topic": "agent_movie",
      "timestamp": "2025-11-18T11:30:00Z"
    },
    {
      "memory_id": "mem_02",
      "content": "Kể rằng thú cưng của bạn ấy là một chú chó tên là 'Milu'.",
      "related_topic": "agent_pets",
      "timestamp": "2025-11-24T14:10:00Z"
    }
  ]
}


