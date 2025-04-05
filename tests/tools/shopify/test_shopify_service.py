#!/usr/bin/env python3
"""
Tests for the Shopify API service.
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os

from app.tools.shopify.service import ShopifyService


class TestShopifyService(unittest.TestCase):
    """Test cases for ShopifyService class"""

    def setUp(self):
        """Set up test fixtures"""
        # Save original environment variables
        self.original_env = os.environ.copy()

        # Set up test environment variables
        os.environ["SHOPIFY_SHOP_DOMAIN"] = "test-store.myshopify.com"
        os.environ["SHOPIFY_API_VERSION"] = "2023-10"
        os.environ["SHOPIFY_ACCESS_TOKEN"] = "test_access_token"

        # Create service
        self.service = ShopifyService()

    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_init(self):
        """Test service initialization"""
        service = ShopifyService()
        self.assertFalse(service.initialized)
        self.assertIsNone(service.shop_domain)
        self.assertIsNone(service.api_version)
        self.assertIsNone(service.access_token)
        self.assertIsNone(service.base_url)
        self.assertIsNone(service.headers)

    def test_initialize(self):
        """Test service initialization with environment variables"""
        self.service.initialize()

        self.assertTrue(self.service.initialized)
        self.assertEqual(self.service.shop_domain, "test-store.myshopify.com")
        self.assertEqual(self.service.api_version, "2023-10")
        self.assertEqual(self.service.access_token, "test_access_token")
        self.assertEqual(self.service.base_url,
                         "https://test-store.myshopify.com/admin/api/2023-10/")
        self.assertIn("X-Shopify-Access-Token", self.service.headers)
        self.assertEqual(
            self.service.headers["X-Shopify-Access-Token"], "test_access_token")
        self.assertIn("Content-Type", self.service.headers)
        self.assertEqual(
            self.service.headers["Content-Type"], "application/json")

    def test_initialize_with_api_key(self):
        """Test service initialization with API key and password"""
        # Clear access token and set API key/password
        os.environ.pop("SHOPIFY_ACCESS_TOKEN")
        os.environ["SHOPIFY_API_KEY"] = "test_api_key"
        os.environ["SHOPIFY_API_PASSWORD"] = "test_api_password"

        service = ShopifyService()
        service.initialize()

        self.assertTrue(service.initialized)
        self.assertEqual(service.api_key, "test_api_key")
        self.assertEqual(service.api_password, "test_api_password")
        self.assertNotIn("X-Shopify-Access-Token", service.headers)

        # Check auth tuple
        auth = service._get_auth()
        self.assertEqual(auth, ("test_api_key", "test_api_password"))

    def test_initialize_missing_credentials(self):
        """Test service initialization with missing credentials"""
        # Clear credentials
        os.environ.pop("SHOPIFY_ACCESS_TOKEN")

        service = ShopifyService()
        result = service.initialize()

        self.assertFalse(result)
        self.assertFalse(service.initialized)

    def test_initialize_missing_shop_domain(self):
        """Test service initialization with missing shop domain"""
        # Clear shop domain
        os.environ.pop("SHOPIFY_SHOP_DOMAIN")

        service = ShopifyService()

        # Should raise ValueError due to required env var
        with self.assertRaises(ValueError):
            service.initialize()

    @patch('httpx.AsyncClient.get')
    async def test_make_request_get(self, mock_get):
        """Test _make_request GET method"""
        # Initialize service
        self.service.initialize()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "products": [{"id": 1, "title": "Test Product"}]}
        mock_get.return_value = mock_response

        # Make request
        result = await self.service._make_request("get", "products.json", params={"limit": 10})

        # Verify
        mock_get.assert_called_once()
        self.assertEqual(
            result, {"products": [{"id": 1, "title": "Test Product"}]})

    @patch('httpx.AsyncClient.post')
    async def test_make_request_post(self, mock_post):
        """Test _make_request POST method"""
        # Initialize service
        self.service.initialize()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "product": {"id": 1, "title": "Test Product"}}
        mock_post.return_value = mock_response

        # Make request
        result = await self.service._make_request("post", "products.json",
                                                  json_data={"product": {"title": "Test Product"}})

        # Verify
        mock_post.assert_called_once()
        self.assertEqual(
            result, {"product": {"id": 1, "title": "Test Product"}})

    @patch('httpx.AsyncClient.put')
    async def test_make_request_put(self, mock_put):
        """Test _make_request PUT method"""
        # Initialize service
        self.service.initialize()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "product": {"id": 1, "title": "Updated Product"}}
        mock_put.return_value = mock_response

        # Make request
        result = await self.service._make_request("put", "products/1.json",
                                                  json_data={"product": {"title": "Updated Product"}})

        # Verify
        mock_put.assert_called_once()
        self.assertEqual(
            result, {"product": {"id": 1, "title": "Updated Product"}})

    @patch('httpx.AsyncClient.delete')
    async def test_make_request_delete(self, mock_delete):
        """Test _make_request DELETE method"""
        # Initialize service
        self.service.initialize()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.content = b''
        mock_delete.return_value = mock_response

        # Make request
        result = await self.service._make_request("delete", "products/1.json")

        # Verify
        mock_delete.assert_called_once()
        self.assertIsNone(result)

    @patch('httpx.AsyncClient.get')
    async def test_make_request_error(self, mock_get):
        """Test _make_request error handling"""
        # Initialize service
        self.service.initialize()

        # Setup mock response with error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errors": "Not found"}
        mock_get.return_value = mock_response

        # Make request - should raise exception
        with self.assertRaises(Exception) as context:
            await self.service._make_request("get", "products/99999.json")

        self.assertIn("Shopify API error: 404", str(context.exception))
        self.assertIn("Not found", str(context.exception))

    @patch('httpx.AsyncClient.get')
    async def test_get_products(self, mock_get):
        """Test get_products method"""
        # Initialize service
        self.service.initialize()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "products": [{"id": 1, "title": "Test Product"}]}
        mock_get.return_value = mock_response

        # Get products
        result = await self.service.get_products(limit=10, vendor="Test Vendor")

        # Verify
        expected_url = "https://test-store.myshopify.com/admin/api/2023-10/products.json"
        expected_params = {"limit": 10, "vendor": "Test Vendor"}
        mock_get.assert_called_with(expected_url, params=expected_params,
                                    headers=self.service.headers, auth=None)
        self.assertEqual(
            result, {"products": [{"id": 1, "title": "Test Product"}]})

    @patch('httpx.AsyncClient.get')
    async def test_get_orders(self, mock_get):
        """Test get_orders method"""
        # Initialize service
        self.service.initialize()

        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orders": [{"id": 1, "name": "#1001"}]}
        mock_get.return_value = mock_response

        # Get orders
        result = await self.service.get_orders(limit=10, status="open")

        # Verify
        expected_url = "https://test-store.myshopify.com/admin/api/2023-10/orders.json"
        expected_params = {"limit": 10, "status": "open"}
        mock_get.assert_called_with(expected_url, params=expected_params,
                                    headers=self.service.headers, auth=None)
        self.assertEqual(result, {"orders": [{"id": 1, "name": "#1001"}]})

    @patch('httpx.AsyncClient.get')
    async def test_get_collections(self, mock_get):
        """Test get_collections method"""
        # Initialize service
        self.service.initialize()

        # Setup mock responses for both collection types
        custom_response = MagicMock()
        custom_response.status_code = 200
        custom_response.json.return_value = {
            "custom_collections": [{"id": 1, "title": "Custom Collection"}]}

        smart_response = MagicMock()
        smart_response.status_code = 200
        smart_response.json.return_value = {
            "smart_collections": [{"id": 2, "title": "Smart Collection"}]}

        mock_get.side_effect = [custom_response, smart_response]

        # Get collections
        result = await self.service.get_collections(limit=10)

        # Verify
        expected_url_custom = "https://test-store.myshopify.com/admin/api/2023-10/custom_collections.json"
        expected_url_smart = "https://test-store.myshopify.com/admin/api/2023-10/smart_collections.json"
        expected_params = {"limit": 10}

        # Check that both collection types were fetched
        self.assertEqual(mock_get.call_count, 2)

        # Check the result contains both types
        self.assertIn("custom_collections", result)
        self.assertIn("smart_collections", result)
        self.assertEqual(result["custom_collections"][0]
                         ["title"], "Custom Collection")
        self.assertEqual(result["smart_collections"][0]
                         ["title"], "Smart Collection")


if __name__ == '__main__':
    unittest.main()
