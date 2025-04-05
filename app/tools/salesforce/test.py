#!/usr/bin/env python3
"""
Unit tests for Salesforce API tools.
"""
import unittest
import os
import json
import asyncio
from unittest.mock import patch, MagicMock

# Import the service and tools
from app.tools.salesforce.service import SalesforceService
from app.tools.salesforce.tools import *


class TestSalesforceService(unittest.TestCase):
    """Test the Salesforce service class"""

    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["SF_USERNAME"] = "test@example.com"
        os.environ["SF_PASSWORD"] = "testpassword"
        os.environ["SF_SECURITY_TOKEN"] = "testsecuritytoken"

        # Create service instance
        self.service = SalesforceService()

        # Mock the Salesforce module
        self.sf_mock = MagicMock()
        self.service.sf_module = self.sf_mock

        # Initialize service
        self.service.initialize()

    def test_initialize(self):
        """Test service initialization"""
        self.assertTrue(self.service.initialized)
        self.assertEqual(self.service.username, "test@example.com")
        self.assertEqual(self.service.password, "testpassword")
        self.assertEqual(self.service.security_token, "testsecuritytoken")

    @patch('app.tools.salesforce.service.SalesforceService._ensure_connected')
    def test_query(self, mock_ensure_connected):
        """Test query method"""
        # Mock client and response
        mock_client = MagicMock()
        mock_query_result = {
            "records": [{"Id": "001", "Name": "Test Account"}],
            "totalSize": 1,
            "done": True
        }
        mock_client.query.return_value = mock_query_result
        self.service.client = mock_client

        # Execute query
        result = asyncio.run(self.service.query(
            "SELECT Id, Name FROM Account"))

        # Verify
        mock_client.query.assert_called_once_with(
            "SELECT Id, Name FROM Account")
        self.assertEqual(result["totalSize"], 1)
        self.assertEqual(result["records"][0]["Name"], "Test Account")

    @patch('app.tools.salesforce.service.SalesforceService._ensure_connected')
    def test_create(self, mock_ensure_connected):
        """Test create method"""
        # Mock client and response
        mock_client = MagicMock()
        mock_account = MagicMock()
        mock_account.create.return_value = {"success": True, "id": "001"}
        setattr(mock_client, "Account", mock_account)
        self.service.client = mock_client

        # Execute create
        data = {"Name": "Test Account"}
        result = asyncio.run(self.service.create("Account", data))

        # Verify
        mock_account.create.assert_called_once_with(data)
        self.assertTrue(result["success"])
        self.assertEqual(result["id"], "001")

    @patch('app.tools.salesforce.service.SalesforceService._ensure_connected')
    def test_update(self, mock_ensure_connected):
        """Test update method"""
        # Mock client and response
        mock_client = MagicMock()
        mock_account = MagicMock()
        mock_account.update.return_value = 204  # Success status code
        setattr(mock_client, "Account", mock_account)
        self.service.client = mock_client

        # Execute update
        data = {"Name": "Updated Account"}
        result = asyncio.run(self.service.update("Account", "001", data))

        # Verify
        mock_account.update.assert_called_once_with("001", data)
        self.assertTrue(result["success"])
        self.assertEqual(result["id"], "001")

    @patch('app.tools.salesforce.service.SalesforceService._ensure_connected')
    def test_delete(self, mock_ensure_connected):
        """Test delete method"""
        # Mock client and response
        mock_client = MagicMock()
        mock_account = MagicMock()
        mock_account.delete.return_value = 204  # Success status code
        setattr(mock_client, "Account", mock_account)
        self.service.client = mock_client

        # Execute delete
        result = asyncio.run(self.service.delete("Account", "001"))

        # Verify
        mock_account.delete.assert_called_once_with("001")
        self.assertTrue(result["success"])
        self.assertEqual(result["id"], "001")


class TestSalesforceTools(unittest.TestCase):
    """Test the Salesforce tool functions"""

    def setUp(self):
        """Set up test environment"""
        # Create service mock
        self.service_mock = MagicMock(spec=SalesforceService)

    def test_sf_query(self):
        """Test sf_query tool function"""
        # Set up mock
        query_result = {
            "records": [{"Id": "001", "Name": "Test Account"}],
            "totalSize": 1,
            "done": True
        }
        self.service_mock.query = MagicMock(return_value=query_result)

        # Execute function
        result = asyncio.run(
            sf_query(self.service_mock, "SELECT Id, Name FROM Account"))

        # Verify
        self.service_mock.query.assert_called_once_with(
            "SELECT Id, Name FROM Account")
        result_json = json.loads(result)
        self.assertEqual(result_json["totalSize"], 1)
        self.assertEqual(result_json["records"][0]["Name"], "Test Account")

    def test_sf_create(self):
        """Test sf_create tool function"""
        # Set up mock
        create_result = {
            "success": True,
            "id": "001",
            "errors": []
        }
        self.service_mock.create = MagicMock(return_value=create_result)

        # Execute function
        data = {"Name": "Test Account"}
        result = asyncio.run(sf_create(self.service_mock, "Account", data))

        # Verify
        self.service_mock.create.assert_called_once_with("Account", data)
        result_json = json.loads(result)
        self.assertTrue(result_json["success"])
        self.assertEqual(result_json["id"], "001")

    def test_sf_update(self):
        """Test sf_update tool function"""
        # Set up mock
        update_result = {
            "success": True,
            "id": "001",
            "status_code": 204
        }
        self.service_mock.update = MagicMock(return_value=update_result)

        # Execute function
        data = {"Name": "Updated Account"}
        result = asyncio.run(
            sf_update(self.service_mock, "Account", "001", data))

        # Verify
        self.service_mock.update.assert_called_once_with(
            "Account", "001", data)
        result_json = json.loads(result)
        self.assertTrue(result_json["success"])
        self.assertEqual(result_json["id"], "001")

    def test_sf_delete(self):
        """Test sf_delete tool function"""
        # Set up mock
        delete_result = {
            "success": True,
            "id": "001",
            "status_code": 204
        }
        self.service_mock.delete = MagicMock(return_value=delete_result)

        # Execute function
        result = asyncio.run(sf_delete(self.service_mock, "Account", "001"))

        # Verify
        self.service_mock.delete.assert_called_once_with("Account", "001")
        result_json = json.loads(result)
        self.assertTrue(result_json["success"])
        self.assertEqual(result_json["id"], "001")


if __name__ == "__main__":
    unittest.main()
