# QuickBooks MCP Integration Guide

This guide explains how to integrate the QuickBooks API with your MCP server to enable Claude to interact with QuickBooks data.

## Prerequisites

- A QuickBooks Online account (Developer or Production)
- A registered app in the Intuit Developer portal
- Python 3.9+ with `requests` and `python-dotenv` packages installed

## Setup Process

### 1. Create a QuickBooks Developer Account

1. Visit [Intuit Developer](https://developer.intuit.com/) and sign up for an account
2. Create a new app in the developer dashboard
3. Configure your app with the following settings:
   - **App Type**: Choose "Accounting" for QuickBooks Online
   - **Redirect URIs**: Add `http://localhost:8080/callback` for the configuration utility
   - **Scopes**: Select "Accounting" scope

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Configure QuickBooks Integration

#### Option A: Using the Configuration Utility

1. Save the QuickBooks Configuration Utility script to `qb_config.py`
2. Run the setup process:

```bash
python qb_config.py setup
```

3. Follow the prompts to enter your Client ID and Client Secret
4. The utility will open a browser for authorization
5. After authorization, the utility will save the configuration to `qb_config.json` and create a `.env` file

#### Option B: Manual Configuration

1. Create a `.env` file in the root directory of your MCP server with the following variables:

```
QB_CLIENT_ID=your_client_id
QB_CLIENT_SECRET=your_client_secret
QB_REDIRECT_URI=your_redirect_uri
QB_REFRESH_TOKEN=your_refresh_token
QB_REALM_ID=your_company_id
```

### 4. Integrate with MCP Server

1. Save the QuickBooks Tool implementation to `tools/quickbooks.py`
2. Update your `mcp_unified_server.py` file to import and register the QuickBooks tool:

```python
# Initialize QuickBooks tools
try:
    from tools.quickbooks import get_quickbooks_tools, set_external_mcp, initialize_quickbooks_service

    # Pass our MCP instance to the quickbooks module
    set_external_mcp(mcp)

    # Initialize quickbooks tools
    initialize_quickbooks_service()

    # Register quickbooks tools
    quickbooks_tools = get_quickbooks_tools()
    for tool_name, tool_func in quickbooks_tools.items():
        # Register each quickbooks tool with the main MCP instance
        tool_name_str = tool_name if isinstance(tool_name, str) else tool_name.value
        mcp.tool(name=tool_name_str)(tool_func)

    logging.info("QuickBooks tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load QuickBooks tools: {e}")
```

## Available Tools

The QuickBooks integration provides the following tools:

### Company Information
- `qb_get_company_info` - Get basic information about the company

### Customer Management
- `qb_get_customers` - Get a list of customers
- `qb_get_customer` - Get a specific customer by ID
- `qb_create_customer` - Create a new customer
- `qb_update_customer` - Update an existing customer

### Invoice Management
- `qb_get_invoices` - Get a list of invoices
- `qb_get_invoice` - Get a specific invoice by ID
- `qb_create_invoice` - Create a new invoice

### Product/Service Management
- `qb_get_items` - Get a list of products and services
- `qb_get_item` - Get a specific item by ID
- `qb_create_item` - Create a new product or service

### Account Management
- `qb_get_accounts` - Get a list of accounts
- `qb_get_account` - Get a specific account by ID

### Vendor Management
- `qb_get_vendors` - Get a list of vendors
- `qb_get_vendor` - Get a specific vendor by ID
- `qb_create_vendor` - Create a new vendor

### Bill Management
- `qb_get_bills` - Get a list of bills
- `qb_get_bill` - Get a specific bill by ID
- `qb_create_bill` - Create a new bill

### Reports
- `qb_get_profit_loss` - Get a profit and loss report
- `qb_get_balance_sheet` - Get a balance sheet report
- `qb_get_cash_flow` - Get a cash flow report

### Advanced
- `qb_query` - Execute a custom query using QuickBooks Query Language (similar to SQL)

## Usage Examples

### Example 1: Getting Company Information

```python
from mcp.client import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Get company information
result = client.call_tool("qb_get_company_info")
print(result)
```

### Example 2: Creating a Customer

```python
from mcp.client import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Create a new customer
result = client.call_tool("qb_create_customer", {
    "display_name": "John Doe",
    "given_name": "John",
    "family_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "555-123-4567",
    "company_name": "Doe Enterprises",
    "billing_address": {
        "Line1": "123 Main St",
        "City": "Anytown",
        "CountrySubDivisionCode": "CA",
        "PostalCode": "12345",
        "Country": "USA"
    }
})
print(result)
```

