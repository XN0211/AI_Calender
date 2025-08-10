import requests
import json

# Test the Flask app endpoints
BASE_URL = "http://127.0.0.1:5000"

def test_basic_functionality():
    """Test basic calendar functionality"""
    print("Testing basic functionality...")
    
    # Test 1: Get notes
    try:
        response = requests.get(f"{BASE_URL}/get_notes")
        if response.status_code == 200:
            print("✅ GET /get_notes - Success")
        else:
            print(f"❌ GET /get_notes - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_notes - Error: {e}")
    
    # Test 2: Get labels
    try:
        response = requests.get(f"{BASE_URL}/get_labels")
        if response.status_code == 200:
            print("✅ GET /get_labels - Success")
        else:
            print(f"❌ GET /get_labels - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_labels - Error: {e}")
    
    # Test 3: Get week dates
    try:
        response = requests.get(f"{BASE_URL}/get_week_dates")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /get_week_dates - Success: {len(data.get('week_dates', []))} dates")
        else:
            print(f"❌ GET /get_week_dates - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_week_dates - Error: {e}")

def test_ai_functionality():
    """Test AI functionality"""
    print("\nTesting AI functionality...")
    
    # Test 1: Generate AI plan
    try:
        data = {"goal": "weekly fitness and study schedule"}
        response = requests.post(f"{BASE_URL}/generate_plan", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ POST /generate_plan - Success")
                print(f"   Generated {len(result.get('plan', {}))} days of activities")
            else:
                print(f"❌ POST /generate_plan - Failed: {result.get('error')}")
        else:
            print(f"❌ POST /generate_plan - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /generate_plan - Error: {e}")
    
    # Test 2: Ask AI
    try:
        data = {"question": "What activities do I have scheduled for this week?"}
        response = requests.post(f"{BASE_URL}/ask_ai", json=data)
        if response.status_code == 200:
            result = response.json()
            if "answer" in result:
                print("✅ POST /ask_ai - Success")
                print(f"   AI Response: {result['answer'][:100]}...")
            else:
                print(f"❌ POST /ask_ai - Failed: {result.get('error')}")
        else:
            print(f"❌ POST /ask_ai - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /ask_ai - Error: {e}")

def test_analytics_functionality():
    """Test analytics functionality"""
    print("\nTesting analytics functionality...")
    
    # Test 1: Get calendar stats
    try:
        response = requests.get(f"{BASE_URL}/get_calendar_stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /get_calendar_stats - Success")
            print(f"   Total notes: {data.get('total_notes', 0)}")
            print(f"   Days with notes: {data.get('total_days_with_notes', 0)}")
        else:
            print(f"❌ GET /get_calendar_stats - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_calendar_stats - Error: {e}")
    
    # Test 2: Get time allocation analysis
    try:
        response = requests.get(f"{BASE_URL}/analyze_time_allocation")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /analyze_time_allocation - Success")
            print(f"   Total activities: {data.get('total_activities', 0)}")
            print(f"   Categories analyzed: {len(data.get('chart_data', []))}")
        else:
            print(f"❌ GET /analyze_time_allocation - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /analyze_time_allocation - Error: {e}")
    
    # Test 3: Get countdowns
    try:
        response = requests.get(f"{BASE_URL}/get_countdowns")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /get_countdowns - Success")
            print(f"   Total countdowns: {data.get('statistics', {}).get('total', 0)}")
        else:
            print(f"❌ GET /get_countdowns - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_countdowns - Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing AI Calendar Application...")
    print("=" * 50)
    
    test_basic_functionality()
    test_ai_functionality()
    test_analytics_functionality()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nTo access the application:")
    print("1. Make sure the Flask server is running: py app.py")
    print("2. Open your browser and go to: http://127.0.0.1:5000")
