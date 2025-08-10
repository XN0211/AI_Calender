from flask import Flask, render_template, request, jsonify
import json
import os
import re
from datetime import datetime, timedelta
import google.generativeai as genai
import logging
import random # Added for fallback_categorization
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
NOTES_FILE = "notes.json"
LABELS_FILE = "labels.json"

# Configure Gemini API
genai.configure(api_key="classified")

def load_notes():
    """Load notes from JSON file with error handling"""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to parse notes.json, starting with empty data")
                return {}
    return {}

def save_notes(notes):
    """Save notes to JSON file with proper formatting"""
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def load_labels():
    """Load date labels from JSON file with error handling"""
    if os.path.exists(LABELS_FILE):
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to parse labels.json, starting with empty data")
                return {}
    return {}

def save_labels(labels):
    """Save date labels to JSON file with proper formatting"""
    with open(LABELS_FILE, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)

def get_current_week_dates():
    """Get the next 7 days starting from today in YYYY-MM-DD format"""
    today = datetime.now()
    week_dates = []
    for i in range(7):
        date = today + timedelta(days=i)
        week_dates.append(date.strftime("%Y-%m-%d"))
    return week_dates

def get_month_dates(year, month):
    """Get all dates for a specific month"""
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month + 1, 0)
    
    dates = []
    current = first_day
    while current <= last_day:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    return dates

def parse_ai_plan(ai_response):
    """Parse AI response to extract daily plans with improved error handling"""
    try:
        logger.info(f"Parsing AI response: {ai_response[:200]}...")
        
        # Try to extract structured plan from AI response
        lines = ai_response.strip().split('\n')
        daily_plans = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for date patterns like "Monday:", "週一:", "Day 1:", etc.
            date_patterns = [
                r'^(週[一二三四五六日]|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Day \d+)[:：]\s*(.+)',
                r'^(\d{1,2}月\d{1,2}日)[:：]\s*(.+)',
                r'^(\d{4}-\d{2}-\d{2})[:：]\s*(.+)',
                r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[:：]\s*(.+)',
                r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[:：]\s*(.+)'
            ]
            
            for pattern in date_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    date_key = match.group(1)
                    activities_text = match.group(2)
                    
                    # Handle different activity separators
                    if '、' in activities_text:
                        activities = activities_text.split('、')
                    elif ',' in activities_text:
                        activities = activities_text.split(',')
                    elif ';' in activities_text:
                        activities = activities_text.split(';')
                    else:
                        activities = [activities_text]
                    
                    # Clean up activities
                    cleaned_activities = []
                    for act in activities:
                        act = act.strip()
                        if act and act not in ['', ' ', '•', '-']:
                            # Remove common prefixes
                            act = re.sub(r'^[•\-*]\s*', '', act)
                            cleaned_activities.append(act)
                    
                    if cleaned_activities:
                        daily_plans[date_key] = cleaned_activities
                        logger.info(f"Parsed {date_key}: {cleaned_activities}")
                    break
        
        logger.info(f"Successfully parsed {len(daily_plans)} days")
        return daily_plans
        
    except Exception as e:
        logger.error(f"Error parsing AI plan: {e}")
        return {}

def map_weekday_to_date(weekday, week_dates):
    """Map weekday names to actual dates with improved mapping"""
    weekday_mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        '週一': 0, '週二': 1, '週三': 2, '週四': 3,
        '週五': 4, '週六': 5, '週日': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    weekday_lower = weekday.lower()
    if weekday_lower in weekday_mapping:
        day_index = weekday_mapping[weekday_lower]
        if day_index < len(week_dates):
            return week_dates[day_index]
    
    # Try to extract day number from "Day X" format
    day_match = re.match(r'day\s*(\d+)', weekday_lower)
    if day_match:
        day_num = int(day_match.group(1)) - 1  # Convert to 0-based index
        if 0 <= day_num < len(week_dates):
            return week_dates[day_num]
    
    logger.warning(f"Could not map weekday '{weekday}' to date")
    return None

def create_fallback_plan(goal, week_dates):
    """Create a simple fallback plan when AI parsing fails"""
    logger.info("Creating fallback plan")
    
    fallback_activities = {
        '週一': [f"Start {goal} today", "Set daily goals"],
        '週二': [f"Continue {goal} focus", "Track progress"],
        '週三': [f"Mid-week {goal} review", "Adjust plans if needed"],
        '週四': [f"Advance {goal} projects", "Prepare for weekend"],
        '週五': [f"Complete {goal} tasks", "Week review"],
        '週六': [f"Light {goal} activity", "Rest and recharge"],
        '週日': [f"Plan next week", "Rest and prepare"]
    }
    
    return fallback_activities

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_notes", methods=["GET"])
def get_notes():
    """Get all notes from the calendar"""
    notes = load_notes()
    return jsonify(notes)

