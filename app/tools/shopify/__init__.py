#!/usr/bin/env python3
"""
Shopify API integration tools for the MCP toolkit.
"""

from .service import ShopifyService
from .tools import (
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

__all__ = [
    'ShopifyService',
    
    # Product tools
    'get_products',
    'get_product',
    'create_product',
    'update_product',
    'delete_product',
    
    # Order tools
    'get_orders',
    'get_order',
    'create_order',
    'cancel_order',
    
    # Customer tools
    'get_customers',
    'get_customer',
    'create_customer',
    'update_customer',
    
    # Inventory tools
    'get_inventory',
    'update_inventory',
    
    # Collection tools
    'get_collections',
    'create_collection',
    'update_collection'
]
