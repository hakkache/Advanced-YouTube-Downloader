# 📅 YouTube Downloader Scheduler

## Overview
The YouTube Downloader now includes a powerful scheduler feature that allows you to schedule downloads for a future date and time. This feature supports all download types (single videos, batch downloads, and playlist selections) with full video or segment downloads.

## Features
- ⏰ **Schedule Downloads**: Set specific date and time for automatic downloads
- 📹 **All Download Types**: Single videos, batch downloads, and playlist selections
- ✂️ **Segment Support**: Schedule full video or specific time segment downloads
- 📅 **Calendar View**: Visual calendar showing all scheduled downloads with status
- 🔄 **Real-time Status**: Track download progress (scheduled, downloading, completed, failed)
- 🎯 **Background Service**: Automatic execution of scheduled downloads
- 💾 **Persistent Storage**: Scheduled downloads survive app restarts

## How to Use

### 1. Access the Scheduler
- Open the YouTube Downloader app
- Click on the **"⏰ Scheduler"** tab

### 2. Schedule a Download
1. **Choose Download Type**:
   - 📹 Single Video
   - 📋 Batch Videos  
   - 🎬 Playlist Selection

2. **Set Schedule Time**:
   - Select date using the date picker
   - Set time using the time input (24-hour format)

3. **Configure Download Options**:
   - Video quality (Best Quality, 1080p, 720p, 480p, 360p)
   - Audio choice (With Audio, Video Only, Audio Only)
   - Create subfolder option

4. **Add Content**:
   - **Single Video**: Enter YouTube URL and optional time segments
   - **Batch Videos**: Add multiple URLs with individual time segments
   - **Playlist Selection**: Enter playlist URL and select specific videos

5. **Schedule the Download**:
   - Click the "Schedule Download" button
   - The download will be added to your scheduled downloads list

### 3. Monitor Scheduled Downloads
- View all scheduled downloads in the calendar/list below the scheduling form
- Each download shows:
  - 📝 Title and type
  - 📅 Scheduled date and time
  - 📊 Current status
  - 🎯 Control buttons (cancel if needed)

## Real-time Progress Monitoring

### 📊 Live Progress Updates
When scheduled downloads are executing, you can monitor their progress in real-time:

1. **Progress Indicators**:
   - 📈 Progress bars showing download percentage
   - ⚡ Download speed (MB/s)
   - ⏱️ Estimated time remaining (ETA)
   - 💾 Downloaded vs. Total file size

2. **Batch/Playlist Progress**:
   - Overall progress across all videos
   - Current video number (e.g., "Video 3/10")
   - Individual video progress within the batch
   - Current video title/URL being downloaded

3. **Status Updates**:
   - Real-time status changes (scheduled → downloading → completed)
   - Last updated timestamp
   - Error messages for failed downloads

### 🔄 Viewing Progress
- **Scheduler Tab**: All progress is displayed in the scheduled downloads section
- **Refresh Button**: Click "🔄 Refresh Status" to get the latest updates
- **Auto-detection**: The app automatically detects active downloads
- **Live Updates**: Progress information updates every few seconds during downloads

### 💡 Progress Tips
- Keep the Streamlit app open to monitor progress
- Use the refresh button to see the latest status
- Check the scheduler service terminal for detailed logs
- Progress continues even if you refresh the app page

## Status Types
- 🟡 **Scheduled**: Waiting for scheduled time
- 🔵 **Downloading**: Currently downloading with live progress
- 🟢 **Completed**: Successfully downloaded
- 🔴 **Failed**: Download failed (with error details)

## Background Service
For automatic execution of scheduled downloads:

1. **Start the Service**:
   ```bash
   python scheduler_service.py
   ```

2. **Keep Running**: The service checks for due downloads every 60 seconds
3. **Automatic Downloads**: Downloads start automatically at scheduled times

## File Storage
- Scheduled downloads are stored in `scheduled_downloads.json`
- Download history includes scheduled downloads
- Files are saved in the standard downloads folder with date subfolders

## Tips
- **Time Format**: Use 24-hour format (e.g., 14:30 for 2:30 PM)
- **Advance Planning**: Schedule downloads during off-peak hours
- **Background Service**: Keep the scheduler service running for automatic execution
- **Monitoring**: Check the History tab to see completed scheduled downloads

## Troubleshooting
- **Service Not Running**: Scheduled downloads won't execute without the background service
- **Failed Downloads**: Check error messages in the status for troubleshooting
- **Missing Downloads**: Verify the scheduled time hasn't passed and service is running
- **File Conflicts**: Downloads with the same name will have numbers appended

## Example Use Cases
- **Overnight Downloads**: Schedule large playlists during low-usage hours
- **Bandwidth Management**: Schedule downloads for specific times
- **Content Preparation**: Download educational content before meetings/classes
- **Batch Processing**: Schedule multiple downloads at different times

Enjoy your automated YouTube downloads! 🎉