@app.route("/get_labels", methods=["GET"])
def get_labels():
    """Get all date labels from the calendar"""
    labels = load_labels()
    return jsonify(labels)

@app.route("/save_label", methods=["POST"])
def save_label():
    """Save a label for a specific date"""
    data = request.get_json()
    date = data.get("date")
    label = data.get("label")
    color = data.get("color", "#ff6b6b")  # Default color

    if not date or not label:
        return jsonify({"error": "Please provide date and label"}), 400

    # Validate color format
    if not re.match(r'^#[0-9a-fA-F]{6}$', color):
        return jsonify({"error": "Invalid color format. Use hex format (e.g., #ff6b6b)"}), 400

    labels = load_labels()
    labels[date] = {
        "label": label,
        "color": color,
        "created_at": datetime.now().isoformat()
    }
    save_labels(labels)
    return jsonify({"status": "success"})

@app.route("/update_label", methods=["POST"])
def update_label():
    """Update a label for a specific date"""
    data = request.get_json()
    date = data.get("date")
    label = data.get("label")
    color = data.get("color")

    if not date or not label:
        return jsonify({"error": "Please provide date and label"}), 400

    # Validate color format if provided
    if color and not re.match(r'^#[0-9a-fA-F]{6}$', color):
        return jsonify({"error": "Invalid color format. Use hex format (e.g., #ff6b6b)"}), 400

    labels = load_labels()
    if date not in labels:
        return jsonify({"error": "Label not found for this date"}), 404

    labels[date]["label"] = label
    if color:
        labels[date]["color"] = color
    labels[date]["updated_at"] = datetime.now().isoformat()
    
    save_labels(labels)
    return jsonify({"status": "success"})

@app.route("/delete_label", methods=["POST"])
def delete_label():
    """Delete a label from a specific date"""
    data = request.get_json()
    date = data.get("date")

    if not date:
        return jsonify({"error": "Please provide date"}), 400

    labels = load_labels()
    if date in labels:
        del labels[date]
        save_labels(labels)
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Label not found for this date"}), 404

@app.route("/get_labels_for_month", methods=["GET"])
def get_labels_for_month():
    """Get labels for a specific month"""
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    
    if year is None or month is None:
        return jsonify({"error": "Please provide year and month parameters"}), 400
    
    month_dates = get_month_dates(year, month)
    labels = load_labels()
    
    month_labels = {}
    for date in month_dates:
        if date in labels:
            month_labels[date] = labels[date]
    
    return jsonify(month_labels)

@app.route("/get_notes_for_month", methods=["GET"])
def get_notes_for_month():
    """Get notes for a specific month"""
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    
    if year is None or month is None:
        return jsonify({"error": "Please provide year and month parameters"}), 400
    
    month_dates = get_month_dates(year, month)
    notes = load_notes()
    
    month_notes = {}
    for date in month_dates:
        if date in notes:
            month_notes[date] = notes[date]
    
    return jsonify(month_notes)

@app.route("/save_note", methods=["POST"])
def save_note():
    """Save a single note for a specific date"""
    data = request.get_json()
    date = data.get("date")
    content = data.get("content")

    if not date or content is None:
        return jsonify({"error": "Please provide date and content"}), 400

    notes = load_notes()
    notes.setdefault(date, [])
    notes[date].append(content)
    save_notes(notes)
    return jsonify({"status": "success"})

@app.route("/update_note", methods=["POST"])
def update_note():
    """Update all notes for a specific date"""
    data = request.get_json()
    date = data.get("date")
    contents = data.get("contents")

    if not date or not isinstance(contents, list):
        return jsonify({"error": "Please provide date and contents list"}), 400

    notes = load_notes()
    notes[date] = contents
    save_notes(notes)
    return jsonify({"status": "success"})

@app.route("/delete_note", methods=["POST"])
def delete_note():
    """Delete a specific note from a date"""
    data = request.get_json()
    date = data.get("date")
    note_index = data.get("note_index")

    if not date or note_index is None:
        return jsonify({"error": "Please provide date and note index"}), 400

    notes = load_notes()
    if date in notes and 0 <= note_index < len(notes[date]):
        notes[date].pop(note_index)
        if not notes[date]:  # Remove date if no notes left
            del notes[date]
        save_notes(notes)
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Note not found"}), 404

