Dưới đây là nội dung toàn bộ tài liệu **"AI\_V1\_Platform\_Architecture\_v3.pdf"** được chuyển đổi sang định dạng Markdown, bao gồm các tiêu đề, danh sách và bảng biểu được tái tạo lại theo đúng cấu trúc gốc.

-----

# [cite\_start]1. ĐẶC TẢ KIẾN TRÚC AI PLATFORM: HƯỚNG DẪN CHI TIẾT CHO PRODUCT TEAM (Tái Cấu Trúc V3) [cite: 1, 2]

**Version:** 3.0
[cite\_start]**Date:** 24/11/2025 [cite: 3]

-----

## [cite\_start]2. Tóm Tắt Điều Hành và Bối Cảnh Chiến Lược (Context) [cite: 4]

### 2.1. [cite\_start]Tóm Tắt Điều Hành (Executive Summary) [cite: 5]

[cite\_start]Tài liệu này là bản đặc tả chi tiết về kiến trúc AI Platform của Pika, được tái cấu trúc theo mô hình 3 lớp chức năng rõ ràng: **Orchestration**, **Conversation**, và **Context Handling**[cite: 6].

[cite\_start]Kiến trúc này được thiết kế để hướng dẫn Product Team trong việc phát triển và vận hành sản phẩm, đảm bảo tính nhất quán, khả năng mở rộng, và tập trung vào việc tạo ra một trải nghiệm học tiếng Anh giao tiếp được cá nhân hóa sâu sắc cho trẻ em[cite: 7].

### 2.2. [cite\_start]Bối Cảnh Chiến Lược (Context) [cite: 8]

| Khía Cạnh | Mục Tiêu Cấp Cao / Mô Tả Chi Tiết | Ý Nghĩa Chiến Lược cho Product Team |
| :--- | :--- | :--- |
| **Mục Tiêu** | Tăng Retention và Engagement của trẻ em thông qua trải nghiệm học tiếng Anh giao tiếp được cá nhân hóa. | Mọi tính năng mới phải được đo lường dựa trên tác động của nó đến hai chỉ số này trong bối cảnh giáo dục. |
| **Lợi Thế Cạnh Tranh** | Kiến trúc 3 lớp tách biệt rõ ràng giữa hoạch định (Orchestration), thực thi (Conversation), và dữ liệu (Context), cho phép phát triển độc lập, tối ưu hóa chuyên sâu từng mảng, và tăng tốc độ ra mắt tính năng mới. | Cho phép Product Team tập trung vào chiến lược điều phối và trải nghiệm hội thoại mà không bị ràng buộc bởi các chi tiết kỹ thuật của việc quản lý dữ liệu. |
| **Đối Tượng Người Dùng** | Trẻ em (từ 6-12 tuổi) học tiếng Anh giao tiếp. | Yêu cầu cao về Safety (An toàn), Engagement (Hấp dẫn), và Personalization (Cá nhân hóa) theo độ tuổi. |
[cite\_start][cite: 9]

### 2.3. [cite\_start]Tổng Quan Kiến Trúc 3 Lớp [cite: 10]

[cite\_start]Kiến trúc được chia thành 3 Container (Lớp) chính, mỗi lớp chịu trách nhiệm cho một mảng chức năng riêng biệt và tương tác với nhau thông qua các API được định nghĩa rõ ràng[cite: 11].

| Container | Chức Năng Cốt Lõi | Ví Dụ Hoạt Động |
| :--- | :--- | :--- |
| **1. Orchestration System** | **Hoạch định và Điều phối:** Quyết định “Hôm nay trẻ nên làm gì?" và điều chỉnh kế hoạch đó dựa trên các sự kiện. | Xây dựng Daily Activities List, chèn một GameAgent vào hàng đợi khi trẻ học quá lâu. |
| **2. Conversational AI Agent** | **Thực thi và Tương tác:** Giao tiếp trực tiếp với người dùng trong từng hoạt động cụ thể. | Thực hiện một bài học về phát âm, trò chuyện về chủ đề khủng long, chơi một game đố vui. |
| **3. Context Handling** | **Quản lý và Cập nhật Dữ liệu:** Thu thập, xử lý, và duy trì tất cả dữ liệu về người dùng và mối quan hệ. | Cập nhật điểm tình bạn cuối ngày, lưu một “ký ức chung” mới vào Mem0. |
[cite\_start][cite: 12]

![](image/Pasted%20image%2020251124180701.png)

-----

## [cite\_start]3. Container 1: Orchestration System (Hệ Thống Điều Phối) [cite: 33]

### 3.1. [cite\_start]Tổng Quan và Sơ Đồ Tương Tác [cite: 34]

