
```
**a. Thu thập các chỉ số từ `daily_metrics`:**

* `total_turns`: Tổng số lượt trò chuyện trong ngày. => BE bắt (vì nếu AI bắt thì bắt kiểu gì)

* `user_initiated_questions`: Số lần người dùng chủ động hỏi Pika. (Cái này làm sao để mà tính, lồng LLMs vào luồng học ? )

* `followup_topics_count`: Tên chủ đề mới do người dùng gợi ý.=> Là cái gì, và BE bắt hay sao.

* `session_emotion`: Cảm xúc chủ đạo trong ngày ('interesting', 'boring', 'neutral', 'angry', 'happy','sad'). => Đo cảm xúc mỗi bài hay mỗi ngày ?

* `new_memories_count`: Số ký ức mới được tạo. => tính toán ở module Mem0???.

* `topic_details`: Chi tiết tương tác cho từng topic (số turn, số câu hỏi). => ??? Làm sao để extract.

Bạn có recommend cách tính score nào dễ dàng cho các bên ko?
```


=> Oke thế cái này AI sẽ quản lý hết và BE cần truyền log toàn bộ 1 ngày cho phía AI để đêm phía AI sẽ chạy xử lý => tính ra điểm daily_score. 
=> Gửi lại daily_score ứng với mỗi user_id cho phía BE, phía BE cập nhật vào điểm friendly_ship 



---
# Nếu để cuối ngày AI call để lấy log từ BE thì tèo luôn ấy chứ. 
=> Nên sau mỗi conversation thì BE gửi conversation luôn cho phía AI. 
Phía AI xử lý luôn để update luôn và cộng dồn vào daily_score.
=> 


---

1. Từ việc sau khi kết thúc 1 cuộc hội thoại phía BE gửi user_id kèm log cho phía AI. 
Phía AI xử lý log luôn và tíh điểm daily_score và code API phía BE để update điểm friendlyship_score.
(vậy là 2 đầu API và 1 luồng logic xử lý để tính điểm) => Friendly_ship score được update liên tục mà ko cần đợi đến cuối ngày. 
Cục DB Friendlyship sẽ quản lý tất cả điều này (để về sau còn trích ra: total_turns và topic_score, ... các chỉ số khác, giúp cho việc chọn lựa các con Agent (Greeting Agent, Talk Agent, Game/Activity Agent ) phù hợp không chỉ với Phrase1, 2, 3, ... mà còn khớp với các logic phức tạp khác (nếu có) về friendlyship. 


2. DB cục friendlyship_score, friendlyship_level  --- mappping với 1 loạt logic chọn Greeting Agent, Talk Agent, Game/Activity Agent . 
- Cần define 1 đầu API để truyền user_id và friendlyship_level, loại cần lấy và số lượng cần lấy => thì sẽ lấy ra. 

Nói chung đây là module Context Handling quản lý Friendlyship và Kho Agent ứng với friendlyship_level. 

---
Viết tài liệu triển khai chi tiết từ Product -> Technical. 