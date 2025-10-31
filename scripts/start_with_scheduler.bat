@echo off
REM Advanced YouTube Downloader - Start with Scheduler Service
REM This script starts both the main application and scheduler service

echo.
echo ==========================================
echo  Advanced YouTube Downloader + Scheduler
echo ==========================================
echo.

REM Navigate to parent directory
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run scripts\run_app.bat first to set up the environment
    pause
    exit /b 1
)

echo Starting YouTube Downloader with Scheduler...
echo.

REM Activate virtual environment for both processes
call venv\Scripts\activate.bat

echo Starting Streamlit App...
start "YouTube Downloader App" cmd /k "cd /d "%~dp0.." && venv\Scripts\activate.bat && streamlit run app.py --server.port 8501"

echo.
echo Waiting 5 seconds before starting scheduler service...
timeout /t 5 /nobreak >nul

echo Starting Scheduler Service...
start "Scheduler Service" cmd /k "cd /d "%~dp0.." && venv\Scripts\activate.bat && python scheduler_service.py"

echo.
echo ==========================================
echo  Both services are now running!
echo ==========================================
echo.
echo 🌐 Web App: http://localhost:8501
echo 📅 Scheduler service is running in the background
echo.
echo 📋 Instructions:
echo   - Use the web interface to schedule downloads
echo   - The scheduler service will automatically execute scheduled downloads
echo   - Close both command windows to stop all services
echo.
echo Press any key to exit this window (services will continue running)...
pause >nul