**Chức năng cốt lõi:** Orchestration System là “bộ não” của Pika, chịu trách nhiệm hoạch định chiến lược và điều phối toàn bộ trải nghiệm của người dùng. [cite\_start]Nó quyết định trẻ sẽ làm gì, khi nào, và linh hoạt điều chỉnh kế hoạch đó dựa trên các sự kiện phát sinh, ngay cả khi trẻ không ở trong ứng dụng[cite: 35, 36].

![](image/Pasted%20image%2020251124180753.png)

**Luồng hoạt động chính:**

1.  [cite\_start]**Master Orchestration** được kích hoạt hàng ngày, nhận dữ liệu từ Container 3 (Context Handling) để xây dựng một **Daily Activities List** (kế hoạch hoạt động trong ngày)[cite: 64].
2.  [cite\_start]Kế hoạch này được lưu vào **Queue Management** dưới dạng một hàng đợi ưu tiên[cite: 65].
3.  [cite\_start]Khi người dùng bắt đầu phiên học, **Orchestration Agent** sẽ lấy hoạt động có độ ưu tiên cao nhất từ hàng đợi và yêu cầu Container 2 (Conversational AI Agent) thực thi[cite: 66].
4.  [cite\_start]Trong khi đó, **Trigger Agent** liên tục lắng nghe các sự kiện (ví dụ: trẻ học quá 15 phút, hoặc 3 ngày không vào học)[cite: 67]. [cite\_start]Khi một sự kiện xảy ra, nó sẽ chèn một hoạt động mới vào hàng đợi, làm thay đổi kế hoạch ban đầu[cite: 68].
5.  [cite\_start]**Talk/Game Management** và **Agent Generator** là các module hỗ trợ, cung cấp các agent phù hợp và tạo ra các agent mới khi cần[cite: 69].

### 3.2. [cite\_start]Master Orchestration [cite: 70]

[cite\_start]**Chức năng:** Là bộ não hoạch định chiến lược, sử dụng LLM để xây dựng một kế hoạch hoạt động hàng ngày (Daily Activities List) được cá nhân hóa sâu sắc cho mỗi người dùng[cite: 71].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Input** | - `user_id` để xác định người dùng.<br>- **Context JSON:** Một đối tượng JSON toàn diện từ Context Provider, bao gồm `learning_status`, `friendship_status`, và `user_profile`. |
| **Logic Xử Lý** | **1. Prompt Construction:** Xây dựng một prompt chi tiết cho LLM, bao gồm Context JSON và 10 Nguyên Tắc Vàng (Guiding Principles) về sư phạm.<br>**2. LLM Inference:** Gửi prompt đến LLM để nhận về một kế hoạch chiến lược (danh sách hoạt động và lý do).<br>**3. List Building (V1):** Chuyển đổi kế hoạch chiến lược thành một danh sách có thể thực thi với `activity_id` và `priority` cụ thể. Trong V1, logic này là cố định (rule-based) để đảm bảo tính ổn định. |
| **Output** | **Daily Activities List:** Một mảng JSON chứa các hoạt động cho ngày hôm đó, được sắp xếp theo thứ tự ưu tiên. |
[cite\_start][cite: 72]

### 3.3. [cite\_start]Orchestration Agent [cite: 73]

[cite\_start]**Chức năng:** Là người quản lý và thực thi, chịu trách nhiệm lấy các hoạt động từ Queue Management và điều phối việc thực thi chúng trong phiên học[cite: 74].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Input** | - `user_id` khi bắt đầu phiên học.<br>- Tín hiệu hoàn thành từ hoạt động hiện tại. |
| **Logic Xử Lý** | 1. Khi phiên học bắt đầu, gọi Queue Management để lấy hoạt động có `priority` cao nhất.<br>2. Yêu cầu **In-session Routing** (Container 2) thực thi `activity_id` tương ứng.<br>3. Chờ nhận tín hiệu “hoàn thành” (`activity_completed`).<br>4. Lặp lại bước 1 để lấy hoạt động tiếp theo. |
| **Output** | - Yêu cầu thực thi đến In-session Routing.<br>- Tín hiệu kết thúc phiên học khi hàng đợi trống hoặc người dùng thoát. |
[cite\_start][cite: 75]

### 3.4. [cite\_start]Talk/Game Management [cite: 76]

