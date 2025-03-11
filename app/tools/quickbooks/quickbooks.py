#!/usr/bin/env python3
import os
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import requests
from urllib.parse import urlencode

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("QuickBooks tools MCP reference set")


class QuickBooksTools(str, Enum):
    """Enum of QuickBooks tool names"""
    GET_COMPANY_INFO = "qb_get_company_info"
    GET_CUSTOMERS = "qb_get_customers"
    GET_CUSTOMER = "qb_get_customer"
    CREATE_CUSTOMER = "qb_create_customer"
    UPDATE_CUSTOMER = "qb_update_customer"

    GET_INVOICES = "qb_get_invoices"
    GET_INVOICE = "qb_get_invoice"
    CREATE_INVOICE = "qb_create_invoice"

    GET_ITEMS = "qb_get_items"
    GET_ITEM = "qb_get_item"
    CREATE_ITEM = "qb_create_item"

    GET_ACCOUNTS = "qb_get_accounts"
    GET_ACCOUNT = "qb_get_account"

    GET_VENDORS = "qb_get_vendors"
    GET_VENDOR = "qb_get_vendor"
    CREATE_VENDOR = "qb_create_vendor"

    GET_BILLS = "qb_get_bills"
    GET_BILL = "qb_get_bill"
    CREATE_BILL = "qb_create_bill"

    GET_PROFIT_LOSS = "qb_get_profit_loss"
    GET_BALANCE_SHEET = "qb_get_balance_sheet"
    GET_CASH_FLOW = "qb_get_cash_flow"

    QUERY = "qb_query"


