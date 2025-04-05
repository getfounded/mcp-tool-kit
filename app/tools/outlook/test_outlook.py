#!/usr/bin/env python3
"""
Unit tests for Outlook API tools.
"""
import unittest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock

# Import the service and tools
from app.tools.outlook.service import OutlookService
from app.tools.outlook.tools import *
from app.tools.utils.auth import MicrosoftAuth


class TestOutlookService(unittest.TestCase):
    """Test the Outlook service class"""

    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["MS_GRAPH_CLIENT_ID"] = "test_client_id"
        os.environ["MS_GRAPH_CLIENT_SECRET"] = "test_client_secret"
        os.environ["MS_GRAPH_TENANT_ID"] = "test_tenant_id"

        # Create service instance
        self.service = OutlookService()

        # Initialize service
        self.service.initialize()

        # Mock auth handler
        self.service.auth_handler = MagicMock(spec=MicrosoftAuth)
        self.service.auth_handler.is_authenticated.return_value = True
        self.service.auth_handler.get_auth_headers.return_value = {
            "Authorization": "Bearer test_token"}

    def test_initialize(self):
        """Test service initialization"""
        self.assertTrue(self.service.initialized)
        self.assertEqual(self.service.client_id, "test_client_id")
        self.assertEqual(self.service.client_secret, "test_client_secret")
        self.assertEqual(self.service.tenant_id, "test_tenant_id")

    @patch('requests.request')
    async def test_get_emails(self, mock_request):
        """Test get_emails method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "123",
                    "subject": "Test Email",
                    "receivedDateTime": "2023-10-01T12:00:00Z",
                    "isRead": False,
                    "from": {"emailAddress": {"address": "sender@example.com", "name": "Sender"}},
                    "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
                    "ccRecipients": [],
                    "body": {"contentType": "html", "content": "<p>Test content</p>"}
                }
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.get_emails("inbox", 10, 0, True)

        # Verify
        mock_request.assert_called()
        self.assertIn("value", result)
        self.assertEqual(result["value"][0]["subject"], "Test Email")

    @patch('requests.request')
    async def test_send_email(self, mock_request):
        """Test send_email method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 202  # Accepted
        mock_request.return_value = mock_response

        # Execute method
        to_recipients = ["recipient@example.com"]
        subject = "Test Subject"
        body = "<p>Test body</p>"

        result = await self.service.send_email(to_recipients, subject, body)

        # Verify
        mock_request.assert_called()
        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["subject"], "Test Subject")

    @patch('requests.request')
    async def test_get_calendar_events(self, mock_request):
        """Test get_calendar_events method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "event123",
                    "subject": "Test Event",
                    "start": {"dateTime": "2023-10-10T10:00:00", "timeZone": "UTC"},
                    "end": {"dateTime": "2023-10-10T11:00:00", "timeZone": "UTC"},
                    "organizer": {"emailAddress": {"address": "organizer@example.com", "name": "Organizer"}},
                    "location": {"displayName": "Test Location"},
                    "isOnlineMeeting": False
                }
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.get_calendar_events(
            "2023-10-01T00:00:00Z",
            "2023-10-31T23:59:59Z",
            10, 0, "UTC"
        )

        # Verify
        mock_request.assert_called()
        self.assertIn("value", result)
        self.assertEqual(result["value"][0]["subject"], "Test Event")


class TestOutlookTools(unittest.TestCase):
    """Test the Outlook tool functions"""

    def setUp(self):
        """Set up test environment"""
        # Create service mock
        self.service_mock = MagicMock(spec=OutlookService)
        self.service_mock.auth_handler = MagicMock()

    def test_outlook_authenticate(self):
        """Test outlook_authenticate tool function"""
        # Set up mock
        self.service_mock.auth_handler.authenticate_client_credentials = MagicMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        self.service_mock.auth_handler.token_expires_at = 1698765432

        # Execute function
        result = asyncio.run(outlook_authenticate(
            self.service_mock, "client_credentials"))

        # Verify
        self.service_mock.auth_handler.authenticate_client_credentials.assert_called_once()
        result_json = json.loads(result)
        self.assertEqual(result_json["status"], "authenticated")
        self.assertEqual(result_json["token_type"], "Bearer")

    def test_outlook_get_emails(self):
        """Test outlook_get_emails tool function"""
        # Set up mock
        emails_result = {
            "value": [
                {
                    "id": "123",
                    "subject": "Test Email",
                    "from": "sender@example.com"
                }
            ],
            "total": 1
        }
        self.service_mock.get_emails = MagicMock(return_value=emails_result)

        # Execute function
        result = asyncio.run(outlook_get_emails(self.service_mock))

        # Verify
        self.service_mock.get_emails.assert_called_once_with(
            "inbox", 10, 0, True)
        result_json = json.loads(result)
        self.assertIn("value", result_json)
        self.assertEqual(result_json["value"][0]["subject"], "Test Email")

    def test_outlook_send_email(self):
        """Test outlook_send_email tool function"""
        # Set up mock
        send_result = {
            "status": "sent",
            "to": ["recipient@example.com"],
            "subject": "Test Subject"
        }
        self.service_mock.send_email = MagicMock(return_value=send_result)

        # Execute function
        to_recipients = ["recipient@example.com"]
        subject = "Test Subject"
        body = "<p>Test body</p>"

        result = asyncio.run(outlook_send_email(
            self.service_mock, to_recipients, subject, body
        ))

        # Verify
        self.service_mock.send_email.assert_called_once_with(
            to_recipients, subject, body, "HTML", None, None
        )
        result_json = json.loads(result)
        self.assertEqual(result_json["status"], "sent")
        self.assertEqual(result_json["subject"], "Test Subject")

    def test_outlook_get_calendar_events(self):
        """Test outlook_get_calendar_events tool function"""
        # Set up mock
        events_result = {
            "value": [
                {
                    "id": "event123",
                    "subject": "Test Event",
                    "start": "2023-10-10T10:00:00",
                    "end": "2023-10-10T11:00:00"
                }
            ],
            "total": 1
        }
        self.service_mock.get_calendar_events = MagicMock(
            return_value=events_result)

        # Execute function
        result = asyncio.run(outlook_get_calendar_events(self.service_mock))

        # Verify
        self.service_mock.get_calendar_events.assert_called_once_with(
            None, None, 10, 0, None)
        result_json = json.loads(result)
        self.assertIn("value", result_json)
        self.assertEqual(result_json["value"][0]["subject"], "Test Event")


if __name__ == "__main__":
    unittest.main()
