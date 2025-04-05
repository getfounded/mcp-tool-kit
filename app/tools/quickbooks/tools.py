#!/usr/bin/env python3
"""
QuickBooks tool functions.
"""
import json
from typing import Dict, List, Optional, Any, Union

from app.tools.base.registry import register_tool
from app.tools.quickbooks.service import QuickBooksService


@register_tool(
    name="qb_get_company_info",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get company information from QuickBooks"
)
async def get_company_info(self):
    """Get company information from QuickBooks"""
    try:
        result = await self.get_company_info()
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_customers",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get customers from QuickBooks"
)
async def get_customers(self, max_results: int = 1000, start_position: int = 1, query: str = None):
    """Get customers from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "DisplayName LIKE '%Jones%'")
    """
    try:
        result = await self.get_customers(max_results, start_position, query)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_customer",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get a specific customer from QuickBooks by ID"
)
async def get_customer(self, customer_id: str):
    """Get a specific customer from QuickBooks by ID

    Parameters:
    - customer_id: The ID of the customer to retrieve
    """
    try:
        result = await self.get_customer(customer_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_create_customer",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Create a new customer in QuickBooks"
)
async def create_customer(self, display_name: str, given_name: str = None, family_name: str = None,
                          email: str = None, phone: str = None, company_name: str = None,
                          billing_address: Dict = None):
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

        result = await self.create_customer({"Customer": customer_data})
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_update_customer",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Update an existing customer in QuickBooks"
)
async def update_customer(self, customer_id: str, display_name: str = None, given_name: str = None,
                          family_name: str = None, email: str = None, phone: str = None,
                          company_name: str = None, billing_address: Dict = None,
                          sync_token: str = None):
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
    try:
        if not sync_token:
            # Get current customer to get sync token
            current_customer = await self.get_customer(customer_id)
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

        result = await self.update_customer({"Customer": customer_data})
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_invoices",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get invoices from QuickBooks"
)
async def get_invoices(self, max_results: int = 1000, start_position: int = 1, query: str = None):
    """Get invoices from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "TxnDate >= '2023-01-01'")
    """
    try:
        result = await self.get_invoices(max_results, start_position, query)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_invoice",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get a specific invoice from QuickBooks by ID"
)
async def get_invoice(self, invoice_id: str):
    """Get a specific invoice from QuickBooks by ID

    Parameters:
    - invoice_id: The ID of the invoice to retrieve
    """
    try:
        result = await self.get_invoice(invoice_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_create_invoice",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Create a new invoice in QuickBooks"
)
async def create_invoice(self, customer_id: str, line_items: List[Dict], txn_date: str = None,
                         due_date: str = None, private_note: str = None):
    """Create a new invoice in QuickBooks

    Parameters:
    - customer_id: The ID of the customer for the invoice (required)
    - line_items: List of line items - each should include ItemRef/value, Description, Amount, DetailType (usually "SalesItemLineDetail")
    - txn_date: The transaction date (YYYY-MM-DD)
    - due_date: The due date (YYYY-MM-DD)
    - private_note: Private note for the invoice
    """
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

        result = await self.create_invoice({"Invoice": invoice_data})
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_items",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get items (products/services) from QuickBooks"
)
async def get_items(self, max_results: int = 1000, start_position: int = 1, query: str = None):
    """Get items (products/services) from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "Type = 'Service'")
    """
    try:
        result = await self.get_items(max_results, start_position, query)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_item",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get a specific item from QuickBooks by ID"
)
async def get_item(self, item_id: str):
    """Get a specific item from QuickBooks by ID

    Parameters:
    - item_id: The ID of the item to retrieve
    """
    try:
        result = await self.get_item(item_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_create_item",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Create a new item (product/service) in QuickBooks"
)
async def create_item(self, name: str, type: str, unit_price: float, income_account_id: str,
                      expense_account_id: str = None, description: str = None, taxable: bool = True):
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

        result = await self.create_item({"Item": item_data})
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_accounts",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get accounts from QuickBooks"
)
async def get_accounts(self, max_results: int = 1000, start_position: int = 1, query: str = None):
    """Get accounts from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "AccountType = 'Income'")
    """
    try:
        result = await self.get_accounts(max_results, start_position, query)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_account",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get a specific account from QuickBooks by ID"
)
async def get_account(self, account_id: str):
    """Get a specific account from QuickBooks by ID

    Parameters:
    - account_id: The ID of the account to retrieve
    """
    try:
        result = await self.get_account(account_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_vendors",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get vendors from QuickBooks"
)
async def get_vendors(self, max_results: int = 1000, start_position: int = 1, query: str = None):
    """Get vendors from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "DisplayName LIKE '%Supply%'")
    """
    try:
        result = await self.get_vendors(max_results, start_position, query)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_vendor",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get a specific vendor from QuickBooks by ID"
)
async def get_vendor(self, vendor_id: str):
    """Get a specific vendor from QuickBooks by ID

    Parameters:
    - vendor_id: The ID of the vendor to retrieve
    """
    try:
        result = await self.get_vendor(vendor_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_create_vendor",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Create a new vendor in QuickBooks"
)
async def create_vendor(self, display_name: str, given_name: str = None, family_name: str = None,
                        email: str = None, phone: str = None, company_name: str = None,
                        address: Dict = None):
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

        result = await self.create_vendor({"Vendor": vendor_data})
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_bills",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get bills from QuickBooks"
)
async def get_bills(self, max_results: int = 1000, start_position: int = 1, query: str = None):
    """Get bills from QuickBooks

    Parameters:
    - max_results: Maximum number of results to return (default: 1000)
    - start_position: Starting position for pagination (default: 1)
    - query: Optional query filter (e.g., "TxnDate >= '2023-01-01'")
    """
    try:
        result = await self.get_bills(max_results, start_position, query)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_bill",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get a specific bill from QuickBooks by ID"
)
async def get_bill(self, bill_id: str):
    """Get a specific bill from QuickBooks by ID

    Parameters:
    - bill_id: The ID of the bill to retrieve
    """
    try:
        result = await self.get_bill(bill_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_create_bill",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Create a new bill in QuickBooks"
)
async def create_bill(self, vendor_id: str, line_items: List[Dict], txn_date: str = None,
                      due_date: str = None, memo: str = None):
    """Create a new bill in QuickBooks

    Parameters:
    - vendor_id: The ID of the vendor for the bill (required)
    - line_items: List of line items - each should include ItemRef/value, Description, Amount, DetailType (usually "AccountBasedExpenseLineDetail")
    - txn_date: The transaction date (YYYY-MM-DD)
    - due_date: The due date (YYYY-MM-DD)
    - memo: Memo for the bill
    """
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

        result = await self.create_bill({"Bill": bill_data})
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_profit_loss",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get profit and loss report from QuickBooks"
)
async def get_profit_loss(self, start_date: str, end_date: str, accounting_method: str = "Accrual"):
    """Get profit and loss report from QuickBooks

    Parameters:
    - start_date: Start date for the report (YYYY-MM-DD)
    - end_date: End date for the report (YYYY-MM-DD)
    - accounting_method: Accounting method (Accrual or Cash)
    """
    try:
        result = await self.get_profit_loss_report(start_date, end_date, accounting_method)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_balance_sheet",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get balance sheet report from QuickBooks"
)
async def get_balance_sheet(self, start_date: str, end_date: str, accounting_method: str = "Accrual"):
    """Get balance sheet report from QuickBooks

    Parameters:
    - start_date: Start date for the report (YYYY-MM-DD)
    - end_date: End date for the report (YYYY-MM-DD)
    - accounting_method: Accounting method (Accrual or Cash)
    """
    try:
        result = await self.get_balance_sheet_report(start_date, end_date, accounting_method)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_get_cash_flow",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Get cash flow report from QuickBooks"
)
async def get_cash_flow(self, start_date: str, end_date: str, accounting_method: str = "Accrual"):
    """Get cash flow report from QuickBooks

    Parameters:
    - start_date: Start date for the report (YYYY-MM-DD)
    - end_date: End date for the report (YYYY-MM-DD)
    - accounting_method: Accounting method (Accrual or Cash)
    """
    try:
        result = await self.get_cash_flow_report(start_date, end_date, accounting_method)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="qb_query",
    category="QuickBooks",
    service_class=QuickBooksService,
    description="Execute a custom query using QuickBooks Query Language"
)
async def query(self, query_string: str):
    """Execute a custom query using QuickBooks Query Language

    Parameters:
    - query_string: The query string to execute (e.g., "SELECT * FROM Invoice WHERE TotalAmt > '100.00'")
    """
    try:
        result = await self.query(query_string)
        return result
    except Exception as e:
        return {"error": str(e)}
