#!/usr/bin/env python3
"""
Shopify API tools implementations.
"""
import json
from typing import Dict, List, Optional, Any, Union

from app.tools.base.registry import register_tool
from .service import ShopifyService

# Product Tools


@register_tool(
    name="shopify_get_products",
    category="shopify",
    service_class=ShopifyService,
    description="Get a list of products from the Shopify store"
)
async def get_products(self, limit: int = 50, page_info: Optional[str] = None,
                       collection_id: Optional[str] = None, product_type: Optional[str] = None,
                       vendor: Optional[str] = None) -> str:
    """
    Get a list of products from the Shopify store.

    Args:
        limit: Maximum number of products to return (default: 50, max: 250)
        page_info: Pagination parameter (from previous response)
        collection_id: Filter by collection ID
        product_type: Filter by product type
        vendor: Filter by vendor name

    Returns:
        JSON string containing product data
    """
    try:
        result = await self.get_products(limit, page_info, collection_id, product_type, vendor)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving products: {str(e)}"


@register_tool(
    name="shopify_get_product",
    category="shopify",
    service_class=ShopifyService,
    description="Get a specific product by ID"
)
async def get_product(self, product_id: str) -> str:
    """
    Get a specific product by ID.

    Args:
        product_id: The ID of the product to retrieve

    Returns:
        JSON string containing product data
    """
    if not product_id:
        raise ValueError("product_id is required")

    try:
        result = await self.get_product(product_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving product: {str(e)}"


@register_tool(
    name="shopify_create_product",
    category="shopify",
    service_class=ShopifyService,
    description="Create a new product in the Shopify store"
)
async def create_product(self, title: str, product_type: Optional[str] = None,
                         vendor: Optional[str] = None, body_html: Optional[str] = None,
                         variants: Optional[List[Dict]] = None, images: Optional[List[Dict]] = None,
                         tags: Optional[str] = None) -> str:
    """
    Create a new product in the Shopify store.

    Args:
        title: Product title (required)
        product_type: Type of product
        vendor: Vendor name
        body_html: Product description in HTML format
        variants: List of variant objects
        images: List of image objects
        tags: Comma-separated list of tags

    Returns:
        JSON string containing the created product data
    """
    if not title:
        raise ValueError("title is required")

    try:
        product_data = {
            "title": title
        }

        if product_type:
            product_data["product_type"] = product_type

        if vendor:
            product_data["vendor"] = vendor

        if body_html:
            product_data["body_html"] = body_html

        if variants:
            product_data["variants"] = variants

        if images:
            product_data["images"] = images

        if tags:
            product_data["tags"] = tags

        result = await self.create_product(product_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating product: {str(e)}"


@register_tool(
    name="shopify_update_product",
    category="shopify",
    service_class=ShopifyService,
    description="Update an existing product in the Shopify store"
)
async def update_product(self, product_id: str, title: Optional[str] = None,
                         product_type: Optional[str] = None, vendor: Optional[str] = None,
                         body_html: Optional[str] = None, variants: Optional[List[Dict]] = None,
                         images: Optional[List[Dict]] = None, tags: Optional[str] = None) -> str:
    """
    Update an existing product in the Shopify store.

    Args:
        product_id: The ID of the product to update (required)
        title: Product title
        product_type: Type of product
        vendor: Vendor name
        body_html: Product description in HTML format
        variants: List of variant objects
        images: List of image objects
        tags: Comma-separated list of tags

    Returns:
        JSON string containing the updated product data
    """
    if not product_id:
        raise ValueError("product_id is required")

    try:
        # Build product data from parameters that are provided
        product_data = {}

        if title:
            product_data["title"] = title

        if product_type:
            product_data["product_type"] = product_type

        if vendor:
            product_data["vendor"] = vendor

        if body_html:
            product_data["body_html"] = body_html

        if variants:
            product_data["variants"] = variants

        if images:
            product_data["images"] = images

        if tags:
            product_data["tags"] = tags

        # If no parameters were provided, return an error
        if not product_data:
            return "Error: At least one field to update must be provided"

        result = await self.update_product(product_id, product_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating product: {str(e)}"


@register_tool(
    name="shopify_delete_product",
    category="shopify",
    service_class=ShopifyService,
    description="Delete a product from the Shopify store"
)
async def delete_product(self, product_id: str) -> str:
    """
    Delete a product from the Shopify store.

    Args:
        product_id: The ID of the product to delete (required)

    Returns:
        Confirmation message
    """
    if not product_id:
        raise ValueError("product_id is required")

    try:
        await self.delete_product(product_id)
        return f"Product {product_id} deleted successfully"
    except Exception as e:
        return f"Error deleting product: {str(e)}"

# Order Tools


@register_tool(
    name="shopify_get_orders",
    category="shopify",
    service_class=ShopifyService,
    description="Get a list of orders from the Shopify store"
)
async def get_orders(self, limit: int = 50, page_info: Optional[str] = None,
                     status: Optional[str] = None, financial_status: Optional[str] = None,
                     fulfillment_status: Optional[str] = None) -> str:
    """
    Get a list of orders from the Shopify store.

    Args:
        limit: Maximum number of orders to return (default: 50, max: 250)
        page_info: Pagination parameter (from previous response)
        status: Filter by order status (e.g., 'open', 'closed', 'any')
        financial_status: Filter by financial status (e.g., 'pending', 'paid', 'refunded')
        fulfillment_status: Filter by fulfillment status (e.g., 'fulfilled', 'partial', 'unfulfilled')

    Returns:
        JSON string containing order data
    """
    try:
        result = await self.get_orders(limit, page_info, status, financial_status, fulfillment_status)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving orders: {str(e)}"


@register_tool(
    name="shopify_get_order",
    category="shopify",
    service_class=ShopifyService,
    description="Get a specific order by ID"
)
async def get_order(self, order_id: str) -> str:
    """
    Get a specific order by ID.

    Args:
        order_id: The ID of the order to retrieve

    Returns:
        JSON string containing order data
    """
    if not order_id:
        raise ValueError("order_id is required")

    try:
        result = await self.get_order(order_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving order: {str(e)}"


@register_tool(
    name="shopify_create_order",
    category="shopify",
    service_class=ShopifyService,
    description="Create a new order in the Shopify store"
)
async def create_order(self, line_items: List[Dict], customer: Optional[Dict] = None,
                       shipping_address: Optional[Dict] = None, billing_address: Optional[Dict] = None,
                       email: Optional[str] = None, note: Optional[str] = None) -> str:
    """
    Create a new order in the Shopify store.

    Args:
        line_items: List of line item objects (required)
        customer: Customer object
        shipping_address: Shipping address object
        billing_address: Billing address object
        email: Customer email
        note: Order note

    Returns:
        JSON string containing the created order data
    """
    if not line_items:
        raise ValueError("line_items is required")

    try:
        order_data = {
            "line_items": line_items
        }

        if customer:
            order_data["customer"] = customer

        if shipping_address:
            order_data["shipping_address"] = shipping_address

        if billing_address:
            order_data["billing_address"] = billing_address

        if email:
            order_data["email"] = email

        if note:
            order_data["note"] = note

        result = await self.create_order(order_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating order: {str(e)}"


@register_tool(
    name="shopify_cancel_order",
    category="shopify",
    service_class=ShopifyService,
    description="Cancel an order in the Shopify store"
)
async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> str:
    """
    Cancel an order in the Shopify store.

    Args:
        order_id: The ID of the order to cancel (required)
        reason: Reason for cancellation

    Returns:
        JSON string containing the canceled order data
    """
    if not order_id:
        raise ValueError("order_id is required")

    try:
        result = await self.cancel_order(order_id, reason)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error canceling order: {str(e)}"

# Customer Tools


@register_tool(
    name="shopify_get_customers",
    category="shopify",
    service_class=ShopifyService,
    description="Get a list of customers from the Shopify store"
)
async def get_customers(self, limit: int = 50, page_info: Optional[str] = None,
                        query: Optional[str] = None) -> str:
    """
    Get a list of customers from the Shopify store.

    Args:
        limit: Maximum number of customers to return (default: 50, max: 250)
        page_info: Pagination parameter (from previous response)
        query: Search query for filtering customers

    Returns:
        JSON string containing customer data
    """
    try:
        result = await self.get_customers(limit, page_info, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving customers: {str(e)}"


@register_tool(
    name="shopify_get_customer",
    category="shopify",
    service_class=ShopifyService,
    description="Get a specific customer by ID"
)
async def get_customer(self, customer_id: str) -> str:
    """
    Get a specific customer by ID.

    Args:
        customer_id: The ID of the customer to retrieve

    Returns:
        JSON string containing customer data
    """
    if not customer_id:
        raise ValueError("customer_id is required")

    try:
        result = await self.get_customer(customer_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving customer: {str(e)}"


@register_tool(
    name="shopify_create_customer",
    category="shopify",
    service_class=ShopifyService,
    description="Create a new customer in the Shopify store"
)
async def create_customer(self, first_name: str, last_name: str, email: str,
                          phone: Optional[str] = None, verified_email: bool = False,
                          addresses: Optional[List[Dict]] = None, note: Optional[str] = None) -> str:
    """
    Create a new customer in the Shopify store.

    Args:
        first_name: Customer's first name (required)
        last_name: Customer's last name (required)
        email: Customer's email address (required)
        phone: Customer's phone number
        verified_email: Whether the customer's email is verified
        addresses: List of address objects
        note: Customer note

    Returns:
        JSON string containing the created customer data
    """
    if not first_name:
        raise ValueError("first_name is required")

    if not last_name:
        raise ValueError("last_name is required")

    if not email:
        raise ValueError("email is required")

    try:
        customer_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "verified_email": verified_email
        }

        if phone:
            customer_data["phone"] = phone

        if addresses:
            customer_data["addresses"] = addresses

        if note:
            customer_data["note"] = note

        result = await self.create_customer(customer_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating customer: {str(e)}"


@register_tool(
    name="shopify_update_customer",
    category="shopify",
    service_class=ShopifyService,
    description="Update an existing customer in the Shopify store"
)
async def update_customer(self, customer_id: str, first_name: Optional[str] = None,
                          last_name: Optional[str] = None, email: Optional[str] = None,
                          phone: Optional[str] = None, addresses: Optional[List[Dict]] = None,
                          note: Optional[str] = None) -> str:
    """
    Update an existing customer in the Shopify store.

    Args:
        customer_id: The ID of the customer to update (required)
        first_name: Customer's first name
        last_name: Customer's last name
        email: Customer's email address
        phone: Customer's phone number
        addresses: List of address objects
        note: Customer note

    Returns:
        JSON string containing the updated customer data
    """
    if not customer_id:
        raise ValueError("customer_id is required")

    try:
        # Build customer data from parameters that are provided
        customer_data = {}

        if first_name:
            customer_data["first_name"] = first_name

        if last_name:
            customer_data["last_name"] = last_name

        if email:
            customer_data["email"] = email

        if phone:
            customer_data["phone"] = phone

        if addresses:
            customer_data["addresses"] = addresses

        if note:
            customer_data["note"] = note

        # If no parameters were provided, return an error
        if not customer_data:
            return "Error: At least one field to update must be provided"

        result = await self.update_customer(customer_id, customer_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating customer: {str(e)}"

# Inventory Tools


@register_tool(
    name="shopify_get_inventory",
    category="shopify",
    service_class=ShopifyService,
    description="Get inventory levels from the Shopify store"
)
async def get_inventory(self, inventory_item_ids: Optional[List[str]] = None,
                        location_id: Optional[str] = None) -> str:
    """
    Get inventory levels from the Shopify store.

    Args:
        inventory_item_ids: List of inventory item IDs to filter by
        location_id: Location ID to filter by

    Returns:
        JSON string containing inventory data
    """
    try:
        result = await self.get_inventory_levels(inventory_item_ids, location_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving inventory: {str(e)}"


@register_tool(
    name="shopify_update_inventory",
    category="shopify",
    service_class=ShopifyService,
    description="Update inventory levels in the Shopify store"
)
async def update_inventory(self, inventory_item_id: str, location_id: str, adjustment: int) -> str:
    """
    Update inventory levels in the Shopify store.

    Args:
        inventory_item_id: The ID of the inventory item (required)
        location_id: The ID of the location (required)
        adjustment: Adjustment value (positive or negative) (required)

    Returns:
        JSON string containing the updated inventory data
    """
    if not inventory_item_id:
        raise ValueError("inventory_item_id is required")

    if not location_id:
        raise ValueError("location_id is required")

    try:
        result = await self.adjust_inventory(inventory_item_id, location_id, adjustment)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating inventory: {str(e)}"

# Collection Tools


@register_tool(
    name="shopify_get_collections",
    category="shopify",
    service_class=ShopifyService,
    description="Get collections from the Shopify store"
)
async def get_collections(self, limit: int = 50, page_info: Optional[str] = None) -> str:
    """
    Get collections from the Shopify store (both custom and smart collections).

    Args:
        limit: Maximum number of collections to return (default: 50, max: 250)
        page_info: Pagination parameter (from previous response)

    Returns:
        JSON string containing collection data
    """
    try:
        result = await self.get_collections(limit, page_info)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving collections: {str(e)}"


@register_tool(
    name="shopify_create_collection",
    category="shopify",
    service_class=ShopifyService,
    description="Create a new collection in the Shopify store"
)
async def create_collection(self, title: str, collection_type: str = "custom",
                            body_html: Optional[str] = None, image: Optional[Dict] = None,
                            published: bool = True, rules: Optional[List[Dict]] = None) -> str:
    """
    Create a new collection in the Shopify store.

    Args:
        title: Collection title (required)
        collection_type: Type of collection ("custom" or "smart") (default: "custom")
        body_html: Collection description in HTML format
        image: Image object
        published: Whether the collection is published
        rules: List of rules for smart collections

    Returns:
        JSON string containing the created collection data
    """
    if not title:
        raise ValueError("title is required")

    # Validate collection_type
    if collection_type not in ("custom", "smart"):
        raise ValueError("collection_type must be 'custom' or 'smart'")

    # Smart collections require rules
    if collection_type == "smart" and not rules:
        raise ValueError("rules are required for smart collections")

    try:
        # Build collection data
        collection_data = {
            "title": title,
            "published": published
        }

        if body_html:
            collection_data["body_html"] = body_html

        if image:
            collection_data["image"] = image

        if collection_type == "smart" and rules:
            collection_data["rules"] = rules

        result = await self.create_collection(collection_data, collection_type)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating collection: {str(e)}"


@register_tool(
    name="shopify_update_collection",
    category="shopify",
    service_class=ShopifyService,
    description="Update an existing collection in the Shopify store"
)
async def update_collection(self, collection_id: str, collection_type: str = "custom",
                            title: Optional[str] = None, body_html: Optional[str] = None,
                            image: Optional[Dict] = None, published: Optional[bool] = None,
                            rules: Optional[List[Dict]] = None) -> str:
    """
    Update an existing collection in the Shopify store.

    Args:
        collection_id: The ID of the collection to update (required)
        collection_type: Type of collection ("custom" or "smart") (default: "custom")
        title: Collection title
        body_html: Collection description in HTML format
        image: Image object
        published: Whether the collection is published
        rules: List of rules for smart collections

    Returns:
        JSON string containing the updated collection data
    """
    if not collection_id:
        raise ValueError("collection_id is required")

    # Validate collection_type
    if collection_type not in ("custom", "smart"):
        raise ValueError("collection_type must be 'custom' or 'smart'")

    try:
        # Build collection data from parameters that are provided
        collection_data = {}

        if title:
            collection_data["title"] = title

        if body_html:
            collection_data["body_html"] = body_html

        if image:
            collection_data["image"] = image

        if published is not None:
            collection_data["published"] = published

        if collection_type == "smart" and rules:
            collection_data["rules"] = rules

        # If no parameters were provided, return an error
        if not collection_data:
            return "Error: At least one field to update must be provided"

        result = await self.update_collection(collection_id, collection_data, collection_type)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating collection: {str(e)}"
