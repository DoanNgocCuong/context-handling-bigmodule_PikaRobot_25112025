"""
Simple test script for health check endpoint.
Run this to verify the health check API works.
"""
import requests
import json

def test_health_check():
    """Test health check endpoint."""
    url = "http://localhost:8000/v1/health"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")
        
        if response.status_code == 200:
            print("\n✅ Health check passed!")
        else:
            print(f"\n⚠️ Health check returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running:")
        print("   uvicorn app.main_app:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_health_check()

