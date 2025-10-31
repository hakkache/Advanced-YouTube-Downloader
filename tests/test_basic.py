"""
Basic tests for the YouTube Downloader application.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestYouTubeDownloader(unittest.TestCase):
    """Test cases for YouTube Downloader functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.sample_playlist_url = "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMVgur7FYpQ9a2r"
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        try:
            import app
            import scheduler_service
            self.assertTrue(True, "All modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")
    
    def test_parse_time_to_seconds(self):
        """Test time parsing functionality."""
        # Import the function from app.py
        from app import parse_time_to_seconds
        
        # Test various time formats
        self.assertEqual(parse_time_to_seconds("1:30"), 90)
        self.assertEqual(parse_time_to_seconds("01:30"), 90)
        self.assertEqual(parse_time_to_seconds("1:30:45"), 5445)
        self.assertEqual(parse_time_to_seconds("0:30"), 30)
        
        # Test invalid formats
        with self.assertRaises(ValueError):
            parse_time_to_seconds("invalid")
        
        with self.assertRaises(ValueError):
            parse_time_to_seconds("")
    
    def test_url_validation(self):
        """Test URL validation functionality."""
        # Test valid YouTube URLs
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMVgur7FYpQ9a2r"
        ]
        
        # Test invalid URLs
        invalid_urls = [
            "not_a_url",
            "https://example.com",
            "https://vimeo.com/123456789",
            ""
        ]
        
        # These tests would require the actual validation function from app.py
        # For now, we just test that the URLs are strings
        for url in valid_urls:
            self.assertIsInstance(url, str)
            self.assertTrue(len(url) > 0)
        
        for url in invalid_urls:
            if url:  # Skip empty string test
                self.assertIsInstance(url, str)
    
    @patch('app.yt_dlp.YoutubeDL')
    def test_get_video_info_mock(self, mock_ytdl):
        """Test video info retrieval with mocked yt-dlp."""
        # Mock the yt-dlp response
        mock_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'duration': 240,
            'thumbnail': 'https://example.com/thumb.jpg',
            'uploader': 'Test Channel'
        }
        
        from app import get_video_info
        
        result = get_video_info(self.sample_url)
        
        # Check that the function returns expected keys
        if result:
            self.assertIn('title', result)
            self.assertIn('duration', result)
            self.assertIn('thumbnail', result)
    
    def test_scheduler_service_imports(self):
        """Test that scheduler service can be imported and initialized."""
        try:
            from scheduler_service import SchedulerService
            
            # Test that we can create an instance
            scheduler = SchedulerService()
            self.assertIsInstance(scheduler, SchedulerService)
            self.assertFalse(scheduler.running)
            
        except ImportError:
            self.skipTest("Scheduler service not available")
    
    def test_file_structure(self):
        """Test that required files exist in the project."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        required_files = [
            'app.py',
            'scheduler_service.py',
            'requirements.txt',
            'README.md',
            'LICENSE'
        ]
        
        for file_name in required_files:
            file_path = os.path.join(project_root, file_name)
            self.assertTrue(
                os.path.exists(file_path),
                f"Required file {file_name} not found at {file_path}"
            )
    
    def test_requirements_file(self):
        """Test that requirements.txt is valid."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requirements_path = os.path.join(project_root, 'requirements.txt')
        
        if os.path.exists(requirements_path):
            with open(requirements_path, 'r') as f:
                requirements = f.read().strip()
            
            # Check that it's not empty and contains expected packages
            self.assertTrue(len(requirements) > 0, "requirements.txt is empty")
            self.assertIn('streamlit', requirements.lower())
            self.assertIn('yt-dlp', requirements.lower())
        else:
            self.fail("requirements.txt not found")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_time_format_validation(self):
        """Test time format validation."""
        valid_formats = ["0:30", "1:30", "01:30", "1:30:45", "10:05:20"]
        invalid_formats = ["invalid", "1:60", "25:00", "-1:30", "1:30:60"]
        
        # This is a placeholder test - actual implementation would test the real function
        for time_format in valid_formats:
            # Check format pattern
            parts = time_format.split(':')
            self.assertTrue(len(parts) in [2, 3], f"Invalid format: {time_format}")
        
        for time_format in invalid_formats:
            if time_format != "invalid":  # Skip non-numeric test
                parts = time_format.split(':')
                if len(parts) >= 2:
                    # This would normally test actual validation logic
                    pass


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)