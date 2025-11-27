### **Nội dung file `2_Daily_Update_Logic.md`**

# Tài liệu 2: Logic cập nhật các variable cuối ngày

**Mục đích:** Tài liệu này mô tả chi tiết quy trình kỹ thuật để cập nhật các biến trạng thái tình bạn (`friendship variables`) vào cuối mỗi ngày, dựa trên các tương tác của người dùng trong ngày.

**1. Tổng quan**

Một tác vụ nền (background job), chẳng hạn như Cron Job hoặc một hàm serverless được lên lịch, sẽ được thực thi một lần mỗi ngày vào thời điểm ít người dùng hoạt động (ví dụ: 23:59 theo múi giờ địa phương). Tác vụ này sẽ đọc dữ liệu tương tác thô trong ngày (`daily_metrics`), tính toán các thay đổi, và cập nhật vào bản ghi trạng thái tình bạn dài hạn.

**2. Quy trình thực thi (Execution Flow)**

1. **Trigger:** Tác vụ được kích hoạt tự động theo lịch đã định.
2. **Query:** Hệ thống truy vấn cơ sở dữ liệu để lấy tất cả các bản ghi người dùng có `daily_metrics` không rỗng (tức là những người dùng đã có tương tác trong ngày).
3. **Iteration:** Hệ thống lặp qua từng bản ghi người dùng và thực hiện các bước tính toán sau:

   **a. Thu thập các chỉ số từ `daily_metrics`:**

   * `total_turns`: Tổng số lượt trò chuyện trong ngày.
   * `user_initiated_questions`: Số lần người dùng chủ động hỏi Pika.
   * `followup_topics_count`: Tên chủ đề mới do người dùng gợi ý.
   * `session_emotion`: Cảm xúc chủ đạo trong ngày ('interesting', 'boring', 'neutral', 'angry', 'happy','sad').
   * `new_memories_count`: Số ký ức mới được tạo.
   * `topic_details`: Chi tiết tương tác cho từng topic (số turn, số câu hỏi).

   **b. Tính toán `daily_change_score` cho `friendship_score`:**

   * **Base Score:** `base_score = total_turns * 0.5`
   * **Engagement Bonus:** `engagement_bonus = (user_initiated_questions * 3) + (followup_topics_count * 5)`
   * **Emotion Bonus:**
     * Nếu `session_emotion` là 'interesting': `emotion_bonus = +15`
     * Nếu `session_emotion` là 'boring': `emotion_bonus = -15`
     * Các trường hợp khác: `emotion_bonus = 0`
   * **Memory Bonus:** `memory_bonus = new_memories_count * 5`
   * **Tổng điểm thay đổi:** `daily_change_score = base_score + engagement_bonus + emotion_bonus + memory_bonus`

   **c. Cập nhật các biến trạng thái:**

   * **`friendship_score`:** `friendship_score` (mới) = `friendship_score` (cũ) + `daily_change_score`.
   * **`friendship_level`:** Cập nhật lại cấp độ (`PHASE1_STRANGER`, `PHASE2_ACQUAINTANCE`, `PHASE3_FRIEND`) dựa trên ngưỡng điểm của `friendship_score` mới.
     * `0 - 500`: PHASE1_STRANGER
     * `500 - 3000`: PHASE2_ACQUAINTANCE
     * `> 3000`: PHASE3_FRIEND
   * **`topic_metrics`:** Lặp qua `daily_metrics.topic_details`. Với mỗi topic:
     * `topic_score` (mới) = `topic_score` (cũ) + (`turns` * 0.5 + `user_questions` * 3).
     * `total_turns` (mới) = `total_turns` (cũ) + `turns`.
     * Cập nhật `last_talked_date` thành ngày hiện tại.
   * **`streak_day`:**
     * Nếu `last_interaction_date` là ngày hôm qua -> `streak_day` += 1.
     * Nếu không -> reset `streak_day` = 1.
   * **`last_interaction_date`:** Cập nhật thành ngày hiện tại.
4. **Cleanup:** Sau khi tất cả các biến dài hạn đã được cập nhật, reset đối tượng `daily_metrics` thành rỗng hoặc xóa nó đi.
5. **Save:** Lưu (commit) bản ghi người dùng đã được cập nhật trở lại cơ sở dữ liệu.

**3. Xử lý lỗi (Error Handling)**

Nếu có lỗi xảy ra trong quá trình cập nhật cho một người dùng, hệ thống cần ghi log lỗi chi tiết (`user_id`, bước bị lỗi, thông điệp lỗi) và bỏ qua người dùng đó để tiếp tục xử lý những người dùng khác, tránh làm gián đoạn toàn bộ tác vụ. Cần có cơ chế để chạy lại tác vụ cho những người dùng bị lỗi.
