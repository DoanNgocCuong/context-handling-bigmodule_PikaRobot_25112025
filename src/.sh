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
