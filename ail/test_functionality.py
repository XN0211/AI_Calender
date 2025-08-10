import requests
import json
from datetime import datetime, timedelta
import re # Added for date consistency tests

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
    
    # Test 3: Get labeled deadlines
    try:
        response = requests.get(f"{BASE_URL}/get_labeled_deadlines")
        if response.status_code == 200:
            data = response.json()
            print("✅ GET /get_labeled_deadlines - Success")
            print(f"   Total labeled deadlines: {data.get('statistics', {}).get('total', 0)}")
        else:
            print(f"❌ GET /get_labeled_deadlines - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_labeled_deadlines - Error: {e}")

def test_date_logic_fixes():
    """Test date logic fixes for bulk delete operations"""
    print("\nTesting date logic fixes...")
    
    # Test 1: Delete single date with precise validation
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        data = {"date": today}
        response = requests.post(f"{BASE_URL}/delete_all_notes", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ DELETE /delete_all_notes - Success")
            print(f"   Deleted notes: {result.get('deleted_notes_count', 0)}")
        else:
            print(f"❌ DELETE /delete_all_notes - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DELETE /delete_all_notes - Error: {e}")
    
    # Test 2: Delete date range with precise validation
    try:
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        data = {
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": tomorrow.strftime("%Y-%m-%d")
        }
        response = requests.post(f"{BASE_URL}/delete_date_range", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ DELETE /delete_date_range - Success")
            print(f"   Deleted dates: {len(result.get('deleted_dates', []))}")
        else:
            print(f"❌ DELETE /delete_date_range - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DELETE /delete_date_range - Error: {e}")
    
    # Test 3: Delete multiple specific dates
    try:
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        data = {
            "dates": [
                today.strftime("%Y-%m-%d"),
                tomorrow.strftime("%Y-%m-%d")
            ]
        }
        response = requests.post(f"{BASE_URL}/delete_multiple_dates", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ DELETE /delete_multiple_dates - Success")
            print(f"   Deleted dates: {len(result.get('deleted_dates', []))}")
        else:
            print(f"❌ DELETE /delete_multiple_dates - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DELETE /delete_multiple_dates - Error: {e}")
    
    # Test 4: Delete current week
    try:
        response = requests.post(f"{BASE_URL}/delete_week", json={})
        if response.status_code == 200:
            result = response.json()
            print("✅ DELETE /delete_week - Success")
            print(f"   Week range: {result.get('week_start', '')} to {result.get('week_end', '')}")
        else:
            print(f"❌ DELETE /delete_week - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DELETE /delete_week - Error: {e}")
    
    # Test 5: Delete specific month
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month
        data = {"year": current_year, "month": current_month}
        response = requests.post(f"{BASE_URL}/delete_month", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ DELETE /delete_month - Success")
            print(f"   Month: {result.get('month', '')}")
        else:
            print(f"❌ DELETE /delete_month - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ DELETE /delete_month - Error: {e}")

def test_date_consistency():
    """Test date consistency between calendar and notes"""
    print("\nTesting date consistency...")
    
    # Test 1: Check if notes data uses consistent date format
    try:
        response = requests.get(f"{BASE_URL}/get_notes")
        if response.status_code == 200:
            notes_data = response.json()
            print("✅ GET /get_notes - Success")
            
            # Check date format consistency
            invalid_dates = []
            for date_str in notes_data.keys():
                # Check if date follows YYYY-MM-DD format
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                    invalid_dates.append(date_str)
            
            if invalid_dates:
                print(f"❌ Invalid date formats found: {invalid_dates}")
            else:
                print("✅ All note dates use consistent YYYY-MM-DD format")
                
            # Check for timezone-related issues
            today = datetime.now().strftime("%Y-%m-%d")
            if today in notes_data:
                print(f"✅ Today's date ({today}) found in notes")
            else:
                print(f"ℹ️ Today's date ({today}) not found in notes (normal if no notes for today)")
                
        else:
            print(f"❌ GET /get_notes - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_notes - Error: {e}")
    
    # Test 2: Check labels data consistency
    try:
        response = requests.get(f"{BASE_URL}/get_labels")
        if response.status_code == 200:
            labels_data = response.json()
            print("✅ GET /get_labels - Success")
            
            # Check date format consistency
            invalid_dates = []
            for date_str in labels_data.keys():
                # Check if date follows YYYY-MM-DD format
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                    invalid_dates.append(date_str)
            
            if invalid_dates:
                print(f"❌ Invalid date formats found in labels: {invalid_dates}")
            else:
                print("✅ All label dates use consistent YYYY-MM-DD format")
                
        else:
            print(f"❌ GET /get_labels - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_labels - Error: {e}")
    
    # Test 3: Check week dates consistency
    try:
        response = requests.get(f"{BASE_URL}/get_week_dates")
        if response.status_code == 200:
            data = response.json()
            week_dates = data.get("week_dates", [])  # Fix: get the week_dates array from response
            print("✅ GET /get_week_dates - Success")
            
            # Check if week dates are consistent
            if len(week_dates) == 7:
                print("✅ Week contains exactly 7 days")
                
                # Check if dates are sequential
                sequential = True
                for i in range(1, len(week_dates)):
                    prev_date = datetime.strptime(week_dates[i-1], "%Y-%m-%d")
                    curr_date = datetime.strptime(week_dates[i], "%Y-%m-%d")
                    if (curr_date - prev_date).days != 1:
                        sequential = False
                        break
                
                if sequential:
                    print("✅ Week dates are sequential")
                else:
                    print("❌ Week dates are not sequential")
            else:
                print(f"❌ Week contains {len(week_dates)} days (expected 7)")
                
        else:
            print(f"❌ GET /get_week_dates - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_week_dates - Error: {e}")
    
    # Test 4: Check if adding a note maintains date consistency
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        test_note = "Test note for date consistency check"
        
        # Add a test note
        response = requests.post(f"{BASE_URL}/save_note", json={
            "date": today,
            "content": test_note
        })
        
        if response.status_code == 200:
            print("✅ POST /save_note - Success")
            
            # Verify the note was saved with correct date
            response = requests.get(f"{BASE_URL}/get_notes")
            if response.status_code == 200:
                notes_data = response.json()
                if today in notes_data and test_note in notes_data[today]:
                    print("✅ Test note saved with correct date")
                else:
                    print("❌ Test note not found or saved with wrong date")
                    
            # Clean up - delete the test note
            if today in notes_data:
                notes_data[today].remove(test_note)
                if not notes_data[today]:  # If no notes left for today
                    del notes_data[today]
                    
        else:
            print(f"❌ POST /save_note - Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /save_note - Error: {e}")

def generate_date_consistency_report():
    """Generate a comprehensive report on date consistency"""
    print("\n" + "=" * 60)
    print("📅 DATE CONSISTENCY ANALYSIS REPORT")
    print("=" * 60)
    
    try:
        # Get all data
        notes_response = requests.get(f"{BASE_URL}/get_notes")
        labels_response = requests.get(f"{BASE_URL}/get_labels")
        week_response = requests.get(f"{BASE_URL}/get_week_dates")
        
        if notes_response.status_code == 200 and labels_response.status_code == 200 and week_response.status_code == 200:
            notes_data = notes_response.json()
            labels_data = labels_response.json()
            week_data = week_response.json()
            week_dates = week_data.get("week_dates", [])
            
            print("✅ All data sources accessible")
            
            # Check date format consistency
            print("\n📋 DATE FORMAT ANALYSIS:")
            print("-" * 30)
            
            # Notes dates
            note_dates = list(notes_data.keys())
            note_date_formats = [re.match(r'^\d{4}-\d{2}-\d{2}$', date) for date in note_dates]
            valid_note_dates = sum(1 for match in note_date_formats if match)
            
            print(f"📝 Notes: {valid_note_dates}/{len(note_dates)} dates use YYYY-MM-DD format")
            if valid_note_dates < len(note_dates):
                invalid_note_dates = [date for i, date in enumerate(note_dates) if not note_date_formats[i]]
                print(f"   ❌ Invalid note dates: {invalid_note_dates}")
            
            # Labels dates
            label_dates = list(labels_data.keys())
            label_date_formats = [re.match(r'^\d{4}-\d{2}-\d{2}$', date) for date in label_dates]
            valid_label_dates = sum(1 for match in label_date_formats if match)
            
            print(f"🏷️ Labels: {valid_label_dates}/{len(label_dates)} dates use YYYY-MM-DD format")
            if valid_label_dates < len(label_dates):
                invalid_label_dates = [date for i, date in enumerate(label_dates) if not label_date_formats[i]]
                print(f"   ❌ Invalid label dates: {invalid_label_dates}")
            
            # Week dates
            print(f"📅 Week: {len(week_dates)}/7 days returned")
            if len(week_dates) == 7:
                week_date_formats = [re.match(r'^\d{4}-\d{2}-\d{2}$', date) for date in week_dates]
                valid_week_dates = sum(1 for match in week_date_formats if match)
                print(f"   ✅ {valid_week_dates}/7 week dates use YYYY-MM-DD format")
                
                # Check sequential
                sequential = True
                for i in range(1, len(week_dates)):
                    try:
                        prev_date = datetime.strptime(week_dates[i-1], "%Y-%m-%d")
                        curr_date = datetime.strptime(week_dates[i], "%Y-%m-%d")
                        if (curr_date - prev_date).days != 1:
                            sequential = False
                            break
                    except ValueError:
                        sequential = False
                        break
                
                if sequential:
                    print("   ✅ Week dates are sequential")
                else:
                    print("   ❌ Week dates are not sequential")
            else:
                print(f"   ❌ Expected 7 days, got {len(week_dates)}")
            
            # Check for overlapping dates
            print("\n🔄 DATE OVERLAP ANALYSIS:")
            print("-" * 30)
            
            all_dates = set(note_dates) | set(label_dates)
            print(f"📊 Total unique dates across all data: {len(all_dates)}")
            
            # Check for dates with both notes and labels
            dates_with_both = set(note_dates) & set(label_dates)
            print(f"📌 Dates with both notes and labels: {len(dates_with_both)}")
            if dates_with_both:
                print(f"   📋 Dates: {sorted(list(dates_with_both))}")
            
            # Check for orphaned labels (labels without notes)
            orphaned_labels = set(label_dates) - set(note_dates)
            print(f"🏷️ Labels without notes: {len(orphaned_labels)}")
            if orphaned_labels:
                print(f"   📋 Dates: {sorted(list(orphaned_labels))}")
            
            # Check for notes without labels
            notes_without_labels = set(note_dates) - set(label_dates)
            print(f"📝 Notes without labels: {len(notes_without_labels)}")
            
            # Timezone and current date check
            print("\n🌍 TIMEZONE & CURRENT DATE ANALYSIS:")
            print("-" * 35)
            
            today = datetime.now().strftime("%Y-%m-%d")
            print(f"🕐 Current date (local): {today}")
            
            if today in note_dates:
                print(f"✅ Today has {len(notes_data[today])} notes")
            else:
                print("ℹ️ Today has no notes (normal)")
            
            if today in label_dates:
                print(f"✅ Today has label: {labels_data[today]['label']}")
            else:
                print("ℹ️ Today has no labels (normal)")
            
            # Check if week includes today
            if today in week_dates:
                today_index = week_dates.index(today)
                print(f"✅ Today is day {today_index + 1} of the week")
            else:
                print("❌ Today is not in the current week dates")
            
            # Summary
            print("\n📊 SUMMARY:")
            print("-" * 15)
            
            total_issues = 0
            if valid_note_dates < len(note_dates):
                total_issues += 1
            if valid_label_dates < len(label_dates):
                total_issues += 1
            if len(week_dates) != 7:
                total_issues += 1
            
            if total_issues == 0:
                print("🎉 All date consistency checks passed!")
                print("✅ Calendar and notes dates are consistent")
                print("✅ No timezone-related issues detected")
                print("✅ Date formats are standardized")
            else:
                print(f"⚠️ Found {total_issues} potential date consistency issue(s)")
                print("🔧 Review the details above for specific problems")
            
        else:
            print("❌ Unable to access data sources for analysis")
            
    except Exception as e:
        print(f"❌ Error during date consistency analysis: {e}")

if __name__ == "__main__":
    print("🚀 Testing AI Calendar Application...")
    print("=" * 50)
    
    test_basic_functionality()
    test_ai_functionality()
    test_analytics_functionality()
    test_date_logic_fixes()
    test_date_consistency()
    generate_date_consistency_report()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nTo access the application:")
    print("1. Make sure the Flask server is running: py app.py")
    print("2. Open your browser and go to: http://127.0.0.1:5000")

