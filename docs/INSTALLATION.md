# Installation Guide

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: Version 3.7 or higher
- **RAM**: Minimum 4GB (8GB recommended for large downloads)
- **Storage**: At least 1GB free space (more for downloads)
- **Internet**: Stable broadband connection

## Quick Installation (Recommended)

### Windows Users

1. **Download the Project**
   ```bash
   git clone https://github.com/hakkache/Advanced-YouTube-Downloader.git
   cd Advanced-YouTube-Downloader
   ```

2. **Run the Setup Script**
   - Double-click `run_app.bat`
   - The script will automatically:
     - Create a Python virtual environment
     - Install all required dependencies
     - Start the application

3. **Access the Application**
   - Open your browser and go to `http://localhost:8501`
   - The application will automatically open

### macOS/Linux Users

1. **Download the Project**
   ```bash
   git clone https://github.com/hakkache/Advanced-YouTube-Downloader.git
   cd Advanced-YouTube-Downloader
   ```

2. **Make Setup Script Executable** (Linux/macOS)
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Manual Setup** (Alternative)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Manual Installation

### Step 1: Install Python
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: Use Homebrew `brew install python3` or download from python.org
- **Linux**: Use package manager `sudo apt install python3 python3-pip`

### Step 2: Verify Installation
```bash
python --version  # Should show 3.7 or higher
pip --version     # Should show pip version
```

### Step 3: Clone Repository
```bash
git clone https://github.com/hakkache/Advanced-YouTube-Downloader.git
cd Advanced-YouTube-Downloader
```

### Step 4: Create Virtual Environment
```bash
python -m venv venv
```

### Step 5: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 6: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 7: Run Application
```bash
streamlit run app.py
```

## Dependencies

The application requires the following Python packages:

```
streamlit>=1.28.0          # Web application framework
yt-dlp>=2023.7.6          # YouTube downloader engine
ffmpeg-python>=0.2.0      # Video processing
schedule>=1.2.0           # Task scheduling
streamlit-calendar>=0.7.0  # Calendar widget
streamlit-datetime-picker>=0.0.2  # DateTime picker
```

### FFmpeg Installation

FFmpeg is automatically handled by yt-dlp, but for manual installation:

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:

```env
# Download settings
DEFAULT_QUALITY=720
DEFAULT_AUDIO=with_audio
ORGANIZE_BY_DATE=true

# Application settings
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost

# Download paths
DOWNLOADS_DIR=./downloads
TEMP_DIR=./temp
```

### Custom Settings
You can modify default settings in the application sidebar or by editing the configuration section in `app.py`.

## Troubleshooting

### Common Issues

#### 1. Python Not Found
```bash
# Add Python to PATH or use full path
C:\Python39\python.exe -m pip install -r requirements.txt
```

#### 2. Permission Errors
```bash
# Windows: Run as Administrator
# macOS/Linux: Use sudo for system-wide installation
sudo pip install -r requirements.txt
```

#### 3. Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

#### 4. FFmpeg Issues
- Ensure FFmpeg is installed and in PATH
- Try reinstalling yt-dlp: `pip install --upgrade yt-dlp`

#### 5. Network Issues
- Check firewall settings
- Try using VPN if YouTube is blocked
- Verify internet connection

### Virtual Environment Issues

#### Activation Problems
```bash
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1

# Command Prompt
venv\Scripts\activate.bat
```

#### Deactivation
```bash
deactivate
```

### Dependency Conflicts
```bash
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- May need to enable long path support
- Antivirus might flag downloaded files

### macOS
- May need Xcode Command Line Tools
- Use Terminal application
- Check Gatekeeper settings for downloaded files

### Linux
- Install development headers if needed
- Use package manager for system dependencies
- Check file permissions for downloads folder

## Verification

After installation, verify everything works:

1. **Start the application**
2. **Test a simple download**:
   - Go to Download tab
   - Enter: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - Click "Get Video Info"
   - Click "Download"

3. **Check the downloads folder** for the downloaded file

## Getting Help

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Review the error messages** in the terminal
3. **Check GitHub Issues** for similar problems
4. **Create a new issue** with:
   - Your operating system
   - Python version
   - Error messages
   - Steps to reproduce

## Updating

To update to the latest version:

```bash
cd Advanced-YouTube-Downloader
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstallation

To remove the application:

1. **Delete the project folder**
2. **Remove the virtual environment**
3. **Optional**: Uninstall Python packages if not used elsewhere

```bash
# Remove virtual environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Remove project
cd ..
rm -rf Advanced-YouTube-Downloader
```