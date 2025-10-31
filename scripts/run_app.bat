@echo off
REM Advanced YouTube Downloader - Windows Setup and Launch Script
REM This script sets up the environment and starts the application

echo.
echo =========================================
echo   Advanced YouTube Downloader Setup
echo =========================================
echo.

REM Navigate to parent directory to find requirements.txt
cd /d "%~dp0.."

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install required libraries
echo.
echo Installing required libraries...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    echo Trying to install without quiet mode for detailed error information...
    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo Creating project directories...
if not exist downloads mkdir downloads

REM Check if FFmpeg is available (optional but recommended)
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: FFmpeg not found in PATH
    echo Video segment features may not work properly
    echo You can download FFmpeg from: https://ffmpeg.org/download.html
) else (
    echo FFmpeg found and ready for video processing
)

echo.
echo =========================================
echo   Setup completed successfully!
echo =========================================
echo.
echo Starting Advanced YouTube Downloader...
echo The application will open in your default web browser
echo URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo Close this window to exit completely
echo.

REM Run the Streamlit application
streamlit run app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo The application encountered an error.
    pause
)
