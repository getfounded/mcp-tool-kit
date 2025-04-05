#!/usr/bin/env python3
"""
QuickBooks service for MCP toolkit.
"""
import os
import json
import base64
import logging
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any, Union

from app.tools.base.service import ToolServiceBase
from app.tools.utils.auth import create_auth_handler, OAuth2Auth


class QuickBooksService(ToolServiceBase):
    """Service to handle QuickBooks API operations"""

    def __init__(self):
        """Initialize the QuickBooks service"""
        super().__init__()

        # Initialize credentials from environment
        self.client_id = self.get_env_var("QB_CLIENT_ID", required=False)
        self.client_secret = self.get_env_var(
            "QB_CLIENT_SECRET", required=False)
        self.redirect_uri = self.get_env_var("QB_REDIRECT_URI", required=False)
        self.refresh_token = self.get_env_var(
            "QB_REFRESH_TOKEN", required=False)
        self.realm_id = self.get_env_var("QB_REALM_ID", required=False)

        # Initialize token variables
        self.access_token = None
        self.token_expires = None

        # API URLs
        self.base_url = "https://quickbooks.api.intuit.com/v3/company"
        self.auth_base_url = "https://oauth.platform.intuit.com/oauth2/v1"

        # Create rate limiter for API requests
        self.create_rate_limiter("default", 150, 60)  # 150 requests per minute

        # Initialize authentication
        self._init_auth()

    def _init_auth(self):
        """Initialize OAuth2 authentication for QuickBooks"""
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            self.logger.warning(
                "QuickBooks OAuth2 credentials not fully configured")
            return False

        self.auth_handler = create_auth_handler(
            "quickbooks",
            "oauth2",
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            auth_url=f"{self.auth_base_url}/authorize",
            token_url=f"{self.auth_base_url}/tokens/bearer",
            scopes=["com.intuit.quickbooks.accounting"]
        )

        # If we have a refresh token, try to load it into the auth handler
        if self.refresh_token:
            self.auth_handler.refresh_token = self.refresh_token

        return True

    def initialize(self) -> bool:
        """Initialize the service"""
        if not all([self.client_id, self.client_secret, self.redirect_uri, self.refresh_token, self.realm_id]):
            self.logger.warning(
                "QuickBooks API credentials not fully configured. Please set QB_CLIENT_ID, QB_CLIENT_SECRET, "
                "QB_REDIRECT_URI, QB_REFRESH_TOKEN, and QB_REALM_ID environment variables."
            )

        self.initialized = True
        return True

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
            # Apply rate limiting
            self.apply_rate_limit("default", 150, 60, wait=True)

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
        self._is_initialized()
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
            # Apply rate limiting
            self.apply_rate_limit("default", 150, 60, wait=True)

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
