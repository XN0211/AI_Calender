#!/usr/bin/env python3
"""
AI Smart Calendar Runner
Simple script to start the AI Smart Calendar application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ Error: app.py not found")
        print("Please run this script from the project directory")
        sys.exit(1)
    
    # Check if requirements are installed
    try:
        import flask
        import google.generativeai
    except ImportError as e:
        print(f"❌ Error: Missing dependency - {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

def main():
    """Main function to run the application"""
    print("🤖 Starting AI Smart Calendar...")
    print()
    
    # Check requirements
    check_requirements()
    
    # Set environment variables if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading environment variables from .env file")
        with open(env_file, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    # Start the Flask application
    print("🚀 Starting Flask server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
