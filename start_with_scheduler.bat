@echo off
echo Starting YouTube Downloader with Scheduler...
echo.

echo Starting Streamlit App...
start "YouTube Downloader App" cmd /k "cd /d "%~dp0" && streamlit run app.py"

echo.
echo Waiting 5 seconds before starting scheduler service...
timeout /t 5 /nobreak >nul

echo Starting Scheduler Service...
start "Scheduler Service" cmd /k "cd /d "%~dp0" && python scheduler_service.py"

echo.
echo Both services are now running!
echo - App: http://localhost:8502
echo - Scheduler service is running in the background
echo.
echo Press any key to exit...
pause >nul
