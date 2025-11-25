# Tài liệu 3: Logic chọn Talk/Game-Agent đầu ngày

**Mục đích:** Tài liệu này mô tả thuật toán chi tiết để hệ thống tự động chọn ra một danh sách các hoạt động (1 Greeting và 4 Talk/Game) phù hợp cho người dùng mỗi khi họ bắt đầu một phiên tương tác mới trong ngày.

**1. Tổng quan**

Logic lựa chọn được thực hiện theo một quy trình phân cấp: `friendship_score` xác định "Phase" (giai đoạn tình bạn), "Phase" giới hạn các "Kho" hoạt động có thể sử dụng, và các biến số tình bạn khác (`topic_metrics`, `lastday_emotion`, `dynamic_memory`, `streak_day`) sẽ ưu tiên hóa việc lựa chọn trong các kho đó.

**2. Quy trình lựa chọn (Selection Algorithm)**

Khi người dùng mở ứng dụng lần đầu trong ngày, một dịch vụ sẽ được gọi với `user_id` làm đầu vào.

1.  **Bước 1: Tải dữ liệu và Xác định Phase**
    *   Tải bản ghi `friendship_status` mới nhất của người dùng.
    *   Xác định `Phase` dựa trên `friendship_score`:
        *   **Phase 1 (Stranger):** `friendship_score` < 500
        *   **Phase 2 (Acquaintance):** 500 ≤ `friendship_score` ≤ 3000
        *   **Phase 3 (Friend):** `friendship_score` > 3000

2.  **Bước 2: Lọc các Kho Hoạt động (Pool Filtering)**
    *   Dựa vào `Phase` đã xác định, hệ thống sẽ giới hạn các kho được phép truy cập:
        *   **Kho Greeting:** V1 (Phase 1), V1+V2 (Phase 2), V1+V2+V3 (Phase 3).
        *   **Kho Talk (Agent):** Các agent "Bề mặt" (Phase 1), mở khóa agent "Trường học", "Bạn bè" (Phase 2), mở khóa agent "Gia đình", "Lịch sử chung" (Phase 3).
        *   **Kho Game/Activity:** Các game đơn giản (Phase 1), game cá nhân hóa (Phase 2), game dự án chung (Phase 3).

3.  **Bước 3: Chọn Greeting (Priority-Based Selection)**
    *   Hệ thống kiểm tra các điều kiện đặc biệt theo thứ tự ưu tiên nghiêm ngặt, tùy thuộc vào `Phase`.
    *   **Ví dụ cho Phase 3 (Bạn Thân):**
        1.  Kiểm tra `user.birthday` == hôm nay -> **Chọn `S2 (Birthday)`**.
        2.  Kiểm tra `last_interaction_date` cách đây > 7 ngày -> **Chọn `S4 (Returning After Long Absence)`**.
        3.  Kiểm tra `lastday_emotion` -> Nếu có cảm xúc sad sẽ dùng Agent greeting hỏi cảm xúc.
        4.  Kiểm tra `last_day_follow_up_topic` -> Nếu có sẽ chọn Agent greeting follow up topic hôm trước.
    *   Nếu không có điều kiện nào thỏa mãn, chọn ngẫu nhiên một Greeting từ kho Greeting của `Phase` đó (ưu tiên những Greeting chưa được sử dụng gần đây).

4.  **Bước 4: Chọn 4 Talk/Game (Weighted Candidate Selection)**
    *   **a. Tạo danh sách ứng viên (Candidate List):**
        *   **Ứng viên sở thích:** Lấy 2 Agent có `topic_score` cao nhất từ `topic_metrics`.
        *   **Ứng viên khám phá:** Lấy 1 Agent ngẫu nhiên từ kho Talk của `Phase` mà người dùng ít tương tác (top 10 topic `total_turns` thấp nhất)
        *   **Ứng viên cảm xúc:** Nếu `lastday_emotion` là tiêu cực, các Game/Talk vui vẻ, hài hước sẽ được thêm vào.
        *   **Ứng viên Game:** Thêm các game từ kho Game của `Phase` vào danh sách.

    *   **b. Lắp ráp danh sách cuối cùng (Final Assembly):**
        *   Từ danh sách ứng viên, chọn ra 4 hoạt động.
        *   Áp dụng **Tỷ lệ Talk:Activity** của `Phase` để cân bằng số lượng (ví dụ Phase 1 là 40:60, có thể là 2 Talk, 2 Game hoặc 1 Talk, 3 Game).
        *   Áp dụng bộ lọc **chống lặp**: Đảm bảo 5 Agent greeting talk ko trùng nội dung ví dụ ko cùng hỏi về cảm xúc, ko cùng hỏi về 1 topic.
        *   Ưu tiên các ứng viên có trọng số cao hơn (ví dụ: từ sở thích, ký ức).

5.  **Bước 5: Trả về kết quả**
    *   Hệ thống trả về một danh sách có thứ tự, bao gồm 1 `greeting_id` và 4 `activity_id` (có thể là talk hoặc game) xếp lần lượt
