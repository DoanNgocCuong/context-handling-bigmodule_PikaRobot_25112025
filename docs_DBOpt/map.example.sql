--- Initial data for friendship_agent_mapping
-- Greeting agents cho STRANGER
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('STRANGER', 'GREETING', 'greeting_welcome', 'Welcome Greeting', 'Chào mừng người dùng mới', 1.0, TRUE),
('STRANGER', 'GREETING', 'greeting_intro', 'Introduce Pika', 'Giới thiệu về Pika', 1.5, TRUE);

-- Talk agents cho STRANGER
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('STRANGER', 'TALK', 'talk_hobbies', 'Hobbies Talk', 'Nói về sở thích', 1.0, TRUE),
('STRANGER', 'TALK', 'talk_school', 'School Life Talk', 'Nói về học tập', 1.0, TRUE),
('STRANGER', 'TALK', 'talk_pets', 'Pets Talk', 'Nói về thú cưng', 0.8, TRUE);

-- Game agents cho STRANGER
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('STRANGER', 'GAME_ACTIVITY', 'game_drawing', 'Drawing Game', 'Trò chơi vẽ', 1.0, TRUE),
('STRANGER', 'GAME_ACTIVITY', 'game_riddle', 'Riddle Game', 'Trò chơi đố', 0.9, TRUE);

-- Greeting agents cho ACQUAINTANCE
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('ACQUAINTANCE', 'GREETING', 'greeting_streak_5days', 'Streak 5 Days', 'Chúc mừng 5 ngày liên tiếp', 1.5, TRUE),
('ACQUAINTANCE', 'GREETING', 'greeting_memory_recall', 'Memory Recall', 'Nhắc lại ký ức chung', 2.0, TRUE);

-- Talk agents cho ACQUAINTANCE
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('ACQUAINTANCE', 'TALK', 'talk_movie_preference', 'Movie Preference', 'Nói về phim yêu thích', 1.2, TRUE),
('ACQUAINTANCE', 'TALK', 'talk_dreams', 'Dreams Talk', 'Nói về ước mơ', 1.0, TRUE);

-- Game agents cho ACQUAINTANCE
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('ACQUAINTANCE', 'GAME_ACTIVITY', 'game_20questions', '20 Questions', 'Trò chơi 20 câu hỏi', 1.0, TRUE),
('ACQUAINTANCE', 'GAME_ACTIVITY', 'game_story_building', 'Story Building', 'Xây dựng câu chuyện chung', 1.5, TRUE);

-- Greeting agents cho FRIEND
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('FRIEND', 'GREETING', 'greeting_special_moment', 'Special Moment', 'Khoảnh khắc đặc biệt', 2.0, TRUE),
('FRIEND', 'GREETING', 'greeting_anniversary', 'Anniversary', 'Kỷ niệm ngày gặp nhau', 2.5, TRUE);

-- Talk agents cho FRIEND
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('FRIEND', 'TALK', 'talk_deep_conversation', 'Deep Conversation', 'Cuộc trò chuyện sâu sắc', 1.5, TRUE),
('FRIEND', 'TALK', 'talk_future_plans', 'Future Plans', 'Nói về kế hoạch tương lai', 1.3, TRUE);

-- Game agents cho FRIEND
INSERT INTO friendship_agent_mapping (friendship_level, agent_type, agent_id, agent_name, agent_description, weight, is_active)
VALUES 
('FRIEND', 'GAME_ACTIVITY', 'game_adventure', 'Adventure Quest', 'Cuộc phiêu lưu chung', 1.5, TRUE),
('FRIEND', 'GAME_ACTIVITY', 'game_collaborative_art', 'Collaborative Art', 'Tạo tác phẩm nghệ thuật chung', 2.0, TRUE);