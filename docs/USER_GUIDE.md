# User Guide

## Getting Started

Welcome to the Advanced YouTube Downloader! This comprehensive guide will help you make the most of all the features available in this application.

## Interface Overview

The application uses a tabbed interface with the following sections:

### Main Tabs
- **📥 Download**: Single video downloads
- **📋 Batch Download**: Multiple video downloads
- **🎬 Playlist Manager**: Playlist handling
- **⏰ Scheduler**: Schedule downloads for later
- **📚 History**: View download history
- **📁 File Manager**: Manage downloaded files

### Sidebar Settings
- **Audio Options**: Control audio inclusion
- **Quality Settings**: Set default video quality
- **Organization**: Enable date-based folders
- **Advanced Settings**: Additional configuration options

## Single Video Downloads

### Basic Download Process

1. **Navigate to the Download Tab**
2. **Enter Video URL**
   - Paste a YouTube video URL
   - Example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

3. **Select Quality**
   - Best Quality (recommended)
   - 1080p, 720p, 480p, or 360p

4. **Choose Audio Option**
   - **With Audio**: Complete video with sound
   - **Video Only**: Video without audio track
   - **Audio Only**: Extract audio only (MP3)

5. **Get Video Information**
   - Click "Get Video Info" to preview
   - View title, duration, and thumbnail
   - Verify the correct video before downloading

6. **Start Download**
   - Click "Download" to begin
   - Monitor progress with the real-time progress bar

### Advanced Features

#### Video Segments
Download specific portions of a video:

1. **Enable Custom Time Range**
   - Check "Set custom time range"
   
2. **Set Start Time** (optional)
   - Format: `MM:SS` or `HH:MM:SS`
   - Example: `1:30` for 1 minute 30 seconds
   
3. **Set End Time** (optional)
   - Same format as start time
   - Example: `5:45` to stop at 5 minutes 45 seconds

4. **Download Segment**
   - The application will download the full video first
   - Then automatically trim to your specified segment
   - Both full and trimmed versions are saved

## Batch Downloads

Perfect for downloading multiple videos with the same settings.

### Setting Up Batch Downloads

1. **Navigate to Batch Download Tab**

2. **Enter Multiple URLs**
   - One URL per line in the text area
   - Example:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   https://www.youtube.com/watch?v=jNQXAC9IVRw
   https://www.youtube.com/watch?v=y6120QOlsfU
   ```

3. **Configure Global Settings**
   - Select quality for all videos
   - Choose audio option for all videos
   - Enable/disable date organization

4. **Individual Time Ranges** (Optional)
   - Check "Set custom time ranges for individual videos"
   - Enter time ranges for each URL:
   ```
   https://youtube.com/watch?v=abc123 | 1:30 | 3:45
   https://youtube.com/watch?v=def456 | | 2:30
   https://youtube.com/watch?v=ghi789 | 0:15 |
   ```
   - Format: `URL | start_time | end_time`
   - Leave start or end empty if not needed

5. **Start Batch Download**
   - Click "Download All Videos"
   - Monitor progress for each video individually

## Playlist Management

Download entire playlists or select specific videos.

### Loading a Playlist

1. **Navigate to Playlist Manager Tab**

2. **Enter Playlist URL**
   - Paste YouTube playlist URL
   - Example: `https://www.youtube.com/playlist?list=PLxxx...`

3. **Load Playlist Information**
   - Click "Load Playlist"
   - Wait for video list to populate

### Selecting Videos

1. **Review Video List**
   - Each video shows title and duration
   - Videos are numbered for easy reference

2. **Select Videos to Download**
   - Check boxes next to desired videos
   - Use "Select All" for entire playlist
   - Use "Deselect All" to clear selections

3. **Individual Time Ranges** (Optional)
   - Set custom time ranges for specific videos
   - Enter in format: `start_time - end_time`
   - Example: `1:30 - 5:45` or just `- 3:00` for first 3 minutes

4. **Configure Download Settings**
   - Select quality and audio options
   - Enable date organization if desired

5. **Download Selected Videos**
   - Click "Download Selected Videos"
   - Monitor progress for the entire batch

## Scheduler

Schedule downloads for automatic execution at specific times.

### Scheduling a Download

1. **Navigate to Scheduler Tab**

2. **Choose Download Type**
   - Single Video
   - Batch Videos
   - Playlist Selection

3. **Set Schedule Time**
   - **Date**: Use the date picker
   - **Time**: Enter in 24-hour format (e.g., 14:30 for 2:30 PM)

4. **Configure Download Options**
   - Quality, audio choice, subfolder creation
   - Same options as immediate downloads

5. **Enter Content Based on Type**

   **Single Video:**
   - Enter YouTube URL
   - Optional: Set start and end times for segments

   **Batch Videos:**
   - Enter multiple URLs (one per line)
   - Optional: Set individual time ranges

   **Playlist Selection:**
   - Enter playlist URL
   - The playlist will be loaded at execution time
   - All videos will be downloaded unless configured otherwise

6. **Schedule the Download**
   - Click "Schedule Download"
   - Download appears in the scheduled list below

### Managing Scheduled Downloads