[cite\_start]**Chức năng:** Hoạt động như một chuyên gia về sở thích, chịu trách nhiệm chọn ra một `agent_id` (Talk hoặc Game) phù hợp nhất khi được Master Orchestration hoặc Trigger Agent yêu cầu[cite: 77].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Input** | - `user_id` để truy cập `friendship_status`.<br>- **Context:** Gợi ý từ LLM (ví dụ: `{topic: "dinosaurs"}`). |
| **Logic Xử Lý** | **1. Xác định Phase:** Dựa trên `friendship_score` để xác định giai đoạn tình bạn (Stranger, Acquaintance, Friend).<br>**2. Lọc Kho Hoạt động:** Giới hạn các kho Talk/Game được phép truy cập dựa trên Phase.<br>**3. Tạo Danh sách Ứng viên:** Tạo một danh sách các agent tiềm năng dựa trên context, sở thích (`topic_metrics`), và ký ức chung (`dynamic_memory`).<br>**4. Chọn Ứng viên Tốt nhất:** Ưu tiên các ứng viên và áp dụng bộ lọc chống lặp để chọn ra agent phù hợp nhất. |
| **Output** | Một `agent_id` duy nhất. |
[cite\_start][cite: 78]

### 3.5. [cite\_start]Agent Generator [cite: 79]

[cite\_start]**Chức năng:** Tự động sinh ra các agent mới (chủ yếu là Learn Agent và Talk Agent) dựa trên một mẫu (template) và dữ liệu đầu vào, giúp giảm tải công việc thủ công và tăng khả năng cá nhân hóa[cite: 80].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Input** | - `user_profile`: Để hiểu về điểm mạnh, điểm yếu của trẻ.<br>- `agent_template`: Một cấu trúc định sẵn cho một loại agent (ví dụ: template cho một Learn Agent sửa lỗi ngữ pháp). |
| **Logic Xử Lý** | 1. Nhận yêu cầu tạo agent (ví dụ: từ Trigger Agent sau khi phát hiện trẻ sai ngữ pháp nhiều).<br>2. Chọn `agent_template` phù hợp (ví dụ: `template_grammar_review`).<br>3. Điền các thông tin cụ thể vào template từ `user_profile` (ví dụ: `error_type: "simple_past_tense"`).<br>4. Lưu cấu hình agent mới vào cơ sở dữ liệu và trả về `agent_id` mới. |
| **Output** | Một `agent_id` mới, sẵn sàng để được chèn vào hàng đợi. |
[cite\_start][cite: 81]

### 3.6. [cite\_start]Queue Management (Daily Activities List) [cite: 82]

[cite\_start]**Chức năng:** Hoạt động như một hàng đợi ưu tiên (Priority Queue), lưu trữ và quản lý kế hoạch hoạt động hàng ngày[cite: 83].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Cấu Trúc Dữ Liệu** | Một danh sách (list/array) các đối tượng, mỗi đối tượng đại diện cho một hoạt động và có các trường: `activity_id`, `activity_type`, và `priority`. |
| **Logic Hoạt Động** | - **Thêm (Enqueue):** Khi một hoạt động mới được thêm vào, danh sách sẽ tự động được sắp xếp lại dựa trên priority (số càng cao, ưu tiên càng lớn).<br>- **Lấy (Dequeue):** Luôn trả về và xóa hoạt động ở đầu danh sách (có priority cao nhất).<br>- **Linh hoạt:** Cho phép các hoạt động có độ ưu tiên cao (ví dụ: từ Trigger Agent) "chen ngang” vào kế hoạch đã định sẵn. |
| **Đặc Điểm** | - **Minh bạch:** Cung cấp một cái nhìn rõ ràng về những gì người dùng sẽ làm tiếp theo. |
[cite\_start][cite: 84]

### 3.7. [cite\_start]Trigger Agent (Out-of-session Orchestration) [cite: 85]

[cite\_start]**Chức năng:** Hoạt động như một hệ thống giám sát ngầm, lắng nghe các sự kiện xảy ra cả trong và ngoài phiên học để điều chỉnh kế hoạch một cách linh hoạt[cite: 86].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Input** | - **Time-based Events:** Các sự kiện dựa trên thời gian (ví dụ: đã 3 ngày trôi qua kể từ lần học cuối).<br>- **Event-based Events:** Các sự kiện dựa trên hành động (ví dụ: trẻ vừa hoàn thành một bài học với điểm số thấp, hoặc vừa học liên tục 15 phút). |
| **Logic Xử Lý** | 1. Lắng nghe các sự kiện từ hệ thống.<br>2. Khi một sự kiện khớp với một quy tắc đã định (trigger rule), thực hiện hành động tương ứng.<br>3. Hành động phổ biến nhất là yêu cầu Agent Generator tạo một agent mới và/hoặc chèn trực tiếp một `activity_id` vào Queue Management với độ ưu tiên cao. |
| **Output** | Một yêu cầu cập nhật đến Queue Management. |
| **Ví dụ** | - **Sự kiện:** `long_learning_session` (học \> 15 phút).<br>- **Hành động:** Yêu cầu Talk/Game Management chọn một GameAgent yêu thích và chèn vào hàng đợi với `priority: 8` để giảm căng thẳng. |
[cite\_start][cite: 87]