class QuickBooksService:
    """Service to handle QuickBooks API operations"""

    def __init__(self, client_id, client_secret, redirect_uri, refresh_token=None, realm_id=None):
        """Initialize the QuickBooks service with OAuth credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.realm_id = realm_id

        # Initialize token variables
        self.access_token = None
        self.token_expires = None

        # API URLs
        self.base_url = "https://quickbooks.api.intuit.com/v3/company"
        self.auth_base_url = "https://oauth.platform.intuit.com/oauth2/v1"

    async def _ensure_token(self):
        """Ensure we have a valid access token"""
        # Check if token is still valid
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return

        if not self.refresh_token:
            raise ValueError(
                "Refresh token not provided. Cannot authenticate.")

        # Prepare the token request
        token_url = f"{self.auth_base_url}/tokens/bearer"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode()}"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }

        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data.get("access_token")
            # Store new refresh token if provided
            if "refresh_token" in token_data:
                self.refresh_token = token_data.get("refresh_token")

            # Set expiration time
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in -
                                                            300)  # 5 min buffer
        except Exception as e:
            raise ValueError(f"Failed to refresh access token: {str(e)}")

    async def _make_request(self, method, endpoint, params=None, data=None, minor_version=None):
        """Make an authenticated request to the QuickBooks API"""
        await self._ensure_token()

        if not self.realm_id:
            raise ValueError(
                "Realm ID (company ID) not provided. Cannot make API requests.")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Add QuickBooks API minor version if specified
        if minor_version:
            headers["Intuit-Tid"] = f"{minor_version}"

        url = f"{self.base_url}/{self.realm_id}/{endpoint}"

        try:
            if method.lower() == "get":
                response = requests.get(url, headers=headers, params=params)
            elif method.lower() == "post":
                response = requests.post(
                    url, headers=headers, params=params, data=json.dumps(data) if data else None)
            elif method.lower() == "put":
                response = requests.put(
                    url, headers=headers, params=params, data=json.dumps(data) if data else None)
            elif method.lower() == "delete":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for errors
            response.raise_for_status()

            # Parse JSON response if it exists
            if response.content:
                return response.json()
            return {"status": "success"}
        except requests.exceptions.HTTPError as e:
            error_msg = f"QuickBooks API error: {e}"
            try:
                error_data = e.response.json()
                error_msg = f"{error_msg} - {json.dumps(error_data)}"
            except:
                pass
            raise ValueError(error_msg)
        except Exception as e:
            raise ValueError(
                f"Error making request to QuickBooks API: {str(e)}")

    # Company Info
    async def get_company_info(self):
        """Get company information"""
        return await self._make_request("get", "companyinfo/" + self.realm_id)

    # Customer Operations
    async def get_customers(self, max_results=1000, start_position=1, query=None):
        """Get all customers"""
        if query:
            return await self._make_request("get", f"query?query=select * from Customer where {query}")

        params = {
            "maxResults": max_results,
            "startPosition": start_position
        }
        return await self._make_request("get", "query", params={"query": "select * from Customer"})

    async def get_customer(self, customer_id):
        """Get a specific customer by ID"""
        return await self._make_request("get", f"customer/{customer_id}")

    async def create_customer(self, customer_data):
        """Create a new customer"""
        return await self._make_request("post", "customer", data=customer_data)

    async def update_customer(self, customer_data):
        """Update an existing customer"""
        if "Id" not in customer_data:
            raise ValueError("Customer ID is required for updates")

        return await self._make_request("post", "customer", data=customer_data)

    # Invoice Operations
    async def get_invoices(self, max_results=1000, start_position=1, query=None):
        """Get all invoices"""
        if query:
            return await self._make_request("get", f"query?query=select * from Invoice where {query}")

        return await self._make_request("get", "query", params={"query": "select * from Invoice"})

    async def get_invoice(self, invoice_id):
        """Get a specific invoice by ID"""
        return await self._make_request("get", f"invoice/{invoice_id}")

    async def create_invoice(self, invoice_data):
        """Create a new invoice"""
        return await self._make_request("post", "invoice", data=invoice_data)

    # Item (Products/Services) Operations
    async def get_items(self, max_results=1000, start_position=1, query=None):
        """Get all items (products/services)"""
        if query:
            return await self._make_request("get", f"query?query=select * from Item where {query}")

        return await self._make_request("get", "query", params={"query": "select * from Item"})

    async def get_item(self, item_id):
        """Get a specific item by ID"""
        return await self._make_request("get", f"item/{item_id}")

    async def create_item(self, item_data):
        """Create a new item"""
        return await self._make_request("post", "item", data=item_data)

    # Account Operations
    async def get_accounts(self, max_results=1000, start_position=1, query=None):
        """Get all accounts"""
        if query:
            return await self._make_request("get", f"query?query=select * from Account where {query}")

        return await self._make_request("get", "query", params={"query": "select * from Account"})

    async def get_account(self, account_id):
        """Get a specific account by ID"""
        return await self._make_request("get", f"account/{account_id}")

    # Vendor Operations
    async def get_vendors(self, max_results=1000, start_position=1, query=None):
        """Get all vendors"""
        if query:
            return await self._make_request("get", f"query?query=select * from Vendor where {query}")

        return await self._make_request("get", "query", params={"query": "select * from Vendor"})

    async def get_vendor(self, vendor_id):
        """Get a specific vendor by ID"""
        return await self._make_request("get", f"vendor/{vendor_id}")

    async def create_vendor(self, vendor_data):
        """Create a new vendor"""
        return await self._make_request("post", "vendor", data=vendor_data)

    # Bill Operations
    async def get_bills(self, max_results=1000, start_position=1, query=None):
        """Get all bills"""
        if query:
            return await self._make_request("get", f"query?query=select * from Bill where {query}")

        return await self._make_request("get", "query", params={"query": "select * from Bill"})

    async def get_bill(self, bill_id):
        """Get a specific bill by ID"""
        return await self._make_request("get", f"bill/{bill_id}")

    async def create_bill(self, bill_data):
        """Create a new bill"""
        return await self._make_request("post", "bill", data=bill_data)

    # Report Operations
    async def get_profit_loss_report(self, start_date, end_date, accounting_method="Accrual"):
        """Get profit and loss report"""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "accounting_method": accounting_method
        }
        return await self._make_request("get", "reports/ProfitAndLoss", params=params)

    async def get_balance_sheet_report(self, start_date, end_date, accounting_method="Accrual"):
        """Get balance sheet report"""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "accounting_method": accounting_method
        }
        return await self._make_request("get", "reports/BalanceSheet", params=params)

    async def get_cash_flow_report(self, start_date, end_date, accounting_method="Accrual"):
        """Get cash flow report"""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "accounting_method": accounting_method
        }
        return await self._make_request("get", "reports/CashFlow", params=params)

    # General Query
    async def query(self, query_string):
        """Execute a custom query using QuickBooks query language"""
        encoded_query = urlencode({"query": query_string})
        return await self._make_request("get", f"query?{encoded_query}")


# Tool function definitions that will be registered with MCP
async def qb_get_company_info(ctx: Context = None) -> str:
    """Get company information from QuickBooks"""
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_company_info()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving company information: {str(e)}"


async def qb_get_customers(max_results: int = 1000, start_position: int = 1, query: str = None, ctx: Context = None) -> str:
    """Get customers from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "DisplayName LIKE '%Jones%'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_customers(max_results, start_position, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving customers: {str(e)}"


