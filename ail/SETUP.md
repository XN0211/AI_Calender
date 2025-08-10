# 🚀 Quick Setup Guide

## Prerequisites

- Python 3.7 or higher
- Google Gemini AI API key (free tier available)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get Your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

## Step 3: Configure the Application

### Option A: Using Environment Variables (Recommended)

1. Create a `.env` file in the project root:
```bash
# Copy the template
cp env_template.txt .env
```

2. Edit the `.env` file and add your API key:
```
GEMINI_API_KEY=your-actual-api-key-here
```

### Option B: Direct Configuration

Edit `config.py` and update the `GEMINI_API_KEY` line:
```python
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'your-actual-api-key-here'
```

## Step 4: Run the Application

### Option A: Using the startup script (Recommended)
```bash
python run.py
```

### Option B: Direct Flask run
```bash
python app.py
```

## Step 5: Access the Application

Open your browser and go to: `http://localhost:5000`

## 🎯 Quick Test

Run the test script to verify everything is working:
```bash
python test_app.py
```

## 📱 Features Available

- **AI Weekly Planning**: Generate smart schedules with AI
- **Interactive Calendar**: Click dates to add/edit notes
- **Learning Analytics**: Track study metrics and get insights
- **AI Q&A**: Ask questions about your schedule
- **Responsive Design**: Works on desktop and mobile

## 🔧 Troubleshooting

### API Key Issues
- Make sure your API key is valid and has quota remaining
- Check the Google AI Studio console for usage limits

### Port Already in Use
- Change the port in `.env` file: `PORT=5001`
- Or kill the process using port 5000

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version`

## 🚀 Next Steps

1. Try generating an AI plan with a goal like "weekly fitness and study schedule"
2. Add some notes to different dates
3. Ask AI questions about your schedule
4. Add learning metrics to track your progress

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your API key is correct
3. Make sure all dependencies are installed
4. Try the test script: `python test_app.py`

---

**Happy Planning! 🎉**

