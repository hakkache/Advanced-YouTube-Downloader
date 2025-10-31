#!/usr/bin/env python3
"""
Background Scheduler Service for YouTube Downloader
This script runs in the background to check and execute scheduled downloads
"""

import time
import threading
from datetime import datetime
import sys
import os

# Add the main directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import (
    get_scheduled_downloads, 
    execute_scheduled_download, 
    update_scheduled_download_status
)

class SchedulerService:
    def __init__(self, check_interval=60):  # Check every 60 seconds
        self.check_interval = check_interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the scheduler service"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print("📅 Scheduler service started - checking every 60 seconds")
    
    def stop(self):
        """Stop the scheduler service"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("📅 Scheduler service stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self._check_scheduled_downloads()
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
            
            # Wait for next check
            time.sleep(self.check_interval)
    
    def _check_scheduled_downloads(self):
        """Check for downloads that are ready to execute"""
        scheduled_downloads = get_scheduled_downloads()
        current_time = datetime.now()
        
        for download in scheduled_downloads:
            if download['status'] == 'scheduled':
                scheduled_time = datetime.fromisoformat(download['scheduled_time'])
                
                # Check if it's time to start the download
                if current_time >= scheduled_time:
                    print(f"🚀 Starting scheduled download: {download['title']}")
                    
                    # Execute in a separate thread to not block the scheduler
                    download_thread = threading.Thread(
                        target=execute_scheduled_download,
                        args=(download,),
                        daemon=True
                    )
                    download_thread.start()

def main():
    """Main function to run the scheduler service"""
    print("📅 YouTube Downloader Scheduler Service")
    print("=" * 50)
    
    scheduler = SchedulerService()
    
    try:
        scheduler.start()
        
        # Keep the service running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down scheduler service...")
        scheduler.stop()

if __name__ == "__main__":
    main()
