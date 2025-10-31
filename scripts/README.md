# Scripts Directory

This directory contains utility scripts for setting up and running the Advanced YouTube Downloader.

## Available Scripts

### Windows Scripts (.bat)

#### `run_app.bat`
**Main setup and launch script for Windows**
- Sets up Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Launches the Streamlit application
- **Usage**: Double-click to run or execute from command prompt

#### `start_with_scheduler.bat`
**Launch both app and scheduler service**
- Starts the main Streamlit application
- Starts the background scheduler service
- Both services run simultaneously
- **Usage**: Double-click after initial setup with `run_app.bat`

### Unix Scripts (.sh)

#### `setup.sh`
**Main setup and launch script for macOS/Linux**
- Sets up Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Launches the Streamlit application
- **Usage**: `chmod +x setup.sh && ./setup.sh`

### Python Scripts (.py)

#### `quick_status_check.py`
**System status and diagnostic tool**
- Checks file availability
- Shows scheduled downloads status
- Displays active download progress
- Lists implemented features
- **Usage**: `python quick_status_check.py`

## Quick Start

### Windows Users
1. Double-click `run_app.bat`
2. Wait for setup to complete
3. Application opens automatically in browser

### macOS/Linux Users
1. Open terminal in project root
2. Run: `chmod +x scripts/setup.sh`
3. Run: `./scripts/setup.sh`
4. Application opens automatically in browser

### With Scheduler (Windows)
1. First run `run_app.bat` for initial setup
2. Then double-click `start_with_scheduler.bat`
3. Both app and scheduler will be running

## Troubleshooting

### Common Issues

**Python not found**
- Ensure Python 3.8+ is installed
- Add Python to system PATH

**Permission denied (Linux/macOS)**
- Make script executable: `chmod +x scripts/setup.sh`

**Virtual environment issues**
- Delete `venv` folder and run setup again
- Ensure you have permission to create directories

**Port already in use**
- Close other applications using port 8501
- Or modify the port in the script

### Manual Setup
If scripts don't work, you can set up manually:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Script Customization

You can modify these scripts for your needs:

- Change default port (8501)
- Modify installation directories
- Add custom environment variables
- Include additional setup steps

## Docker Alternative

For containerized deployment, use the provided Docker files:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run with scheduler
docker-compose --profile scheduler up --build
```