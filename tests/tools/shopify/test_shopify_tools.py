#!/usr/bin/env python3
"""
Tests for the Shopify API tools.
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os

from app.tools.base.registry import clear_registry, get_all_tools, get_tools_by_category
from app.tools.shopify.service import ShopifyService
from app.tools.shopify.tools import (
    # Product tools
    get_products,
    get_product,
    create_product,
    update_product,
    delete_product,

    # Order tools
    get_orders,
    get_order,
    create_order,
    cancel_order,

    # Customer tools
    get_customers,
    get_customer,
    create_customer,
    update_customer,

    # Inventory tools
    get_inventory,
    update_inventory,

    # Collection tools
    get_collections,
    create_collection,
    update_collection
)


class TestShopifyTools(unittest.TestCase):
    """Test cases for Shopify tools"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock service
        self.service = MagicMock(spec=ShopifyService)
        self.service.initialized = True

    def tearDown(self):
        """Clean up after tests"""
        clear_registry()

    def test_tool_registration(self):
        """Test that tools are properly registered"""
        # Get all registered tools
        tools = get_all_tools()

        # Get all tools in shopify category
        shopify_tools = get_tools_by_category("shopify")

        # Check that our tools are registered
        self.assertIn("shopify_get_products", tools)
        self.assertIn("shopify_get_product", tools)
        self.assertIn("shopify_create_product", tools)
        self.assertIn("shopify_update_product", tools)
        self.assertIn("shopify_delete_product", tools)

        self.assertIn("shopify_get_orders", tools)
        self.assertIn("shopify_get_order", tools)
        self.assertIn("shopify_create_order", tools)
        self.assertIn("shopify_cancel_order", tools)

        self.assertIn("shopify_get_customers", tools)
        self.assertIn("shopify_get_customer", tools)
        self.assertIn("shopify_create_customer", tools)
        self.assertIn("shopify_update_customer", tools)

        self.assertIn("shopify_get_inventory", tools)
        self.assertIn("shopify_update_inventory", tools)

        self.assertIn("shopify_get_collections", tools)
        self.assertIn("shopify_create_collection", tools)
        self.assertIn("shopify_update_collection", tools)

        # Check that all tools have the correct category
        for tool_name, tool_info in shopify_tools.items():
            self.assertEqual(tool_info["category"], "shopify")
            self.assertEqual(tool_info["service_class"], ShopifyService)
            self.assertIsNotNone(tool_info["description"])

    # Product Tool Tests

    async def test_get_products(self):
        """Test get_products tool"""
        # Setup mock service method
        products_data = {"products": [{"id": 1, "title": "Test Product"}]}
        self.service.get_products = AsyncMock(return_value=products_data)

        # Call the tool
        result = await get_products(self.service, limit=10, vendor="Test Vendor")

        # Verify
        self.service.get_products.assert_called_with(
            10, None, None, None, "Test Vendor")
        self.assertIsInstance(result, str)

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, products_data)

    async def test_get_product(self):
        """Test get_product tool"""
        # Setup mock service method
        product_data = {"product": {"id": 1, "title": "Test Product"}}
        self.service.get_product = AsyncMock(return_value=product_data)

        # Call the tool
        result = await get_product(self.service, product_id="1")

        # Verify
        self.service.get_product.assert_called_with("1")
        self.assertIsInstance(result, str)

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, product_data)

        # Test with missing product_id
        with self.assertRaises(ValueError):
            await get_product(self.service, product_id="")

    async def test_create_product(self):
        """Test create_product tool"""
        # Setup mock service method
        product_data = {"product": {"id": 1, "title": "New Product"}}
        self.service.create_product = AsyncMock(return_value=product_data)

        # Call the tool
        result = await create_product(
            self.service,
            title="New Product",
            product_type="Test Type",
            vendor="Test Vendor"
        )

        # Verify
        self.service.create_product.assert_called_once()
        product_arg = self.service.create_product.call_args[0][0]
        self.assertEqual(product_arg["title"], "New Product")
        self.assertEqual(product_arg["product_type"], "Test Type")
        self.assertEqual(product_arg["vendor"], "Test Vendor")

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, product_data)

        # Test with missing title
        with self.assertRaises(ValueError):
            await create_product(self.service, title="")

    async def test_update_product(self):
        """Test update_product tool"""
        # Setup mock service method
        product_data = {"product": {"id": 1, "title": "Updated Product"}}
        self.service.update_product = AsyncMock(return_value=product_data)

        # Call the tool
        result = await update_product(
            self.service,
            product_id="1",
            title="Updated Product"
        )

        # Verify
        self.service.update_product.assert_called_once()
        self.assertEqual(self.service.update_product.call_args[0][0], "1")
        product_arg = self.service.update_product.call_args[0][1]
        self.assertEqual(product_arg["title"], "Updated Product")

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, product_data)

        # Test with missing product_id
        with self.assertRaises(ValueError):
            await update_product(self.service, product_id="")

        # Test with no update fields
        result = await update_product(self.service, product_id="1")
        self.assertIn("At least one field to update must be provided", result)

    async def test_delete_product(self):
        """Test delete_product tool"""
        # Setup mock service method
        self.service.delete_product = AsyncMock(return_value=None)

        # Call the tool
        result = await delete_product(self.service, product_id="1")

        # Verify
        self.service.delete_product.assert_called_with("1")
        self.assertIn("deleted successfully", result)

        # Test with missing product_id
        with self.assertRaises(ValueError):
            await delete_product(self.service, product_id="")

    # Order Tool Tests

    async def test_get_orders(self):
        """Test get_orders tool"""
        # Setup mock service method
        orders_data = {"orders": [{"id": 1, "name": "#1001"}]}
        self.service.get_orders = AsyncMock(return_value=orders_data)

        # Call the tool
        result = await get_orders(
            self.service,
            limit=10,
            status="open",
            financial_status="paid"
        )

        # Verify
        self.service.get_orders.assert_called_with(
            10, None, "open", "paid", None)
        self.assertIsInstance(result, str)

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, orders_data)

    # Customer Tool Tests

    async def test_create_customer(self):
        """Test create_customer tool"""
        # Setup mock service method
        customer_data = {"customer": {
            "id": 1, "first_name": "John", "last_name": "Doe"}}
        self.service.create_customer = AsyncMock(return_value=customer_data)

        # Call the tool
        result = await create_customer(
            self.service,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123-456-7890"
        )

        # Verify
        self.service.create_customer.assert_called_once()
        customer_arg = self.service.create_customer.call_args[0][0]
        self.assertEqual(customer_arg["first_name"], "John")
        self.assertEqual(customer_arg["last_name"], "Doe")
        self.assertEqual(customer_arg["email"], "john.doe@example.com")
        self.assertEqual(customer_arg["phone"], "123-456-7890")

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, customer_data)

        # Test with missing required fields
        with self.assertRaises(ValueError):
            await create_customer(self.service, first_name="", last_name="Doe", email="john.doe@example.com")

        with self.assertRaises(ValueError):
            await create_customer(self.service, first_name="John", last_name="", email="john.doe@example.com")

        with self.assertRaises(ValueError):
            await create_customer(self.service, first_name="John", last_name="Doe", email="")

    # Inventory Tool Tests

    async def test_update_inventory(self):
        """Test update_inventory tool"""
        # Setup mock service method
        inventory_data = {"inventory_level": {
            "inventory_item_id": 123, "available": 10}}
        self.service.adjust_inventory = AsyncMock(return_value=inventory_data)

        # Call the tool
        result = await update_inventory(
            self.service,
            inventory_item_id="123",
            location_id="456",
            adjustment=5
        )

        # Verify
        self.service.adjust_inventory.assert_called_with("123", "456", 5)
        self.assertIsInstance(result, str)

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, inventory_data)

        # Test with missing required fields
        with self.assertRaises(ValueError):
            await update_inventory(self.service, inventory_item_id="", location_id="456", adjustment=5)

        with self.assertRaises(ValueError):
            await update_inventory(self.service, inventory_item_id="123", location_id="", adjustment=5)

    # Collection Tool Tests

    async def test_create_collection(self):
        """Test create_collection tool"""
        # Setup mock service method
        collection_data = {"custom_collection": {
            "id": 1, "title": "New Collection"}}
        self.service.create_collection = AsyncMock(
            return_value=collection_data)

        # Call the tool
        result = await create_collection(
            self.service,
            title="New Collection",
            collection_type="custom",
            body_html="<p>Collection description</p>"
        )

        # Verify
        self.service.create_collection.assert_called_once()
        collection_arg = self.service.create_collection.call_args[0][0]
        collection_type_arg = self.service.create_collection.call_args[0][1]
        self.assertEqual(collection_arg["title"], "New Collection")
        self.assertEqual(
            collection_arg["body_html"], "<p>Collection description</p>")
        self.assertEqual(collection_type_arg, "custom")

        # Parse result and check
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result, collection_data)

        # Test with missing title
        with self.assertRaises(ValueError):
            await create_collection(self.service, title="")

        # Test with invalid collection_type
        with self.assertRaises(ValueError):
            await create_collection(self.service, title="New Collection", collection_type="invalid")

        # Test missing rules for smart collection
        with self.assertRaises(ValueError):
            await create_collection(self.service, title="New Collection", collection_type="smart")


if __name__ == '__main__':
    unittest.main()
