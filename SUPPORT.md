# Support

## Getting Help

If you need help with the Advanced YouTube Downloader, there are several ways to get assistance:

## 📚 Documentation

Before seeking help, please check our comprehensive documentation:

- **[User Guide](docs/USER_GUIDE.md)**: Complete guide for using all features
- **[Installation Guide](docs/INSTALLATION.md)**: Step-by-step installation instructions  
- **[API Documentation](docs/API.md)**: Technical reference for developers
- **[Scheduler Guide](SCHEDULER_README.md)**: Advanced scheduler feature documentation

## 🐛 Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to see if your problem has already been reported
2. **Check the documentation** to ensure you're using the feature correctly
3. **Try the latest version** to see if the issue has been resolved
4. **Gather information** about your system and the specific problem

### Creating a New Issue

If you can't find a solution, create a new issue:

- **Bug Reports**: Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature Requests**: Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Questions**: Create a general issue or use GitHub Discussions

**Include the following information:**
- Operating system and version
- Python version
- Application version
- Steps to reproduce the issue
- Error messages (if any)
- Screenshots (if applicable)

## 💬 Community Support

### GitHub Discussions

For general questions, discussions, and community support:
- **[GitHub Discussions](https://github.com/hakkache/Advanced-YouTube-Downloader/discussions)**

### Discussion Categories

- **💡 Ideas**: Share and discuss new feature ideas
- **❓ Q&A**: Ask questions and get help from the community
- **🗣️ General**: General discussions about the project
- **📢 Announcements**: Stay updated with project news

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

**Python Not Found**
```bash
# Verify Python installation
python --version
python3 --version

# If not installed, download from python.org
```

**Permission Errors**
```bash
# Windows: Run as Administrator
# macOS/Linux: Use sudo for system installations
sudo pip install -r requirements.txt
```

**Virtual Environment Issues**
```bash
# Create new virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### Application Issues

**Streamlit Won't Start**
- Check if port 8501 is available
- Try a different port: `streamlit run app.py --server.port 8502`
- Verify all dependencies are installed

**Download Failures**
- Check internet connection
- Verify YouTube URL is correct and accessible
- Try different quality settings
- Check if video is region-restricted

**Scheduler Not Working**
- Ensure `scheduler_service.py` is running
- Check system time and timezone settings
- Verify downloads folder permissions

#### Performance Issues

**Slow Downloads**
- Check internet connection speed
- Try lower quality settings
- Close other bandwidth-intensive applications
- Consider scheduling downloads for off-peak hours

**High Memory Usage**
- Close other applications
- Try downloading smaller batches
- Restart the application periodically

### Diagnostic Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test basic functionality
python -c "import streamlit, yt_dlp; print('Dependencies OK')"

# Check FFmpeg (optional but recommended)
ffmpeg -version
```

## 📧 Direct Contact

For sensitive issues, security concerns, or private matters:

- **Email**: [Create appropriate contact email]
- **Security Issues**: Please follow our [Security Policy](SECURITY.md)

## 🤝 Contributing

Want to help improve the project? See our [Contributing Guide](docs/CONTRIBUTING.md):

- Report bugs and issues
- Suggest new features  
- Improve documentation
- Submit code improvements
- Help other users in discussions

## 📋 Feature Requests

Have an idea for a new feature? We'd love to hear it!

1. **Check existing requests** to avoid duplicates
2. **Use the feature request template** for consistency
3. **Provide detailed information** about the use case
4. **Consider implementation complexity** and user benefit

## 🚀 Priority Support

Currently, all support is provided on a volunteer basis by the community and maintainers. 

**Response Times (Estimated):**
- **Critical bugs**: 24-48 hours
- **General issues**: 3-7 days  
- **Feature requests**: 1-2 weeks
- **Questions**: 1-3 days

## 📖 Self-Help Resources

### Video Tutorials
- Coming soon: YouTube tutorials for common tasks
- Community-created guides and walkthroughs

### FAQ

**Q: Can I download copyrighted content?**
A: Only download content you have permission to use. Respect copyright laws and YouTube's terms of service.

**Q: Why are some downloads failing?**
A: Common causes include region restrictions, private videos, or network issues. Check the error message for specific details.

**Q: Can I download entire channels?**
A: Currently, you can download playlists. Full channel downloading is planned for future releases.

**Q: How do I update the application?**
A: Use `git pull origin main` to get the latest version, then reinstall dependencies if needed.

## 🌍 Community Guidelines

When seeking support:

- **Be respectful** to other community members
- **Provide clear information** about your issue
- **Follow up** if you resolve the issue yourself
- **Help others** when you can
- **Search first** before asking questions

## 📊 Status Pages

- **GitHub Status**: Check if GitHub services are operational
- **YouTube Status**: Some issues may be related to YouTube service problems
- **Internet Archive**: For yt-dlp related issues, check upstream status

## 🔄 Update Notifications

Stay informed about updates and important announcements:

- **Watch the repository** for release notifications
- **Follow the project** to get updates in your GitHub feed
- **Check the [Changelog](CHANGELOG.md)** for version information

---

**Remember**: The community is here to help, but please be patient and respectful. We're all working together to make this project better! 🚀