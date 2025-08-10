# AI Smart Calendar - 智能行事曆

A comprehensive AI-powered smart calendar web application built with Flask, featuring Google Gemini AI integration for intelligent planning and scheduling assistance.

## 🌟 Features

### 📅 Interactive Monthly Calendar
- **Full monthly calendar view** with navigation between months
- **Click-to-select dates** for adding, editing, and managing notes
- **Visual indicators** for today's date, selected date, and dates with notes
- **Note previews** directly on calendar days
- **Responsive design** that works on desktop, tablet, and mobile devices

### 🤖 AI-Powered Planning
- **Intelligent weekly plan generation** using Google Gemini AI
- **Natural language goal input** (e.g., "weekly fitness and study schedule")
- **Automatic parsing and calendar integration** of AI-generated plans
- **Smart activity decomposition** into individual calendar entries

### 💬 AI Q&A Assistant
- **Schedule analysis and advice** based on existing calendar data
- **Personalized recommendations** for time management
- **Natural language queries** about your schedule
- **Context-aware responses** considering your current commitments

### 📝 Note Management
- **Add, edit, and delete notes** for any date
- **Modal-based editing interface** for seamless note management
- **Real-time updates** across all calendar views
- **Persistent storage** in JSON format

### 📊 Quick Overview Features
- **Weekly overview panel** showing current week's schedule
- **Note count indicators** for each day
- **Today highlighting** for easy navigation
- **Calendar statistics** and activity tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Google Gemini API key

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd ai-smart-calendar
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   
   **Option A: Direct configuration (for testing)**
   - The API key is already configured in `app.py` for demonstration
   
   **Option B: Environment variable (recommended for production)**
   - Create a `.env` file in the project root
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Update `app.py` to use environment variable:
     ```python
     import os
     from dotenv import load_dotenv
     load_dotenv()
     genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
     ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start using your AI Smart Calendar!

## 📖 Usage Guide

### Basic Calendar Operations

1. **Navigating the Calendar**
   - Use the arrow buttons to move between months
   - Click on any date to select it
   - Today's date is highlighted in orange
   - Selected date is highlighted in blue

2. **Adding Notes**
   - Select a date by clicking on it
   - Type your note in the text area
   - Click "Add Note" or press Enter
   - Notes appear as previews on calendar days

3. **Editing Notes**
   - Click the "Edit" button next to any note
   - Modify the content in the modal window
   - Click "Save" to update the note

4. **Deleting Notes**
   - Click the "Delete" button next to any note
   - Confirm the deletion in the popup dialog

### AI Planning Features

1. **Generating Weekly Plans**
   - Go to the "AI Planning" tab
   - Enter your goal in natural language:
     - "weekly fitness and study schedule"
     - "prepare for final exams"
     - "work-life balance routine"
     - "daily meditation and exercise plan"
   - Click "Generate Plan"
   - AI will create a detailed 7-day schedule
   - All activities are automatically added to your calendar

2. **AI Q&A About Your Schedule**
   - Go to the "AI Q&A" tab
   - Ask questions about your schedule:
     - "When do I have free time this week?"
     - "What's my busiest day?"
     - "Suggest a better time for exercise"
     - "How can I improve my schedule?"
   - Get personalized advice based on your current commitments

### Advanced Features

1. **Weekly Overview**
   - View your current week's schedule at a glance
   - See note counts for each day
   - Quick navigation to any day

2. **Calendar Statistics**
   - Access via `/get_calendar_stats` endpoint
   - View total notes, active days, and recent activity

## 🏗️ Architecture

### Backend (Flask)
- **`app.py`**: Main Flask application with all routes and AI integration
- **`notes.json`**: Persistent storage for all calendar data
- **Google Gemini AI**: Natural language processing and plan generation

### Frontend (Vanilla JavaScript)
- **`templates/index.html`**: Main application interface
- **`static/script.js`**: Calendar logic and UI interactions
- **`static/style.css`**: Modern, responsive styling

### Key Components

1. **Calendar Class**: Handles all calendar rendering and interactions
2. **AIAssistant Class**: Manages AI planning and Q&A functionality
3. **Modal System**: Provides seamless note editing experience
4. **Responsive Design**: Works across all device sizes

## 🔧 API Endpoints

### Calendar Operations
- `GET /get_notes` - Retrieve all notes
- `GET /get_notes_for_month?year=X&month=Y` - Get notes for specific month
- `POST /save_note` - Add a new note
- `POST /update_note` - Update all notes for a date
- `POST /delete_note` - Delete a specific note
- `POST /delete_all_notes` - Delete all notes for a date

### AI Features
- `POST /generate_plan` - Generate AI weekly plan
- `POST /ask_ai` - Ask AI about schedule

### Utility
- `GET /get_week_dates` - Get current week dates
- `GET /get_calendar_stats` - Get calendar statistics
- `POST /debug/ai_response` - Debug AI response parsing

## 🎨 Customization

### Styling
- Modify `static/style.css` to change colors, fonts, and layout
- The application uses CSS Grid and Flexbox for responsive design
- Color scheme can be easily customized in the CSS variables

### AI Prompts
- Customize AI behavior by modifying prompts in `app.py`
- Adjust the `generate_plan()` and `ask_ai()` functions
- Fine-tune parsing logic in `parse_ai_plan()`

### Features
- Add new calendar views (yearly, daily)
- Implement recurring events
- Add calendar sharing functionality
- Integrate with external calendar services

## 🔒 Security Considerations

### For Production Use
1. **API Key Security**
   - Use environment variables for API keys
   - Never commit API keys to version control
   - Consider using a secrets management service

2. **Data Validation**
   - Add input validation for all user inputs
   - Implement rate limiting for AI endpoints
   - Add CSRF protection

3. **File Security**
   - Secure the `notes.json` file with proper permissions
   - Consider using a database for larger deployments
   - Implement backup strategies

## 🐛 Troubleshooting

### Common Issues

1. **AI Plan Generation Fails**
   - Check your Gemini API key is valid
   - Ensure you have sufficient API quota
   - Check the console for error messages

2. **Calendar Not Loading**
   - Verify all static files are in the correct locations
   - Check browser console for JavaScript errors
   - Ensure Flask is running on the correct port

3. **Notes Not Saving**
   - Check file permissions for `notes.json`
   - Verify the Flask server has write access
   - Check for JSON syntax errors in the file

### Debug Mode
- Enable debug mode in Flask for detailed error messages
- Use the `/debug/ai_response` endpoint to test AI parsing
- Check browser developer tools for frontend issues

## 📈 Performance Optimization

### For Large Calendars
- Implement pagination for calendar views
- Add caching for frequently accessed data
- Optimize AI response parsing for large datasets

### For High Traffic
- Consider using a production WSGI server (Gunicorn)
- Implement database storage instead of JSON files
- Add Redis caching for AI responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing capabilities
- Flask framework for the web application foundation
- Font Awesome for the beautiful icons
- The open source community for inspiration and tools

---

**Happy Planning! 🎉**

For support or questions, please open an issue in the repository.
