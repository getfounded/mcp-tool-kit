#!/usr/bin/env python3
"""
Shopify API service implementation for MCP toolkit.
"""
import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from app.tools.base.service import ToolServiceBase


class ShopifyService(ToolServiceBase):
    """Service to handle Shopify API operations"""

    def __init__(self):
        """Initialize Shopify service with default values"""
        super().__init__()
        self.shop_domain = None
        self.api_version = None
        self.api_key = None
        self.api_password = None
        self.access_token = None
        self.base_url = None
        self.headers = None

    def initialize(self) -> bool:
        """
        Initialize the Shopify service with credentials from environment variables.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Get credentials from environment variables
            self.shop_domain = self.get_env_var(
                "SHOPIFY_SHOP_DOMAIN", required=True)
            self.api_version = self.get_env_var(
                "SHOPIFY_API_VERSION", default="2023-10")
            self.api_key = self.get_env_var("SHOPIFY_API_KEY")
            self.api_password = self.get_env_var("SHOPIFY_API_PASSWORD")
            self.access_token = self.get_env_var("SHOPIFY_ACCESS_TOKEN")

            # Validate credentials
            if not ((self.api_key and self.api_password) or self.access_token):
                self.logger.error(
                    "Either (api_key and api_password) or access_token must be provided")
                return False

            # Set base URL for API calls
            self.base_url = f"https://{self.shop_domain}/admin/api/{self.api_version}/"

            # Set request headers
            self.headers = self._get_headers()

            # Create rate limiter (Shopify has a limit of 2 requests per second by default)
            self.create_rate_limiter("shopify_api", 2, 1.0)

            self.initialized = True
            self.logger.info("Shopify service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Shopify service: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate appropriate headers based on authentication method.

        Returns:
            Dict[str, str]: Headers for API requests
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.access_token:
            headers["X-Shopify-Access-Token"] = self.access_token

        return headers

    def _get_auth(self) -> Optional[tuple]:
        """
        Return appropriate auth tuple if using API key.

        Returns:
            Optional[tuple]: Auth tuple for requests or None
        """
        if self.api_key and self.api_password:
            return (self.api_key, self.api_password)
        return None

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                            data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Any:
        """
        Make a rate-limited request to Shopify API.

        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON data for request body

        Returns:
            Response data from API

        Raises:
            ValueError: If method is unsupported
            Exception: If API returns an error
        """
        self._is_initialized()

        # Apply rate limiting
        self.apply_rate_limit("shopify_api", 2, 1.0)

        url = urljoin(self.base_url, endpoint)
        auth = self._get_auth()

        import httpx
        async with httpx.AsyncClient() as client:
            if method.lower() == "get":
                response = await client.get(url, params=params, headers=self.headers, auth=auth)
            elif method.lower() == "post":
                response = await client.post(url, params=params, json=json_data, headers=self.headers, auth=auth)
            elif method.lower() == "put":
                response = await client.put(url, params=params, json=json_data, headers=self.headers, auth=auth)
            elif method.lower() == "delete":
                response = await client.delete(url, params=params, headers=self.headers, auth=auth)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for Shopify API response errors
            if response.status_code >= 400:
                error_msg = f"Shopify API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {json.dumps(error_detail)}"
                except:
                    error_msg += f" - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            # Parse response if it has content
            if response.status_code != 204 and response.content:  # No content
                return response.json()
            return None

    # Product operations
    async def get_products(self, limit: int = 50, page_info: Optional[str] = None,
                           collection_id: Optional[str] = None, product_type: Optional[str] = None,
                           vendor: Optional[str] = None) -> Dict:
        """
        Get a list of products from the Shopify store.

        Args:
            limit: Maximum number of products to return
            page_info: Pagination parameter from previous response
            collection_id: Filter by collection ID
            product_type: Filter by product type
            vendor: Filter by vendor name

        Returns:
            Dict containing product data
        """
        params = {"limit": limit}

        if page_info:
            params["page_info"] = page_info

        if collection_id:
            params["collection_id"] = collection_id

        if product_type:
            params["product_type"] = product_type

        if vendor:
            params["vendor"] = vendor

        return await self._make_request("get", "products.json", params=params)

    async def get_product(self, product_id: str) -> Dict:
        """
        Get a specific product by ID.

        Args:
            product_id: The ID of the product to retrieve

        Returns:
            Dict containing product data
        """
        return await self._make_request("get", f"products/{product_id}.json")

    async def create_product(self, product_data: Dict) -> Dict:
        """
        Create a new product.

        Args:
            product_data: Product data dictionary

        Returns:
            Dict containing the created product data
        """
        return await self._make_request("post", "products.json", json_data={"product": product_data})

    async def update_product(self, product_id: str, product_data: Dict) -> Dict:
        """
        Update an existing product.

        Args:
            product_id: The ID of the product to update
            product_data: Updated product data

        Returns:
            Dict containing the updated product data
        """
        return await self._make_request("put", f"products/{product_id}.json", json_data={"product": product_data})

    async def delete_product(self, product_id: str) -> None:
        """
        Delete a product.

        Args:
            product_id: The ID of the product to delete

        Returns:
            None
        """
        return await self._make_request("delete", f"products/{product_id}.json")

    # Order operations
    async def get_orders(self, limit: int = 50, page_info: Optional[str] = None,
                         status: Optional[str] = None, financial_status: Optional[str] = None,
                         fulfillment_status: Optional[str] = None) -> Dict:
        """
        Get a list of orders.

        Args:
            limit: Maximum number of orders to return
            page_info: Pagination parameter from previous response
            status: Filter by order status
            financial_status: Filter by financial status
            fulfillment_status: Filter by fulfillment status

        Returns:
            Dict containing order data
        """
        params = {"limit": limit}

        if page_info:
            params["page_info"] = page_info

        if status:
            params["status"] = status

        if financial_status:
            params["financial_status"] = financial_status

        if fulfillment_status:
            params["fulfillment_status"] = fulfillment_status

        return await self._make_request("get", "orders.json", params=params)

    async def get_order(self, order_id: str) -> Dict:
        """
        Get a specific order by ID.

        Args:
            order_id: The ID of the order to retrieve

        Returns:
            Dict containing order data
        """
        return await self._make_request("get", f"orders/{order_id}.json")

    async def create_order(self, order_data: Dict) -> Dict:
        """
        Create a new order.

        Args:
            order_data: Order data dictionary

        Returns:
            Dict containing the created order data
        """
        return await self._make_request("post", "orders.json", json_data={"order": order_data})

    async def update_order(self, order_id: str, order_data: Dict) -> Dict:
        """
        Update an existing order.

        Args:
            order_id: The ID of the order to update
            order_data: Updated order data

        Returns:
            Dict containing the updated order data
        """
        return await self._make_request("put", f"orders/{order_id}.json", json_data={"order": order_data})

    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> Dict:
        """
        Cancel an order.

        Args:
            order_id: The ID of the order to cancel
            reason: Reason for cancellation

        Returns:
            Dict containing the canceled order data
        """
        data = {}
        if reason:
            data["reason"] = reason

        return await self._make_request("post", f"orders/{order_id}/cancel.json", json_data=data)

    # Customer operations
    async def get_customers(self, limit: int = 50, page_info: Optional[str] = None,
                            query: Optional[str] = None) -> Dict:
        """
        Get a list of customers.

        Args:
            limit: Maximum number of customers to return
            page_info: Pagination parameter from previous response
            query: Search query for filtering customers

        Returns:
            Dict containing customer data
        """
        params = {"limit": limit}

        if page_info:
            params["page_info"] = page_info

        if query:
            params["query"] = query

        return await self._make_request("get", "customers.json", params=params)

    async def get_customer(self, customer_id: str) -> Dict:
        """
        Get a specific customer by ID.

        Args:
            customer_id: The ID of the customer to retrieve

        Returns:
            Dict containing customer data
        """
        return await self._make_request("get", f"customers/{customer_id}.json")

    async def create_customer(self, customer_data: Dict) -> Dict:
        """
        Create a new customer.

        Args:
            customer_data: Customer data dictionary

        Returns:
            Dict containing the created customer data
        """
        return await self._make_request("post", "customers.json", json_data={"customer": customer_data})

    async def update_customer(self, customer_id: str, customer_data: Dict) -> Dict:
        """
        Update an existing customer.

        Args:
            customer_id: The ID of the customer to update
            customer_data: Updated customer data

        Returns:
            Dict containing the updated customer data
        """
        return await self._make_request("put", f"customers/{customer_id}.json", json_data={"customer": customer_data})

    # Inventory operations
    async def get_inventory_levels(self, inventory_item_ids: Optional[List[str]] = None,
                                   location_id: Optional[str] = None) -> Dict:
        """
        Get inventory levels.

        Args:
            inventory_item_ids: List of inventory item IDs to filter by
            location_id: Location ID to filter by

        Returns:
            Dict containing inventory level data
        """
        params = {}

        if inventory_item_ids:
            params["inventory_item_ids"] = ",".join(
                str(id) for id in inventory_item_ids)

        if location_id:
            params["location_id"] = location_id

        return await self._make_request("get", "inventory_levels.json", params=params)

    async def adjust_inventory(self, inventory_item_id: str, location_id: str, adjustment: int) -> Dict:
        """
        Adjust inventory level.

        Args:
            inventory_item_id: The ID of the inventory item
            location_id: The ID of the location
            adjustment: Adjustment value (positive or negative)

        Returns:
            Dict containing adjusted inventory data
        """
        data = {
            "inventory_item_id": inventory_item_id,
            "location_id": location_id,
            "available_adjustment": adjustment
        }

        return await self._make_request("post", "inventory_levels/adjust.json", json_data=data)

    # Collections operations
    async def get_collections(self, limit: int = 50, page_info: Optional[str] = None) -> Dict:
        """
        Get a list of collections (both custom and smart).

        Args:
            limit: Maximum number of collections to return
            page_info: Pagination parameter from previous response

        Returns:
            Dict containing collection data
        """
        params = {"limit": limit}

        if page_info:
            params["page_info"] = page_info

        # First get custom collections
        custom = await self._make_request("get", "custom_collections.json", params=params)

        # Then get smart collections
        smart = await self._make_request("get", "smart_collections.json", params=params)

        # Combine them
        result = {"custom_collections": custom.get("custom_collections", [])}
        result["smart_collections"] = smart.get("smart_collections", [])

        return result

    async def create_collection(self, collection_data: Dict, collection_type: str = "custom") -> Dict:
        """
        Create a new collection.

        Args:
            collection_data: Collection data dictionary
            collection_type: Type of collection ("custom" or "smart")

        Returns:
            Dict containing the created collection data
        """
        if collection_type == "custom":
            return await self._make_request("post", "custom_collections.json",
                                            json_data={"custom_collection": collection_data})
        else:
            return await self._make_request("post", "smart_collections.json",
                                            json_data={"smart_collection": collection_data})

    async def update_collection(self, collection_id: str, collection_data: Dict,
                                collection_type: str = "custom") -> Dict:
        """
        Update an existing collection.

        Args:
            collection_id: The ID of the collection to update
            collection_data: Updated collection data
            collection_type: Type of collection ("custom" or "smart")

        Returns:
            Dict containing the updated collection data
        """
        if collection_type == "custom":
            return await self._make_request("put", f"custom_collections/{collection_id}.json",
                                            json_data={"custom_collection": collection_data})
        else:
            return await self._make_request("put", f"smart_collections/{collection_id}.json",
                                            json_data={"smart_collection": collection_data})
