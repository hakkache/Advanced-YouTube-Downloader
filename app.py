import streamlit as st
import yt_dlp
import os
import time
import json
import threading
import subprocess
from datetime import datetime, timedelta
import concurrent.futures
from urllib.parse import urlparse, parse_qs
import schedule

def trim_video_segment(input_file, start_seconds=None, end_seconds=None):
    """Trim video segment using FFmpeg after download."""
    
    print(f"DEBUG: trim_video_segment called with: input_file='{input_file}', start_seconds={start_seconds}, end_seconds={end_seconds}")
    
    if start_seconds is None and end_seconds is None:
        print("DEBUG: No trimming needed - both start and end are None")
        return None
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"DEBUG: Input file does not exist: {input_file}")
        return None
    
    # Generate output filename
    base_name, ext = os.path.splitext(input_file)
    output_file = f"{base_name}_trimmed{ext}"
    
    print(f"DEBUG: Input file: {input_file}")
    print(f"DEBUG: Output file: {output_file}")
    
    # Build FFmpeg command
    cmd = ['ffmpeg', '-i', input_file, '-y']  # -y to overwrite output file
    
    # Add start time
    if start_seconds is not None:
        cmd.extend(['-ss', str(start_seconds)])
    
    # Add duration or end time
    if end_seconds is not None:
        if start_seconds is not None:
            duration = end_seconds - start_seconds
            cmd.extend(['-t', str(duration)])
        else:
            cmd.extend(['-t', str(end_seconds)])
    
    # Copy codecs for faster processing (no re-encoding)
    cmd.extend(['-c', 'copy', output_file])
    
    try:
        cmd_str = ' '.join(cmd)
        print(f"DEBUG: Running FFmpeg command: {cmd_str}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"DEBUG: FFmpeg return code: {result.returncode}")
        if result.stdout:
            print(f"DEBUG: FFmpeg stdout: {result.stdout}")
        if result.stderr:
            print(f"DEBUG: FFmpeg stderr: {result.stderr}")
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                print(f"DEBUG: FFmpeg trimming successful - output file created")
                return output_file
            else:
                print(f"DEBUG: FFmpeg completed but output file not found")
                return None
        else:
            print(f"DEBUG: FFmpeg failed with return code {result.returncode}")
            return None
    except subprocess.TimeoutExpired:
        print("DEBUG: FFmpeg trimming timed out")
        return None
    except Exception as e:
        print(f"DEBUG: FFmpeg trimming failed with exception: {e}")
        return None

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            # Don't call st.error to avoid ScriptRunContext warnings
            return None

def get_playlist_info(url):
    """Extract playlist information"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extractor_retries': 3,
        'fragment_retries': 3,
        'retry_sleep_functions': {'http': lambda n: 0.5 * n},
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                return info
            return None
        except Exception as e:
            # Don't call st.error to avoid ScriptRunContext warnings
            return None

def is_playlist_url(url):
    """Check if URL is a playlist"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return 'list' in query_params or 'playlist' in url.lower()

class DownloadProgress:
    def __init__(self):
        self.progress = 0
        self.status = "Waiting"
        self.filename = ""
        self.speed = 0
        self.eta = 0
        self.downloaded_mb = 0
        self.total_mb = 0
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                self.progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.total_mb = d['total_bytes'] / (1024 * 1024)
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                self.progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                self.total_mb = d['total_bytes_estimate'] / (1024 * 1024)
            
            self.downloaded_mb = d['downloaded_bytes'] / (1024 * 1024)
            self.speed = d.get('speed', 0) or 0
            self.eta = d.get('eta', 0) or 0
            self.status = "Downloading"
            self.filename = d.get('filename', '')
        elif d['status'] == 'finished':
            self.progress = 100
            self.status = "Completed"
            self.filename = d.get('filename', '')

class BatchProgress:
    def __init__(self):
        self.current_video = 0
        self.total_videos = 0
        self.current_progress = 0
        self.overall_progress = 0
        self.current_filename = ""
        self.current_status = "Waiting"
        self.success_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.current_speed = 0
        self.current_eta = 0
        self.current_downloaded_mb = 0
        self.current_total_mb = 0
        
    def update_video_count(self, total):
        self.total_videos = total
        
    def next_video(self):
        self.current_video += 1
        self.current_progress = 0
        self.current_filename = ""
        self.current_status = "Starting"
        self.current_speed = 0
        self.current_eta = 0
        self.current_downloaded_mb = 0
        self.current_total_mb = 0
        
    def video_completed(self, success=True):
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        self.overall_progress = ((self.current_video - 1) / self.total_videos) * 100
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                self.current_progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.current_total_mb = d['total_bytes'] / (1024 * 1024)
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                self.current_progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                self.current_total_mb = d['total_bytes_estimate'] / (1024 * 1024)
            
            self.current_downloaded_mb = d['downloaded_bytes'] / (1024 * 1024)
            self.current_speed = d.get('speed', 0) or 0
            self.current_eta = d.get('eta', 0) or 0
            self.current_status = "Downloading"
            self.current_filename = d.get('filename', '')
            
            # Update overall progress
            video_weight = 1.0 / self.total_videos
            completed_videos_progress = ((self.current_video - 1) / self.total_videos) * 100
            current_video_progress = (self.current_progress / 100) * video_weight * 100
            self.overall_progress = completed_videos_progress + current_video_progress
            
        elif d['status'] == 'finished':
            self.current_progress = 100
            self.current_status = "Completed"
            self.current_filename = d.get('filename', '')
            
    def get_eta_remaining(self):
        if self.overall_progress <= 0:
            return 0
        elapsed_time = time.time() - self.start_time
        if self.overall_progress > 0:
            total_estimated_time = (elapsed_time / self.overall_progress) * 100
            return max(0, total_estimated_time - elapsed_time)
        return 0

class DownloadController:
    def __init__(self):
        self.is_paused = False
        self.should_stop = False
        self.download_thread = None
        self.download_result = None
        self.download_complete = False
        self.is_finished = False
        # Progress data for thread-safe UI updates
        self.progress_data = {
            'status': 'waiting',
            'progress': 0,
            'downloaded_mb': 0,
            'total_mb': 0,
            'speed_mb_per_sec': 0,
            'eta_minutes': 0,
            'eta_seconds': 0,
            'filename': '',
            'last_update_time': 0,
            'last_downloaded_bytes': 0
        }
        
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False
        
    def stop(self):
        self.should_stop = True
        if self.download_thread and self.download_thread.is_alive():
            self.download_thread.join(timeout=2)
            
    def reset(self):
        self.is_paused = False
        self.should_stop = False
        self.download_thread = None
        self.download_result = None
        self.download_complete = False
        self.is_finished = False
        # Reset progress data
        self.progress_data = {
            'status': 'waiting',
            'progress': 0,
            'downloaded_mb': 0,
            'total_mb': 0,
            'speed_mb_per_sec': 0,
            'eta_minutes': 0,
            'eta_seconds': 0,
            'filename': '',
            'last_update_time': 0,
            'last_downloaded_bytes': 0
        }

class PlaylistVideoProgress:
    def __init__(self):
        self.progress = 0
        self.status = ""
        self.speed = ""
        self.eta = ""
        self.is_completed = False
        self.last_update_time = time.time()
        self.last_downloaded_bytes = 0
    
    def update_progress(self, d):
        """Update progress data without making UI calls"""
        if d['status'] == 'downloading':
            current_time = time.time()
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if 'total_bytes' in d and d['total_bytes']:
                total_bytes = d['total_bytes']
                self.progress = (downloaded_bytes / total_bytes) * 100
                
                downloaded_mb = downloaded_bytes / (1024 * 1024)
                total_mb = total_bytes / (1024 * 1024)
                self.status = f"🔄 {self.progress:.1f}% ({downloaded_mb:.1f} MB / {total_mb:.1f} MB)"
                
                # Calculate speed and ETA
                if current_time - self.last_update_time > 1.0:
                    time_diff = current_time - self.last_update_time
                    bytes_diff = downloaded_bytes - self.last_downloaded_bytes
                    speed_bytes_per_sec = bytes_diff / time_diff
                    speed_mb_per_sec = speed_bytes_per_sec / (1024 * 1024)
                    
                    if speed_bytes_per_sec > 0:
                        eta_seconds = (total_bytes - downloaded_bytes) / speed_bytes_per_sec
                        eta_minutes = int(eta_seconds // 60)
                        eta_seconds = int(eta_seconds % 60)
                        
                        self.speed = f"⚡ {speed_mb_per_sec:.2f} MB/s"
                        self.eta = f"⏱️ {eta_minutes}m {eta_seconds}s"
                    
                    self.last_update_time = current_time
                    self.last_downloaded_bytes = downloaded_bytes
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                total_bytes = d['total_bytes_estimate']
                self.progress = (downloaded_bytes / total_bytes) * 100
                
                downloaded_mb = downloaded_bytes / (1024 * 1024)
                total_mb = total_bytes / (1024 * 1024)
                self.status = f"🔄 {self.progress:.1f}% (~{downloaded_mb:.1f} MB / ~{total_mb:.1f} MB)"
            else:
                downloaded_mb = downloaded_bytes / (1024 * 1024)
                self.status = f"🔄 {downloaded_mb:.1f} MB downloaded"
        elif d['status'] == 'finished':
            self.progress = 100
            self.status = "✅ Video completed!"
            self.speed = ""
            self.eta = ""
            self.is_completed = True

def save_download_history(video_info, quality, file_path):
    """Save download to history"""
    history_file = "download_history.json"
    history = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    download_record = {
        'title': video_info.get('title', 'Unknown'),
        'url': video_info.get('webpage_url', ''),
        'quality': quality,
        'file_path': file_path,
        'download_date': datetime.now().isoformat(),
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
    }
    
    history.append(download_record)
    
    # Keep only last 100 downloads
    if len(history) > 100:
        history = history[-100:]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_download_history():
    """Get download history"""
    history_file = "download_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def download_video(url, quality, audio_choice="with_audio", output_path="downloads", progress_callback=None, controller=None, start_time=None, end_time=None):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Set format based on selected quality and audio option
    if audio_choice == "video_only":
        if quality == "1080p":
            format_option = "bestvideo[height<=1080]"
        elif quality == "720p":
            format_option = "bestvideo[height<=720]"
        elif quality == "480p":
            format_option = "bestvideo[height<=480]"
        elif quality == "360p":
            format_option = "bestvideo[height<=360]"
        else:  # Best Quality
            format_option = "bestvideo"
    elif quality == "Audio Only":
        format_option = "bestaudio/best"
    else:  # with_audio (default)
        if quality == "1080p":
            format_option = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif quality == "720p":
            format_option = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality == "480p":
            format_option = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif quality == "360p":
            format_option = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        else:  # Best Quality
            format_option = "bestvideo+bestaudio/best"
    
    ydl_opts = {
        'format': format_option,
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        # Add more robust options for YouTube issues
        'extractor_retries': 3,
        'fragment_retries': 3,
        'retry_sleep_functions': {'http': lambda n: 0.5 * n},
    }
    
    # Initialize segment_info at function level to avoid scope issues
    segment_info = {}
    
    # Add time range options if specified using yt-dlp's built-in download_sections
    if start_time or end_time:
        def time_to_seconds(time_str):
            """Convert time string (HH:MM:SS or MM:SS) to seconds."""
            if not time_str:
                return None
            try:
                parts = time_str.split(':')
                if len(parts) == 2:  # MM:SS format
                    minutes, seconds = int(parts[0]), int(parts[1])
                    return minutes * 60 + seconds
                elif len(parts) == 3:  # HH:MM:SS format
                    hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                    return hours * 3600 + minutes * 60 + seconds
                else:
                    return None
            except (ValueError, IndexError):
                return None

        start_seconds = time_to_seconds(start_time) if start_time and start_time != "00:00:00" else None
        end_seconds = time_to_seconds(end_time) if end_time and end_time.strip() else None

        # Configure segment download by downloading full video and then trimming with FFmpeg
        # Note: We download the full video and trim it afterwards due to yt-dlp limitations
        if start_seconds is not None or end_seconds is not None:
            segment_info = {
                'start_seconds': start_seconds,
                'end_seconds': end_seconds,
                'start_time': start_time,
                'end_time': end_time
            }
            
            # Update output template to include time range info
            time_suffix = ""
            if start_time and start_time != "00:00:00":
                time_suffix += f"_{start_time.replace(':', '')}"
            if end_time and end_time.strip():
                time_suffix += f"_to_{end_time.replace(':', '')}"
            
            if time_suffix:
                ydl_opts['outtmpl'] = os.path.join(output_path, f'%(title)s{time_suffix}.%(ext)s')
            
            print(f"DEBUG: Will trim video after download")
            print(f"DEBUG: Time range: {start_time} to {end_time} ({start_seconds}s to {end_seconds}s)")
    
    # Add progress hook with pause/stop control if provided
    if progress_callback:
        def controlled_progress_hook(d):
            if controller and controller.should_stop:
                raise Exception("Download stopped by user")
            
            # Handle pause functionality
            while controller and controller.is_paused and not controller.should_stop:
                time.sleep(0.1)
            
            if controller and controller.should_stop:
                raise Exception("Download stopped by user")
                
            progress_callback(d)
        
        ydl_opts['progress_hooks'] = [controlled_progress_hook]
    
    # If audio only, change the extension
    if quality == "Audio Only":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    # If video only, ensure no audio
    if audio_choice == "video_only" and quality != "Audio Only":
        ydl_opts['postprocessors'] = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Check for stop before starting
            if controller and controller.should_stop:
                return False, "Download stopped by user"
            
            # Get video info for history
            info = ydl.extract_info(url, download=False)
            
            # Check for stop after getting info
            if controller and controller.should_stop:
                return False, "Download stopped by user"
            
            # Download the video
            ydl.download([url])
            
            # Get the downloaded filename
            expected_filename = ydl.prepare_filename(info)
            
            # Perform segment trimming if required
            if segment_info:
                print("DEBUG: Starting post-download segment trimming...")
                try:
                    start_sec = segment_info.get('start_seconds')
                    end_sec = segment_info.get('end_seconds')
                    print(f"DEBUG: Calling trim_video_segment with start_sec={start_sec}, end_sec={end_sec}")
                    trimmed_filename = trim_video_segment(expected_filename, start_sec, end_sec)
                    if trimmed_filename:
                        # Delete the original full video file
                        if os.path.exists(expected_filename):
                            os.remove(expected_filename)
                            print(f"DEBUG: Deleted original file: {expected_filename}")
                        expected_filename = trimmed_filename
                        print(f"DEBUG: Segment trimming completed: {trimmed_filename}")
                    else:
                        print("DEBUG: Segment trimming failed, keeping original file")
                except Exception as trim_error:
                    print(f"DEBUG: Exception during trimming: {trim_error}")
                    print("DEBUG: Keeping original file due to trimming error")
            
            # Mark as completed if we have a controller
            if controller:
                controller.progress_data['status'] = 'completed'
                controller.progress_data['progress'] = 100
                controller.is_finished = True
            
            # Save to history only if completed successfully
            save_download_history(info, f"{quality} ({audio_choice})", expected_filename)
            
            return True, expected_filename
        except Exception as e:
            error_msg = str(e)
            if "stopped by user" in error_msg:
                return False, "Download stopped by user"
            elif "ffmpeg" in error_msg.lower() or "postprocessor" in error_msg.lower():
                return False, f"FFmpeg error (time range may be invalid): {e}"
            elif "fragment" in error_msg.lower():
                return False, f"YouTube streaming error (try different quality): {e}"
            else:
                # Don't call st.error from background thread - just return the error
                return False, f"Error downloading video: {e}"

def download_playlist(playlist_url, quality, audio_choice="with_audio", max_downloads=None, progress_container=None, start_time=None, end_time=None):
    """Download videos from a playlist with enhanced progress tracking"""
    playlist_info = get_playlist_info(playlist_url)
    if not playlist_info or 'entries' not in playlist_info:
        return False, "Invalid playlist URL"
    
    entries = playlist_info['entries']
    if max_downloads:
        entries = entries[:max_downloads]
    
    results = []
    start_time = time.time()
    
    # Create progress elements if container is provided
    if progress_container:
        with progress_container:
            st.markdown("#### 📊 Playlist Progress")
            playlist_progress = st.progress(0)
            playlist_status = st.empty()
            playlist_stats = st.empty()
            
            st.markdown("#### 🎬 Current Video")
            current_video_info = st.empty()
            video_progress = st.progress(0)
            video_status = st.empty()
            video_speed = st.empty()
            video_eta = st.empty()
    
    for i, entry in enumerate(entries):
        if entry:
            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
            video_title = entry.get('title', 'Unknown')
            
            if progress_container:
                # Update playlist progress
                playlist_progress.progress(i / len(entries))
                playlist_status.markdown(f"**Processing video {i+1}/{len(entries)}**")
                
                # Show playlist statistics
                if i > 0:
                    elapsed_time = time.time() - start_time
                    avg_time_per_video = elapsed_time / i
                    estimated_total_time = avg_time_per_video * len(entries)
                    remaining_time = estimated_total_time - elapsed_time
                    remaining_minutes = int(remaining_time // 60)
                    remaining_seconds = int(remaining_time % 60)
                    successful_so_far = sum(1 for r in results if r['success'])
                    playlist_stats.markdown(f"**⏱️ ETA: {remaining_minutes}m {remaining_seconds}s | ✅ Success: {successful_so_far}/{i} | ❌ Failed: {i - successful_so_far}**")
                
                # Show current video info
                current_video_info.markdown(f"**🎬 {video_title}**")
                current_video_info.caption(f"URL: {video_url}")
                
                # Reset video progress elements
                video_progress.progress(0)
                video_status.empty()
                video_speed.empty()
                video_eta.empty()
                
                # Progress tracking for individual video - no direct UI calls
                video_progress_tracker = PlaylistVideoProgress()
                
                def update_video_progress(d):
                    # Only update the tracker, no direct UI calls
                    video_progress_tracker.update_progress(d)
                
                success, filename = download_video(video_url, quality, audio_choice, "downloads", update_video_progress, None, start_time, end_time)
                
                # Update UI with final progress after download completes
                if success:
                    video_progress.progress(100)
                    video_status.markdown("**✅ Video completed!**")
                else:
                    video_status.markdown("**❌ Video failed!**")
                video_speed.empty()
                video_eta.empty()
            else:
                # Fallback without progress display
                success, filename = download_video(video_url, quality, audio_choice, "downloads", None, None, start_time, end_time)
            
            results.append({'success': success, 'title': video_title, 'filename': filename})
    
    # Final progress update
    if progress_container:
        playlist_progress.progress(1.0)
        playlist_status.markdown("**✅ PLAYLIST DOWNLOAD COMPLETED - PROCESS STOPPED**")
        
        # Final statistics
        total_time = time.time() - start_time
        total_minutes = int(total_time // 60)
        total_seconds = int(total_time % 60)
        successful_count = sum(1 for r in results if r['success'])
        playlist_stats.markdown(f"**🏁 COMPLETED | Total time: {total_minutes}m {total_seconds}s | ✅ Success: {successful_count}/{len(entries)} | ❌ Failed: {len(entries) - successful_count}**")
    
    return True, results

# Set up the Streamlit app
st.set_page_config(page_title="Advanced YouTube Downloader", page_icon="🎬", layout="wide")

# Initialize session state
if 'download_progress' not in st.session_state:
    st.session_state.download_progress = DownloadProgress()

if 'download_state' not in st.session_state:
    st.session_state.download_state = {
        'is_downloading': False,
        'is_paused': False,
        'should_stop': False,
        'current_download': None,
        'last_progress': 0,  # Track last progress to avoid flickering
        'last_status': '',   # Track last status message
        'batch_state': {
            'is_downloading': False,
            'is_paused': False,
            'should_stop': False,
            'current_index': 0,
            'urls': [],
            'results': []
        }
    }

# Black and Green Modern CSS styling
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling - Dark background */
    .main {
        padding-top: 2rem;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        min-height: 100vh;
    }
    
    /* Override Streamlit's default background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    /* Custom font for entire app */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #0a0a0a;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #22c55e 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(34, 197, 94, 0.3);
        text-align: center;
        border: 2px solid #22c55e;
    }
    
    .main-title {
        color: #22c55e;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .main-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling - Dark theme */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        border-right: 2px solid #22c55e;
    }
    
    /* Button styling - Green theme */
    .stButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: black !important;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.6);
        color: black !important;
    }
    
    .stButton > button:focus {
        color: black !important;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.3);
    }
    
    /* Card-like containers - Dark with green accents */
    .info-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        border: 1px solid #22c55e;
        margin: 1rem 0;
    }
    
    .info-card h1, .info-card h2, .info-card h3, .info-card h4, .info-card h5, .info-card h6 {
        color: #22c55e !important;
    }
    
    .info-card p, .info-card div, .info-card span {
        color: #e5e7eb !important;
    }
    
    /* Progress bar styling - Green */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        border-radius: 10px;
        height: 12px;
    }
    
    .stProgress > div > div {
        background-color: #374151;
        border-radius: 10px;
        height: 12px;
    }
    
    /* Metric styling - Dark cards with green accents */
    .metric-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #22c55e;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3);
    }
    
    .metric-label {
        color: #9ca3af;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #22c55e;
        font-size: 24px;
        font-weight: 700;
    }
    
    /* General text improvements - Light text on dark background */
    h1, h2, h3, h4, h5, h6 {
        color: #22c55e !important;
        font-weight: 600 !important;
    }
    
    p, div, span, label {
        color: #e5e7eb !important;
    }
    
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #e5e7eb !important;
    }
    
    /* Force text visibility in all components */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label {
        color: #22c55e !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    .stRadio label, .stCheckbox label {
        color: #22c55e !important;
        font-weight: 500 !important;
    }
    
    .stMetric label, .stMetric > div > div {
        color: #22c55e !important;
        font-weight: 600 !important;
    }
    
    .stMetric .metric-value {
        color: #22c55e !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar text - Light on dark */
    .css-1d391kg .stMarkdown, .css-1d391kg .stMarkdown p, .css-1d391kg .stMarkdown div {
        color: #e5e7eb !important;
    }
    
    .css-1d391kg h3, .css-1d391kg h4 {
        color: #22c55e !important;
        font-weight: 600 !important;
    }
    
    .css-1d391kg p, .css-1d391kg div, .css-1d391kg span {
        color: #e5e7eb !important;
    }
    
    /* Text in all inputs and selects - Dark inputs with light text */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        background-color: #374151 !important;
        color: #e5e7eb !important;
        border: 1px solid #22c55e !important;
        font-weight: 500 !important;
    }
    
    /* Text in radio buttons and checkboxes */
    .stRadio > div > div, .stCheckbox > label > div {
        color: #e5e7eb !important;
    }
    
    /* Text in expanders */
    .streamlit-expanderHeader, .streamlit-expanderHeader p {
        color: #22c55e !important;
        font-weight: 600 !important;
        background: #1a1a1a !important;
    }
    
    .streamlit-expanderContent, .streamlit-expanderContent p, .streamlit-expanderContent div {
        color: #e5e7eb !important;
        background: #262626 !important;
    }
    
    /* Tab styling - Dark with green accents */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #1a1a1a;
        border-radius: 10px;
        padding: 4px;
        border: 1px solid #22c55e;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: none;
        background: #374151;
        transition: all 0.3s ease;
        color: #e5e7eb !important;
        border: 1px solid #4b5563;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #4b5563;
        color: #e5e7eb !important;
        border-color: #22c55e;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: black !important;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
        border: 1px solid #22c55e !important;
    }
    
    .stTabs [aria-selected="true"]:hover {
        color: black !important;
    }
    
    .stTabs [data-baseweb="tab"] span {
        color: inherit !important;
    }
    
    /* Input field styling - Dark theme */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #22c55e;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 500;
        color: #e5e7eb !important;
        background-color: #374151 !important;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #22c55e;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
        outline: none;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
        font-weight: 400;
    }
    
    /* Select box styling - Dark theme */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #22c55e;
        background-color: #374151 !important;
    }
    
    .stSelectbox > div > div > div {
        color: #e5e7eb !important;
        font-weight: 500;
        font-size: 16px;
    }
    
    .stSelectbox label {
        color: #22c55e !important;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Success/Error message styling - Dark theme */
    .stSuccess {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stSuccess > div {
        color: black !important;
        font-weight: 600 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stError > div {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stInfo > div {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stWarning > div {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* File item styling - Dark theme */
    .file-item {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border: 1px solid #22c55e;
        transition: all 0.3s ease;
    }
    
    .file-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(34, 197, 94, 0.3);
    }
    
    .file-item h1, .file-item h2, .file-item h3, .file-item h4, .file-item h5, .file-item h6 {
        color: #22c55e !important;
    }
    
    .file-item p, .file-item div, .file-item span {
        color: #e5e7eb !important;
    }
    
    /* Expander styling - Dark theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        border-radius: 10px;
        border: 1px solid #22c55e;
        font-weight: 600;
        color: #22c55e !important;
        padding: 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #262626 0%, #374151 100%);
    }
    
    .streamlit-expanderContent {
        background: #262626;
        border: 1px solid #22c55e;
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 1rem;
    }
    
    /* Sidebar radio buttons */
    .stRadio > div {
        background: transparent;
        padding: 1rem;
        border-radius: 10px;
        border: none;
    }
    
    .stRadio label {
        color: #22c55e !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    .stRadio > div > div, .stRadio > div > div > div {
        color: #e5e7eb !important;
    }
    
    /* Radio button styling - Dark theme */
    .stRadio [role="radiogroup"] > label {
        color: #e5e7eb !important;
        background: #374151;
        border: 1px solid #22c55e;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .stRadio [role="radiogroup"] > label > div {
        color: #e5e7eb !important;
    }
    
    /* Checkbox styling - Dark theme */
    .stCheckbox > label {
        background: #374151;
        padding: 0.75rem;
        border-radius: 8px;
        transition: background 0.3s ease;
        color: #e5e7eb !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: 1px solid #22c55e;
    }
    
    .stCheckbox > label:hover {
        background: #4b5563;
        border-color: #22c55e;
    }
    
    .stCheckbox > label > div {
        color: #e5e7eb !important;
    }
    
    /* Number input styling - Dark theme */
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #22c55e;
        padding: 12px 16px;
        font-size: 16px;
        font-weight: 500;
        color: #e5e7eb !important;
        background-color: #374151 !important;
    }
    
    .stNumberInput label {
        color: #22c55e !important;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Text area styling - Dark theme */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #22c55e;
        padding: 12px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 500;
        color: #e5e7eb !important;
        background-color: #374151 !important;
        resize: vertical;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #22c55e;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
        outline: none;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #9ca3af;
        font-weight: 400;
    }
    
    .stTextArea label {
        color: #22c55e !important;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Icon styling */
    .icon {
        display: inline-block;
        margin-right: 8px;
        font-size: 1.2em;
    }
    
    /* Progress section styling */
    .progress-section {
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #22c55e;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    .progress-section h4 {
        color: #22c55e !important;
        margin-bottom: 1rem !important;
    }
    
    .current-video-info {
        background: linear-gradient(135deg, #262626 0%, #374151 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #22c55e;
    }
    
    /* Control buttons styling */
    .control-buttons {
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #1a1a1a 0%, #262626 100%);
        border-radius: 10px;
        border: 1px solid #22c55e;
    }
    
    /* Pause button - Orange */
    [data-testid="stButton"] button[aria-label*="Pause"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: black !important;
    }
    
    /* Resume button - Blue */
    [data-testid="stButton"] button[aria-label*="Resume"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }
    
    /* Stop button - Red */
    [data-testid="stButton"] button[aria-label*="Stop"] {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        color: white !important;
    }
    
    /* Skip button - Purple */
    [data-testid="stButton"] button[aria-label*="Skip"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Modern header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🎬 Advanced YouTube Downloader</h1>
    <p class="main-subtitle">Download YouTube videos and playlists with professional quality and advanced features</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Download format options
    st.markdown("#### 🎵 Audio Options")
    audio_options = {
        "with_audio": "🎵 Video with Audio",
        "video_only": "🎥 Video Only (No Audio)",
        "audio_only": "🎵 Audio Only"
    }
    
    # Create modern radio buttons
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    audio_choice = st.radio("Select audio option:", list(audio_options.keys()), 
                           format_func=lambda x: audio_options[x])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced settings
    st.markdown("#### 🔧 Advanced Settings")
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    create_subfolder = st.checkbox("📅 Organize by date", value=True)
    max_playlist_downloads = st.number_input("📊 Max playlist downloads (0 = all)", 
                                           min_value=0, max_value=100, value=10)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # YouTube download issues info
    st.markdown("#### ⚠️ YouTube Download Issues")
    with st.expander("📖 Common Issues & Solutions"):
        st.markdown("""
        **If downloads fail with 'fragment not found' errors:**
        
        🔹 **YouTube SABR Streaming**: YouTube sometimes forces SABR streaming which can cause download failures
        
        🔹 **Solutions to try:**
        - Try a different quality setting (720p instead of 1080p)
        - Use "Audio Only" if you just need the audio
        - Wait a few minutes and try again
        - Try the video URL without any timestamp parameters
        
        🔹 **Alternative approach:**
        - Copy the video URL without `&t=` parameters
        - Choose a lower quality setting first
        - Some videos work better with "Video Only" option
        """)
    
    # App info
    st.markdown("---")
    st.markdown("#### 💡 Quick Tips")
    st.markdown("""
    - Use **Video Only** for silent videos
    - Enable **Organize by date** for better file management
    - Use **Custom Time Range** to download video segments
    - Time format: HH:MM:SS or MM:SS (e.g., 01:30 or 00:01:30)
    - Check **History** tab for all downloads
    - Use **File Manager** to manage downloads
    """)
    
    st.markdown("---")
    st.markdown("#### 🚀 Version")
    st.markdown("**v2.0** - Advanced Edition")
    st.markdown("Made with ❤️ using Streamlit")

# Scheduler Functions
def save_scheduled_downloads(scheduled_downloads):
    """Save scheduled downloads to file"""
    scheduler_file = "scheduled_downloads.json"
    with open(scheduler_file, 'w', encoding='utf-8') as f:
        json.dump(scheduled_downloads, f, indent=2, ensure_ascii=False)

def get_scheduled_downloads():
    """Get scheduled downloads"""
    scheduler_file = "scheduled_downloads.json"
    if os.path.exists(scheduler_file):
        try:
            with open(scheduler_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def update_scheduled_download_status(download_id, status, result=None):
    """Update the status of a scheduled download"""
    scheduled_downloads = get_scheduled_downloads()
    for download in scheduled_downloads:
        if download.get('id') == download_id:
            download['status'] = status
            download['last_updated'] = datetime.now().isoformat()
            if result:
                download['result'] = result
            break
    save_scheduled_downloads(scheduled_downloads)

def execute_scheduled_download(download_data):
    """Execute a scheduled download with progress tracking"""
    try:
        download_id = download_data['id']
        download_type = download_data['type']
        
        # Update status to downloading
        update_scheduled_download_status(download_id, 'downloading')
        
        # Create download path
        output_path = os.path.join(os.getcwd(), "downloads")
        if download_data.get('create_subfolder', True):
            date_folder = datetime.now().strftime("%Y-%m-%d")
            output_path = os.path.join(output_path, date_folder)
        
        # Progress tracking function for scheduled downloads
        def update_scheduled_progress(d):
            """Update progress information in the scheduled downloads file"""
            try:
                progress_info = {
                    'status': d['status'],
                    'timestamp': datetime.now().isoformat()
                }
                
                if d['status'] == 'downloading':
                    # Calculate progress percentage
                    if 'total_bytes' in d and d['total_bytes']:
                        progress_info['progress'] = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        progress_info['total_mb'] = d['total_bytes'] / (1024 * 1024)
                    elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                        progress_info['progress'] = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                        progress_info['total_mb'] = d['total_bytes_estimate'] / (1024 * 1024)
                    else:
                        progress_info['progress'] = 0
                        progress_info['total_mb'] = 0
                    
                    progress_info['downloaded_mb'] = d['downloaded_bytes'] / (1024 * 1024)
                    progress_info['speed'] = d.get('speed', 0) or 0
                    progress_info['eta'] = d.get('eta', 0) or 0
                    progress_info['filename'] = d.get('filename', '')
                
                elif d['status'] == 'finished':
                    progress_info['progress'] = 100
                    progress_info['filename'] = d.get('filename', '')
                
                # Update the scheduled download with progress info
                scheduled_downloads = get_scheduled_downloads()
                for download in scheduled_downloads:
                    if download.get('id') == download_id:
                        download['progress'] = progress_info
                        break
                save_scheduled_downloads(scheduled_downloads)
                
            except Exception as e:
                print(f"Progress update error: {e}")
        
        if download_type == 'single':
            # Single video download with progress tracking
            success, result = download_video(
                download_data['url'],
                download_data['quality'],
                download_data['audio_choice'],
                output_path,
                update_scheduled_progress,  # Add progress callback
                None,  # No controller for scheduled downloads
                download_data.get('start_time'),
                download_data.get('end_time')
            )
            
        elif download_type == 'batch':
            # Batch download with progress tracking
            results = []
            total_videos = len(download_data['urls'])
            
            for i, url_data in enumerate(download_data['urls']):
                # Update batch progress
                batch_progress_info = {
                    'status': 'downloading',
                    'current_video': i + 1,
                    'total_videos': total_videos,
                    'batch_progress': ((i / total_videos) * 100),
                    'current_url': url_data['url'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update scheduled download with batch progress
                scheduled_downloads = get_scheduled_downloads()
                for download in scheduled_downloads:
                    if download.get('id') == download_id:
                        download['progress'] = batch_progress_info
                        break
                save_scheduled_downloads(scheduled_downloads)
                
                # Download individual video with progress
                def batch_video_progress(d):
                    # Update individual video progress within batch
                    batch_progress_info['video_progress'] = {
                        'status': d['status'],
                        'progress': 0
                    }
                    
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d and d['total_bytes']:
                            batch_progress_info['video_progress']['progress'] = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                            batch_progress_info['video_progress']['progress'] = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                        
                        batch_progress_info['video_progress']['downloaded_mb'] = d['downloaded_bytes'] / (1024 * 1024)
                        batch_progress_info['video_progress']['speed'] = d.get('speed', 0) or 0
                        batch_progress_info['video_progress']['eta'] = d.get('eta', 0) or 0
                    
                    # Update the scheduled download
                    scheduled_downloads = get_scheduled_downloads()
                    for download in scheduled_downloads:
                        if download.get('id') == download_id:
                            download['progress'] = batch_progress_info
                            break
                    save_scheduled_downloads(scheduled_downloads)
                
                success, result = download_video(
                    url_data['url'],
                    download_data['quality'],
                    download_data['audio_choice'],
                    output_path,
                    batch_video_progress,
                    None,
                    url_data.get('start_time'),
                    url_data.get('end_time')
                )
                results.append({'url': url_data['url'], 'success': success, 'result': result})
            
            # Overall success if more than 50% succeeded
            success_count = sum(1 for r in results if r['success'])
            success = success_count > len(results) / 2
            result = f"{success_count}/{len(results)} videos downloaded successfully"
            
        elif download_type == 'playlist':
            # Playlist download with progress tracking
            results = []
            total_videos = len(download_data['videos'])
            
            for i, video_data in enumerate(download_data['videos']):
                # Update playlist progress
                playlist_progress_info = {
                    'status': 'downloading',
                    'current_video': i + 1,
                    'total_videos': total_videos,
                    'playlist_progress': ((i / total_videos) * 100),
                    'current_title': video_data['title'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update scheduled download with playlist progress
                scheduled_downloads = get_scheduled_downloads()
                for download in scheduled_downloads:
                    if download.get('id') == download_id:
                        download['progress'] = playlist_progress_info
                        break
                save_scheduled_downloads(scheduled_downloads)
                
                # Download individual video with progress
                def playlist_video_progress(d):
                    # Update individual video progress within playlist
                    playlist_progress_info['video_progress'] = {
                        'status': d['status'],
                        'progress': 0
                    }
                    
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d and d['total_bytes']:
                            playlist_progress_info['video_progress']['progress'] = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                            playlist_progress_info['video_progress']['progress'] = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                        
                        playlist_progress_info['video_progress']['downloaded_mb'] = d['downloaded_bytes'] / (1024 * 1024)
                        playlist_progress_info['video_progress']['speed'] = d.get('speed', 0) or 0
                        playlist_progress_info['video_progress']['eta'] = d.get('eta', 0) or 0
                    
                    # Update the scheduled download
                    scheduled_downloads = get_scheduled_downloads()
                    for download in scheduled_downloads:
                        if download.get('id') == download_id:
                            download['progress'] = playlist_progress_info
                            break
                    save_scheduled_downloads(scheduled_downloads)
                
                success, result = download_video(
                    video_data['url'],
                    download_data['quality'],
                    download_data['audio_choice'],
                    output_path,
                    playlist_video_progress,
                    None,
                    video_data.get('start_time'),
                    video_data.get('end_time')
                )
                results.append({'title': video_data['title'], 'success': success, 'result': result})
            
            # Overall success if more than 50% succeeded
            success_count = sum(1 for r in results if r['success'])
            success = success_count > len(results) / 2
            result = f"{success_count}/{len(results)} videos downloaded successfully"
        
        # Clear progress info and update final status
        scheduled_downloads = get_scheduled_downloads()
        for download in scheduled_downloads:
            if download.get('id') == download_id:
                if 'progress' in download:
                    del download['progress']  # Clear progress info
                break
        save_scheduled_downloads(scheduled_downloads)
        
        if success:
            update_scheduled_download_status(download_id, 'completed', result)
        else:
            update_scheduled_download_status(download_id, 'failed', result)
            
    except Exception as e:
        # Clear progress info on error
        scheduled_downloads = get_scheduled_downloads()
        for download in scheduled_downloads:
            if download.get('id') == download_id:
                if 'progress' in download:
                    del download['progress']
                break
        save_scheduled_downloads(scheduled_downloads)
        update_scheduled_download_status(download_id, 'failed', str(e))

def check_and_run_scheduled_downloads():
    """Check for scheduled downloads that are ready to run"""
    scheduled_downloads = get_scheduled_downloads()
    current_time = datetime.now()
    
    for download in scheduled_downloads:
        if download['status'] == 'scheduled':
            scheduled_time = datetime.fromisoformat(download['scheduled_time'])
            if current_time >= scheduled_time:
                # Run the download in a separate thread
                threading.Thread(
                    target=execute_scheduled_download,
                    args=(download,),
                    daemon=True
                ).start()

def create_calendar_events(scheduled_downloads):
    """Create calendar events from scheduled downloads"""
    events = []
    for download in scheduled_downloads:
        scheduled_time = datetime.fromisoformat(download['scheduled_time'])
        
        # Determine color based on status
        color_map = {
            'scheduled': '#3b82f6',  # Blue
            'downloading': '#f59e0b',  # Orange
            'completed': '#10b981',  # Green
            'failed': '#ef4444'  # Red
        }
        
        status_icon = {
            'scheduled': '📅',
            'downloading': '⬇️',
            'completed': '✅',
            'failed': '❌'
        }
        
        title_prefix = status_icon.get(download['status'], '📅')
        
        event = {
            'title': f"{title_prefix} {download['title'][:30]}{'...' if len(download['title']) > 30 else ''}",
            'start': scheduled_time.strftime('%Y-%m-%d %H:%M'),
            'end': (scheduled_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M'),
            'color': color_map.get(download['status'], '#3b82f6'),
            'id': download['id'],
            'extendedProps': {
                'status': download['status'],
                'type': download['type'],
                'description': f"Type: {download['type'].title()}\nStatus: {download['status'].title()}"
            }
        }
        events.append(event)
    
    return events

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📥 Download", "📋 Batch Download", "📋 Playlist Manager", "⏰ Scheduler", "📊 History", "📁 File Manager"])

with tab1:
    st.markdown("### 📥 Single Video Download")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    
    # Input for YouTube URL
    st.markdown("#### 🔗 YouTube URL")
    url = st.text_input("Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=... or playlist URL", label_visibility="collapsed")
    
    # Quality selection - adjust based on audio choice
    st.markdown("#### 🎯 Quality Settings")
    if audio_choice == "audio_only":
        quality_options = ["Best Quality"]
        quality = st.selectbox("Audio Quality:", quality_options)
    else:
        quality_options = ["Best Quality", "1080p", "720p", "480p", "360p"]
        quality = st.selectbox("Video Quality:", quality_options)
    
    # Time range selection
    st.markdown("#### ⏱️ Download Range")
    download_full_video = st.radio(
        "Choose download option:",
        ["📺 Complete Video", "✂️ Custom Time Range"],
        help="Select whether to download the complete video or a specific time segment"
    )
    
    start_time = "00:00:00"
    end_time = None
    
    if download_full_video == "✂️ Custom Time Range":
        col_start, col_end = st.columns(2)
        
        with col_start:
            start_time = st.text_input(
                "⏮️ Start Time (HH:MM:SS or MM:SS)",
                value="00:00:00",
                placeholder="00:01:30",
                help="Format: HH:MM:SS or MM:SS (e.g., 01:30 or 00:01:30)"
            )
        
        with col_end:
            end_time = st.text_input(
                "⏭️ End Time (HH:MM:SS or MM:SS)",
                placeholder="00:05:00",
                help="Format: HH:MM:SS or MM:SS (e.g., 05:00 or 00:05:00). Leave empty for end of video."
            )
        
        # Show duration calculation if both times are provided
        if start_time and end_time:
            try:
                def parse_time(time_str):
                    parts = time_str.split(':')
                    if len(parts) == 2:  # MM:SS
                        return int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:  # HH:MM:SS
                        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    return 0
                
                start_seconds = parse_time(start_time)
                end_seconds = parse_time(end_time)
                
                if end_seconds > start_seconds:
                    duration_seconds = end_seconds - start_seconds
                    duration_minutes = duration_seconds // 60
                    duration_secs = duration_seconds % 60
                    st.info(f"📊 **Segment Duration:** {duration_minutes}m {duration_secs}s")
                elif end_seconds <= start_seconds:
                    st.warning("⚠️ End time must be after start time")
            except:
                st.warning("⚠️ Please use valid time format (HH:MM:SS or MM:SS)")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if url and st.button("🔍 Get Video Info", use_container_width=True, type="secondary"):
            with st.spinner("🔄 Fetching video information..."):
                if is_playlist_url(url):
                    playlist_info = get_playlist_info(url)
                    if playlist_info:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.success(f"🎵 Playlist detected: **{playlist_info.get('title', 'Unknown Playlist')}**")
                        st.info(f"📊 Contains **{len(playlist_info.get('entries', []))}** videos")
                        
                        # Show first few videos
                        st.markdown("#### 📋 Preview (First 5 videos):")
                        entries = playlist_info.get('entries', [])[:5]
                        for i, entry in enumerate(entries):
                            if entry:
                                st.markdown(f"**{i+1}.** {entry.get('title', 'Unknown')}")
                        if len(playlist_info.get('entries', [])) > 5:
                            st.markdown(f"*... and {len(playlist_info.get('entries', [])) - 5} more videos*")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to retrieve playlist information. Please check the URL and try again.")
                else:
                    video_info = get_video_info(url)
                    if video_info:
                        st.markdown('<div class="info-card">', unsafe_allow_html=True)
                        st.success("✅ Video information retrieved successfully")
                        
                        # Video title
                        st.markdown(f"### 🎬 {video_info.get('title', 'Unknown Title')}")
                    else:
                        st.error("❌ Failed to retrieve video information. Please check the URL and try again.")
                        
                        # Create three columns for video info layout
                        info_col1, info_col2, info_col3 = st.columns([1, 1, 1])
                        
                        with info_col1:
                            # Display video thumbnail
                            if 'thumbnail' in video_info:
                                st.image(video_info['thumbnail'], caption="Video Thumbnail", width=300)
                            
                            # Duration and Views
                            duration = video_info.get('duration')
                            if duration:
                                minutes, seconds = divmod(duration, 60)
                                hours, minutes = divmod(minutes, 60)
                                if hours > 0:
                                    st.metric("⏱️ Duration", f"{hours}h {minutes}m {seconds}s")
                                else:
                                    st.metric("⏱️ Duration", f"{minutes}m {seconds}s")
                        
                        with info_col2:
                            # Views and Uploader
                            if 'view_count' in video_info:
                                st.metric("👁️ Views", f"{video_info['view_count']:,}")
                            
                            if 'uploader' in video_info:
                                st.metric("👤 Uploader", video_info['uploader'])
                        
                        with info_col3:
                            # Upload date and additional info
                            if 'upload_date' in video_info:
                                upload_date = video_info['upload_date']
                                formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                                st.metric("📅 Upload Date", formatted_date)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if url and st.button("⬇️ Download", use_container_width=True, type="primary"):
            # Reset controller for fresh download
            if 'single_controller' not in st.session_state:
                st.session_state.single_controller = DownloadController()
            else:
                st.session_state.single_controller.reset()
            
            # Store time range settings in session state
            if download_full_video == "✂️ Custom Time Range":
                st.session_state.download_state['start_time'] = start_time if start_time else None
                st.session_state.download_state['end_time'] = end_time if end_time else None
            else:
                st.session_state.download_state['start_time'] = None
                st.session_state.download_state['end_time'] = None
            
            # Immediately set downloading state to show UI
            st.session_state.download_state['is_downloading'] = True
            st.session_state.download_state['is_paused'] = False
            st.session_state.download_state['should_stop'] = False
            st.session_state.download_state['last_progress'] = 0
            st.session_state.download_state['last_status'] = ''
            st.rerun()  # Refresh to show the control UI immediately

# Show download progress UI when download is active or has been started
if st.session_state.download_state['is_downloading']:
    download_path = os.path.join(os.getcwd(), "downloads")
    
    # Create subfolder if option is enabled
    if create_subfolder:
        date_folder = datetime.now().strftime("%Y-%m-%d")
        download_path = os.path.join(download_path, date_folder)

    if is_playlist_url(url):
        # Enhanced playlist download with progress tracking
        st.markdown("### 🔄 Playlist Download Progress")
        
        # Create progress container
        playlist_progress_container = st.container()
        
        max_downloads = max_playlist_downloads if max_playlist_downloads > 0 else None
        # Get time range from session state for playlist downloads
        playlist_start_time = st.session_state.download_state.get('start_time')
        playlist_end_time = st.session_state.download_state.get('end_time')
        success, results = download_playlist(url, quality, audio_choice, max_downloads, playlist_progress_container, playlist_start_time, playlist_end_time)
        
        if success:
            # Celebration and prominent success message
            st.balloons()
            st.success("🎉 **PLAYLIST DOWNLOAD COMPLETED! ✅**")
            st.info("📋 **All playlist downloads have been stopped automatically.**")
            
            # Summary statistics
            successful_downloads = sum(1 for r in results if r['success'])
            failed_downloads = len(results) - successful_downloads
            
            # Create summary box
            with st.container():
                st.markdown("### 📊 Playlist Download Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("✅ Successful", successful_downloads)
                with col2:
                    st.metric("❌ Failed", failed_downloads)
                with col3:
                    st.metric("📁 Total Videos", len(results))
            
            # Show completion time
            current_time = datetime.now().strftime("%H:%M:%S")
            st.success(f"**⏰ Playlist completed at:** {current_time}")
            
            # Show file location
            st.info(f"**📂 Videos saved to:** `{download_path}`")
            
            # Show detailed results in a modern format
            st.markdown("#### 📋 Detailed Results:")
            success_results = [r for r in results if r['success']]
            failed_results = [r for r in results if not r['success']]
            
            if success_results:
                with st.expander(f"✅ Successful Downloads ({len(success_results)})", expanded=True):
                    for i, result in enumerate(success_results, 1):
                        st.success(f"**{i}.** {result['title']}")
            
            if failed_results:
                with st.expander(f"❌ Failed Downloads ({len(failed_results)})", expanded=False):
                    for i, result in enumerate(failed_results, 1):
                        st.error(f"**{i}.** {result['title']}")
            
            # Option to download another playlist
            if st.button("📥 Download Another Playlist", use_container_width=True, type="secondary"):
                st.session_state.download_state['is_downloading'] = False
                st.rerun()
        else:
            st.error("❌ **Playlist Download Failed**")
            st.info("💡 **Tip:** Check the playlist URL and try again")
            
            # Option to try again
            if st.button("🔄 Try Again", use_container_width=True, type="secondary"):
                st.session_state.download_state['is_downloading'] = False
                st.rerun()
    else:
        # Modern progress display with real-time updates and controls
        st.markdown("### 🔄 Download Progress")
        
        # Control buttons - Show immediately when download starts
        control_col1, control_col2, control_col3 = st.columns(3)
        
        # Initialize controller if not exists
        if 'single_controller' not in st.session_state:
            st.session_state.single_controller = DownloadController()
        
        controller = st.session_state.single_controller
        
        with control_col1:
            if st.session_state.download_state['is_paused']:
                if st.button("▶️ Resume", use_container_width=True, type="secondary"):
                    controller.resume()
                    st.session_state.download_state['is_paused'] = False
                    st.rerun()
            else:
                if st.button("⏸️ Pause", use_container_width=True, type="secondary"):
                    controller.pause()
                    st.session_state.download_state['is_paused'] = True
                    st.rerun()
        
        with control_col2:
            if st.button("⏹️ Stop", use_container_width=True, type="secondary"):
                controller.stop()
                st.session_state.download_state['is_downloading'] = False
                st.session_state.download_state['is_paused'] = False
                st.session_state.download_state['should_stop'] = True
                st.warning("🛑 Download stopped by user")
                st.rerun()
          # Progress container - Show immediately
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            speed_text = st.empty()
            eta_text = st.empty()
            
            # Show initial status
            status_text.markdown("**🔄 Preparing download...**")
            
            # Progress tracking function
            def update_progress(d):
                # Thread-safe: only update controller data, not Streamlit components
                if d['status'] == 'downloading':
                    current_time = time.time()
                    downloaded_bytes = d.get('downloaded_bytes', 0)
                    
                    # Update controller progress data (thread-safe)
                    controller.progress_data['status'] = 'downloading'
                    controller.progress_data['downloaded_mb'] = downloaded_bytes / (1024 * 1024)
                    
                    # Calculate progress percentage
                    if 'total_bytes' in d and d['total_bytes']:
                        total_bytes = d['total_bytes']
                        progress = (downloaded_bytes / total_bytes) * 100
                        controller.progress_data['progress'] = progress
                        controller.progress_data['total_mb'] = total_bytes / (1024 * 1024)
                        
                        # Calculate download speed more frequently for smoother updates
                        if current_time - controller.progress_data['last_update_time'] > 0.3:  # Update every 0.3 seconds
                            time_diff = current_time - controller.progress_data['last_update_time']
                            bytes_diff = downloaded_bytes - controller.progress_data['last_downloaded_bytes']
                            speed_bytes_per_sec = bytes_diff / time_diff
                            speed_mb_per_sec = speed_bytes_per_sec / (1024 * 1024)
                            
                            if speed_bytes_per_sec > 0:
                                eta_seconds = (total_bytes - downloaded_bytes) / speed_bytes_per_sec
                                controller.progress_data['speed_mb_per_sec'] = speed_mb_per_sec
                                controller.progress_data['eta_minutes'] = int(eta_seconds // 60)
                                controller.progress_data['eta_seconds'] = int(eta_seconds % 60)
                            
                            controller.progress_data['last_update_time'] = current_time
                            controller.progress_data['last_downloaded_bytes'] = downloaded_bytes
                            
                    elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                        total_bytes = d['total_bytes_estimate']
                        progress = (downloaded_bytes / total_bytes) * 100
                        controller.progress_data['progress'] = progress
                        controller.progress_data['total_mb'] = total_bytes / (1024 * 1024)
                        
                elif d['status'] == 'finished':
                    controller.progress_data['status'] = 'finished'
                    controller.progress_data['progress'] = 100
            
            # Start download logic only if not already started AND not finished
            if (not hasattr(controller, 'download_thread') or not controller.download_thread or not controller.download_thread.is_alive()) and not controller.is_finished:
                controller.reset()
                
                # Get time range from session state BEFORE starting the thread
                download_start_time = st.session_state.download_state.get('start_time')
                download_end_time = st.session_state.download_state.get('end_time')
                
                def download_thread():
                    try:
                        # Use the pre-captured time range values (no session state access in thread)
                        success, filename = download_video(url, quality, audio_choice, download_path, update_progress, controller, download_start_time, download_end_time)
                        controller.download_result = (success, filename)
                    except Exception as e:
                        controller.download_result = (False, str(e))
                    finally:
                        controller.is_finished = True
                
                # Start download in thread
                controller.download_thread = threading.Thread(target=download_thread)
                controller.download_thread.start()
            
            # Dynamic progress updates
            if controller.download_thread and controller.download_thread.is_alive():
                progress_info = controller.progress_data
                
                # Check if paused
                if st.session_state.download_state['is_paused']:
                    status_text.markdown("**⏸️ Download paused - Click Resume to continue**")
                elif progress_info.get('status') == 'downloading':
                    # Always update progress bar for dynamic display
                    current_progress = max(0, min(100, int(progress_info.get('progress', 0))))
                    progress_bar.progress(current_progress)
                    
                    # Update status text
                    if progress_info.get('total_mb', 0) > 0:
                        status_msg = f"**🔄 Downloading: {progress_info['progress']:.1f}% ({progress_info['downloaded_mb']:.1f} MB / {progress_info['total_mb']:.1f} MB)**"
                    else:
                        status_msg = f"**🔄 Downloading: {progress_info['downloaded_mb']:.1f} MB downloaded**"
                    
                    status_text.markdown(status_msg)
                    
                    # Show speed and ETA if available
                    if progress_info.get('speed_mb_per_sec', 0) > 0:
                        speed_text.markdown(f"**⚡ Speed: {progress_info['speed_mb_per_sec']:.2f} MB/s**")
                        eta_text.markdown(f"**⏱️ ETA: {progress_info['eta_minutes']}m {progress_info['eta_seconds']}s**")
                    
                    # Update session state to track changes
                    st.session_state.download_state['last_progress'] = current_progress
                    st.session_state.download_state['last_status'] = status_msg
                    
                elif progress_info.get('status') == 'finished':
                    progress_bar.progress(100)
                    status_text.markdown("**✅ Download completed!**")
                    speed_text.empty()
                    eta_text.empty()
                else:
                    # Still preparing
                    status_text.markdown("**🔄 Starting download...**")
                
            # Check if download is complete FIRST - only if we have a valid result
            if controller.is_finished and controller.download_result and controller.download_result != (None, None):
                success, result = controller.download_result
                # STOP DOWNLOAD PROCESS COMPLETELY
                st.session_state.download_state['is_downloading'] = False
                st.session_state.download_state['is_paused'] = False
                st.session_state.download_state['should_stop'] = False
                # Clear the progress display
                progress_bar.progress(100)
                speed_text.empty()
                eta_text.empty()
                if success:
                    # CLEAR STATUS AND SHOW COMPLETION MESSAGE
                    status_text.markdown("**✅ DOWNLOAD COMPLETED - PROCESS STOPPED**")
                    st.balloons()
                    st.success("🎉 **DOWNLOAD COMPLETED SUCCESSFULLY! ✅**")
                    st.info("📋 **Download process has been stopped automatically.**")
                    with st.container():
                        st.markdown("### 📁 Download Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**📂 Saved to:** `{download_path}`")
                            if os.path.exists(result):
                                file_size = os.path.getsize(result) / (1024 * 1024)  # Size in MB
                                st.info(f"**📏 File size:** {file_size:.1f} MB")
                        with col2:
                            st.info(f"**🎯 Quality:** {quality}")
                            st.info(f"**🎵 Audio:** {audio_options[audio_choice]}")
                            
                            # Show time range info if applicable
                            download_start_time = st.session_state.download_state.get('start_time')
                            download_end_time = st.session_state.download_state.get('end_time')
                            if download_start_time or download_end_time:
                                if download_start_time and download_end_time:
                                    st.info(f"**⏱️ Time Range:** {download_start_time} - {download_end_time}")
                                elif download_start_time:
                                    st.info(f"**⏱️ Start Time:** {download_start_time}")
                                elif download_end_time:
                                    st.info(f"**⏱️ End Time:** {download_end_time}")
                            else:
                                st.info(f"**⏱️ Range:** Complete Video")
                    current_time = datetime.now().strftime("%H:%M:%S")
                    st.success(f"**⏰ Completed at:** {current_time}")
                    if st.button("📥 Download Another Video", use_container_width=True, type="secondary"):
                        # Completely reset everything for a new download
                        st.session_state.download_state['is_downloading'] = False
                        st.session_state.download_state['is_paused'] = False
                        st.session_state.download_state['should_stop'] = False
                        st.session_state.download_state['last_progress'] = 0
                        st.session_state.download_state['last_status'] = ''
                        
                        # Reset controller completely
                        controller.reset()
                        # Force a clean state by recreating the controller
                        st.session_state.single_controller = DownloadController()
                        
                        # Show reset confirmation
                        st.info("🔄 **Ready for new download!**")
                        time.sleep(1)  # Brief pause to show the message
                        st.rerun()
                else:
                    progress_bar.progress(0)
                    speed_text.empty()
                    eta_text.empty()
                    # STOP THE AUTO-REFRESH LOOP - DOWNLOAD FAILED
                    st.session_state.download_state['is_downloading'] = False
                    st.session_state.download_state['is_paused'] = False
                    st.session_state.download_state['should_stop'] = False
                    if 'result' in locals() and "stopped by user" in str(result):
                        status_text.markdown("**🛑 DOWNLOAD STOPPED - PROCESS ENDED**")
                        st.warning("🛑 **Download was stopped by user**")
                        st.info("📋 **Download process has been stopped completely.**")
                    else:
                        status_text.markdown("**❌ DOWNLOAD FAILED - PROCESS STOPPED**")
                # COMPLETELY STOP HERE - NO MORE PROCESSING OR REFRESH
            elif controller.download_thread and controller.download_thread.is_alive():
                # Only continue with progress updates if download is still active and not finished
                progress_info = controller.progress_data
                
                # Check if paused
                if st.session_state.download_state['is_paused']:
                    status_text.markdown("**⏸️ Download paused - Click Resume to continue**")
                elif progress_info.get('status') == 'downloading':
                    # Always update progress bar for dynamic display
                    current_progress = max(0, min(100, int(progress_info.get('progress', 0))))
                    progress_bar.progress(current_progress)
                    
                    # Update status text
                    if progress_info.get('total_mb', 0) > 0:
                        status_msg = f"**🔄 Downloading: {progress_info['progress']:.1f}% ({progress_info['downloaded_mb']:.1f} MB / {progress_info['total_mb']:.1f} MB)**"
                    else:
                        status_msg = f"**🔄 Downloading: {progress_info['downloaded_mb']:.1f} MB downloaded**"
                    
                    status_text.markdown(status_msg)
                    
                    # Show speed and ETA if available
                    if progress_info.get('speed_mb_per_sec', 0) > 0:
                        speed_text.markdown(f"**⚡ Speed: {progress_info['speed_mb_per_sec']:.2f} MB/s**")
                        eta_text.markdown(f"**⏱️ ETA: {progress_info['eta_minutes']}m {progress_info['eta_seconds']}s**")
                    
                    # Update session state to track changes
                    st.session_state.download_state['last_progress'] = current_progress
                    st.session_state.download_state['last_status'] = status_msg
                    
                elif progress_info.get('status') == 'finished':
                    progress_bar.progress(100)
                    status_text.markdown("**✅ Download completed!**")
                    speed_text.empty()
                    eta_text.empty()
                else:
                    # Still preparing
                    status_text.markdown("**🔄 Starting download...**")
                
                # Only refresh if download is still active and not finished
                if not controller.is_finished:
                    time.sleep(0.2)  # Very responsive updates
                    st.rerun()
            elif not controller.is_finished and not controller.download_thread:
                # Starting up - only show if not finished AND thread hasn't started yet
                status_text.markdown("**🔄 Initializing download...**")
                time.sleep(0.3)
                st.rerun()

with tab2:
    st.markdown("### 📋 Batch Download")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("Download multiple videos at once by entering URLs (one per line)")
    
    batch_urls = st.text_area("🔗 Enter YouTube URLs (one per line):", height=150, 
                              placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...\n...")
    
    # Time range selection for batch download
    st.markdown("#### ⏱️ Batch Download Range")
    batch_download_full_video = st.radio(
        "Choose download option for all videos:",
        ["📺 Complete Videos", "✂️ Same Time Range for All", "✂️ Custom Range per Video"],
        help="Apply the same or custom time range to all videos in the batch",
        key="batch_time_range"
    )
    
    batch_start_time = "00:00:00"
    batch_end_time = None
    
    if batch_download_full_video == "✂️ Same Time Range for All":
        pass  # No action needed, defaults will be used
    # For custom range per video, build a list of time ranges
    per_video_time_ranges = []
    if batch_download_full_video == "✂️ Custom Range per Video" and batch_urls:
        urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
        st.markdown('#### ⏱️ Set Custom Time Range for Each Video')
        for idx, url in enumerate(urls):
            with st.expander(f"Video {idx+1}: {url[:60]}{'...' if len(url) > 60 else ''}"):
                col_start, col_end = st.columns(2)
                with col_start:
                    start = st.text_input(f"Start Time (HH:MM:SS or MM:SS) for Video {idx+1}", value="00:00:00", key=f"custom_start_{idx}")
                with col_end:
                    end = st.text_input(f"End Time (HH:MM:SS or MM:SS) for Video {idx+1}", value="", key=f"custom_end_{idx}")
                per_video_time_ranges.append({'start': start, 'end': end})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if batch_urls:
        urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
        
        # Show URL count
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 URLs Found", len(urls))
        with col2:
            st.metric("🎯 Selected Quality", quality)
        with col3:
            st.metric("🎵 Audio Mode", audio_options[audio_choice])
        
        if st.button("📥 Download All", use_container_width=True, type="primary") and not st.session_state.download_state['batch_state']['is_downloading']:
            # Store batch information in session state
            st.session_state.download_state['batch_state']['urls'] = urls
            st.session_state.download_state['batch_state']['current_index'] = 0
            st.session_state.download_state['batch_state']['results'] = []
            st.session_state.download_state['batch_state']['is_downloading'] = True
            st.session_state.download_state['batch_state']['is_paused'] = False
            st.session_state.download_state['batch_state']['should_stop'] = False
            # Store time range settings for batch download
            if batch_download_full_video == "✂️ Same Time Range for All":
                st.session_state.download_state['batch_state']['start_time'] = batch_start_time if batch_start_time else None
                st.session_state.download_state['batch_state']['end_time'] = batch_end_time if batch_end_time else None
                st.session_state.download_state['batch_state']['per_video_time_ranges'] = None
            elif batch_download_full_video == "✂️ Custom Range per Video":
                st.session_state.download_state['batch_state']['start_time'] = None
                st.session_state.download_state['batch_state']['end_time'] = None
                st.session_state.download_state['batch_state']['per_video_time_ranges'] = per_video_time_ranges
            else:
                st.session_state.download_state['batch_state']['start_time'] = None
                st.session_state.download_state['batch_state']['end_time'] = None
                st.session_state.download_state['batch_state']['per_video_time_ranges'] = None
            # Initialize batch controller
            if 'batch_controller' not in st.session_state:
                st.session_state.batch_controller = DownloadController()
            st.rerun()
        
        # Batch download in progress
        if st.session_state.download_state['batch_state']['is_downloading']:
            download_path = os.path.join(os.getcwd(), "downloads")
            if create_subfolder:
                date_folder = datetime.now().strftime("%Y-%m-%d")
                download_path = os.path.join(download_path, date_folder)
            
            # Batch control buttons

            st.markdown("### 🔄 Batch Download Progress")
            batch_control_col1, batch_control_col2, batch_control_col3 = st.columns(3)
            
            batch_controller = st.session_state.batch_controller
            batch_state = st.session_state.download_state['batch_state']
            
            with batch_control_col1:
                if batch_state['is_paused']:
                    if st.button("▶️ Resume Batch", use_container_width=True, type="secondary"):
                        batch_controller.resume()
                        batch_state['is_paused'] = False
                        st.rerun()
                else:
                    if st.button("⏸️ Pause Batch", use_container_width=True, type="secondary"):
                        batch_controller.pause()
                        batch_state['is_paused'] = True
                        st.rerun()
            
            with batch_control_col2:
                if st.button("⏹️ Stop Batch", use_container_width=True, type="secondary"):
                    batch_controller.stop()
                    batch_state['is_downloading'] = False
                    batch_state['is_paused'] = False
                    batch_state['should_stop'] = True
                    st.warning("🛑 Batch download stopped by user")
                    st.rerun()
            
            with batch_control_col3:
                if st.button("⏭️ Skip Current", use_container_width=True, type="secondary"):
                    batch_controller.stop()  # Stop current download
                    # Will automatically move to next video
                    st.info("⏭️ Skipping current video...")
            
            st.markdown('<div class="progress-section">', unsafe_allow_html=True)
            
            # Overall batch progress
            overall_progress_container = st.container()
            with overall_progress_container:
                st.markdown("#### 📊 Overall Progress")
                
                current_index = batch_state['current_index']
                total_urls = len(batch_state['urls'])
                overall_progress = st.progress(current_index / total_urls if total_urls > 0 else 0)
                overall_status = st.empty()
                batch_stats = st.empty()
                
                overall_status.markdown(f"**Processing video {current_index + 1}/{total_urls}**")
                
                if batch_state['is_paused']:
                    batch_stats.markdown("**⏸️ Batch download paused - Click Resume to continue**")
                elif batch_state['should_stop']:
                    batch_stats.markdown("**🛑 Batch download stopped**")
                else:
                    success_count = sum(1 for r in batch_state['results'] if r['success'])
                    failed_count = len(batch_state['results']) - success_count
                    batch_stats.markdown(f"**✅ Completed: {success_count} | ❌ Failed: {failed_count} | 📊 Remaining: {total_urls - current_index}**")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Individual video progress
            st.markdown('<div class="progress-section">', unsafe_allow_html=True)
            current_video_container = st.container()
            
            if current_index < total_urls and not batch_state['should_stop']:
                current_url = batch_state['urls'][current_index]
                
                with current_video_container:
                    st.markdown(f"#### 🎬 Currently downloading: Video {current_index + 1}")
                    st.markdown(f"**URL:** `{current_url[:80]}...`" if len(current_url) > 80 else f"**URL:** `{current_url}`")
                    
                    # Individual video progress elements
                    video_progress = st.progress(0)
                    video_status = st.empty()
                    video_speed = st.empty()
                    video_eta = st.empty()
                    
                    # Initialize batch progress if not exists
                    if 'batch_progress' not in st.session_state:
                        st.session_state.batch_progress = BatchProgress()
                    
                    batch_progress = st.session_state.batch_progress
                    batch_progress.update_video_count(total_urls)
                    batch_progress.next_video()
                    
                    # Progress tracking with real-time UI updates
                    def update_batch_progress(d):
                        if batch_state['is_paused']:
                            return
                        
                        # Update the batch progress tracker
                        batch_progress.progress_hook(d)
                        
                        # Update UI elements in real-time
                        if d['status'] == 'downloading':
                            # Update progress bar
                            video_progress.progress(batch_progress.current_progress / 100)
                            
                            # Update status with download info
                            video_status.markdown(f"**🔄 {batch_progress.current_progress:.1f}% - {batch_progress.current_status}**")
                            
                            # Update speed and ETA
                            if batch_progress.current_speed > 0:
                                speed_mb = batch_progress.current_speed / (1024 * 1024)
                                video_speed.markdown(f"**⚡ Speed:** {speed_mb:.1f} MB/s")
                            
                            if batch_progress.current_eta > 0:
                                eta_minutes = int(batch_progress.current_eta // 60)
                                eta_seconds = int(batch_progress.current_eta % 60)
                                video_eta.markdown(f"**⏱️ ETA:** {eta_minutes}m {eta_seconds}s")
                        
                        elif d['status'] == 'finished':
                            video_progress.progress(1.0)
                            video_status.markdown("**✅ Download completed!**")
                            video_speed.empty()
                            video_eta.empty()
                
                # Get time range for this video
                batch_start_time = batch_state.get('start_time')
                batch_end_time = batch_state.get('end_time')
                per_video_time_ranges = batch_state.get('per_video_time_ranges')
                this_start = batch_start_time
                this_end = batch_end_time
                if per_video_time_ranges and current_index < len(per_video_time_ranges):
                    this_start = per_video_time_ranges[current_index].get('start')
                    this_end = per_video_time_ranges[current_index].get('end')
                
                # Download current video with real-time progress
                try:
                    # Show starting status
                    video_status.markdown("**🚀 Starting download...**")
                    
                    # Process download with progress updates
                    if not batch_state['is_paused'] and not batch_state['should_stop']:
                        success, result = download_video(
                            current_url, 
                            quality, 
                            audio_choice, 
                            download_path, 
                            update_batch_progress, 
                            batch_controller, 
                            this_start, 
                            this_end
                        )
                        
                        # Update UI with final status
                        if success:
                            video_progress.progress(1.0)
                            video_status.markdown("**✅ Video download completed!**")
                            batch_progress.video_completed(True)
                        else:
                            video_status.markdown(f"**❌ Video download failed: {result}**")
                            batch_progress.video_completed(False)
                        
                        video_speed.empty()
                        video_eta.empty()
                        
                        # Store result
                        batch_state['results'].append({
                            'success': success,
                            'filename': result if success else None,
                            'url': current_url,
                            'error': result if not success else None
                        })
                        
                        # Move to next video
                        batch_state['current_index'] += 1
                        
                        # Update overall progress
                        overall_progress.progress(batch_state['current_index'] / total_urls)
                        overall_status.markdown(f"**Processing video {batch_state['current_index'] + 1}/{total_urls}**")
                        
                        # Update batch statistics
                        success_count = sum(1 for r in batch_state['results'] if r['success'])
                        failed_count = len(batch_state['results']) - success_count
                        batch_stats.markdown(f"**✅ Completed: {success_count} | ❌ Failed: {failed_count} | 📊 Remaining: {total_urls - batch_state['current_index']}**")
                        
                        # Brief pause before next video
                        time.sleep(1)
                        st.rerun()
                        
                except Exception as e:
                    video_status.markdown(f"**❌ Error: {str(e)}**")
                    batch_state['results'].append({
                        'success': False,
                        'filename': None,
                        'url': current_url,
                        'error': str(e)
                    })
                    batch_state['current_index'] += 1
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Results container
            results_container = st.container()
            
            # Show results for completed downloads
            if batch_state['results']:
                with results_container:
                    st.markdown("#### 📊 Download Results")
                    for i, result in enumerate(batch_state['results'], 1):
                        if result['success']:
                            st.success(f"✅ **Video {i}** successfully downloaded")
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            if "stopped by user" in str(error_msg):
                                st.info(f"⏭️ **Video {i}** skipped by user")
                            else:
                                st.error(f"❌ **Video {i}** failed to download: {error_msg}")
            
            # Check if batch is complete
            if batch_state['current_index'] >= len(batch_state['urls']) or batch_state['should_stop']:
                # Final statistics
                success_count = sum(1 for r in batch_state['results'] if r.get('success', False))
                total_count = len(batch_state['urls'])
                failed_count = batch_state['current_index'] - success_count if batch_state['should_stop'] else total_count - success_count
                
                overall_progress.progress(1.0)
                overall_status.markdown("**✅ BATCH DOWNLOAD COMPLETED - PROCESS STOPPED**")
                
                # Enhanced completion message
                st.balloons()
                
                if batch_state['should_stop']:
                    st.warning("🛑 **Batch Download Stopped by User**")
                    st.info("📋 **Batch download process has been stopped.**")
                    batch_stats.markdown(f"**🛑 Stopped after {batch_state['current_index']} videos**")
                else:
                    st.success("🎉 **BATCH DOWNLOAD COMPLETED! ✅**")
                    st.info("📋 **All batch downloads have been stopped automatically.**")
                    batch_stats.markdown(f"**🏁 All {total_count} videos processed**")
                
                # Create completion summary
                with st.container():
                    st.markdown("### 📊 Batch Download Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("✅ Successful", success_count)
                    with col2:
                        st.metric("❌ Failed", failed_count)
                    with col3:
                        st.metric("📁 Total Processed", batch_state['current_index'])
                    with col4:
                        success_rate = (success_count / batch_state['current_index']) * 100 if batch_state['current_index'] > 0 else 0
                        st.metric("📈 Success Rate", f"{success_rate:.1f}%")
                
                # Show completion time and location
                current_time = datetime.now().strftime("%H:%M:%S")
                st.success(f"**⏰ Batch completed at:** {current_time}")
                st.info(f"**📂 Videos saved to:** `{download_path}`")
                
                # Show final results based on success rate
                if success_count == total_count and not batch_state['should_stop']:
                    st.success(f"🎉 **Perfect! All {total_count} videos downloaded successfully!**")
                elif success_count > 0:
                    st.warning(f"⚠️ **Partial Success:** {success_count}/{batch_state['current_index']} videos downloaded")
                    st.info("💡 **Tip:** Failed videos might work with different quality settings")
                else:
                    st.error("❌ **No videos were downloaded successfully**")
                    st.info("💡 **Tip:** Check URLs and try different quality settings")
                
                # Option to start a new batch
                if st.button("📥 Start New Batch Download", use_container_width=True, type="secondary"):
                    batch_state['is_downloading'] = False
                    batch_state['current_index'] = 0
                    batch_state['urls'] = []
                    batch_state['results'] = []
                    batch_controller.reset()
                    st.rerun()
                
                # Reset batch state
                batch_state['is_downloading'] = False
                batch_controller.reset()
    else:
        st.info("💡 Enter YouTube URLs above to start batch downloading")

with tab3:
    st.markdown("### � Playlist Manager")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("📋 **Advanced Playlist Downloads** - Select specific videos and set custom time ranges for each")
    
    # Playlist URL input
    st.markdown("#### 🔗 Playlist URL")
    playlist_url = st.text_input("Enter YouTube Playlist URL", placeholder="https://www.youtube.com/playlist?list=...", label_visibility="collapsed", key="playlist_url_input")
    
    # Initialize playlist session state
    if 'playlist_manager' not in st.session_state:
        st.session_state.playlist_manager = {
            'playlist_info': None,
            'selected_videos': {},
            'video_time_ranges': {},
            'is_downloading': False,
            'download_progress': {}
        }
    
    if playlist_url and st.button("🔍 Load Playlist", use_container_width=True, type="secondary"):
        with st.spinner("🔄 Loading playlist information..."):
            playlist_info = get_playlist_info(playlist_url)
            if playlist_info:
                st.session_state.playlist_manager['playlist_info'] = playlist_info
                st.session_state.playlist_manager['selected_videos'] = {}
                st.session_state.playlist_manager['video_time_ranges'] = {}
                st.success(f"✅ Loaded playlist: **{playlist_info.get('title', 'Unknown Playlist')}**")
                st.rerun()
            else:
                st.error("❌ Failed to load playlist. Please check the URL and try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display playlist contents if loaded
    if st.session_state.playlist_manager['playlist_info']:
        playlist_info = st.session_state.playlist_manager['playlist_info']
        entries = playlist_info.get('entries', [])

        # Selection controls
        st.markdown("#### 🎛️ Selection Controls")
        selection_col1, selection_col2, selection_col3 = st.columns(3)

        with selection_col1:
            if st.button("✅ Select All", use_container_width=True, type="secondary"):
                for i, entry in enumerate(entries):
                    if entry:
                        st.session_state.playlist_manager['selected_videos'][i] = True
                st.rerun()

        with selection_col2:
            if st.button("❌ Deselect All", use_container_width=True, type="secondary"):
                st.session_state.playlist_manager['selected_videos'] = {}
                st.rerun()

        with selection_col3:
            if st.button("🔄 Reset Time Ranges", use_container_width=True, type="secondary"):
                st.session_state.playlist_manager['video_time_ranges'] = {}
                st.rerun()

        # Video list with selection and time range options
        st.markdown("#### 🎬 Video Selection & Time Ranges")

        # Show videos in batches to avoid overwhelming the UI
        videos_per_page = 10
        total_pages = (len(entries) + videos_per_page - 1) // videos_per_page

        if total_pages > 1:
            page = st.selectbox("📄 Page", range(1, total_pages + 1), key="playlist_page") - 1
        else:
            page = 0

        start_idx = page * videos_per_page
        end_idx = min(start_idx + videos_per_page, len(entries))

        for i in range(start_idx, end_idx):
            entry = entries[i]
            if entry:
                video_id = entry.get('id', f'video_{i}')
                video_title = entry.get('title', 'Unknown Title')
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                duration = entry.get('duration')

                with st.expander(f"🎬 {i+1}. {video_title}" + (f" ({duration//60}:{duration%60:02d})" if duration else ""), expanded=False):
                    video_col1, video_col2 = st.columns([2, 3])

                    with video_col1:
                        # Video selection checkbox
                        is_selected = st.checkbox(
                            "✅ Select this video",
                            value=st.session_state.playlist_manager['selected_videos'].get(i, False),
                            key=f"select_video_{i}"
                        )

                        # Update session state and clean up dictionary
                        if is_selected:
                            st.session_state.playlist_manager['selected_videos'][i] = True
                        else:
                            # Remove from dictionary when deselected to keep it clean
                            if i in st.session_state.playlist_manager['selected_videos']:
                                del st.session_state.playlist_manager['selected_videos'][i]

                        if is_selected:
                            st.success("🎯 Selected for download")
                        else:
                            st.info("⏹️ Not selected")

                        # Show video info
                        st.markdown(f"**🔗 URL:** [{video_url[:40]}...]({video_url})")
                        if duration:
                            st.markdown(f"**⏱️ Duration:** {duration//60}:{duration%60:02d}")

                    with video_col2:
                        if is_selected:
                            # Time range options for selected videos
                            st.markdown("**⏱️ Download Options**")

                            time_option = st.radio(
                                "Choose download option:",
                                ["📺 Complete Video", "✂️ Custom Time Range"],
                                key=f"time_option_{i}",
                                help=f"Select whether to download the complete video or a specific segment for video {i+1}"
                            )

                            if time_option == "✂️ Custom Time Range":
                                time_col1, time_col2 = st.columns(2)

                                with time_col1:
                                    start_time = st.text_input(
                                        "⏮️ Start Time",
                                        value="00:00:00",
                                        placeholder="00:01:30",
                                        help="Format: HH:MM:SS or MM:SS",
                                        key=f"start_time_{i}"
                                    )

                                with time_col2:
                                    end_time = st.text_input(
                                        "⏭️ End Time",
                                        placeholder="00:05:00",
                                        help="Format: HH:MM:SS or MM:SS. Leave empty for end of video.",
                                        key=f"end_time_{i}"
                                    )

                                # Store time range in session state
                                st.session_state.playlist_manager['video_time_ranges'][i] = {
                                    'start': start_time if start_time != "00:00:00" else None,
                                    'end': end_time if end_time else None
                                }

                                # Show duration calculation
                                if start_time and end_time:
                                    try:
                                        def parse_time(time_str):
                                            parts = time_str.split(':')
                                            if len(parts) == 2:  # MM:SS
                                                return int(parts[0]) * 60 + int(parts[1])
                                            elif len(parts) == 3:  # HH:MM:SS
                                                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                                            return 0

                                        start_seconds = parse_time(start_time)
                                        end_seconds = parse_time(end_time)

                                        if end_seconds > start_seconds:
                                            duration_seconds = end_seconds - start_seconds
                                            duration_minutes = duration_seconds // 60
                                            duration_secs = duration_seconds % 60
                                            st.info(f"📊 **Segment Duration:** {duration_minutes}m {duration_secs}s")
                                        else:
                                            st.warning("⚠️ End time must be after start time")
                                    except:
                                        st.warning("⚠️ Please use valid time format (HH:MM:SS or MM:SS)")
                            else:
                                # Remove time range if complete video is selected
                                if i in st.session_state.playlist_manager['video_time_ranges']:
                                    del st.session_state.playlist_manager['video_time_ranges'][i]
                        else:
                            st.info("⏹️ Select this video to configure download options")

        # Playlist overview (moved here to reflect latest state)
        st.markdown("#### 📊 Playlist Overview")
        overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

        with overview_col1:
            st.metric("🎬 Total Videos", len(entries))
        with overview_col2:
            selected_count = len([v for v in st.session_state.playlist_manager['selected_videos'].values() if v])
            st.metric("✅ Selected", selected_count)
        with overview_col3:
            st.metric("🎯 Quality", quality)
        with overview_col4:
            st.metric("🎵 Audio Mode", audio_options[audio_choice])

        # Show pagination info
        if total_pages > 1:
            st.info(f"📄 Showing videos {start_idx + 1}-{end_idx} of {len(entries)} (Page {page + 1} of {total_pages})")
        
        # Download controls
        selected_videos = [i for i, selected in st.session_state.playlist_manager['selected_videos'].items() if selected]
        
        if selected_videos:
            st.markdown("---")
            st.markdown("#### 🚀 Download Selected Videos")
            
            download_col1, download_col2 = st.columns(2)
            
            with download_col1:
                st.success(f"✅ **{len(selected_videos)} videos selected** for download")
                
                # Show summary of time ranges
                segment_count = len([i for i in selected_videos if i in st.session_state.playlist_manager['video_time_ranges']])
                if segment_count > 0:
                    st.info(f"✂️ **{segment_count} videos** have custom time ranges")
            
            with download_col2:
                if st.button("🚀 Download Selected Videos", use_container_width=True, type="primary"):
                    # Prepare download list
                    download_list = []
                    for i in selected_videos:
                        entry = entries[i]
                        if entry:
                            video_id = entry.get('id')
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            video_title = entry.get('title', 'Unknown Title')
                            
                            # Get time range if set
                            time_range = st.session_state.playlist_manager['video_time_ranges'].get(i, {})
                            start_time = time_range.get('start')
                            end_time = time_range.get('end')
                            
                            download_list.append({
                                'url': video_url,
                                'title': video_title,
                                'index': i + 1,
                                'start_time': start_time,
                                'end_time': end_time
                            })
                    
                    # Store in session state for download processing
                    st.session_state.playlist_manager['download_list'] = download_list
                    st.session_state.playlist_manager['is_downloading'] = True
                    st.session_state.playlist_manager['current_download_index'] = 0
                    st.session_state.playlist_manager['download_results'] = []
                    
                    st.success("🚀 Starting download of selected videos...")
                    st.rerun()
        else:
            st.info("💡 Select videos above to enable download options")
        
        # Download progress section
        if st.session_state.playlist_manager['is_downloading']:
            st.markdown("---")
            st.markdown("### 🔄 Downloading Selected Videos")
            
            download_list = st.session_state.playlist_manager['download_list']
            current_index = st.session_state.playlist_manager['current_download_index']
            results = st.session_state.playlist_manager['download_results']
            
            # Overall progress
            overall_progress = st.progress(current_index / len(download_list) if download_list else 0)
            overall_status = st.empty()
            
            overall_status.markdown(f"**Downloading video {current_index + 1} of {len(download_list)}**")
            
            # Current video info
            if current_index < len(download_list):
                current_video = download_list[current_index]
                st.markdown(f"#### 🎬 Current: {current_video['title']}")
                
                # Create download path
                download_path = os.path.join(os.getcwd(), "downloads")
                if create_subfolder:
                    date_folder = datetime.now().strftime("%Y-%m-%d")
                    download_path = os.path.join(download_path, date_folder)
                
                # Download current video
                with st.spinner(f"Downloading video {current_index + 1}..."):
                    success, result = download_video(
                        current_video['url'],
                        quality,
                        audio_choice,
                        download_path,
                        None,  # No progress callback for now
                        None,  # No controller
                        current_video['start_time'],
                        current_video['end_time']
                    )
                
                # Store result
                results.append({
                    'success': success,
                    'title': current_video['title'],
                    'result': result,
                    'index': current_video['index']
                })
                
                # Show result
                if success:
                    st.success(f"✅ Downloaded: {current_video['title']}")
                else:
                    st.error(f"❌ Failed: {current_video['title']} - {result}")
                
                # Move to next video
                st.session_state.playlist_manager['current_download_index'] += 1
                
                # Check if all downloads complete
                if st.session_state.playlist_manager['current_download_index'] >= len(download_list):
                    # All downloads complete
                    overall_progress.progress(1.0)
                    overall_status.markdown("**✅ All downloads completed!**")
                    
                    # Show final results
                    success_count = sum(1 for r in results if r['success'])
                    st.balloons()
                    st.success(f"🎉 **Playlist download completed!** ✅ {success_count}/{len(results)} videos downloaded successfully")
                    
                    # Reset download state
                    st.session_state.playlist_manager['is_downloading'] = False
                    
                    if st.button("📋 Download More Videos", use_container_width=True, type="secondary"):
                        st.rerun()
                else:
                    # Continue with next video
                    st.rerun()
            
            # Show completed downloads
            if results:
                st.markdown("#### 📊 Download Results")
                for result in results:
                    if result['success']:
                        st.success(f"✅ Video {result['index']}: {result['title']}")
                    else:
                        st.error(f"❌ Video {result['index']}: {result['title']} - {result['result']}")

with tab4:
    st.markdown("### ⏰ Download Scheduler")
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("📅 **Schedule downloads for later** - Set specific date and time for automatic downloads")
    
    # Auto-refresh mechanism for real-time updates
    if 'scheduler_last_refresh' not in st.session_state:
        st.session_state.scheduler_last_refresh = datetime.now()
    
    # Check if any downloads are currently downloading
    scheduled_downloads = get_scheduled_downloads()
    has_downloading = any(d['status'] == 'downloading' for d in scheduled_downloads)
    
    # Auto-refresh controls
    refresh_col1, refresh_col2 = st.columns([3, 1])
    with refresh_col1:
        if has_downloading:
            st.info("⬇️ Active downloads detected - Use refresh button to update progress")
    with refresh_col2:
        if st.button("🔄 Refresh Status", type="secondary"):
            st.session_state.scheduler_last_refresh = datetime.now()
            st.rerun()
    
    # Initialize scheduler session state if needed
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = {
            'scheduled_downloads': []
        }
    
    # Load scheduled downloads and run checker
    try:
        st.session_state.scheduler['scheduled_downloads'] = get_scheduled_downloads()
        check_and_run_scheduled_downloads()
    except Exception as e:
        st.warning(f"Scheduler initialization warning: {e}")
        st.session_state.scheduler['scheduled_downloads'] = []
    
    # Scheduler options
    scheduler_mode = st.radio(
        "What would you like to schedule?",
        ["📹 Single Video", "📋 Batch Videos", "🎬 Playlist Selection"],
        help="Choose the type of download to schedule"
    )
    
    st.markdown("#### 📅 Schedule Settings")
    
    # Date and time selection
    schedule_col1, schedule_col2 = st.columns(2)
    
    with schedule_col1:
        schedule_date = st.date_input(
            "📅 Select Date",
            value=st.session_state.get("schedule_date", datetime.now().date() + timedelta(days=1)),
            min_value=datetime.now().date(),
            key="schedule_date"
        )
    
    with schedule_col2:
        schedule_time = st.time_input(
            "🕐 Select Time",
            value=st.session_state.get("schedule_time", (datetime.now() + timedelta(minutes=1)).time()),
            key="schedule_time"
        )
    
    scheduled_datetime = datetime.combine(schedule_date, schedule_time)
    
    if scheduled_datetime <= datetime.now():
        st.warning("⚠️ Please select a future date and time")
    else:
        st.success(f"📅 Scheduled for: {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("#### ⚙️ Download Configuration")
    
    if scheduler_mode == "📹 Single Video":
        # Single video scheduling
        video_url = st.text_input("🔗 Video URL", placeholder="https://www.youtube.com/watch?v=...")
        
        # Time range options
        time_range_option = st.radio(
            "Download Range:",
            ["📺 Complete Video", "✂️ Custom Time Range"],
            key="scheduler_time_range"
        )
        
        start_time = None
        end_time = None
        
        if time_range_option == "✂️ Custom Time Range":
            time_col1, time_col2 = st.columns(2)
            with time_col1:
                start_time = st.text_input("⏮️ Start Time", value="00:00:00", placeholder="00:01:30")
            with time_col2:
                end_time = st.text_input("⏭️ End Time", placeholder="00:05:00")
        
        if st.button("⏰ Schedule Single Video", use_container_width=True, type="primary") and video_url:
            if scheduled_datetime > datetime.now():
                # Create scheduled download
                download_id = f"single_{int(datetime.now().timestamp())}"
                scheduled_download = {
                    'id': download_id,
                    'type': 'single',
                    'title': f"Single Video - {video_url[:50]}...",
                    'url': video_url,
                    'quality': quality,
                    'audio_choice': audio_choice,
                    'start_time': start_time if start_time != "00:00:00" else None,
                    'end_time': end_time if end_time else None,
                    'scheduled_time': scheduled_datetime.isoformat(),
                    'status': 'scheduled',
                    'created_time': datetime.now().isoformat(),
                    'create_subfolder': create_subfolder
                }
                
                # Save to file
                scheduled_downloads = get_scheduled_downloads()
                scheduled_downloads.append(scheduled_download)
                save_scheduled_downloads(scheduled_downloads)
                
                st.success(f"✅ Video scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
                st.rerun()
    
    elif scheduler_mode == "📋 Batch Videos":
        # Batch videos scheduling
        batch_urls = st.text_area("🔗 Video URLs (one per line):", height=150)
        
        # Time range options for batch
        batch_time_option = st.radio(
            "Time Range for All Videos:",
            ["📺 Complete Videos", "✂️ Same Time Range for All"],
            key="scheduler_batch_time"
        )
        
        batch_start_time = None
        batch_end_time = None
        
        if batch_time_option == "✂️ Same Time Range for All":
            time_col1, time_col2 = st.columns(2)
            with time_col1:
                batch_start_time = st.text_input("⏮️ Start Time", value="00:00:00", key="batch_start")
            with time_col2:
                batch_end_time = st.text_input("⏭️ End Time", key="batch_end")
        
        if st.button("⏰ Schedule Batch Videos", use_container_width=True, type="primary") and batch_urls:
            if scheduled_datetime > datetime.now():
                urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
                
                # Create URL data
                url_data = []
                for url in urls:
                    url_data.append({
                        'url': url,
                        'start_time': batch_start_time if batch_start_time != "00:00:00" else None,
                        'end_time': batch_end_time if batch_end_time else None
                    })
                
                download_id = f"batch_{int(datetime.now().timestamp())}"
                scheduled_download = {
                    'id': download_id,
                    'type': 'batch',
                    'title': f"Batch Download - {len(urls)} videos",
                    'urls': url_data,
                    'quality': quality,
                    'audio_choice': audio_choice,
                    'scheduled_time': scheduled_datetime.isoformat(),
                    'status': 'scheduled',
                    'created_time': datetime.now().isoformat(),
                    'create_subfolder': create_subfolder
                }
                
                scheduled_downloads = get_scheduled_downloads()
                scheduled_downloads.append(scheduled_download)
                save_scheduled_downloads(scheduled_downloads)
                
                st.success(f"✅ Batch of {len(urls)} videos scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
                st.rerun()
    
    elif scheduler_mode == "🎬 Playlist Selection":
        # Playlist selection scheduling
        st.info("🔄 To schedule playlist selections, first load a playlist in the Playlist Manager tab, select your videos, then return here to schedule them.")
        
        # Check if there are selected videos in playlist manager
        if 'playlist_manager' in st.session_state and st.session_state.playlist_manager.get('selected_videos'):
            selected_videos = [i for i, selected in st.session_state.playlist_manager['selected_videos'].items() if selected]
            playlist_info = st.session_state.playlist_manager.get('playlist_info')
            
            if selected_videos and playlist_info:
                entries = playlist_info.get('entries', [])
                st.success(f"✅ Found {len(selected_videos)} selected videos from playlist: {playlist_info.get('title', 'Unknown')}")
                
                if st.button("⏰ Schedule Selected Playlist Videos", use_container_width=True, type="primary"):
                    if scheduled_datetime > datetime.now():
                        # Create video data
                        video_data = []
                        for i in selected_videos:
                            if i < len(entries) and entries[i]:
                                entry = entries[i]
                                video_id = entry.get('id')
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                
                                # Get time range if set
                                time_range = st.session_state.playlist_manager['video_time_ranges'].get(i, {})
                                
                                video_data.append({
                                    'url': video_url,
                                    'title': entry.get('title', 'Unknown'),
                                    'start_time': time_range.get('start'),
                                    'end_time': time_range.get('end')
                                })
                        
                        download_id = f"playlist_{int(datetime.now().timestamp())}"
                        scheduled_download = {
                            'id': download_id,
                            'type': 'playlist',
                            'title': f"Playlist Selection - {len(video_data)} videos",
                            'videos': video_data,
                            'quality': quality,
                            'audio_choice': audio_choice,
                            'scheduled_time': scheduled_datetime.isoformat(),
                            'status': 'scheduled',
                            'created_time': datetime.now().isoformat(),
                            'create_subfolder': create_subfolder
                        }
                        
                        scheduled_downloads = get_scheduled_downloads()
                        scheduled_downloads.append(scheduled_download)
                        save_scheduled_downloads(scheduled_downloads)
                        
                        st.success(f"✅ {len(video_data)} playlist videos scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
                        st.rerun()
        else:
            st.info("💡 No videos selected in Playlist Manager. Please go to the Playlist Manager tab first.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calendar and Scheduled Downloads Section
    st.markdown("---")
    st.markdown("### 📅 Scheduled Downloads Calendar")
    
    # Refresh scheduled downloads from file
    scheduled_downloads = get_scheduled_downloads()
    st.session_state.scheduler['scheduled_downloads'] = scheduled_downloads
    
    if scheduled_downloads:
        # Calendar view (simplified)
        st.markdown("#### 📋 Upcoming & Recent Downloads")
        
        # Sort by scheduled time
        sorted_downloads = sorted(scheduled_downloads, key=lambda x: x['scheduled_time'], reverse=True)
        
        for download in sorted_downloads[:10]:  # Show last 10
            scheduled_time = datetime.fromisoformat(download['scheduled_time'])
            
            with st.expander(f"{download['title']} - {scheduled_time.strftime('%Y-%m-%d %H:%M')}", expanded=False):
                status_col, details_col, actions_col = st.columns([1, 2, 1])
                
                with status_col:
                    status_colors = {
                        'scheduled': '🟦',
                        'downloading': '🟡',
                        'completed': '🟢',
                        'failed': '🔴'
                    }
                    status_icon = status_colors.get(download['status'], '⚪')
                    st.markdown(f"**Status:** {status_icon} {download['status'].title()}")
                    
                    # Show real-time progress for downloading items
                    if download['status'] == 'downloading' and 'progress' in download:
                        progress_info = download['progress']
                        
                        if download['type'] == 'single':
                            # Single video progress
                            if 'progress' in progress_info:
                                st.progress(progress_info['progress'] / 100)
                                st.caption(f"📊 {progress_info['progress']:.1f}% complete")
                                
                                if 'downloaded_mb' in progress_info and 'total_mb' in progress_info:
                                    st.caption(f"💾 {progress_info['downloaded_mb']:.1f} / {progress_info['total_mb']:.1f} MB")
                                
                                if 'speed' in progress_info and progress_info['speed'] > 0:
                                    speed_mb = progress_info['speed'] / (1024 * 1024)
                                    st.caption(f"⚡ {speed_mb:.1f} MB/s")
                                
                                if 'eta' in progress_info and progress_info['eta'] > 0:
                                    eta_min = int(progress_info['eta'] // 60)
                                    eta_sec = int(progress_info['eta'] % 60)
                                    st.caption(f"⏱️ ETA: {eta_min}m {eta_sec}s")
                        
                        elif download['type'] in ['batch', 'playlist']:
                            # Batch/Playlist progress
                            if 'current_video' in progress_info and 'total_videos' in progress_info:
                                overall_progress = progress_info.get('batch_progress', progress_info.get('playlist_progress', 0))
                                st.progress(overall_progress / 100)
                                st.caption(f"📊 Video {progress_info['current_video']}/{progress_info['total_videos']}")
                                st.caption(f"📈 {overall_progress:.1f}% overall")
                                
                                # Current video progress
                                if 'video_progress' in progress_info:
                                    video_prog = progress_info['video_progress']
                                    if 'progress' in video_prog:
                                        st.caption(f"🎬 Current: {video_prog['progress']:.1f}%")
                                    
                                    if 'speed' in video_prog and video_prog['speed'] > 0:
                                        speed_mb = video_prog['speed'] / (1024 * 1024)
                                        st.caption(f"⚡ {speed_mb:.1f} MB/s")
                
                with details_col:
                    st.markdown(f"**Type:** {download['type'].title()}")
                    st.markdown(f"**Quality:** {download.get('quality', 'N/A')}")
                    st.markdown(f"**Audio:** {download.get('audio_choice', 'N/A')}")
                    
                    # Show additional details for downloading items
                    if download['status'] == 'downloading' and 'progress' in download:
                        progress_info = download['progress']
                        
                        if download['type'] == 'batch' and 'current_url' in progress_info:
                            st.markdown(f"**Current URL:** `{progress_info['current_url'][:40]}...`")
                        elif download['type'] == 'playlist' and 'current_title' in progress_info:
                            st.markdown(f"**Current Video:** {progress_info['current_title'][:30]}...")
                        
                        if 'filename' in progress_info and progress_info['filename']:
                            filename = os.path.basename(progress_info['filename'])
                            st.markdown(f"**File:** {filename[:30]}...")
                    
                    if download.get('result'):
                        st.markdown(f"**Result:** {download['result']}")
                
                with actions_col:
                    if download['status'] == 'scheduled':
                        if st.button(f"🗑️ Cancel", key=f"cancel_{download['id']}"):
                            # Remove from scheduled downloads
                            updated_downloads = [d for d in scheduled_downloads if d['id'] != download['id']]
                            save_scheduled_downloads(updated_downloads)
                            st.success("🗑️ Download cancelled")
                            st.rerun()
                    
                    elif download['status'] == 'downloading':
                        st.info("⬇️ Downloading...")
                        # Auto-refresh button for real-time updates
                        if st.button("🔄 Refresh Progress", key=f"refresh_{download['id']}"):
                            st.rerun()
        
        # Statistics
        st.markdown("#### 📊 Scheduler Statistics")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            scheduled_count = len([d for d in scheduled_downloads if d['status'] == 'scheduled'])
            st.metric("📅 Scheduled", scheduled_count)
        
        with stats_col2:
            downloading_count = len([d for d in scheduled_downloads if d['status'] == 'downloading'])
            st.metric("⬇️ Downloading", downloading_count)
        
        with stats_col3:
            completed_count = len([d for d in scheduled_downloads if d['status'] == 'completed'])
            st.metric("✅ Completed", completed_count)
        
        with stats_col4:
            failed_count = len([d for d in scheduled_downloads if d['status'] == 'failed'])
            st.metric("❌ Failed", failed_count)
    else:
        st.info("📅 No scheduled downloads yet. Create your first scheduled download above!")

with tab5:
    st.markdown("### 📊 Download History")
    
    history = get_download_history()
    
    if history:
        # Statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_downloads = len(history)
        total_size = sum(h.get('file_size', 0) for h in history) / (1024**3)  # GB
        recent_downloads = len([h for h in history if (datetime.now() - datetime.fromisoformat(h['download_date'].replace('Z', '+00:00').replace('+00:00', ''))).days < 7])
        
        with col1:
            st.metric("📊 Total Downloads", total_downloads)
        with col2:
            st.metric("💾 Total Size", f"{total_size:.2f} GB")
        with col3:
            st.metric("📅 This Week", recent_downloads)
        with col4:
            avg_size = (sum(h.get('file_size', 0) for h in history) / len(history)) / (1024**2) if history else 0
            st.metric("📈 Avg Size", f"{avg_size:.1f} MB")
        
        st.markdown("---")
        
        # Search functionality
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_term = st.text_input("🔍 Search history", placeholder="Search by title or URL...")
        
        with search_col2:
            if st.button("🗑️ Clear All History", type="secondary"):
                if os.path.exists("download_history.json"):
                    os.remove("download_history.json")
                st.success("🧹 History cleared!")
                st.rerun()
        
        # Filter history based on search
        if search_term:
            filtered_history = [h for h in history if search_term.lower() in h['title'].lower() or search_term.lower() in h['url'].lower()]
        else:
            filtered_history = history
        
        # Display history with modern cards
        st.markdown("#### 📋 Recent Downloads")
        

        
        if filtered_history:
            for i, record in enumerate(reversed(filtered_history[-20:])):  # Show last 20
                with st.expander(f"🎬 {record['title']} • {record['download_date'][:10]}", expanded=False):
                    hist_col1, hist_col2 = st.columns(2)
                    
                    with hist_col1:
                        st.markdown(f"**🎬 Title:** {record['title']}")
                        st.markdown(f"**🎯 Quality:** `{record['quality']}`")
                        st.markdown(f"**📅 Date:** {record['download_date'][:19]}")
                    
                    with hist_col2:
                        st.markdown(f"**🔗 URL:** [{record['url'][:50]}...]({record['url']})")
                        if record['file_size'] > 0:
                            size_mb = record['file_size'] / (1024 * 1024)
                            st.markdown(f"**💾 Size:** {size_mb:.2f} MB")
                        
                        if os.path.exists(record['file_path']):
                            st.success("✅ File exists")
                        else:
                            st.error("❌ File not found")
        else:
            st.info("� No downloads match your search criteria")
    
    else:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.info("📝 No download history available yet. Start downloading videos to see them here!")
        st.markdown('</div>', unsafe_allow_html=True)

with tab6:
    st.markdown("### 📁 File Manager")
    
    # Show download folder contents with enhanced information
    download_base_path = os.path.join(os.getcwd(), "downloads")
    
    if os.path.exists(download_base_path):
        # Calculate total size and file count
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(download_base_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        

        
        # Storage overview cards
        overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
        
        with overview_col1:
            st.metric("📊 Total Files", file_count)
        with overview_col2:
            st.metric("💾 Total Size", f"{total_size / (1024**3):.2f} GB")
        with overview_col3:
            avg_size = (total_size / file_count) / (1024**2) if file_count > 0 else 0
            st.metric("📈 Avg File Size", f"{avg_size:.1f} MB")
        with overview_col4:
            if st.button("🗂️ Open Downloads Folder", type="secondary"):
                os.startfile(download_base_path)
        
        st.markdown("---")
        
        # File management controls
        management_col1, management_col2 = st.columns(2)
        
        with management_col1:
            st.markdown("#### 🎛️ Quick Actions")
            
        with management_col2:
            sort_option = st.selectbox("📊 Sort by:", ["Newest First", "Oldest First", "Largest First", "Smallest First", "Name A-Z", "Name Z-A"])
        
        st.markdown("#### � Downloaded Files")
        
        # Get all files recursively
        all_files = []
        for root, dirs, files in os.walk(download_base_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, download_base_path)
                if os.path.exists(file_path):
                    file_stats = os.stat(file_path)
                    file_size = file_stats.st_size / (1024 * 1024)  # Convert to MB
                    mod_time = datetime.fromtimestamp(file_stats.st_mtime)
                    
                    all_files.append({
                        'name': file,
                        'path': rel_path,
                        'size': file_size,
                        'modified': mod_time,
                        'full_path': file_path
                    })
        
        # Sort files based on selection
        if sort_option == "Newest First":
            all_files.sort(key=lambda x: x['modified'], reverse=True)
        elif sort_option == "Oldest First":
            all_files.sort(key=lambda x: x['modified'])
        elif sort_option == "Largest First":
            all_files.sort(key=lambda x: x['size'], reverse=True)
        elif sort_option == "Smallest First":
            all_files.sort(key=lambda x: x['size'])
        elif sort_option == "Name A-Z":
            all_files.sort(key=lambda x: x['name'].lower())
        elif sort_option == "Name Z-A":
            all_files.sort(key=lambda x: x['name'].lower(), reverse=True)
        
        # Display files in modern cards
        if all_files:
            for file_info in all_files:
                with st.container():
                    st.markdown('<div class="file-item">', unsafe_allow_html=True)
                    
                    file_col1, file_col2, file_col3, file_col4 = st.columns([4, 1, 1, 1])
                    
                    with file_col1:
                        # File icon based on extension
                        ext = os.path.splitext(file_info['name'])[1].lower()
                        if ext in ['.mp4', '.avi', '.mkv', '.mov']:
                            icon = "🎬"
                        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                            icon = "🎵"
                        else:
                            icon = "📄"
                        
                        st.markdown(f"**{icon} {file_info['name']}**")
                        if file_info['path'] != file_info['name']:  # Show subfolder
                            st.caption(f"📁 {os.path.dirname(file_info['path'])}")
                    
                    with file_col2:
                        st.markdown(f"**{file_info['size']:.1f} MB**")
                    
                    with file_col3:
                        st.markdown(f"**{file_info['modified'].strftime('%Y-%m-%d')}**")
                        st.caption(file_info['modified'].strftime('%H:%M'))
                    
                    with file_col4:
                        delete_key = f"delete_{hash(file_info['full_path'])}"
                        if st.button("🗑️", key=delete_key, help="Delete file", type="secondary"):
                            try:
                                os.remove(file_info['full_path'])
                                st.success(f"🗑️ Deleted {file_info['name']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting file: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📂 No files found in downloads folder")
    
    else:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.info("📁 No downloads folder found. Download a video to create the folder automatically!")
        st.markdown("💡 **Tip:** Your downloaded files will appear here once you start downloading.")
        st.markdown('</div>', unsafe_allow_html=True)




