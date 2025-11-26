```
# 1. Install dependencies
cd src
pip install -r requirements.txt

# 2. Setup environment (optional)
cp .env.example .env

# 3. Run server
uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020

# 4. Test health check
curl http://localhost:8000/v1/health

# Or use test script
python test_health.py
```


----

1. Health check
```
curl -X 'GET' \
  'http://localhost:30020/v1/health' \
  -H 'accept: application/json'
```
# 2. From conversation_id -> calculate score -> update friendship_status:
```
## 2.1 Test GET conversation
curl -X GET "http://localhost:8000/v1/conversations/conv_id_2003doanngoccuong" \
  -H "Content-Type: application/json"

## 2.2 Test POST calculate score
curl -X POST "http://localhost:8000/v1/friendship_status/calculate-score/conv_id_2003doanngoccuong" \
  -H "Content-Type: application/json"

## 2.3 Test POST update friendship_status
curl -X POST "http://localhost:8000/v1/friendship_status/calculate-score-and-update" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_doanngoccuong",
    "conversation_id": "conv_id_2003doanngoccuong"
  }'
```




3. From user_id -> get suggested activities:
```
curl -X POST "http://localhost:8000/v1/activities/suggest" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_doanngoccuong"
  }'
```