# API Documentation

## Overview
This document describes the internal API structure and key functions used in the Advanced YouTube Downloader application.

## Core Classes and Functions

### Video Download Functions

#### `download_video(url, quality, audio_choice, progress_callback=None, organize_by_date=True, start_time=None, end_time=None)`
Downloads a single YouTube video with specified parameters.

**Parameters:**
- `url` (str): YouTube video URL
- `quality` (str): Video quality ("best", "1080", "720", "480", "360")
- `audio_choice` (str): Audio option ("with_audio", "no_audio", "audio_only")
- `progress_callback` (callable, optional): Progress update function
- `organize_by_date` (bool): Whether to organize files by date
- `start_time` (str, optional): Start time for video segment (format: "MM:SS" or "HH:MM:SS")
- `end_time` (str, optional): End time for video segment

**Returns:**
- `dict`: Download result with status and file path

#### `batch_download(urls, quality, audio_choice, progress_callback=None, organize_by_date=True, time_ranges=None)`
Downloads multiple videos in batch.

**Parameters:**
- `urls` (list): List of YouTube video URLs
- `quality` (str): Video quality for all videos
- `audio_choice` (str): Audio option for all videos
- `progress_callback` (callable, optional): Progress update function
- `organize_by_date` (bool): Whether to organize files by date
- `time_ranges` (dict, optional): Dictionary mapping URLs to time ranges

**Returns:**
- `list`: List of download results for each video

### Playlist Functions

#### `get_playlist_videos(playlist_url)`
Retrieves video information from a YouTube playlist.

**Parameters:**
- `playlist_url` (str): YouTube playlist URL

**Returns:**
- `list`: List of video dictionaries with metadata

#### `download_playlist_videos(playlist_url, selected_videos, quality, audio_choice, progress_callback=None)`
Downloads selected videos from a playlist.

**Parameters:**
- `playlist_url` (str): YouTube playlist URL
- `selected_videos` (list): List of selected video indices
- `quality` (str): Video quality
- `audio_choice` (str): Audio option
- `progress_callback` (callable, optional): Progress update function

### Utility Functions

#### `get_video_info(url)`
Retrieves metadata for a YouTube video without downloading.

**Parameters:**
- `url` (str): YouTube video URL

**Returns:**
- `dict`: Video metadata including title, duration, thumbnail

#### `parse_time_to_seconds(time_str)`
Converts time string to seconds.

**Parameters:**
- `time_str` (str): Time in format "MM:SS" or "HH:MM:SS"

**Returns:**
- `int`: Time in seconds

#### `trim_video_segment(input_file, start_seconds=None, end_seconds=None)`
Trims video segment using FFmpeg.

**Parameters:**
- `input_file` (str): Path to input video file
- `start_seconds` (int, optional): Start time in seconds
- `end_seconds` (int, optional): End time in seconds

**Returns:**
- `str`: Path to trimmed video file or None if no trimming needed

### History Management

#### `save_download_history(download_info)`
Saves download information to history.

**Parameters:**
- `download_info` (dict): Download metadata

#### `load_download_history()`
Loads download history from file.

**Returns:**
- `list`: List of download records

#### `search_history(query, history_data)`
Searches download history for matching records.

**Parameters:**
- `query` (str): Search query
- `history_data` (list): History data to search

**Returns:**
- `list`: Filtered history records

### Scheduler Functions

#### `save_scheduled_download(schedule_data)`
Saves a scheduled download to the schedule file.

**Parameters:**
- `schedule_data` (dict): Schedule configuration

#### `get_scheduled_downloads()`
Retrieves all scheduled downloads.

**Returns:**
- `list`: List of scheduled download configurations

#### `execute_scheduled_download(download_id)`
Executes a scheduled download by ID.

**Parameters:**
- `download_id` (str): Unique download identifier

## Configuration Options

### Quality Settings
- `"best"`: Best available quality
- `"1080"`: 1080p resolution
- `"720"`: 720p resolution  
- `"480"`: 480p resolution
- `"360"`: 360p resolution

### Audio Choices
- `"with_audio"`: Video with audio track
- `"no_audio"`: Video only, no audio
- `"audio_only"`: Audio extraction only

### File Organization
- Date-based folders: `downloads/YYYY-MM-DD/`
- Direct downloads: `downloads/`

## Error Handling

All download functions include comprehensive error handling for:
- Invalid URLs
- Network connectivity issues
- File system permissions
- Video availability restrictions
- Format compatibility problems

## Progress Callbacks

Progress callback functions receive a dictionary with:
- `status`: Current operation status
- `percent`: Download percentage (0-100)
- `speed`: Download speed (bytes/second)
- `eta`: Estimated time remaining (seconds)
- `downloaded`: Bytes downloaded
- `total`: Total file size in bytes

## File Formats

### Download History (JSON)
```json
{
  "url": "video_url",
  "title": "video_title",
  "quality": "720",
  "audio_choice": "with_audio",
  "download_time": "2024-07-04 10:30:00",
  "file_path": "/path/to/video.mp4",
  "file_size": "50.2 MB"
}
```

### Scheduled Downloads (JSON)
```json
{
  "id": "unique_id",
  "type": "single|batch|playlist",
  "scheduled_time": "2024-07-04 15:30:00",
  "config": {
    "urls": ["url1", "url2"],
    "quality": "720",
    "audio_choice": "with_audio",
    "time_ranges": {}
  },
  "status": "scheduled|downloading|completed|failed"
}
```