@echo off
REM Batch file to set up Python virtual environment, install requirements, and run the Streamlit application

echo Setting up YouTube Video Downloader...

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install required libraries
echo Installing required libraries...
pip install -r requirements.txt

REM Create downloads directory if it doesn't exist
if not exist downloads mkdir downloads

REM Run the Streamlit application
echo Starting YouTube Video Downloader application...
streamlit run app.py

REM Deactivate virtual environment happens automatically when the batch file ends
