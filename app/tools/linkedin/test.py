#!/usr/bin/env python3
"""
Unit tests for LinkedIn API tools.
"""
import unittest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock

# Import the service and tools
from app.tools.linkedin.service import LinkedInService
from app.tools.linkedin.tools import *
from app.tools.utils.auth import OAuth2Auth


class TestLinkedInService(unittest.TestCase):
    """Test the LinkedIn service class"""

    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["LINKEDIN_CLIENT_ID"] = "test_client_id"
        os.environ["LINKEDIN_CLIENT_SECRET"] = "test_client_secret"
        os.environ["LINKEDIN_REDIRECT_URI"] = "http://localhost:8000/callback"

        # Create service instance
        self.service = LinkedInService()

        # Initialize service
        self.service.initialize()

        # Mock auth handler
        self.service.auth_handler = MagicMock(spec=OAuth2Auth)
        self.service.auth_handler.is_authenticated.return_value = True
        self.service.auth_handler.get_auth_headers.return_value = {
            "Authorization": "Bearer test_token"}

    def test_initialize(self):
        """Test service initialization"""
        self.assertTrue(self.service.initialized)
        self.assertEqual(self.service.client_id, "test_client_id")
        self.assertEqual(self.service.client_secret, "test_client_secret")
        self.assertEqual(self.service.redirect_uri,
                         "http://localhost:8000/callback")

    @patch('requests.request')
    async def test_get_profile(self, mock_request):
        """Test get_profile method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": "123456", "firstName": {
            "localized": {"en_US": "John"}}, "lastName": {"localized": {"en_US": "Doe"}}}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.get_profile()

        # Verify
        mock_request.assert_called()
        self.assertEqual(result["id"], "123456")

    @patch('requests.request')
    async def test_search_people(self, mock_request):
        """Test search_people method"""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "elements": [{"title": {"text": "Test Result"}}]}
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.search_people("test", 10, 0)

        # Verify
        mock_request.assert_called()
        self.assertIn("elements", result)

    @patch('requests.request')
    async def test_post_update(self, mock_request):
        """Test post_update method"""
        # Mock get_profile
        self.service.get_profile = MagicMock(return_value={"id": "123456"})

        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": "post123"}
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        # Execute method
        result = await self.service.post_update("Test post")

        # Verify
        mock_request.assert_called()
        self.assertEqual(result["id"], "post123")


class TestLinkedInTools(unittest.TestCase):
    """Test the LinkedIn tool functions"""

    def setUp(self):
        """Set up test environment"""
        # Create service mock
        self.service_mock = MagicMock(spec=LinkedInService)

    def test_linkedin_get_auth_url(self):
        """Test linkedin_get_auth_url tool function"""
        # Set up mock
        self.service_mock.get_auth_url.return_value = "https://linkedin.com/oauth/test"

        # Execute function
        result = linkedin_get_auth_url(self.service_mock)

        # Verify
        self.service_mock.get_auth_url.assert_called_once()
        self.assertIn("https://linkedin.com/oauth/test", result)

    def test_linkedin_authenticate(self):
        """Test linkedin_authenticate tool function"""
        # Set up mock
        auth_result = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        self.service_mock.authenticate_with_code = MagicMock(
            return_value=auth_result)

        # Execute function
        result = asyncio.run(linkedin_authenticate(
            self.service_mock, "test_code"))

        # Verify
        self.service_mock.authenticate_with_code.assert_called_once_with(
            "test_code")
        result_json = json.loads(result)
        self.assertEqual(result_json["status"], "authenticated")
        self.assertEqual(result_json["expires_in"], 3600)

    def test_linkedin_get_profile(self):
        """Test linkedin_get_profile tool function"""
        # Set up mock
        profile_result = {"id": "123456", "firstName": {
            "localized": {"en_US": "John"}}}
        self.service_mock.get_profile = MagicMock(return_value=profile_result)

        # Execute function
        result = asyncio.run(linkedin_get_profile(self.service_mock))

        # Verify
        self.service_mock.get_profile.assert_called_once()
        result_json = json.loads(result)
        self.assertEqual(result_json["id"], "123456")

    def test_linkedin_search_people(self):
        """Test linkedin_search_people tool function"""
        # Set up mock
        search_result = {"elements": [{"title": {"text": "Test Result"}}]}
        self.service_mock.search_people = MagicMock(return_value=search_result)

        # Execute function
        result = asyncio.run(linkedin_search_people(self.service_mock, "test"))

        # Verify
        self.service_mock.search_people.assert_called_once_with("test", 10, 0)
        result_json = json.loads(result)
        self.assertIn("elements", result_json)

    def test_linkedin_post_update(self):
        """Test linkedin_post_update tool function"""
        # Set up mock
        post_result = {"id": "post123"}
        self.service_mock.post_update = MagicMock(return_value=post_result)

        # Execute function
        result = asyncio.run(linkedin_post_update(
            self.service_mock, "Test post"))

        # Verify
        self.service_mock.post_update.assert_called_once_with(
            "Test post", "PUBLIC")
        result_json = json.loads(result)
        self.assertEqual(result_json["id"], "post123")


if __name__ == "__main__":
    unittest.main()