1. **View Calendar**
   - Visual representation of all scheduled downloads
   - Color-coded by status:
     - 🟡 Yellow: Scheduled
     - 🔵 Blue: Downloading
     - 🟢 Green: Completed
     - 🔴 Red: Failed

2. **Monitor Status**
   - Real-time status updates
   - Progress bars for active downloads
   - Error messages for failed downloads

3. **Cancel Scheduled Downloads**
   - Use cancel button next to scheduled items
   - Only available for downloads that haven't started

### Background Service

For automatic execution, run the scheduler service:

**Windows:**
```batch
double-click start_with_scheduler.bat
```

**Manual Start:**
```bash
python scheduler_service.py
```

The service checks every 60 seconds for due downloads and executes them automatically.

## Download History

Track and search all your downloads.

### Viewing History

1. **Navigate to History Tab**
2. **Browse Download Records**
   - Shows all downloads with timestamps
   - Includes file paths and sizes
   - Displays quality and audio settings used

### Searching History

1. **Use the Search Box**
   - Search by video title, URL, or filename
   - Search is case-insensitive
   - Results update in real-time

2. **Filter by Date**
   - Use date range pickers to filter
   - Show downloads from specific time periods

### Managing History

1. **Clear History**
   - Use "Clear All History" button
   - Removes records but keeps downloaded files

2. **Export History**
   - History is stored in `download_history.json`
   - Can be backed up or transferred

## File Manager

Organize and manage your downloaded files.

### Browsing Files

1. **Navigate to File Manager Tab**
2. **View File Structure**
   - See all files in downloads folder
   - Date-organized folders if enabled
   - File sizes and modification dates

### File Operations

1. **Delete Files**
   - Click delete button next to unwanted files
   - Confirms deletion before proceeding
   - Removes both file and history record

2. **File Information**
   - View file sizes
   - See modification dates
   - Check file formats

3. **Folder Navigation**
   - Browse date-organized folders
   - Navigate through subdirectories

## Settings and Configuration

### Audio Options
- **With Audio**: Downloads video with original audio track
- **Video Only**: Downloads video without audio (smaller file size)
- **Audio Only**: Extracts audio as MP3 file

### Quality Settings
- **Best Quality**: Highest available resolution
- **Specific Resolutions**: 1080p, 720p, 480p, 360p
- Note: Some videos may not have all quality options

### Organization Options
- **Date Subfolders**: Organize downloads by date (`YYYY-MM-DD`)
- **Custom Paths**: Modify download location if needed

### Advanced Settings
- **Concurrent Downloads**: Number of simultaneous downloads
- **Retry Attempts**: Number of retry attempts for failed downloads
- **Timeout Settings**: Network timeout configurations

## Tips for Best Results

### Download Quality
- Use "Best Quality" for most content
- Lower qualities for faster downloads or limited storage
- Audio-only for music or podcasts

### Time Management
- Schedule large downloads during off-peak hours
- Use batch downloads for efficiency
- Monitor progress for long downloads

### Storage Management
- Enable date organization for better file management
- Regularly clean up unwanted files
- Check available disk space before large downloads

### Network Considerations
- Stable internet connection recommended
- Pause other downloads during batch operations
- Use scheduler for automatic overnight downloads

## Troubleshooting

### Common Issues

#### Video Not Available
- Check if video is public and not region-restricted
- Try different quality settings
- Verify URL is correct and complete

#### Slow Downloads
- Check internet connection speed
- Try lower quality settings
- Pause other network activities

#### Audio/Video Sync Issues
- Use "With Audio" option for best results
- Avoid "Video Only" + separate audio downloads
- Check source video quality

#### File Permission Errors
- Run application as administrator (Windows)
- Check downloads folder permissions
- Ensure sufficient disk space

#### Scheduler Not Working
- Verify scheduler service is running
- Check system clock accuracy
- Ensure downloads folder is accessible

### Getting Help

1. **Check Error Messages**: Read any error messages carefully
2. **Verify Settings**: Ensure correct quality and audio options
3. **Test Simple Downloads**: Try a basic video download first
4. **Check Network**: Verify internet connection
5. **Restart Application**: Close and reopen if issues persist

## Keyboard Shortcuts

### General Navigation
- **Tab**: Move between interface elements
- **Enter**: Confirm selections and start downloads
- **Escape**: Cancel dialogs and operations

### Text Input
- **Ctrl+A**: Select all text in input fields
- **Ctrl+C/V**: Copy and paste URLs
- **Ctrl+Z**: Undo in text areas

## Best Practices

### URL Management
- Always test URLs with "Get Video Info" first
- Copy URLs directly from browser address bar
- Avoid shortened URLs when possible

### File Organization
- Use date organization for regular downloads
- Create custom folders for specific projects
- Keep download folders organized and clean

### Performance
- Close other applications during large downloads
- Don't schedule too many simultaneous downloads
- Monitor system resources during batch operations

### Security
- Only download content you have rights to use
- Be cautious with unknown URLs
- Keep the application updated

This guide covers all major features of the Advanced YouTube Downloader. For technical details, see the API documentation. For installation help, refer to the installation guide.