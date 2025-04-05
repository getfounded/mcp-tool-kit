#!/usr/bin/env python3
"""
Unit tests for Microsoft Teams API tools.
"""
import unittest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock

# Import the service and tools
from app.tools.teams.service import TeamsService
from app.tools.teams.tools import *
from app.tools.utils.auth import MicrosoftAuth


class TestTeamsService(unittest.TestCase):
    """Test the Teams service class"""

    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["MS_GRAPH_CLIENT_ID"] = "test_client_id"
        os.environ["MS_GRAPH_CLIENT_SECRET"] = "test_client_secret"
        os.environ["MS_GRAPH_TENANT_ID"] = "test_tenant_id"

        # Create service instance
        self.service = TeamsService()

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
    async def test_get_teams(self, mock_request):
        """Test get_teams method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "team123",
                    "displayName": "Test Team",
                    "description": "Test team description"
                }
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.get_teams(50)

        # Verify
        mock_request.assert_called()
        self.assertIn("value", result)
        self.assertEqual(result["value"][0]["displayName"], "Test Team")

    @patch('requests.request')
    async def test_get_channels(self, mock_request):
        """Test get_channels method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "channel123",
                    "displayName": "Test Channel",
                    "description": "Test channel description"
                }
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.get_channels("team123", 50)

        # Verify
        mock_request.assert_called()
        self.assertIn("value", result)
        self.assertEqual(result["value"][0]["displayName"], "Test Channel")

    @patch('requests.request')
    async def test_send_channel_message(self, mock_request):
        """Test send_channel_message method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "id": "msg123"
        }
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.send_channel_message(
            "team123", "channel123", "Test message", "html", "normal"
        )

        # Verify
        mock_request.assert_called()
        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["id"], "msg123")

    @patch('requests.request')
    async def test_create_meeting(self, mock_request):
        """Test create_meeting method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "id": "meeting123",
            "joinUrl": "https://teams.microsoft.com/meet/123",
            "subject": "Test Meeting"
        }
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.create_meeting(
            "Test Meeting", "2023-10-10T10:00:00Z", "2023-10-10T11:00:00Z"
        )

        # Verify
        mock_request.assert_called()
        self.assertEqual(result["id"], "meeting123")
        self.assertEqual(result["join_url"],
                         "https://teams.microsoft.com/meet/123")


class TestTeamsTools(unittest.TestCase):
    """Test the Teams tool functions"""

    def setUp(self):
        """Set up test environment"""
        # Create service mock
        self.service_mock = MagicMock(spec=TeamsService)
        self.service_mock.auth_handler = MagicMock()

    def test_teams_authenticate(self):
        """Test teams_authenticate tool function"""
        # Set up mock
        self.service_mock.auth_handler.authenticate_client_credentials = MagicMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        self.service_mock.auth_handler.token_expires_at = 1698765432

        # Execute function
        result = asyncio.run(teams_authenticate(
            self.service_mock, "client_credentials"))

        # Verify
        self.service_mock.auth_handler.authenticate_client_credentials.assert_called_once()
        result_json = json.loads(result)
        self.assertEqual(result_json["status"], "authenticated")
        self.assertEqual(result_json["token_type"], "Bearer")

    def test_teams_get_teams(self):
        """Test teams_get_teams tool function"""
        # Set up mock
        teams_result = {
            "value": [
                {
                    "id": "team123",
                    "displayName": "Test Team"
                }
            ],
            "total": 1
        }
        self.service_mock.get_teams = MagicMock(return_value=teams_result)

        # Execute function
        result = asyncio.run(teams_get_teams(self.service_mock, 50))

        # Verify
        self.service_mock.get_teams.assert_called_once_with(50)
        result_json = json.loads(result)
        self.assertIn("value", result_json)
        self.assertEqual(result_json["value"][0]["displayName"], "Test Team")

    def test_teams_get_channels(self):
        """Test teams_get_channels tool function"""
        # Set up mock
        channels_result = {
            "value": [
                {
                    "id": "channel123",
                    "displayName": "Test Channel"
                }
            ],
            "total": 1
        }
        self.service_mock.get_channels = MagicMock(
            return_value=channels_result)

        # Execute function
        result = asyncio.run(teams_get_channels(
            self.service_mock, "team123", 50))

        # Verify
        self.service_mock.get_channels.assert_called_once_with("team123", 50)
        result_json = json.loads(result)
        self.assertIn("value", result_json)
        self.assertEqual(result_json["value"][0]
                         ["displayName"], "Test Channel")

    def test_teams_send_channel_message(self):
        """Test teams_send_channel_message tool function"""
        # Set up mock
        message_result = {
            "id": "msg123",
            "status": "sent",
            "team_id": "team123",
            "channel_id": "channel123"
        }
        self.service_mock.send_channel_message = MagicMock(
            return_value=message_result)

        # Execute function
        result = asyncio.run(teams_send_channel_message(
            self.service_mock, "team123", "channel123", "Test message"
        ))

        # Verify
        self.service_mock.send_channel_message.assert_called_once_with(
            "team123", "channel123", "Test message", "html", "normal"
        )
        result_json = json.loads(result)
        self.assertEqual(result_json["status"], "sent")
        self.assertEqual(result_json["id"], "msg123")

    def test_teams_create_meeting(self):
        """Test teams_create_meeting tool function"""
        # Set up mock
        meeting_result = {
            "id": "meeting123",
            "join_url": "https://teams.microsoft.com/meet/123",
            "subject": "Test Meeting"
        }
        self.service_mock.create_meeting = MagicMock(
            return_value=meeting_result)

        # Execute function
        start_datetime = "2023-10-10T10:00:00Z"
        end_datetime = "2023-10-10T11:00:00Z"
        result = asyncio.run(teams_create_meeting(
            self.service_mock, "Test Meeting", start_datetime, end_datetime
        ))

        # Verify
        self.service_mock.create_meeting.assert_called_once_with(
            "Test Meeting", start_datetime, end_datetime, "UTC", None, True, None
        )
        result_json = json.loads(result)
        self.assertEqual(result_json["id"], "meeting123")
        self.assertEqual(result_json["join_url"],
                         "https://teams.microsoft.com/meet/123")


if __name__ == "__main__":
    unittest.main()
