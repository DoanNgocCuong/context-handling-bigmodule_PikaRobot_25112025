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

2. Tính điểm: 
```
# Test GET conversation
curl -X GET "http://localhost:8000/v1/conversations/conv_id_2003doanngoccuong" \
  -H "Content-Type: application/json"

# Test POST calculate score
curl -X POST "http://localhost:8000/v1/friendship/calculate-score/conv_id_2003doanngoccuong" \
  -H "Content-Type: application/json"
```


