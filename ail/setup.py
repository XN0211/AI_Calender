#!/usr/bin/env python3
"""
AI Smart Calendar Setup Script
This script helps you set up the AI Smart Calendar application.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("🤖 AI Smart Calendar Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file for API key"""
    env_file = Path(".env")
    if env_file.exists():
        print("ℹ️  .env file already exists")
        return
    
    print("🔑 Setting up API key configuration...")
    print("You can get a Google Gemini API key from: https://makersuite.google.com/app/apikey")
    
    api_key = input("Enter your Google Gemini API key (or press Enter to skip): ").strip()
    
    if api_key:
        with open(env_file, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print("✅ .env file created with your API key")
    else:
        print("ℹ️  Skipping API key setup. You can add it later to the .env file")

def create_sample_data():
    """Create sample calendar data"""
    notes_file = Path("notes.json")
    if notes_file.exists():
        print("ℹ️  notes.json already exists")
        return
    
    sample_data = {
        "2024-12-20": [
            "Team meeting at 10:00 AM",
            "Lunch with colleagues",
            "Review project documents"
        ],
        "2024-12-21": [
            "Morning workout",
            "Grocery shopping",
            "Prepare for weekend"
        ]
    }
    
    with open(notes_file, "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print("✅ Sample calendar data created")

def check_file_structure():
    """Verify all required files exist"""
    required_files = [
        "app.py",
        "requirements.txt",
        "templates/index.html",
        "static/script.js",
        "static/style.css"
    ]
    
    print("📁 Checking file structure...")
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        print("Please ensure all files are present in the project directory")
        sys.exit(1)
    
    print("✅ All required files found")

def run_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    try:
        # Test Flask import
        import flask
        print("✅ Flask import successful")
        
        # Test Gemini import
        import google.generativeai as genai
        print("✅ Google Generative AI import successful")
        
        # Test JSON file reading
        with open("notes.json", "r") as f:
            json.load(f)
        print("✅ JSON file reading successful")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start the application:")
    print("   python app.py")
    print()
    print("2. Open your browser and go to:")
    print("   http://localhost:5000")
    print()
    print("3. Start using your AI Smart Calendar!")
    print()
    print("Features you can try:")
    print("• Click on any date to add notes")
    print("• Use AI Planning to generate weekly schedules")
    print("• Ask AI questions about your schedule")
    print()
    print("For help, see the README.md file")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Check file structure
    check_file_structure()
    
    # Install dependencies
    install_dependencies()
    
    # Create environment file
    create_env_file()
    
    # Create sample data
    create_sample_data()
    
    # Run tests
    run_tests()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