@app.route("/delete_all_notes", methods=["POST"])
def delete_all_notes():
    """Delete all notes for a specific date"""
    data = request.get_json()
    date = data.get("date")

    if not date:
        return jsonify({"error": "Please provide date"}), 400

    notes = load_notes()
    if date in notes:
        del notes[date]
        save_notes(notes)
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "No notes found for this date"}), 404

@app.route("/delete_date_range", methods=["POST"])
def delete_date_range():
    """Delete all notes within a date range"""
    data = request.get_json()
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "Please provide both start_date and end_date"}), 400

    try:
        # Validate date format
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_dt > end_dt:
            return jsonify({"error": "Start date must be before or equal to end date"}), 400
            
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    notes = load_notes()
    deleted_dates = []
    deleted_count = 0
    
    # Generate all dates in the range
    current_dt = start_dt
    while current_dt <= end_dt:
        current_date = current_dt.strftime("%Y-%m-%d")
        if current_date in notes:
            deleted_count += len(notes[current_date])
            deleted_dates.append(current_date)
            del notes[current_date]
        current_dt += timedelta(days=1)
    
    if deleted_dates:
        save_notes(notes)
        return jsonify({
            "status": "success",
            "deleted_dates": deleted_dates,
            "deleted_notes_count": deleted_count,
            "message": f"Deleted {len(deleted_dates)} days with {deleted_count} total notes"
        })
    else:
        return jsonify({"error": "No notes found in the specified date range"}), 404

@app.route("/delete_multiple_dates", methods=["POST"])
def delete_multiple_dates():
    """Delete notes for multiple specific dates"""
    data = request.get_json()
    dates = data.get("dates", [])

    if not dates or not isinstance(dates, list):
        return jsonify({"error": "Please provide a list of dates"}), 400

    if len(dates) == 0:
        return jsonify({"error": "Please provide at least one date"}), 400

    notes = load_notes()
    deleted_dates = []
    deleted_count = 0
    
    for date in dates:
        if date in notes:
            deleted_count += len(notes[date])
            deleted_dates.append(date)
            del notes[date]
    
    if deleted_dates:
        save_notes(notes)
        return jsonify({
            "status": "success",
            "deleted_dates": deleted_dates,
            "deleted_notes_count": deleted_count,
            "message": f"Deleted {len(deleted_dates)} days with {deleted_count} total notes"
        })
    else:
        return jsonify({"error": "No notes found for the specified dates"}), 404

