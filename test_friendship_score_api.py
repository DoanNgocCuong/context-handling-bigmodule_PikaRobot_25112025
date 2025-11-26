"""
Test script for Friendship Score Calculation API.
Run this to verify the API works correctly.
"""
import requests
import json
from typing import Dict, Any


def test_get_conversation(conversation_id: str):
    """Test GET /conversations/{conversation_id} endpoint."""
    url = f"http://localhost:8000/v1/conversations/{conversation_id}"
    
    print(f"\n{'='*60}")
    print(f"Testing GET Conversation API")
    print(f"{'='*60}")
    print(f"Conversation ID: {conversation_id}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print("\nResponse:")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ ERROR - Status Code: {response.status_code}")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2, default=str))
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server.")
        print("   Make sure the server is running:")
        print("   uvicorn app.main_app:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_calculate_friendship_score(conversation_id: str):
    """
    Test friendship score calculation API.
    
    Args:
        conversation_id: ID of conversation to calculate score for
    """
    url = f"http://localhost:8000/v1/friendship/calculate-score/{conversation_id}"
    
    print(f"\n{'='*60}")
    print(f"Testing Friendship Score Calculation")
    print(f"{'='*60}")
    print(f"Conversation ID: {conversation_id}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, timeout=10)
        
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print("\nResponse:")
            print(json.dumps(data, indent=2, default=str))
            
            # Display calculation breakdown
            if "data" in data and "calculation_details" in data["data"]:
                details = data["data"]["calculation_details"]
                print("\n" + "="*60)
                print("CALCULATION BREAKDOWN:")
                print("="*60)
                print(f"Total Turns: {details.get('total_turns', 0)}")
                print(f"User Initiated Questions: {details.get('user_initiated_questions', 0)}")
                print(f"Session Emotion: {details.get('session_emotion', 'N/A')}")
                print(f"New Memories Count: {details.get('new_memories_count', 0)}")
                print("-"*60)
                print(f"Base Score: {details.get('base_score', 0)}")
                print(f"Engagement Bonus: {details.get('engagement_bonus', 0)}")
                print(f"Emotion Bonus: {details.get('emotion_bonus', 0)}")
                print(f"Memory Bonus: {details.get('memory_bonus', 0)}")
                print("-"*60)
                print(f"Final Score Change: {details.get('final_score_change', 0)}")
                print("="*60)
        
        elif response.status_code == 404:
            print("❌ CONVERSATION NOT FOUND")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2, default=str))
        
        elif response.status_code == 400:
            print("❌ BAD REQUEST - Invalid format or calculation")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2, default=str))
        
        else:
            print(f"❌ ERROR - Status Code: {response.status_code}")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2, default=str))
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server.")
        print("   Make sure the server is running:")
        print("   uvicorn app.main_app:app --reload --host 0.0.0.0 --port 8000")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def test_with_sample_data():
    """Test with sample conversation data."""
    # Sample conversation IDs to test
    test_cases = [
        "conv_id_2003doanngoccuong",
        "conv_test_123",
        "conv_invalid_999"  # Should fail validation
    ]
    
    for conversation_id in test_cases:
        print("\n" + "="*80)
        print(f"TESTING: {conversation_id}")
        print("="*80)
        
        # Test GET conversation
        test_get_conversation(conversation_id)
        
        # Test calculate score
        test_calculate_friendship_score(conversation_id)
        
        print("\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with provided conversation_id
        conversation_id = sys.argv[1]
        test_get_conversation(conversation_id)
        test_calculate_friendship_score(conversation_id)
    else:
        # Test with sample data
        test_with_sample_data()

