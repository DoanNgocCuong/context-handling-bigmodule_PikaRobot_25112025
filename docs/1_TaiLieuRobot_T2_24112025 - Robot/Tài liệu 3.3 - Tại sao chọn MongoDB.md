# Phân Tích Sâu Về Lựa Chọn Database: MongoDB

Đây là hai câu hỏi rất hay, chạm đúng vào cốt lõi của việc thiết kế kiến trúc hệ thống. Dưới đây là phân tích chi tiết.

---

## 1. MongoDB Lưu Những Gì?

Trong kiến trúc này, MongoDB được đề xuất để làm "bộ não" và "trí nhớ" cho AI, lưu trữ toàn bộ dữ liệu động và có cấu trúc phức tạp. Cụ thể, nó sẽ quản lý 4 collection (tương đương với table trong DB quan hệ) chính:

| Collection | Mục Đích | Cấu Trúc Dữ Liệu (Ví dụ) |
| :--- | :--- | :--- |
| **`friendship_status`** | Lưu trạng thái mối quan hệ của Pika với từng user. Đây là collection được đọc/ghi nhiều nhất. | `{
  "user_id": "user_123",
  "friendship_score": 125.5,
  "friendship_level": "PHASE2_ACQUAINTANCE",
  "streak_day": 5,
  "daily_metrics": {
    "total_turns": 30,
    "user_questions": 4
  }
}` |
| **`topic_metrics`** | Theo dõi mức độ quan tâm của user với từng chủ đề. | `{
  "user_id": "user_123",
  "topic_name": "dinosaurs",
  "topic_score": 78.2,
  "last_discussed": "2025-11-24"
}` |
| **`memories` (Mem0)** | Lưu trữ các "ký ức" quan trọng được LLM trích xuất từ cuộc hội thoại. Dữ liệu phi cấu trúc. | `{
  "memory_id": "mem_abc",
  "user_id": "user_123",
  "content": "User's dog name is Milu",
  "type": "pet_info",
  "metadata": { "source_session": "session_xyz" }
}` |
| **`activity_pools`** | Kho chứa toàn bộ các Talk Agent và Game Agent có thể được lựa chọn. | `{
  "agent_id": "agent_dino_quiz_4",
  "type": "GameAgent",
  "required_phase": "PHASE2_ACQUAINTANCE",
  "topic": "dinosaurs"
}` |

---

## 2. Tại Sao Lại Dùng MongoDB Mà Không Phải DB Hiện Tại?

Đây là một quyết định kiến trúc quan trọng. Việc tách ra một database MongoDB riêng thay vì dùng chung DB hiện tại (nơi lưu `user_profile`) mang lại 4 lợi ích chiến lược sau:

### Lợi Ích 1: Đúng Công Cụ Cho Đúng Việc (Data Model Flexibility)

Loại dữ liệu của hệ thống AI rất khác với dữ liệu `user_profile`.

- **Dữ liệu AI (Friendship, Memory):** Có cấu trúc linh hoạt, bán cấu trúc, và thường xuyên thay đổi. Ví dụ, `daily_metrics` hôm nay có 3 trường, ngày mai có thể thêm trường `session_duration`. `memories` thì hoàn toàn là text phi cấu trúc. MongoDB là một **document database**, cho phép lưu các object JSON/BSON một cách tự nhiên. Việc thêm một trường mới chỉ đơn giản là thêm một key-value vào document, **không cần thay đổi schema**. Đây gọi là **Schema-on-Read**.

- **Dữ liệu User Profile:** Thường có cấu trúc cố định (tên, email, ngày sinh, v.v.). DB hiện tại của bạn (khả năng cao là DB quan hệ như MySQL, PostgreSQL) làm rất tốt việc này với một schema chặt chẽ, được định nghĩa trước. Đây là **Schema-on-Write**.

> **Nói một cách đơn giản:** Bắt một DB quan hệ phải lưu các object `memory` và `daily_metrics` cũng giống như bắt một người chỉ quen sắp xếp hồ sơ theo từng ngăn tủ cố định phải đi sắp xếp một đống đồ chơi đủ loại hình dạng. Rất khó và không hiệu quả. MongoDB sinh ra để làm việc đó.

