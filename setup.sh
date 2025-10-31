#!/bin/bash

# Advanced YouTube Downloader Setup Script for macOS/Linux
# This script sets up the environment and starts the application

echo "🚀 Setting up Advanced YouTube Downloader..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    echo "Visit: https://python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
MIN_VERSION="3.7"

if [ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION is installed, but Python $MIN_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip --quiet

if [ $? -ne 0 ]; then
    echo "⚠️ Warning: Failed to upgrade pip, continuing anyway..."
fi

# Install required libraries
echo "📦 Installing required libraries..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install requirements"
    exit 1
fi

echo "✅ Requirements installed successfully"

# Create downloads directory if it doesn't exist
if [ ! -d "downloads" ]; then
    echo "📁 Creating downloads directory..."
    mkdir downloads
    echo "✅ Downloads directory created"
fi

# Check if FFmpeg is available (optional but recommended)
if command_exists ffmpeg; then
    echo "✅ FFmpeg is available for video processing"
else
    echo "⚠️ FFmpeg is not installed. Video segment features may not work."
    echo "   Install FFmpeg for full functionality:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   - CentOS/RHEL: sudo yum install ffmpeg"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 Starting Advanced YouTube Downloader..."
echo "   The application will open in your default browser"
echo "   URL: http://localhost:8501"
echo ""
echo "📋 Controls:"
echo "   - Ctrl+C to stop the application"
echo "   - Close terminal to exit completely"
echo ""

# Run the Streamlit application
streamlit run app.py

# Deactivation happens automatically when script ends