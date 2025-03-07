# Shopify API Tool for MCP

A comprehensive tool for integrating with the Shopify API, enabling Claude to manage products, orders, customers, inventory, and collections in Shopify stores.

## Features

- **Products Management**: List, create, update, and delete products
- **Orders Management**: List, create, update, and cancel orders  
- **Customers Management**: List, create, and update customers
- **Inventory Management**: Get and adjust inventory levels
- **Collections Management**: List, create, and update collections (both custom and smart)

## Installation

1. Add the `shopify_api.py` file to your `tools` directory in the MCP Unified Server
2. Add `httpx>=0.25.0` to your `requirements.txt` file
3. Update the `mcp_unified_server.py` file to import and register the Shopify module
4. Add Shopify API credentials to your `.env` file

## Configuration

The Shopify API tool requires the following environment variables:

```env
# Shopify API Credentials
SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com
SHOPIFY_API_VERSION=2023-10
# Either use API Key & Password
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_PASSWORD=your_api_password
# OR use Access Token (preferred)
SHOPIFY_ACCESS_TOKEN=your_access_token