-----

## [cite\_start]4. Container 2: Conversational AI Agent (Agent Tương Tác) [cite: 88]

### 4.1. [cite\_start]Tổng Quan và Sơ Đồ Tương Tác [cite: 89]

**Chức năng cốt lõi:** Conversational AI Agent là “bộ mặt” và “giọng nói” của Pika. Container này chịu trách nhiệm thực thi các hoạt động được giao bởi Orchestration System và tương tác trực tiếp với người dùng. [cite\_start]Đây là nơi các cuộc hội thoại, bài học, và trò chơi thực sự diễn ra[cite: 90, 91, 92].

![](image/Pasted%20image%2020251124180850.png)

**Luồng hoạt động chính:**

1.  [cite\_start]**In-session Routing** nhận một `activity_id` từ Orchestration Agent (Container 1)[cite: 119].
2.  [cite\_start]Nó xác định loại agent cần thực thi (Talk, Learn, Game, Workflow) và tải agent đó lên[cite: 120].
3.  [cite\_start]Agent được tải sẽ sử dụng một bộ các **Shared Components** (Thành phần dùng chung) để tương tác với người dùng[cite: 121].
4.  [cite\_start]Người dùng nói, **ASR** chuyển thành văn bản[cite: 122].
5.  [cite\_start]Văn bản được đưa vào **LLM Engine** cùng với prompt của agent để xử lý và tạo ra phản hồi[cite: 123].
6.  [cite\_start]LLM có thể sử dụng **Tooling Layer** để truy cập thông tin bên ngoài hoặc sử dụng **Multimodal Tagging Layer** để làm giàu phản hồi[cite: 124].
7.  [cite\_start]Phản hồi cuối cùng được chuyển đến **TTS** để tạo ra giọng nói của Pika và gửi đến người dùng[cite: 125].
8.  [cite\_start]Trong suốt quá trình, agent liên tục gửi các chỉ số tương tác đến Container 3 (Context Handling) để cập nhật[cite: 126].

### 4.2. [cite\_start]Shared Components (Thành phần dùng chung) [cite: 127]

[cite\_start]Đây là các công nghệ nền tảng được tất cả các agent trong container này sử dụng để đảm bảo một trải nghiệm tương tác mượt mà và nhất quán[cite: 128].

| Component | Chức Năng | Phạm Vi Tác Động của PM |
| :--- | :--- | :--- |
| **ASR** (Automatic Speech Recognition) | Chuyển đổi giọng nói của trẻ thành văn bản với độ chính xác cao. | - Lựa chọn và tinh chỉnh model ASR cho phù hợp với giọng nói trẻ em.<br>- Thiết kế UI/UX cho trạng thái lắng nghe và xử lý. |
| **LLM Engine** | Là bộ não xử lý ngôn ngữ, tạo ra các phản hồi thông minh, phù hợp với ngữ cảnh. | - Lựa chọn model LLM (ví dụ: GPT-4, Gemini).<br>- Thiết kế và tối ưu hóa cấu trúc của System Prompt.<br>- Định nghĩa các quy tắc an toàn (Safety Guardrails). |
| **TTS** (Text-to-Speech) | Chuyển đổi văn bản do LLM tạo ra thành giọng nói tự nhiên, có cảm xúc của Pika. | - Lựa chọn và tinh chỉnh giọng nói của Pika.<br>- Thiết kế cách Pika thể hiện cảm xúc qua giọng nói. |
| **Tooling Layer** | Cung cấp cho LLM khả năng truy cập các công cụ bên ngoài (ví dụ: gọi API thời tiết, tra cứu từ điển). | - Xác định các công cụ cần thiết cho các kịch bản tương tác.<br>- Thiết kế cách LLM yêu cầu và xử lý kết quả từ công cụ. |
| **Multimodal Tagging Layer** | Cho phép LLM gợi ý các hành vi (emotion), media, và hiệu ứng (celebration) thông qua một hệ thống tag đơn giản. | - Định nghĩa danh sách các tag được hỗ trợ (ví dụ: `[EMOTION: happy]`, `[CELEBRATE]`).<br>- Thiết kế cách các tag này được ánh xạ sang các hiệu ứng hình ảnh và âm thanh cụ thể. |
[cite\_start][cite: 130]

### 4.3. [cite\_start]System Prompt Template [cite: 131]

System Prompt là bản chỉ dẫn cốt lõi được gửi đến LLM cho mọi lượt tương tác. Nó quyết định “tính cách” và “năng lực” của Pika.

**Cấu trúc của một System Prompt:**

