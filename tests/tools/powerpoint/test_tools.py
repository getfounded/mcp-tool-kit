#!/usr/bin/env python3
"""
Unit tests for PowerPoint tools.
"""
import unittest
from unittest.mock import MagicMock, patch
import json
import asyncio

from app.tools.powerpoint.tools import (
    ppt_create_presentation,
    ppt_open_presentation,
    ppt_save_presentation,
    ppt_add_slide,
    ppt_add_text,
    ppt_add_image,
    ppt_add_chart,
    ppt_add_table,
    ppt_analyze_presentation,
    ppt_enhance_presentation,
    ppt_generate_presentation,
    ppt_command
)


class TestPowerPointTools(unittest.TestCase):
    """Tests for PowerPoint tool functions"""

    def setUp(self):
        """Set up test environment"""
        self.mock_service = MagicMock()
        self.mock_get_service = patch(
            'app.tools.powerpoint.tools.get_service', return_value=self.mock_service)
        self.mock_get_service.start()

        # Mock the PowerPointCommander
        self.mock_commander = MagicMock()
        self.mock_commander_class = patch(
            'app.tools.powerpoint.tools.PowerPointCommander', return_value=self.mock_commander)
        self.mock_commander_class.start()

    def tearDown(self):
        """Clean up test environment"""
        self.mock_get_service.stop()
        self.mock_commander_class.stop()

    def run_async_test(self, coro):
        """Helper to run async test function"""
        return asyncio.run(coro)

    def test_ppt_create_presentation(self):
        """Test create presentation tool"""
        # Setup mock
        expected_result = {"status": "success", "session_id": "test_session"}
        self.mock_service.create_presentation.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_create_presentation("test_session"))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.create_presentation.assert_called_once_with(
            "test_session", None)

    def test_ppt_open_presentation(self):
        """Test open presentation tool"""
        # Setup mock
        expected_result = {"status": "success",
                           "session_id": "test_session", "file_path": "test.pptx"}
        self.mock_service.open_presentation.return_value = expected_result

        # Call function
        result = self.run_async_test(
            ppt_open_presentation("test_session", "test.pptx"))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.open_presentation.assert_called_once_with(
            "test_session", "test.pptx")

    def test_ppt_save_presentation(self):
        """Test save presentation tool"""
        # Setup mock
        expected_result = {"status": "success", "file_path": "test.pptx"}
        self.mock_service.save_presentation.return_value = expected_result

        # Call function
        result = self.run_async_test(
            ppt_save_presentation("test_session", "test.pptx"))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.save_presentation.assert_called_once_with(
            "test_session", "test.pptx")

    def test_ppt_add_slide(self):
        """Test add slide tool"""
        # Setup mock
        expected_result = {"status": "success", "slide_index": 0}
        self.mock_service.add_slide.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_add_slide(
            "test_session",
            layout_index=1,
            title="Test Slide",
            content="Test Content"
        ))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.add_slide.assert_called_once_with(
            "test_session", 1, "Test Slide", "Test Content"
        )

    def test_ppt_add_text(self):
        """Test add text tool"""
        # Setup mock
        expected_result = {"status": "success"}
        self.mock_service.add_text.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_add_text(
            "test_session", 0, "Test Text",
            left=2.0, top=3.0, width=4.0, height=1.0,
            font_size=20, font_name="Arial", bold=True,
            italic=False, color="FF0000"
        ))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.add_text.assert_called_once_with(
            "test_session", 0, "Test Text",
            2.0, 3.0, 4.0, 1.0,
            20, "Arial", True, False, "FF0000"
        )

    def test_ppt_add_image(self):
        """Test add image tool"""
        # Setup mock
        expected_result = {"status": "success"}
        self.mock_service.add_image.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_add_image(
            "test_session", 0, "image.png",
            left=2.0, top=3.0, width=4.0, height=3.0
        ))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.add_image.assert_called_once_with(
            "test_session", 0, "image.png", 2.0, 3.0, 4.0, 3.0
        )

    def test_ppt_add_chart(self):
        """Test add chart tool"""
        # Setup mock
        expected_result = {"status": "success"}
        self.mock_service.add_chart.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_add_chart(
            "test_session", 0, "column",
            ["Jan", "Feb", "Mar"],
            ["Series 1", "Series 2"],
            [[10, 20, 30], [15, 25, 35]],
            left=2.0, top=3.0, width=6.0, height=4.0,
            chart_title="Test Chart"
        ))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.add_chart.assert_called_once_with(
            "test_session", 0, "column",
            ["Jan", "Feb", "Mar"],
            ["Series 1", "Series 2"],
            [[10, 20, 30], [15, 25, 35]],
            2.0, 3.0, 6.0, 4.0, "Test Chart"
        )

    def test_ppt_add_table(self):
        """Test add table tool"""
        # Setup mock
        expected_result = {"status": "success"}
        self.mock_service.add_table.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_add_table(
            "test_session", 0, 2, 3,
            [["A1", "B1", "C1"], ["A2", "B2", "C2"]],
            left=2.0, top=3.0, width=6.0, height=2.0
        ))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.add_table.assert_called_once_with(
            "test_session", 0, 2, 3,
            [["A1", "B1", "C1"], ["A2", "B2", "C2"]],
            2.0, 3.0, 6.0, 2.0
        )

    def test_ppt_analyze_presentation(self):
        """Test analyze presentation tool"""
        # Setup mock
        expected_result = {
            "status": "success",
            "analysis": {
                "total_slides": 2,
                "word_count": 100
            }
        }
        self.mock_service.analyze_presentation.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_analyze_presentation("test_session"))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.analyze_presentation.assert_called_once_with(
            "test_session")

    def test_ppt_enhance_presentation(self):
        """Test enhance presentation tool"""
        # Setup mock
        expected_result = {
            "status": "success",
            "suggestions": {
                "overall_suggestions": [
                    {"type": "content_density", "suggestion": "Too much text"}
                ]
            }
        }
        self.mock_service.enhance_presentation.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_enhance_presentation("test_session"))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.enhance_presentation.assert_called_once_with(
            "test_session")

    def test_ppt_generate_presentation(self):
        """Test generate presentation tool"""
        # Setup mock
        expected_result = {
            "status": "success",
            "slides_count": 5
        }
        self.mock_service.generate_presentation.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_generate_presentation(
            "test_session", "Test Presentation", "Content for slides"
        ))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_service.generate_presentation.assert_called_once_with(
            "test_session", "Test Presentation", "Content for slides"
        )

    def test_ppt_command(self):
        """Test command tool"""
        # Setup mock
        command = "create new presentation"
        expected_result = {
            "status": "success",
            "message": "Created new presentation"
        }
        self.mock_commander.process_command.return_value = expected_result

        # Call function
        result = self.run_async_test(ppt_command(command))

        # Verify
        expected_json = json.dumps(expected_result, indent=2)
        self.assertEqual(result, expected_json)
        self.mock_commander_class.assert_called_once_with(self.mock_service)
        self.mock_commander.process_command.assert_called_once_with(command)


if __name__ == "__main__":
    unittest.main()
