# Advanced YouTube Downloader

<div align="center">

![Advanced YouTube Downloader](https://img.shields.io/badge/YouTube-Downloader-red?style=for-the-badge&logo=youtube)
![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=for-the-badge&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A powerful, user-friendly web application for downloading YouTube videos, playlists, and managing your media collection with advanced scheduling and batch processing capabilities.**

[🚀 Quick Start](#quick-start) • [� Features](#features) • [📚 Documentation](#documentation) • [🤝 Contributing](#contributing) • [🐛 Issues](https://github.com/hakkache/Advanced-YouTube-Downloader/issues)

</div>

---

## 🌟 Key Highlights

- **🎯 Smart Downloads**: Single videos, batch processing, and complete playlists
- **⏰ Advanced Scheduler**: Schedule downloads for specific dates and times
- **✂️ Video Segments**: Download custom time ranges from any video
- **📊 Real-time Progress**: Live download monitoring with detailed statistics
- **🗂️ Intelligent Organization**: Automatic file organization with history tracking
- **🖥️ Modern Interface**: Clean, intuitive web-based interface
- **🛡️ Safe & Secure**: Local processing with no data collection

## 🚀 Quick Start

### Windows (Recommended)
```batch
# Clone the repository
git clone https://github.com/hakkache/Advanced-YouTube-Downloader.git
cd Advanced-YouTube-Downloader

# Run the setup script (installs everything automatically)
run_app.bat
```

### macOS/Linux
```bash
# Clone the repository
git clone https://github.com/hakkache/Advanced-YouTube-Downloader.git
cd Advanced-YouTube-Downloader

# Make setup script executable and run
chmod +x setup.sh
./setup.sh
```

### Manual Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
streamlit run app.py
```

**Access the application at:** `http://localhost:8501`

## ✨ Features

### 🎥 Download Capabilities
- **Single Videos**: Download any YouTube video with quality selection
- **Batch Processing**: Download multiple videos simultaneously
- **Playlist Support**: Download entire playlists or select specific videos
- **Video Segments**: Extract custom time ranges (e.g., 1:30-5:45)
- **Audio Extraction**: Download audio-only versions in MP3 format
- **Quality Options**: From 360p to 1080p, plus "Best Available"

### ⏰ Advanced Scheduler
- **Scheduled Downloads**: Set specific dates and times for automatic downloads
- **Background Service**: Automatic execution without user intervention
- **Batch Scheduling**: Schedule multiple videos or entire playlists
- **Calendar View**: Visual overview of all scheduled downloads
- **Real-time Monitoring**: Live progress updates for scheduled tasks
- **Persistent Storage**: Schedules survive application restarts

### 📊 Management & Organization
- **Smart File Organization**: Automatic date-based folder structure
- **Download History**: Complete record with search and filtering
- **File Manager**: Built-in file browser with management tools
- **Progress Tracking**: Real-time progress bars and statistics
- **Error Handling**: Comprehensive error reporting and recovery
- **Settings Persistence**: Remembers your preferences

### 🖥️ User Interface
- **Tabbed Interface**: Organized workflow with dedicated sections
- **Responsive Design**: Works on desktop and mobile browsers
- **Real-time Updates**: Live progress monitoring and status updates
- **Intuitive Controls**: Easy-to-use interface for all skill levels
- **Sidebar Settings**: Quick access to configuration options

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 User Guide](docs/USER_GUIDE.md) | Comprehensive guide for all features |
| [🔧 Installation Guide](docs/INSTALLATION.md) | Detailed installation instructions |
| [🔌 API Documentation](docs/API.md) | Technical API reference for developers |
| [🤝 Contributing Guide](docs/CONTRIBUTING.md) | How to contribute to the project |
| [📅 Scheduler Guide](SCHEDULER_README.md) | Advanced scheduler feature documentation |

## 📋 System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 1GB free space (plus space for downloads)
- **Network**: Stable internet connection

### Dependencies
- **Streamlit**: Web application framework
- **yt-dlp**: YouTube download engine
- **FFmpeg**: Video processing (auto-installed)
- **Additional**: See [requirements.txt](requirements.txt)

## 🎯 Usage Examples

### Basic Video Download
1. Open the application at `http://localhost:8501`
2. Paste YouTube URL in the Download tab
3. Select quality and audio options
4. Click "Get Video Info" → "Download"

### Batch Download with Time Ranges
1. Navigate to "Batch Download" tab
2. Enter multiple URLs:
   ```
   https://youtube.com/watch?v=abc123
   https://youtube.com/watch?v=def456
   ```
3. Set individual time ranges (optional)
4. Click "Download All Videos"

### Schedule a Playlist Download
1. Go to "Scheduler" tab
2. Select "Playlist Selection"
3. Set future date and time
4. Enter playlist URL and configure settings
5. Click "Schedule Download"

## 📁 Project Structure

```
Advanced-YouTube-Downloader/
├── app.py                     # Main Streamlit application
├── scheduler_service.py       # Background scheduler service
├── requirements.txt           # Python dependencies
├── run_app.bat               # Windows setup script
├── setup.sh                  # macOS/Linux setup script
├── docs/                     # Documentation
│   ├── USER_GUIDE.md
│   ├── INSTALLATION.md
│   ├── API.md
│   └── CONTRIBUTING.md
├── downloads/                # Downloaded files (created at runtime)
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file for custom settings:
```env
DEFAULT_QUALITY=720
DEFAULT_AUDIO=with_audio
ORGANIZE_BY_DATE=true
STREAMLIT_PORT=8501
```

### Application Settings
- **Quality**: Set default video quality
- **Audio**: Configure default audio options
- **Organization**: Enable date-based file organization
- **Scheduler**: Configure background service settings

## 🚦 Getting Started - Step by Step

### 1. Installation
Choose your installation method from the [Quick Start](#quick-start) section above.

### 2. First Download
1. Start the application using your chosen method
2. Navigate to `http://localhost:8501` in your browser
3. Go to the "Download" tab
4. Enter a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
5. Click "Get Video Info" to preview
6. Select your preferred quality and audio options
7. Click "Download" and monitor the progress

### 3. Explore Features
- Try the **Batch Download** for multiple videos
- Explore **Playlist Manager** for downloading playlists
- Test **Video Segments** for downloading specific time ranges
- Set up **Scheduled Downloads** for automatic processing

## 🤝 Contributing

We welcome contributions from developers of all skill levels! 

### Quick Contribution Guide
1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Test** thoroughly
6. **Submit** a pull request

For detailed guidelines, see our [Contributing Guide](docs/CONTRIBUTING.md).

### Areas for Contribution
- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Testing and quality assurance
- 🎨 UI/UX improvements
- 🌍 Translations and localization

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

### Recent Updates
- **v3.0.0**: Advanced scheduler with background service
- **v2.5.0**: Video segments and enhanced UI
- **v2.0.0**: Playlist support and batch downloads

## � Troubleshooting

### Common Issues

#### Download Failures
- Verify internet connection
- Check YouTube URL validity
- Try different quality settings
- Ensure sufficient disk space

#### Application Won't Start
- Verify Python 3.7+ is installed
- Check all dependencies are installed
- Try running `pip install -r requirements.txt`

#### Scheduler Issues
- Ensure scheduler service is running
- Check system clock accuracy
- Verify downloads folder permissions

For more help, see the [User Guide](docs/USER_GUIDE.md) or [create an issue](https://github.com/hakkache/Advanced-YouTube-Downloader/issues).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **yt-dlp**: The Unlicense
- **Streamlit**: Apache 2.0
- **FFmpeg**: LGPL 2.1

## 🛡️ Security

Security is important to us. Please review our [Security Policy](SECURITY.md) and report any vulnerabilities responsibly.

## 🙏 Acknowledgments

- **yt-dlp team** for the excellent YouTube downloading library
- **Streamlit team** for the amazing web app framework
- **FFmpeg developers** for video processing capabilities
- **Contributors** who help improve this project
- **Community** for feedback and support

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/hakkache/Advanced-YouTube-Downloader)
![GitHub forks](https://img.shields.io/github/forks/hakkache/Advanced-YouTube-Downloader)
![GitHub issues](https://img.shields.io/github/issues/hakkache/Advanced-YouTube-Downloader)
![GitHub pull requests](https://img.shields.io/github/issues-pr/hakkache/Advanced-YouTube-Downloader)

## 📞 Support

- **Documentation**: Start with the [User Guide](docs/USER_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/hakkache/Advanced-YouTube-Downloader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hakkache/Advanced-YouTube-Downloader/discussions)
- **Email**: [Contact the maintainers](mailto:contact@example.com)

---

<div align="center">

**Made with ❤️ for the YouTube downloading community**

[⭐ Star this repo](https://github.com/hakkache/Advanced-YouTube-Downloader) • [🐛 Report Bug](https://github.com/hakkache/Advanced-YouTube-Downloader/issues) • [💡 Request Feature](https://github.com/hakkache/Advanced-YouTube-Downloader/issues)

</div>