@app.route("/delete_week", methods=["POST"])
def delete_week():
    """Delete all notes for the current week"""
    data = request.get_json()
    week_start = data.get("week_start")  # Optional: specific week start date
    
    if week_start:
        try:
            start_dt = datetime.strptime(week_start, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    else:
        # Use current week starting from Monday
        today = datetime.now()
        days_since_monday = today.weekday()
        start_dt = today - timedelta(days=days_since_monday)
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    end_dt = start_dt + timedelta(days=6)
    
    notes = load_notes()
    deleted_dates = []
    deleted_count = 0
    
    current_dt = start_dt
    while current_dt <= end_dt:
        current_date = current_dt.strftime("%Y-%m-%d")
        if current_date in notes:
            deleted_count += len(notes[current_date])
            deleted_dates.append(current_date)
            del notes[current_date]
        current_dt += timedelta(days=1)
    
    if deleted_dates:
        save_notes(notes)
        return jsonify({
            "status": "success",
            "deleted_dates": deleted_dates,
            "deleted_notes_count": deleted_count,
            "week_start": start_dt.strftime("%Y-%m-%d"),
            "week_end": end_dt.strftime("%Y-%m-%d"),
            "message": f"Deleted week from {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')} with {deleted_count} total notes"
        })
    else:
        return jsonify({
            "status": "success",
            "message": f"No notes found for week from {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
        })

@app.route("/delete_month", methods=["POST"])
def delete_month():
    """Delete all notes for a specific month"""
    data = request.get_json()
    year = data.get("year")
    month = data.get("month")
    
    if year is None or month is None:
        return jsonify({"error": "Please provide both year and month"}), 400
    
    try:
        year = int(year)
        month = int(month)
        if month < 1 or month > 12:
            return jsonify({"error": "Month must be between 1 and 12"}), 400
    except ValueError:
        return jsonify({"error": "Year and month must be valid numbers"}), 400
    
    start_dt = datetime(year, month, 1)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_dt = datetime(year, month + 1, 1) - timedelta(days=1)
    
    notes = load_notes()
    deleted_dates = []
    deleted_count = 0
    
    current_dt = start_dt
    while current_dt <= end_dt:
        current_date = current_dt.strftime("%Y-%m-%d")
        if current_date in notes:
            deleted_count += len(notes[current_date])
            deleted_dates.append(current_date)
            del notes[current_date]
        current_dt += timedelta(days=1)
    
    if deleted_dates:
        save_notes(notes)
        month_name = start_dt.strftime("%B %Y")
        return jsonify({
            "status": "success",
            "deleted_dates": deleted_dates,
            "deleted_notes_count": deleted_count,
            "month": month_name,
            "message": f"Deleted {month_name} with {deleted_count} total notes"
        })
    else:
        month_name = start_dt.strftime("%B %Y")
        return jsonify({
            "status": "success",
            "message": f"No notes found for {month_name}"
        })

@app.route("/generate_plan", methods=["POST"])
def generate_plan():
    """Generate AI-powered weekly plan with improved error handling"""
    data = request.get_json()
    planning_goal = data.get("goal", "").strip()
    
    if not planning_goal:
        return jsonify({"error": "Please provide a planning goal"}), 400

    logger.info(f"Generating plan for goal: {planning_goal}")

    # Get current week dates
    week_dates = get_current_week_dates()
    logger.info(f"Week dates: {week_dates}")
    
    # Create prompt for AI planning
    prompt = f"""
    As an AI calendar assistant, please create a detailed weekly schedule based on this goal: "{planning_goal}"
    
    The schedule should start from TODAY and cover the next 7 days. Please provide a structured plan with the following format:
    
    週一: [activities separated by 、]
    週二: [activities separated by 、]
    週三: [activities separated by 、]
    週四: [activities separated by 、]
    週五: [activities separated by 、]
    週六: [activities separated by 、]
    週日: [activities separated by 、]
    
    Note: The first day (週一) represents TODAY, and the schedule covers the next 7 days.
    Make sure each day has 2-4 specific, actionable activities that align with the goal.
    Keep activities concise but descriptive.
    Only respond with the schedule in the exact format requested.
    """

    try:
        # Use Gemini API to generate plan
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        ai_response = response.text
        
        logger.info(f"AI Response received: {ai_response[:300]}...")
        
        # Parse the AI response
        daily_plans = parse_ai_plan(ai_response)
        
        # If parsing failed, create fallback plan
        if not daily_plans:
            logger.warning("AI parsing failed, using fallback plan")
            daily_plans = create_fallback_plan(planning_goal, week_dates)
        
        # Map weekday names to actual dates and save to calendar
        notes = load_notes()
        saved_plans = {}
        
        for weekday, activities in daily_plans.items():
            actual_date = map_weekday_to_date(weekday, week_dates)
            if actual_date:
                notes[actual_date] = activities
                saved_plans[actual_date] = activities
                logger.info(f"Mapped {weekday} to {actual_date}: {activities}")
            else:
                logger.warning(f"Could not map {weekday} to a date")
        
        save_notes(notes)
        
        return jsonify({
            "status": "success",
            "plan": saved_plans,
            "ai_response": ai_response,
            "parsed_plans": daily_plans
        })
        
    except Exception as e:
        logger.error(f"AI planning error: {str(e)}")
        return jsonify({"error": f"AI planning error: {str(e)}"}), 500

@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    """AI Q&A about existing schedule with improved error handling"""
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please provide a question"}), 400
    
    logger.info(f"AI Q&A request: {question}")
    notes = load_notes()
    
    # Create summary of current schedule
    if notes:
        notes_summary = []
        for date, activities in notes.items():
            if isinstance(activities, dict):
                acts = "、".join(activities.get('activities', []))
            else:
                acts = "、".join(activities)
            notes_summary.append(f"{date}: {acts}")
        schedule_text = "\n".join(notes_summary)
        logger.info(f"Current schedule: {schedule_text}")
    else:
        schedule_text = "Currently no scheduled activities."
        logger.info("No current schedule found")
    
    # Create prompt for AI analysis
    prompt = f"""
    You are an AI calendar assistant. Here is the user's current schedule:
    {schedule_text}
    
    User's question: {question}
    
    Please provide a helpful, personalized response based on their schedule. If they're asking for advice, consider their current commitments and suggest improvements. If they're asking about specific dates or activities, provide relevant information. Keep your response concise but informative. Respond in a friendly, helpful tone.
    """
    
    try:
        # Use Gemini API for Q&A
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        answer = response.text
        logger.info(f"AI Q&A response: {answer[:200]}...")
        return jsonify({"answer": answer})
    except Exception as e:
        logger.error(f"AI response error: {str(e)}")
        return jsonify({"error": f"AI response error: {str(e)}"}), 500

@app.route("/get_week_dates", methods=["GET"])
def get_week_dates():
    """Get current week dates for frontend"""
    week_dates = get_current_week_dates()
    return jsonify({"week_dates": week_dates})

@app.route("/get_calendar_stats", methods=["GET"])
def get_calendar_stats():
    """Get calendar statistics"""
    notes = load_notes()
    
    total_notes = sum(len(notes_list) for notes_list in notes.values())
    total_days_with_notes = len(notes)
    
    # Get notes for current week
    week_dates = get_current_week_dates()
    week_notes = sum(len(notes.get(date, [])) for date in week_dates)
    
    stats = {
        "total_notes": total_notes,
        "total_days_with_notes": total_days_with_notes,
        "current_week_notes": week_notes,
        "most_active_day": None,
        "recent_activity": []
    }
    
    # Find most active day
    if notes:
        most_active_date = max(notes.keys(), key=lambda x: len(notes[x]))
        stats["most_active_day"] = {
            "date": most_active_date,
            "note_count": len(notes[most_active_date])
        }
    
    # Get recent activity (last 5 days with notes)
    recent_dates = sorted(notes.keys(), reverse=True)[:5]
    stats["recent_activity"] = [
        {"date": date, "note_count": len(notes[date])} 
        for date in recent_dates
    ]
    
    return jsonify(stats)

@app.route("/analyze_time_allocation", methods=["GET"])
def analyze_time_allocation():
    """Analyze time allocation from calendar data using AI categorization"""
    notes = load_notes()
    
    # Activity categories with AI-friendly descriptions
    activity_categories = {
        "study": {
            "description": "Academic learning, reading, research, exam preparation, homework, studying, educational activities",
            "color": "#4e79a7",
            "icon": "📚",
            "scale_range": (1, 10)  # Intensity scale 1-10
        },
        "exercise": {
            "description": "Physical activities, workouts, sports, fitness training, movement, athletic activities",
            "color": "#f28e2c",
            "icon": "💪",
            "scale_range": (1, 10)  # Intensity scale 1-10
        },
        "rest": {
            "description": "Relaxation, sleep, leisure, downtime, breaks, meditation, peaceful activities",
            "color": "#76b7b2",
            "icon": "😴",
            "scale_range": (1, 10)  # Rest quality scale 1-10
        }
    }
    
    # Analyze activities using AI
    category_counts = {category: 0 for category in activity_categories.keys()}
    category_details = {category: [] for category in activity_categories.keys()}
    category_intensities = {category: [] for category in activity_categories.keys()}
    
    total_activities = 0
    
    for date, activities in notes.items():
        for activity in activities:
            total_activities += 1
            
            # Use AI to categorize and get intensity
            ai_result = categorize_activity_with_ai(activity, activity_categories)
            
            if ai_result:
                category = ai_result['category']
                intensity = ai_result['intensity']
                
                category_counts[category] += 1
                category_details[category].append({
                    "date": date,
                    "activity": activity,
                    "category": category,
                    "intensity": intensity
                })
                category_intensities[category].append(intensity)
    
    # Calculate percentages and averages
    category_percentages = {}
    category_averages = {}
    
    for category, count in category_counts.items():
        if total_activities > 0:
            percentage = (count / total_activities) * 100
        else:
            percentage = 0
        category_percentages[category] = round(percentage, 1)
        
        # Calculate average intensity
        if category_intensities[category]:
            avg_intensity = sum(category_intensities[category]) / len(category_intensities[category])
            category_averages[category] = round(avg_intensity, 1)
        else:
            category_averages[category] = 0
    
    # Prepare chart data
    chart_data = []
    for category, count in category_counts.items():
        if count > 0:
            chart_data.append({
                "category": category,
                "count": count,
                "percentage": category_percentages[category],
                "average_intensity": category_averages[category],
                "color": activity_categories[category]["color"],
                "icon": activity_categories[category]["icon"],
                "scale_range": activity_categories[category]["scale_range"],
                "details": category_details[category]
            })
    
    # Sort by count (descending)
    chart_data.sort(key=lambda x: x["count"], reverse=True)
    
    # Weekly analysis with AI categorization
    week_dates = get_current_week_dates()
    weekly_analysis = {}
    weekly_intensities = {}
    
    for date in week_dates:
        if date in notes:
            daily_categories = {category: 0 for category in activity_categories.keys()}
            daily_intensities = {category: [] for category in activity_categories.keys()}
            
            for activity in notes[date]:
                ai_result = categorize_activity_with_ai(activity, activity_categories)
                
                if ai_result:
                    category = ai_result['category']
                    intensity = ai_result['intensity']
                    
                    daily_categories[category] += 1
                    daily_intensities[category].append(intensity)
            
            weekly_analysis[date] = daily_categories
            weekly_intensities[date] = daily_intensities
    
    return jsonify({
        "total_activities": total_activities,
        "chart_data": chart_data,
        "weekly_analysis": weekly_analysis,
        "weekly_intensities": weekly_intensities,
        "activity_categories": activity_categories
    })

def categorize_activity_with_ai(activity, categories):
    """Use AI to categorize an activity and determine its intensity"""
    try:
        # Create prompt for AI categorization
        prompt = f"""
        Analyze this activity: "{activity}"
        
        Categorize it into one of these categories and provide an intensity score (1-10):
        
        1. STUDY: Academic learning, reading, research, exam preparation, homework, studying, educational activities
           - Intensity 1-3: Light reading, casual learning
           - Intensity 4-6: Regular studying, homework
           - Intensity 7-8: Intensive studying, exam prep
           - Intensity 9-10: All-day study sessions, major exams
        
        2. EXERCISE: Physical activities, workouts, sports, fitness training, movement, athletic activities
           - Intensity 1-3: Light walking, stretching
           - Intensity 4-6: Regular workouts, moderate exercise
           - Intensity 7-8: Intense workouts, sports games
           - Intensity 9-10: Marathon training, competitive sports
        
        3. REST: Relaxation, sleep, leisure, downtime, breaks, meditation, peaceful activities
           - Intensity 1-3: Light relaxation, short breaks
           - Intensity 4-6: Regular rest, leisure activities
           - Intensity 7-8: Deep relaxation, meditation
           - Intensity 9-10: Complete rest days, vacation
        
        Respond in this exact format:
        Category: [study/exercise/rest]
        Intensity: [1-10]
        Reason: [brief explanation]
        """
        
        # Use Gemini API for categorization
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        ai_response = response.text.strip()
        
        # Parse AI response
        category_match = re.search(r'Category:\s*(study|exercise|rest)', ai_response, re.IGNORECASE)
        intensity_match = re.search(r'Intensity:\s*(\d+)', ai_response)
        
        if category_match and intensity_match:
            category = category_match.group(1).lower()
            intensity = int(intensity_match.group(1))
            
            # Ensure intensity is within valid range
            intensity = max(1, min(10, intensity))
            
            return {
                'category': category,
                'intensity': intensity,
                'ai_response': ai_response
            }
        
        # Fallback: use keyword matching if AI fails
        return fallback_categorization(activity, categories)
        
    except Exception as e:
        logger.error(f"AI categorization error for '{activity}': {str(e)}")
        # Fallback to keyword matching
        return fallback_categorization(activity, categories)

def fallback_categorization(activity, categories):
    """Fallback categorization using keyword matching"""
    activity_lower = activity.lower()
    
    # Study keywords
    study_keywords = ["study", "learn", "read", "research", "exam", "test", "quiz", "assignment", 
                     "homework", "project", "paper", "essay", "review", "practice", "course", 
                     "class", "lecture", "tutorial", "workshop", "seminar", "library", "book", 
                     "chapter", "notes", "revision", "preparation"]
    
    # Exercise keywords
    exercise_keywords = ["exercise", "workout", "gym", "run", "jog", "walk", "swim", "bike", 
                        "cycling", "yoga", "pilates", "fitness", "training", "sport", "basketball", 
                        "football", "soccer", "tennis", "volleyball", "badminton", "dance", 
                        "aerobics", "strength", "cardio", "stretch"]
    
    # Rest keywords
    rest_keywords = ["rest", "sleep", "nap", "relax", "break", "vacation", "holiday", "weekend", 
                    "leisure", "free time", "downtime", "chill", "unwind", "recharge", "refresh", 
                    "peace", "quiet", "meditation", "mindfulness"]
    
    # Determine category and intensity
    if any(keyword in activity_lower for keyword in study_keywords):
        intensity = determine_intensity(activity_lower, study_keywords)
        return {'category': 'study', 'intensity': intensity}
    elif any(keyword in activity_lower for keyword in exercise_keywords):
        intensity = determine_intensity(activity_lower, exercise_keywords)
        return {'category': 'exercise', 'intensity': intensity}
    elif any(keyword in activity_lower for keyword in rest_keywords):
        intensity = determine_intensity(activity_lower, rest_keywords)
        return {'category': 'rest', 'intensity': intensity}
    else:
        # Default to rest with low intensity for unknown activities
        return {'category': 'rest', 'intensity': 3}

def determine_intensity(activity, keywords):
    """Determine intensity based on activity description"""
    activity_lower = activity.lower()
    
    # High intensity indicators
    high_intensity_words = ["intense", "hard", "difficult", "challenging", "major", "important", 
                           "critical", "all-day", "marathon", "competition", "exam", "test"]
    
    # Medium intensity indicators
    medium_intensity_words = ["regular", "normal", "standard", "routine", "daily", "weekly"]
    
    # Low intensity indicators
    low_intensity_words = ["light", "easy", "casual", "quick", "short", "brief", "simple"]
    
    if any(word in activity_lower for word in high_intensity_words):
        return random.randint(7, 10)
    elif any(word in activity_lower for word in medium_intensity_words):
        return random.randint(4, 6)
    elif any(word in activity_lower for word in low_intensity_words):
        return random.randint(1, 3)
    else:
        # Default to medium intensity
        return random.randint(4, 6)

@app.route("/get_activity_trends", methods=["GET"])
def get_activity_trends():
    """Get activity trends over time"""
    notes = load_notes()
    
    # Get last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Activity categories (same as above)
    activity_categories = {
        "study": ["study", "learn", "read", "research", "exam", "test", "quiz", "assignment", "homework", "project", "paper", "essay", "review", "practice", "course", "class", "lecture", "tutorial", "workshop", "seminar", "library", "book", "chapter", "notes", "revision", "preparation"],
        "exercise": ["exercise", "workout", "gym", "run", "jog", "walk", "swim", "bike", "cycling", "yoga", "pilates", "fitness", "training", "sport", "basketball", "football", "soccer", "tennis", "volleyball", "badminton", "dance", "aerobics", "strength", "cardio", "stretch"],
        "work": ["work", "job", "office", "meeting", "presentation", "client", "project", "deadline", "report", "email", "call", "conference", "interview", "business", "professional", "task", "assignment", "collaboration", "team", "manager", "colleague", "workplace"],
        "rest": ["rest", "sleep", "nap", "relax", "break", "vacation", "holiday", "weekend", "leisure", "free time", "downtime", "chill", "unwind", "recharge", "refresh", "peace", "quiet", "meditation", "mindfulness"],
        "social": ["friend", "family", "party", "dinner", "lunch", "coffee", "date", "hangout", "visit", "birthday", "celebration", "event", "gathering", "meet", "social", "relationship", "conversation", "chat", "talk"]
    }
    
    # Generate daily trends
    trends = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        daily_data = {
            "date": date_str,
            "total_activities": 0,
            "categories": {category: 0 for category in activity_categories.keys()}
        }
        
        if date_str in notes:
            daily_data["total_activities"] = len(notes[date_str])
            
            for activity in notes[date_str]:
                activity_lower = activity.lower()
                categorized = False
                
                for category, keywords in activity_categories.items():
                    for keyword in keywords:
                        if keyword in activity_lower:
                            daily_data["categories"][category] += 1
                            categorized = True
                            break
                    if categorized:
                        break
        
        trends.append(daily_data)
        current_date += timedelta(days=1)
    
    return jsonify({
        "trends": trends,
        "period": "30_days"
    })

@app.route("/debug/ai_response", methods=["POST"])
def debug_ai_response():
    """Debug endpoint to test AI response parsing"""
    data = request.get_json()
    test_response = data.get("response", "")
    
    if not test_response:
        return jsonify({"error": "Please provide a test response"}), 400
    
    parsed = parse_ai_plan(test_response)
    week_dates = get_current_week_dates()
    
    mapped_plans = {}
    for weekday, activities in parsed.items():
        actual_date = map_weekday_to_date(weekday, week_dates)
        if actual_date:
            mapped_plans[actual_date] = activities
    
    return jsonify({
        "original_response": test_response,
        "parsed_plans": parsed,
        "mapped_plans": mapped_plans,
        "week_dates": week_dates
    })

@app.route("/get_countdowns", methods=["GET"])
def get_countdowns():
    """Get countdown data for important events and deadlines"""
    notes = load_notes()
    labels = load_labels()
    
    # Keywords that indicate important/deadline events
    important_keywords = [
        "deadline", "due", "exam", "test", "quiz", "assignment", "project", "presentation",
        "meeting", "appointment", "interview", "submission", "review", "final", "important",
        "urgent", "critical", "must", "essential", "priority", "deadline", "due date",
        "final exam", "term paper", "thesis", "dissertation", "proposal", "report",
        "conference", "workshop", "seminar", "training", "certification", "license",
        "renewal", "expiry", "expiration", "expires", "expiring", "last day", "final day"
    ]
    
    countdowns = []
    today = datetime.now().date()
    
    # Check notes for important events
    for date_str, activities in notes.items():
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Only include future dates
            if event_date >= today:
                for activity in activities:
                    activity_lower = activity.lower()
                    
                    # Check if activity contains important keywords
                    is_important = any(keyword in activity_lower for keyword in important_keywords)
                    
                    # Also check if the date has an important label
                    has_important_label = False
                    label_text = ""
                    label_color = ""
                    
                    if date_str in labels:
                        label_data = labels[date_str]
                        label_text = label_data.get("label", "")
                        label_color = label_data.get("color", "#ff6b6b")
                        
                        # Check if label indicates importance
                        important_label_keywords = ["important", "urgent", "critical", "deadline", "due", "exam", "test"]
                        has_important_label = any(keyword in label_text.lower() for keyword in important_label_keywords)
                    
                    if is_important or has_important_label:
                        days_remaining = (event_date - today).days
                        
                        # Determine priority level
                        if days_remaining <= 1:
                            priority = "critical"
                            priority_color = "#dc3545"
                        elif days_remaining <= 3:
                            priority = "urgent"
                            priority_color = "#fd7e14"
                        elif days_remaining <= 7:
                            priority = "high"
                            priority_color = "#ffc107"
                        elif days_remaining <= 14:
                            priority = "medium"
                            priority_color = "#17a2b8"
                        else:
                            priority = "low"
                            priority_color = "#6c757d"
                        
                        countdowns.append({
                            "date": date_str,
                            "activity": activity,
                            "days_remaining": days_remaining,
                            "priority": priority,
                            "priority_color": priority_color,
                            "label": label_text if has_important_label else "",
                            "label_color": label_color if has_important_label else "",
                            "is_labeled": has_important_label,
                            "is_keyword_match": is_important
                        })
                        
        except ValueError:
            continue
    
    # Sort by priority and days remaining
    priority_order = {"critical": 0, "urgent": 1, "high": 2, "medium": 3, "low": 4}
    countdowns.sort(key=lambda x: (priority_order[x["priority"]], x["days_remaining"]))
    
    # Get statistics
    total_countdowns = len(countdowns)
    critical_count = len([c for c in countdowns if c["priority"] == "critical"])
    urgent_count = len([c for c in countdowns if c["priority"] == "urgent"])
    high_count = len([c for c in countdowns if c["priority"] == "high"])
    
    return jsonify({
        "countdowns": countdowns,
        "statistics": {
            "total": total_countdowns,
            "critical": critical_count,
            "urgent": urgent_count,
            "high": high_count
        }
    })

@app.route("/mark_as_important", methods=["POST"])
def mark_as_important():
    """Mark an event as important by adding a special label"""
    data = request.get_json()
    date = data.get("date")
    activity = data.get("activity")
    
    if not date or not activity:
        return jsonify({"error": "Please provide date and activity"}), 400
    
    labels = load_labels()
    
    # Create or update label for this date
    if date not in labels:
        labels[date] = {
            "label": "Important Deadline",
            "color": "#dc3545",
            "created_at": datetime.now().isoformat()
        }
    else:
        # Update existing label to mark as important
        labels[date]["label"] = "Important Deadline"
        labels[date]["color"] = "#dc3545"
        labels[date]["updated_at"] = datetime.now().isoformat()
    
    save_labels(labels)
    return jsonify({"status": "success", "message": "Event marked as important"})

@app.route("/unmark_as_important", methods=["POST"])
def unmark_as_important():
    """Remove important marking from an event"""
    data = request.get_json()
    date = data.get("date")
    
    if not date:
        return jsonify({"error": "Please provide date"}), 400
    
    labels = load_labels()
    
    if date in labels:
        # Check if it's an important label
        if "important" in labels[date]["label"].lower() or "deadline" in labels[date]["label"].lower():
            del labels[date]
            save_labels(labels)
            return jsonify({"status": "success", "message": "Important marking removed"})
        else:
            return jsonify({"error": "This date is not marked as important"}), 400
    else:
        return jsonify({"error": "No label found for this date"}), 404

if __name__ == "__main__":
    app.run(debug=True)
