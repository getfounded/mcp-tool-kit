#!/usr/bin/env python3
"""
Unit tests for PowerPoint service.
"""
import unittest
from unittest.mock import MagicMock, patch
import os
import platform
import tempfile
from datetime import datetime

from app.tools.powerpoint.service import PowerPointService


class TestPowerPointService(unittest.TestCase):
    """Tests for PowerPointService class"""

    def setUp(self):
        """Set up test environment"""
        self.service = PowerPointService()
        self.service.initialized = True  # Skip initialization for tests

        # Create a temp directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.service.temp_dir = self.test_dir.name

    def tearDown(self):
        """Clean up test environment"""
        self.test_dir.cleanup()

    def test_get_next_session_id(self):
        """Test session ID generation"""
        session_id1 = self.service._get_next_session_id()
        session_id2 = self.service._get_next_session_id()

        self.assertTrue(session_id1.startswith("ppt_session_"))
        self.assertTrue(session_id2.startswith("ppt_session_"))
        self.assertNotEqual(session_id1, session_id2)

    @patch('platform.system', return_value='Windows')
    @patch('app.tools.powerpoint.service.PowerPointService.validate', return_value=(True, None))
    def test_initialize_windows(self, mock_validate, mock_platform):
        """Test service initialization on Windows"""
        self.service.initialized = False

        with patch('win32com.client.Dispatch') as mock_dispatch:
            mock_app = MagicMock()
            mock_dispatch.return_value = mock_app

            result = self.service.initialize()

            self.assertTrue(result)
            self.assertTrue(self.service.initialized)
            mock_dispatch.assert_called_once_with("PowerPoint.Application")

    @patch('platform.system', return_value='Linux')
    @patch('app.tools.powerpoint.service.PowerPointService.validate', return_value=(True, None))
    def test_initialize_linux(self, mock_validate, mock_platform):
        """Test service initialization on Linux"""
        self.service.initialized = False

        result = self.service.initialize()

        self.assertTrue(result)
        self.assertTrue(self.service.initialized)

    @patch('platform.system', return_value='Windows')
    def test_validate_windows_success(self, mock_platform):
        """Test validation on Windows with dependencies"""
        with patch('builtins.__import__', side_effect=lambda name, *args: None):
            is_valid, message = self.service.validate()
            self.assertTrue(is_valid)
            self.assertIsNone(message)

    @patch('platform.system', return_value='Windows')
    def test_validate_windows_failure(self, mock_platform):
        """Test validation on Windows with missing dependencies"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'win32com'")):
            is_valid, message = self.service.validate()
            self.assertFalse(is_valid)
            self.assertIn("Missing required dependencies", message)

    @patch('platform.system', return_value='Linux')
    def test_validate_linux_success(self, mock_platform):
        """Test validation on Linux with dependencies"""
        with patch('builtins.__import__', side_effect=lambda name, *args: None):
            is_valid, message = self.service.validate()
            self.assertTrue(is_valid)
            self.assertIsNone(message)

    @patch('platform.system', return_value='Linux')
    def test_validate_linux_failure(self, mock_platform):
        """Test validation on Linux with missing dependencies"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'pptx'")):
            is_valid, message = self.service.validate()
            self.assertFalse(is_valid)
            self.assertIn("Missing required dependencies", message)

    @patch('platform.system', return_value='Windows')
    def test_create_presentation_windows(self, mock_platform):
        """Test creating a presentation on Windows"""
        self.service.use_win32com = True
        session_id = "test_session"

        with patch('win32com.client.Dispatch') as mock_dispatch:
            mock_app = MagicMock()
            mock_presentation = MagicMock()
            mock_app.Presentations.Add.return_value = mock_presentation
            self.service._app = mock_app

            result = self.service.create_presentation(session_id)

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["session_id"], session_id)
            self.assertIn(session_id, self.service._active_presentations)
            self.assertEqual(
                self.service._active_presentations[session_id]["platform_type"], "win32com")
            mock_app.Presentations.Add.assert_called_once()

    @patch('platform.system', return_value='Linux')
    def test_create_presentation_linux(self, mock_platform):
        """Test creating a presentation on Linux"""
        self.service.use_win32com = False
        session_id = "test_session"

        with patch('pptx.Presentation') as mock_presentation_class:
            mock_presentation = MagicMock()
            mock_presentation_class.return_value = mock_presentation

            result = self.service.create_presentation(session_id)

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["session_id"], session_id)
            self.assertIn(session_id, self.service._active_presentations)
            self.assertEqual(
                self.service._active_presentations[session_id]["platform_type"], "pptx")
            mock_presentation_class.assert_called_once()

    def test_save_presentation_no_session(self):
        """Test saving a presentation with invalid session"""
        result = self.service.save_presentation("invalid_session")

        self.assertEqual(result["status"], "error")
        self.assertIn("Session not found", result["message"])

    @patch('platform.system', return_value='Windows')
    def test_add_slide_windows(self, mock_platform):
        """Test adding a slide on Windows"""
        self.service.use_win32com = True
        session_id = "test_session"

        # Setup mock presentation
        mock_presentation = MagicMock()
        mock_slide = MagicMock()
        mock_slide.SlideIndex = 1
        mock_slide_master = MagicMock()
        mock_layout = MagicMock()
        mock_slide_master.CustomLayouts.Count = 2
        mock_slide_master.CustomLayouts.Item.return_value = mock_layout
        mock_presentation.SlideMaster = mock_slide_master
        mock_presentation.Slides.Count = 0
        mock_presentation.Slides.AddSlide.return_value = mock_slide

        self.service._active_presentations[session_id] = {
            "presentation": mock_presentation,
            "file_path": None,
            "created_at": datetime.now(),
            "modified_at": datetime.now(),
            "platform_type": "win32com"
        }

        result = self.service.add_slide(
            session_id, layout_index=1, title="Test Slide")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["slide_index"], 0)
        mock_presentation.Slides.AddSlide.assert_called_once()

    @patch('platform.system', return_value='Linux')
    def test_add_slide_linux(self, mock_platform):
        """Test adding a slide on Linux"""
        self.service.use_win32com = False
        session_id = "test_session"

        # Setup mock presentation
        mock_presentation = MagicMock()
        mock_slide = MagicMock()
        mock_layout = MagicMock()
        mock_presentation.slide_layouts = [mock_layout]
        mock_presentation.slides.add_slide.return_value = mock_slide

        self.service._active_presentations[session_id] = {
            "presentation": mock_presentation,
            "file_path": None,
            "created_at": datetime.now(),
            "modified_at": datetime.now(),
            "platform_type": "pptx"
        }

        result = self.service.add_slide(
            session_id, layout_index=0, title="Test Slide")

        self.assertEqual(result["status"], "success")
        mock_presentation.slides.add_slide.assert_called_once_with(mock_layout)

    def test_analyze_presentation_no_session(self):
        """Test analyzing a presentation with invalid session"""
        result = self.service.analyze_presentation("invalid_session")

        self.assertEqual(result["status"], "error")
        self.assertIn("Session not found", result["message"])

    def test_enhance_presentation_no_session(self):
        """Test enhancing a presentation with invalid session"""
        result = self.service.enhance_presentation("invalid_session")

        self.assertEqual(result["status"], "error")
        self.assertIn("Session not found", result["message"])


if __name__ == "__main__":
    unittest.main()