async def qb_get_customer(customer_id: str, ctx: Context = None) -> str:
    """Get a specific customer from QuickBooks by ID

    Parameters:
    - customer_id: The ID of the customer to retrieve
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_customer(customer_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving customer: {str(e)}"


async def qb_create_customer(display_name: str, given_name: str = None, family_name: str = None,
                             email: str = None, phone: str = None, company_name: str = None,
                             billing_address: Dict = None, ctx: Context = None) -> str:
    """Create a new customer in QuickBooks

    Parameters:
    - display_name: The display name for the customer (required)
    - given_name: The customer's first name
    - family_name: The customer's last name
    - email: The customer's email address
    - phone: The customer's phone number
    - company_name: The customer's company name
    - billing_address: Dict containing address information (Line1, City, CountrySubDivisionCode, PostalCode, Country)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        # Build customer data
        customer_data = {
            "DisplayName": display_name
        }

        if given_name:
            customer_data["GivenName"] = given_name

        if family_name:
            customer_data["FamilyName"] = family_name

        if email:
            customer_data["PrimaryEmailAddr"] = {"Address": email}

        if phone:
            customer_data["PrimaryPhone"] = {"FreeFormNumber": phone}

        if company_name:
            customer_data["CompanyName"] = company_name

        if billing_address:
            customer_data["BillAddr"] = billing_address

        result = await qb.create_customer(customer_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating customer: {str(e)}"


async def qb_update_customer(customer_id: str, display_name: str = None, given_name: str = None,
                             family_name: str = None, email: str = None, phone: str = None,
                             company_name: str = None, billing_address: Dict = None,
                             sync_token: str = None, ctx: Context = None) -> str:
    """Update an existing customer in QuickBooks

    Parameters:
    - customer_id: The ID of the customer to update (required)
    - display_name: The display name for the customer
    - given_name: The customer's first name
    - family_name: The customer's last name
    - email: The customer's email address
    - phone: The customer's phone number
    - company_name: The customer's company name
    - billing_address: Dict containing address information (Line1, City, CountrySubDivisionCode, PostalCode, Country)
    - sync_token: The sync token for the customer (required for updates to prevent conflicts)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        if not sync_token:
            # Get current customer to get sync token
            current_customer = await qb.get_customer(customer_id)
            sync_token = current_customer.get("Customer", {}).get("SyncToken")

        # Build customer data
        customer_data = {
            "Id": customer_id,
            "SyncToken": sync_token
        }

        if display_name:
            customer_data["DisplayName"] = display_name

        if given_name:
            customer_data["GivenName"] = given_name

        if family_name:
            customer_data["FamilyName"] = family_name

        if email:
            customer_data["PrimaryEmailAddr"] = {"Address": email}

        if phone:
            customer_data["PrimaryPhone"] = {"FreeFormNumber": phone}

        if company_name:
            customer_data["CompanyName"] = company_name

        if billing_address:
            customer_data["BillAddr"] = billing_address

        result = await qb.update_customer(customer_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error updating customer: {str(e)}"


async def qb_get_invoices(max_results: int = 1000, start_position: int = 1, query: str = None, ctx: Context = None) -> str:
    """Get invoices from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "TxnDate >= '2023-01-01'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_invoices(max_results, start_position, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving invoices: {str(e)}"


async def qb_get_invoice(invoice_id: str, ctx: Context = None) -> str:
    """Get a specific invoice from QuickBooks by ID

    Parameters:
    - invoice_id: The ID of the invoice to retrieve
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_invoice(invoice_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving invoice: {str(e)}"


async def qb_create_invoice(customer_id: str, line_items: List[Dict], txn_date: str = None,
                            due_date: str = None, private_note: str = None, ctx: Context = None) -> str:
    """Create a new invoice in QuickBooks

    Parameters:
    - customer_id: The ID of the customer for the invoice (required)
    - line_items: List of line items - each should include ItemRef/value, Description, Amount, DetailType (usually "SalesItemLineDetail")
    - txn_date: The transaction date (YYYY-MM-DD)
    - due_date: The due date (YYYY-MM-DD)
    - private_note: Private note for the invoice
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        # Build invoice data
        invoice_data = {
            "CustomerRef": {
                "value": customer_id
            },
            "Line": line_items
        }

        if txn_date:
            invoice_data["TxnDate"] = txn_date

        if due_date:
            invoice_data["DueDate"] = due_date

        if private_note:
            invoice_data["PrivateNote"] = private_note

        result = await qb.create_invoice(invoice_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating invoice: {str(e)}"


async def qb_get_items(max_results: int = 1000, start_position: int = 1, query: str = None, ctx: Context = None) -> str:
    """Get items (products/services) from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "Type = 'Service'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_items(max_results, start_position, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving items: {str(e)}"


async def qb_get_item(item_id: str, ctx: Context = None) -> str:
    """Get a specific item from QuickBooks by ID

    Parameters:
    - item_id: The ID of the item to retrieve
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_item(item_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving item: {str(e)}"


async def qb_create_item(name: str, type: str, unit_price: float, income_account_id: str,
                         expense_account_id: str = None, description: str = None, taxable: bool = True,
                         ctx: Context = None) -> str:
    """Create a new item (product/service) in QuickBooks

    Parameters:
    - name: Name of the item (required)
    - type: Type of item (Service, Inventory, NonInventory)
    - unit_price: Price per unit
    - income_account_id: ID of the income account to use
    - expense_account_id: ID of the expense account to use (for inventory items)
    - description: Description of the item
    - taxable: Whether the item is taxable (default: True)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        # Build item data
        item_data = {
            "Name": name,
            "Type": type,
            "IncomeAccountRef": {
                "value": income_account_id
            },
            "Taxable": taxable
        }

        if expense_account_id:
            item_data["ExpenseAccountRef"] = {
                "value": expense_account_id
            }

        if description:
            item_data["Description"] = description

        if unit_price:
            item_data["UnitPrice"] = unit_price

        result = await qb.create_item(item_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating item: {str(e)}"


async def qb_get_accounts(max_results: int = 1000, start_position: int = 1, query: str = None, ctx: Context = None) -> str:
    """Get accounts from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "AccountType = 'Income'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_accounts(max_results, start_position, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving accounts: {str(e)}"


async def qb_get_account(account_id: str, ctx: Context = None) -> str:
    """Get a specific account from QuickBooks by ID

    Parameters:
    - account_id: The ID of the account to retrieve
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_account(account_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving account: {str(e)}"


async def qb_get_vendors(max_results: int = 1000, start_position: int = 1, query: str = None, ctx: Context = None) -> str:
    """Get vendors from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "DisplayName LIKE '%Supply%'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_vendors(max_results, start_position, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving vendors: {str(e)}"


async def qb_get_vendor(vendor_id: str, ctx: Context = None) -> str:
    """Get a specific vendor from QuickBooks by ID

    Parameters:
    - vendor_id: The ID of the vendor to retrieve
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_vendor(vendor_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving vendor: {str(e)}"


async def qb_create_vendor(display_name: str, given_name: str = None, family_name: str = None,
                           email: str = None, phone: str = None, company_name: str = None,
                           address: Dict = None, ctx: Context = None) -> str:
    """Create a new vendor in QuickBooks

    Parameters:
    - display_name: The display name for the vendor (required)
    - given_name: The vendor's first name
    - family_name: The vendor's last name
    - email: The vendor's email address
    - phone: The vendor's phone number
    - company_name: The vendor's company name
    - address: Dict containing address information (Line1, City, CountrySubDivisionCode, PostalCode, Country)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        # Build vendor data
        vendor_data = {
            "DisplayName": display_name
        }

        if given_name:
            vendor_data["GivenName"] = given_name

        if family_name:
            vendor_data["FamilyName"] = family_name

        if email:
            vendor_data["PrimaryEmailAddr"] = {"Address": email}

        if phone:
            vendor_data["PrimaryPhone"] = {"FreeFormNumber": phone}

        if company_name:
            vendor_data["CompanyName"] = company_name

        if address:
            vendor_data["BillAddr"] = address

        result = await qb.create_vendor(vendor_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating vendor: {str(e)}"


async def qb_get_bills(max_results: int = 1000, start_position: int = 1, query: str = None, ctx: Context = None) -> str:
    """Get bills from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "TxnDate >= '2023-01-01'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_bills(max_results, start_position, query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving bills: {str(e)}"


async def qb_get_bill(bill_id: str, ctx: Context = None) -> str:
    """Get a specific bill from QuickBooks by ID

    Parameters:
    - bill_id: The ID of the bill to retrieve
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_bill(bill_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving bill: {str(e)}"


async def qb_create_bill(vendor_id: str, line_items: List[Dict], txn_date: str = None,
                         due_date: str = None, memo: str = None, ctx: Context = None) -> str:
    """Create a new bill in QuickBooks

    Parameters:
    - vendor_id: The ID of the vendor for the bill (required)
    - line_items: List of line items - each should include ItemRef/value, Description, Amount, DetailType (usually "AccountBasedExpenseLineDetail")
    - txn_date: The transaction date (YYYY-MM-DD)
    - due_date: The due date (YYYY-MM-DD)
    - memo: Memo for the bill
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        # Build bill data
        bill_data = {
            "VendorRef": {
                "value": vendor_id
            },
            "Line": line_items
        }

        if txn_date:
            bill_data["TxnDate"] = txn_date

        if due_date:
            bill_data["DueDate"] = due_date

        if memo:
            bill_data["PrivateNote"] = memo

        result = await qb.create_bill(bill_data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating bill: {str(e)}"


async def qb_get_profit_loss(start_date: str, end_date: str, accounting_method: str = "Accrual", ctx: Context = None) -> str:
    """Get profit and loss report from QuickBooks

    Parameters:
    - start_date: Start date for the report (YYYY-MM-DD)
    - end_date: End date for the report (YYYY-MM-DD)
    - accounting_method: Accounting method (Accrual or Cash)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_profit_loss_report(start_date, end_date, accounting_method)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving profit and loss report: {str(e)}"


async def qb_get_balance_sheet(start_date: str, end_date: str, accounting_method: str = "Accrual", ctx: Context = None) -> str:
    """Get balance sheet report from QuickBooks

    Parameters:
    - start_date: Start date for the report (YYYY-MM-DD)
    - end_date: End date for the report (YYYY-MM-DD)
    - accounting_method: Accounting method (Accrual or Cash)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_balance_sheet_report(start_date, end_date, accounting_method)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving balance sheet report: {str(e)}"


async def qb_get_cash_flow(start_date: str, end_date: str, accounting_method: str = "Accrual", ctx: Context = None) -> str:
    """Get cash flow report from QuickBooks

    Parameters:
    - start_date: Start date for the report (YYYY-MM-DD)
    - end_date: End date for the report (YYYY-MM-DD)
    - accounting_method: Accounting method (Accrual or Cash)
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.get_cash_flow_report(start_date, end_date, accounting_method)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving cash flow report: {str(e)}"


async def qb_query(query_string: str, ctx: Context = None) -> str:
    """Execute a custom query using QuickBooks Query Language

    Parameters:
    - query_string: The query string to execute (e.g., "SELECT * FROM Invoice WHERE TotalAmt > '100.00'")
    """
    qb = _get_quickbooks_service()
    if not qb:
        return "QuickBooks API is not configured. Please set the required environment variables."

    try:
        result = await qb.query(query_string)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error executing query: {str(e)}"


# Tool registration and initialization
_quickbooks_service = None


def initialize_quickbooks_service(client_id=None, client_secret=None, redirect_uri=None, refresh_token=None, realm_id=None):
    """Initialize the QuickBooks service with credentials"""
    global _quickbooks_service

    # Use environment variables as fallback
    client_id = client_id or os.environ.get("QB_CLIENT_ID")
    client_secret = client_secret or os.environ.get("QB_CLIENT_SECRET")
    redirect_uri = redirect_uri or os.environ.get("QB_REDIRECT_URI")
    refresh_token = refresh_token or os.environ.get("QB_REFRESH_TOKEN")
    realm_id = realm_id or os.environ.get("QB_REALM_ID")

    if not client_id or not client_secret or not redirect_uri or not refresh_token or not realm_id:
        logging.warning(
            "QuickBooks API credentials not fully configured. Please set QB_CLIENT_ID, QB_CLIENT_SECRET, "
            "QB_REDIRECT_URI, QB_REFRESH_TOKEN, and QB_REALM_ID environment variables."
        )
        return None

    _quickbooks_service = QuickBooksService(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        refresh_token=refresh_token,
        realm_id=realm_id
    )
    return _quickbooks_service


def _get_quickbooks_service():
    """Get or initialize the QuickBooks service"""
    global _quickbooks_service
    if _quickbooks_service is None:
        _quickbooks_service = initialize_quickbooks_service()
    return _quickbooks_service


def get_quickbooks_tools():
    """Get a dictionary of all QuickBooks tools for registration with MCP"""
    return {
        QuickBooksTools.GET_COMPANY_INFO: qb_get_company_info,
        QuickBooksTools.GET_CUSTOMERS: qb_get_customers,
        QuickBooksTools.GET_CUSTOMER: qb_get_customer,
        QuickBooksTools.CREATE_CUSTOMER: qb_create_customer,
        QuickBooksTools.UPDATE_CUSTOMER: qb_update_customer,

        QuickBooksTools.GET_INVOICES: qb_get_invoices,
        QuickBooksTools.GET_INVOICE: qb_get_invoice,
        QuickBooksTools.CREATE_INVOICE: qb_create_invoice,

        QuickBooksTools.GET_ITEMS: qb_get_items,
        QuickBooksTools.GET_ITEM: qb_get_item,
        QuickBooksTools.CREATE_ITEM: qb_create_item,

        QuickBooksTools.GET_ACCOUNTS: qb_get_accounts,
        QuickBooksTools.GET_ACCOUNT: qb_get_account,

        QuickBooksTools.GET_VENDORS: qb_get_vendors,
        QuickBooksTools.GET_VENDOR: qb_get_vendor,
        QuickBooksTools.CREATE_VENDOR: qb_create_vendor,

        QuickBooksTools.GET_BILLS: qb_get_bills,
        QuickBooksTools.GET_BILL: qb_get_bill,
        QuickBooksTools.CREATE_BILL: qb_create_bill,

        QuickBooksTools.GET_PROFIT_LOSS: qb_get_profit_loss,
        QuickBooksTools.GET_BALANCE_SHEET: qb_get_balance_sheet,
        QuickBooksTools.GET_CASH_FLOW: qb_get_cash_flow,

        QuickBooksTools.QUERY: qb_query
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the QuickBooks module with MCP reference and credentials"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_quickbooks_service()
    if service:
        logging.info("QuickBooks API service initialized successfully")
    else:
        logging.warning("Failed to initialize QuickBooks API service")

    return service is not None


# If this file is run directly, print the list of tools
if __name__ == "__main__":
    print("QuickBooks Tools for MCP")
    print("Available tools:")

    # Print tool information
    for tool_name, tool_func in get_quickbooks_tools().items():
        doc = tool_func.__doc__.split(
            "\n")[0] if tool_func.__doc__ else "No description"
        print(f"- {tool_name}: {doc}")
