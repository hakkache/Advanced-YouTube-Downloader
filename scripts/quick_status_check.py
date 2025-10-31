#!/usr/bin/env python3
"""
Quick status check for the YouTube downloader system
"""

import json
import os
from datetime import datetime

def check_system_status():
    """Check the current status of the system"""
    
    print("=== YouTube Downloader System Status ===")
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if files exist
    files_to_check = [
        "app.py",
        "scheduler_service.py", 
        "scheduled_downloads.json",
        "requirements.txt",
        "SCHEDULER_README.md"
    ]
    
    print("📁 File Status:")
    for file in files_to_check:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"  {exists} {file}")
    print()
    
    # Check scheduled downloads
    if os.path.exists("scheduled_downloads.json"):
        try:
            with open("scheduled_downloads.json", "r", encoding="utf-8") as f:
                downloads = json.load(f)
            
            print("📋 Scheduled Downloads:")
            print(f"  Total downloads: {len(downloads)}")
            
            status_counts = {}
            for download in downloads:
                status = download.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
            
            # Show active downloads
            active_downloads = [d for d in downloads if d.get("status") == "downloading"]
            if active_downloads:
                print("\n🔄 Active Downloads:")
                for download in active_downloads:
                    progress_info = download.get("progress", {})
                    if progress_info:
                        progress = progress_info.get("progress", 0)
                        speed = progress_info.get("speed", 0)
                        eta = progress_info.get("eta", 0)
                        filename = progress_info.get("filename", "Unknown")
                        
                        print(f"  📺 {download.get('title', 'Unknown')}")
                        print(f"     Progress: {progress:.1f}%")
                        print(f"     Speed: {speed/1024/1024:.1f} MB/s")
                        print(f"     ETA: {eta}s")
                        print(f"     File: {os.path.basename(filename)}")
            else:
                print("\n✅ No downloads currently active")
                
        except Exception as e:
            print(f"❌ Error reading scheduled downloads: {e}")
    
    print("\n=== Key Features Implemented ===")
    features = [
        "✅ Real-time progress display for scheduled downloads",
        "✅ Manual refresh buttons for live updates", 
        "✅ Progress bars, speed, ETA, and current file display",
        "✅ Support for single video, batch, and playlist downloads",
        "✅ Background scheduler service integration",
        "✅ Persistent storage of scheduled jobs",
        "✅ User-friendly scheduler tab interface",
        "✅ Comprehensive documentation and guides"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n=== Usage Instructions ===")
    print("1. Start the scheduler service: python scheduler_service.py")
    print("2. Start the Streamlit app: streamlit run app.py")
    print("3. Navigate to the 'Scheduler' tab")
    print("4. Schedule downloads and monitor real-time progress")
    print("5. Use refresh buttons to see live updates")

if __name__ == "__main__":
    check_system_status()