1.  [cite\_start]**Persona:** Mô tả chi tiết về tính cách của Pika (thân thiện, tò mò, kiên nhẫn)[cite: 135].
2.  [cite\_start]**Guiding Principles:** Các nguyên tắc bất biến (ví dụ: luôn tích cực, không bao giờ đưa ra lời khuyên y tế)[cite: 136].
3.  [cite\_start]**Context:** Dữ liệu được cung cấp bởi Context Handling, bao gồm thông tin về người dùng, lịch sử trò chuyện, và ký ức chung[cite: 137].
4.  [cite\_start]**Task Instruction:** Chỉ dẫn cụ thể cho nhiệm vụ hiện tại (ví dụ: “Bạn là một Talk Agent, hãy trò chuyện với trẻ về chủ đề khủng long")[cite: 138].
5.  [cite\_start]**User Input:** Lời nói của người dùng (đã được chuyển thành văn bản)[cite: 139].

### 4.4. [cite\_start]Talk Agent [cite: 140]

  * [cite\_start]**Chức năng:** Tập trung vào việc xây dựng và nuôi dưỡng mối quan hệ tình bạn giữa trẻ và Pika thông qua các cuộc trò chuyện tự nhiên, không có mục tiêu học tập rõ ràng[cite: 141].
  * [cite\_start]**Đặc điểm:** Linh hoạt, không theo kịch bản cứng, có khả năng gợi mở và đào sâu vào các chủ đề mà trẻ quan tâm[cite: 142].
  * [cite\_start]**Ví dụ:** `agent_daily_chat_sports_topic`, `agent_encouragement_chat`[cite: 143].

### 4.5. [cite\_start]Learn Agent [cite: 144]

  * [cite\_start]**Chức năng:** Tập trung vào một mục tiêu học tập cụ thể, chẳng hạn như luyện một kỹ năng phát âm, học một bộ từ vựng, hoặc sửa một lỗi ngữ pháp[cite: 145].
  * [cite\_start]**Đặc điểm:** Có cấu trúc rõ ràng, có cơ chế đánh giá đúng/sai, và thường đi kèm với các hoạt động tương tác (ví dụ: lặp lại một câu, trả lời câu hỏi)[cite: 146].
  * [cite\_start]**Ví dụ:** `lesson_review_pronunciation_th`, `learn_agent_irregular_verbs`[cite: 147].

### 4.6. [cite\_start]Workflow [cite: 148]

  * [cite\_start]**Chức năng:** Là một chuỗi các hoạt động được kết nối với nhau để tạo thành một bài học hoàn chỉnh, thường bao gồm nhiều bước và có thể kết hợp cả Learn Agent và Talk Agent[cite: 149].
  * **Đặc điểm:** Có tính tuần tự, mỗi bước phụ thuộc vào kết quả của bước trước. [cite\_start]Thường được sử dụng cho các bài học chính trong lộ trình học tập[cite: 150, 151].
  * [cite\_start]**Ví dụ:** Một workflow học về "simple past tense” có thể bao gồm: (1) Giới thiệu lý thuyết, (2) Luyện tập với câu đơn, (3) Trò chuyện ngắn sử dụng thì quá khứ đơn[cite: 152, 153].

### 4.7. [cite\_start]Game Agent [cite: 154]

  * [cite\_start]**Chức năng:** Cung cấp các trò chơi tương tác để củng cố kiến thức, tăng cường sự hứng thú, và giảm căng thẳng sau các hoạt động học tập[cite: 155].
  * [cite\_start]**Đặc điểm:** Có luật chơi rõ ràng, có tính điểm hoặc phần thưởng, và tập trung vào sự vui vẻ[cite: 156].
  * [cite\_start]**Ví dụ:** `game_dino_quiz_4`, `game_animal_sounds_3`[cite: 157].

### 4.8. [cite\_start]In-session Routing [cite: 158]

**Chức năng:** Hoạt động như một “bộ điều phối cấp thấp” bên trong phiên học. [cite\_start]Nó nhận yêu cầu từ Orchestration Agent và đảm bảo agent tương ứng được tải và thực thi[cite: 159, 160].

| Khía Cạnh | Mô Tả Chi Tiết |
| :--- | :--- |
| **Input** | Một `activity_id` từ Orchestration Agent. |
| **Logic Xử Lý** | 1. Phân tích `activity_id` để xác định loại agent (ví dụ: `game` -\> GameAgent, `lesson_` -\> LearnAgent).<br>2. Tải cấu hình của agent từ cơ sở dữ liệu.<br>3. Xây dựng System Prompt cụ thể cho agent đó.<br>4. Khởi tạo agent và bắt đầu phiên tương tác với người dùng. |
| **Output** | Một agent đang hoạt động, sẵn sàng để tương tác. |
[cite\_start][cite: 161]

-----

## [cite\_start]5. Container 3: Context Handling (Quản Lý Ngữ Cảnh) [cite: 162]

### 5.1. [cite\_start]Tổng Quan và Sơ Đồ Tương Tác [cite: 163]

**Chức năng cốt lõi:** Context Handling là “bộ nhớ” của Pika. Container này chịu trách nhiệm thu thập, xử lý, và duy trì tất cả dữ liệu về người dùng và mối quan hệ của họ với Pika. [cite\_start]Nó cung cấp “nguyên liệu” đầu vào cho Orchestration System để đưa ra các quyết định thông minh và đảm bảo tính liên tục, cá nhân hóa cho trải nghiệm người dùng[cite: 164, 165, 166].

![](image/Pasted%20image%2020251124180917.png)

**Luồng hoạt động chính:**

1.  [cite\_start]Trong suốt quá trình tương tác, Conversational AI Agent (Container 2) liên tục gửi các dữ liệu thô (ví dụ: số lượt trò chuyện, cảm xúc, thông tin quan trọng) đến Context Handling[cite: 188].
2.  [cite\_start]**Daily Metrics Collector** thu thập và lưu trữ tạm thời các chỉ số tương tác trong ngày[cite: 189].
3.  [cite\_start]**Memory Module (Mem0)** tự động phát hiện và lưu trữ các thông tin quan trọng, đáng nhớ dưới dạng có cấu trúc[cite: 190].
4.  [cite\_start]Vào cuối ngày (23:59), một **Daily Background Job** sẽ kích hoạt **Friendship Score Calculator**[cite: 191].
5.  [cite\_start]Calculator đọc dữ liệu từ Daily Metrics, tính toán sự thay đổi, và cập nhật vào các thành phần dài hạn như **Friendship Score**, **Topic Metrics**, và **Dynamic Memory**[cite: 192].
6.  [cite\_start]Khi Orchestration System (Container 1) cần đưa ra quyết định, nó sẽ gọi đến Context Handling để lấy dữ liệu `friendship_status` và memory mới nhất[cite: 193].

### 5.2. [cite\_start]Memory Module (Mem0) [cite: 194]

[cite\_start]**Chức năng:** Hoạt động như một bộ nhớ dài hạn, tự động ghi lại các thông tin quan trọng về người dùng (sở thích, sự kiện trong đời, điểm mạnh/yếu) để Pika có thể “nhớ” và nhắc lại trong các cuộc trò chuyện sau này[cite: 195].

| Component | Chức Năng | Ví Dụ |
| :--- | :--- | :--- |
| **Store Memory** | Tự động phát hiện các thông tin quan trọng từ cuộc hội thoại. | LLM phát hiện câu nói "My dog's name is Milu" và gắn cờ đây là một thông tin cần lưu. |
| **Structure Memory** | Lưu trữ thông tin dưới dạng có cấu trúc (schema-based) để dễ dàng truy vấn. | Lưu dưới dạng `{type: "pet_info", name: "Milu", species: "dog"}`. |
| **Retrieve Memory** | Cung cấp các thông tin liên quan khi được các agent khác yêu cầu. | Khi trò chuyện về chủ đề “động vật”, agent có thể truy vấn Mem0 để hỏi “How is Milu today?". |
[cite\_start][cite: 196]

### 5.3. [cite\_start]Friendship Status Management [cite: 197]

**Chức năng:** Quản lý toàn bộ trạng thái mối quan hệ giữa trẻ và Pika. [cite\_start]Đây là trái tim của việc cá nhân hóa trải nghiệm, quyết định cách Pika tương tác và lựa chọn hoạt động[cite: 198, 199].

| Component | Chức Năng | Cấu Trúc Dữ Liệu (Ví dụ) |
| :--- | :--- | :--- |
| **Daily Metrics Collector** | Thu thập các chỉ số tương tác thô trong một ngày. Dữ liệu này sẽ được xử lý và xóa sau khi cập nhật cuối ngày. | `{"total_turns": 25, "user_initiated_questions": 3, "session_emotion": "interesting"}` |
| **Friendship Score Calculator** | Tính toán sự thay đổi của điểm tình bạn dựa trên các chỉ số trong ngày. | `daily_change_score = (total_turns * 0.5) + (user_questions * 3) + (emotion_bonus)` |
| **Topic Metrics Tracker** | Theo dõi mức độ quan tâm của trẻ đối với từng chủ đề trò chuyện. | `{"agent_movie": {"topic_score": 45.0, "total_turns": 50}, "agent_animal": {"topic_score": 22.5}}` |
| **Dynamic Memory Manager** | Lưu trữ các “ký ức chung” cụ thể, những khoảnh khắc đáng nhớ giữa trẻ và Pika. | `[{"memory_id": "mem_01", "content": "Hứa sẽ cùng nhau xem phim Vùng Đất Linh Hồn."}]` |
[cite\_start][cite: 200]

### 5.4. [cite\_start]Daily Update Logic (Logic Cập Nhật Cuối Ngày) [cite: 201]

[cite\_start]Đây là một quy trình tự động (background job) chạy vào cuối mỗi ngày để đảm bảo dữ liệu `friendship_status` luôn được cập nhật, phản ánh đúng các tương tác trong ngày[cite: 202].

**Quy trình thực thi:**

1.  [cite\_start]**Trigger:** Tác vụ được kích hoạt tự động vào 23:59 mỗi ngày[cite: 204].
2.  [cite\_start]**Query:** Lấy tất cả các bản ghi người dùng có `daily_metrics` không rỗng[cite: 205].
3.  [cite\_start]**Calculate:** Với mỗi người dùng, gọi Friendship Score Calculator để tính toán `daily_change_score`[cite: 206, 207].
4.  [cite\_start]**Update:** [cite: 208]
      * [cite\_start]Cập nhật `friendship_score` và `friendship_level`[cite: 209].
      * [cite\_start]Cập nhật `topic_score` và `total_turns` trong `topic_metrics`[cite: 210].
      * [cite\_start]Cập nhật `streak_day` và `last_interaction_date`[cite: 211].
5.  [cite\_start]**Cleanup:** Reset `daily_metrics` về rỗng để chuẩn bị cho ngày hôm sau[cite: 212].

-----

## [cite\_start]6. Phạm Vi Tác Động của Product Team và Kỹ Thuật [cite: 213]

[cite\_start]Bảng dưới đây phân định rõ trách nhiệm giữa Product Team (PM) và Kỹ Thuật (Engineering) trong việc phát triển và vận hành AI Platform[cite: 214].

| Container | Trách Nhiệm của Product Team (PM) | Trách Nhiệm của Kỹ Thuật (Engineering) |
| :--- | :--- | :--- |
| **1. Orchestration System** | - Định nghĩa **Guiding Principles** cho Master Orchestration.<br>- Thiết kế **Trigger Rules** (ví dụ: khi nào chèn game, khi nào chèn bài ôn tập).<br>- Xác định **Priority Levels** cho các loại hoạt động.<br>- Thiết kế logic lựa chọn cho Talk/Game Management. | - Xây dựng và tối ưu hóa pipeline của Master Orchestration.<br>- Triển khai cơ chế lắng nghe sự kiện của Trigger Agent.<br>- Xây dựng API cho Talk/Game Management.<br>- Đảm bảo Queue Management hoạt động ổn định. |
| **2. Conversational AI Agent** | - Thiết kế **Persona** và giọng văn của Pika.<br>- Viết và tối ưu hóa **System Prompt** cho các loại agent.<br>- Định nghĩa các **Tools** cần thiết cho Tooling Layer.<br>- Thiết kế danh sách **Multimodal Tags** và trải nghiệm đi kèm.<br>- Thiết kế nội dung cho các Learn Agent và Workflow. | - Tinh chỉnh và triển khai các model ASR, LLM, TTS.<br>- Xây dựng Tooling Layer và các API kết nối.<br>- Xây dựng AI Wrapper để xử lý Multimodal Tags.<br>- Xây dựng bộ khung (framework) để chạy các loại agent khác nhau. |
| **3. Context Handling** | - Định nghĩa cấu trúc dữ liệu của Mem0 và Friendship Status.<br>- Thiết kế công thức tính **Friendship Score** và các chỉ số liên quan.<br>- Xác định các loại thông tin cần được lưu vào Mem0.<br>- Thiết kế các cấp độ tình bạn (Friendship Levels) và ý nghĩa của chúng. | - Xây dựng và vận hành cơ sở dữ liệu NoSQL.<br>- Triển khai logic tự động phát hiện và lưu trữ của Mem0.<br>- Xây dựng background job để chạy Daily Update Logic.<br>- Đảm bảo tính toàn vẹn và bảo mật của dữ liệu người dùng. |
[cite\_start][cite: 215]

-----

## [cite\_start]7. Quy Trình Triển Khai Ý Tưởng Sản Phẩm [cite: 216]

1.  [cite\_start]**Ý tưởng (Idea):** PM có một ý tưởng mới, ví dụ: “Pika nên có một hoạt động ôn tập từ vựng hàng tuần”[cite: 217].
2.  **Phân loại (Categorize):** PM xác định ý tưởng này thuộc về container nào. [cite\_start]Trong ví dụ này, nó thuộc về **Orchestration System** (vì liên quan đến việc chèn một hoạt động mới vào kế hoạch)[cite: 218, 219].
3.  **Đặc tả (Specification):** PM viết đặc tả chi tiết cho ý tưởng:
      * [cite\_start]**Trigger:** Time-based, kích hoạt vào mỗi Chủ Nhật hàng tuần[cite: 221].
      * [cite\_start]**Action:** Chèn một `weeklyVocabularyReviewAgent` vào Daily Activities List với `priority: 9`[cite: 222].
      * [cite\_start]**Agent:** `WeeklyVocabularyReviewAgent` sẽ lấy 10 từ vựng mà trẻ hay sai nhất trong tuần từ `learning_status` để ôn tập[cite: 223].
4.  [cite\_start]**Triển khai (Implementation):** [cite: 224]
      * [cite\_start]Team Kỹ thuật (Orchestration): Thêm một quy tắc mới vào Trigger Agent[cite: 225].
      * [cite\_start]Team Kỹ thuật (Conversation): Xây dựng `WeeklyVocabularyReviewAgent` theo đặc tả[cite: 226].
5.  [cite\_start]**Kiểm thử và Ra mắt (Test & Launch):** Tính năng được kiểm thử và triển khai[cite: 227].

-----

## [cite\_start]8. Câu Hỏi Thường Gặp (Q\&A) [cite: 228]

[cite\_start]**Q1: Tại sao lại tách thành 3 container riêng biệt?** [cite: 229]
**A:** Việc tách thành 3 container (Orchestration, Conversation, Context) giúp chúng ta:
(1) [cite\_start]**Phát triển độc lập:** Mỗi team có thể tập trung vào một mảng mà không ảnh hưởng đến các team khác[cite: 230].
(2) [cite\_start]**Tối ưu hóa chuyên sâu:** Có thể lựa chọn công nghệ tốt nhất cho từng nhiệm vụ (ví dụ: dùng LLM cho hoạch định, dùng model nhỏ hơn cho conversation)[cite: 231].
(3) [cite\_start]**Dễ dàng mở rộng:** Có thể thay thế hoặc nâng cấp một container mà không cần xây dựng lại toàn bộ hệ thống[cite: 232].

[cite\_start]**Q2: Master Orchestration và Orchestration Agent khác nhau như thế nào?** [cite: 233]
[cite\_start]**A:** Hãy tưởng tượng **Master Orchestration** là một nhà chiến lược quân sự, người ngồi trong phòng và vạch ra kế hoạch tác chiến cho cả một ngày[cite: 234]. [cite\_start]**Orchestration Agent** là một sĩ quan chỉ huy ngoài mặt trận, người nhận kế hoạch đó và ra lệnh cho từng đơn vị (Talk Agent, Learn Agent) thực hiện nhiệm vụ của mình theo đúng thứ tự[cite: 235].

[cite\_start]**Q3: Trigger Agent có thể làm gián đoạn phiên học của trẻ không?** [cite: 236]
**A:** Không. [cite\_start]Trigger Agent không trực tiếp làm gián đoạn[cite: 237]. [cite\_start]Nó chỉ chèn một hoạt động mới vào hàng đợi (Queue Management)[cite: 238]. Hoạt động đó chỉ được thực thi sau khi trẻ hoàn thành hoạt động hiện tại. [cite\_start]Điều này đảm bảo luồng học tập của trẻ không bị cắt ngang một cách đột ngột[cite: 239, 240].

[cite\_start]**Q4: Dữ liệu trong Context Handling được cập nhật khi nào?** [cite: 241]
**A:** Có hai luồng cập nhật:
(1) [cite\_start]**Cập nhật thời gian thực:** Các chỉ số cơ bản như `total_turns` được cập nhật ngay trong phiên học[cite: 242].
(2) **Cập nhật cuối ngày:** Các chỉ số quan trọng như `friendship_score` và `topic_metrics` được tính toán và cập nhật một lần vào cuối ngày thông qua một background job. [cite\_start]Điều này giúp giảm tải cho hệ thống và đảm bảo tính nhất quán của dữ liệu[cite: 243, 244].

[cite\_start]**Q5: Làm thế nào để thêm một Game mới vào hệ thống?** [cite: 245]
**A:** Quy trình bao gồm:
(1) [cite\_start]**Team Game:** Xây dựng Game Agent mới[cite: 246].
(2) [cite\_start]**Team Kỹ thuật (Conversation):** Tích hợp Game Agent vào framework[cite: 247].
(3) **PM:** Cập nhật kho hoạt động của Talk/Game Management để module này có thể lựa chọn game mới dựa trên các quy tắc đã định. [cite\_start]Master Orchestration không cần thay đổi gì[cite: 248, 249].