### Lợi Ích 2: Tách Biệt Workload & Đảm Bảo Performance

Đây là lý do quan trọng nhất. Hệ thống AI và hệ thống Backend chính có "mô hình truy cập" (access pattern) hoàn toàn khác nhau, nếu dùng chung sẽ "dẫm chân" lên nhau và làm chậm cả hai.

- **Workload của AI System:**
  - **Write-heavy:** Rất nhiều lượt ghi nhỏ, liên tục trong ngày (cập nhật `daily_metrics`).
  - **Batch Update lớn:** Một tác vụ cực lớn vào 23:59, cập nhật hàng triệu user cùng lúc.
  - **Complex Read:** Các truy vấn phức tạp để lấy context cho Master Orchestration khi user bắt đầu phiên.

- **Workload của Backend chính:**
  - **Transactional Read/Write:** Các giao dịch nhanh, đơn giản như đọc/ghi thông tin user, xử lý đăng nhập, v.v.

> **Rủi ro khi dùng chung:** Hãy tưởng tượng vào 23:59, background job của AI đang chạy, chiếm dụng toàn bộ tài nguyên của DB để tính toán `friendship_score` cho hàng triệu user. Đúng lúc đó, một user khác cố gắng đăng nhập. Request đăng nhập của họ sẽ bị treo hoặc rất chậm vì DB đang quá tải. **Việc tách riêng 2 DB đảm bảo background job của AI không bao giờ ảnh hưởng đến trải nghiệm người dùng trên app.** Đây là một nguyên tắc cốt lõi của kiến trúc Microservices.

### Lợi Ích 3: Khả Năng Mở Rộng (Scalability)

Dữ liệu AI sẽ phình to rất nhanh. Mỗi user, mỗi ngày đều tạo ra `metrics`. Mỗi cuộc hội thoại có thể tạo ra nhiều `memories`. 

- **MongoDB** được thiết kế để **mở rộng theo chiều ngang (horizontal scaling / sharding)** một cách dễ dàng. Khi dữ liệu quá lớn, bạn có thể thêm nhiều server hơn để chia tải. Điều này cực kỳ quan trọng cho một hệ thống có hàng triệu user.

- **DB quan hệ truyền thống** thường **mở rộng theo chiều dọc (vertical scaling)**, tức là nâng cấp server mạnh hơn, đắt tiền hơn. Việc mở rộng theo chiều ngang với DB quan hệ phức tạp hơn rất nhiều.

### Lợi Ích 4: Tốc Độ Phát Triển (Developer Velocity)

Tech stack đề xuất cho AI là Python/FastAPI. Các thư viện Python làm việc với MongoDB (như Pymongo, Motor) rất mạnh mẽ và tự nhiên. Developer có thể thao tác với dữ liệu như với một dictionary trong Python, giúp code sạch hơn và phát triển nhanh hơn.

### Bảng So Sánh Nhanh

| Tiêu Chí | DB Backend Hiện Tại (Giả định là SQL) | MongoDB (NoSQL) cho AI System |
| :--- | :--- | :--- |
| **Mô hình dữ liệu** | Bảng, Cột, Dòng (Cấu trúc cố định) | Document, Collection (JSON/BSON linh hoạt) | 
| **Schema** | Chặt chẽ, định nghĩa trước (Schema-on-Write) | Linh hoạt, không bắt buộc (Schema-on-Read) | 
| **Workload phù hợp** | Giao dịch (Transactional), báo cáo | Dữ liệu động, bán cấu trúc, lượng lớn | 
| **Khả năng mở rộng** | Khó mở rộng chiều ngang | Dễ dàng mở rộng chiều ngang (Sharding) | 
| **Rủi ro khi dùng chung** | Cao (AI job có thể làm sập BE chính) | Thấp (Tách biệt hoàn toàn) | 

**Kết luận:** Việc sử dụng MongoDB không phải là thêm một công nghệ mới cho vui, mà là một quyết định kiến trúc có chủ đích để đảm bảo **performance, khả năng mở rộng, và tốc độ phát triển** cho một hệ thống AI phức tạp và có yêu cầu đặc thù. Nó giúp hệ thống AI và hệ thống Backend chính hoạt động độc lập, hiệu quả và không ảnh hưởng lẫn nhau.
