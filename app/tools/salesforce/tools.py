#!/usr/bin/env python3
"""
Salesforce API tools for MCP toolkit.
"""
import json
from typing import Dict, Any

from app.tools.base.registry import register_tool
from app.tools.salesforce.service import SalesforceService


@register_tool(
    name="sf_query",
    category="salesforce",
    service_class=SalesforceService,
    description="Execute a SOQL query against Salesforce"
)
async def sf_query(self, soql_query: str) -> str:
    """
    Execute a SOQL (Salesforce Object Query Language) query

    Parameters:
    - soql_query: A valid SOQL query string, e.g. "SELECT Id, Name FROM Account LIMIT 10"

    Returns:
    JSON string containing the query results with records, totalSize, and done status
    """
    try:
        result = await self.query(soql_query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_create",
    category="salesforce",
    service_class=SalesforceService,
    description="Create a new record in Salesforce"
)
async def sf_create(self, object_name: str, data: Dict[str, Any]) -> str:
    """
    Create a new record in Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - data: Dictionary containing the field values for the new record

    Returns:
    JSON string containing the creation result with success status and record ID
    """
    try:
        result = await self.create(object_name, data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_update",
    category="salesforce",
    service_class=SalesforceService,
    description="Update an existing record in Salesforce"
)
async def sf_update(self, object_name: str, record_id: str, data: Dict[str, Any]) -> str:
    """
    Update an existing record in Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - record_id: The ID of the record to update
    - data: Dictionary containing the field values to update

    Returns:
    JSON string containing the update result with success status
    """
    try:
        result = await self.update(object_name, record_id, data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_delete",
    category="salesforce",
    service_class=SalesforceService,
    description="Delete a record from Salesforce"
)
async def sf_delete(self, object_name: str, record_id: str) -> str:
    """
    Delete a record from Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - record_id: The ID of the record to delete

    Returns:
    JSON string containing the delete result with success status
    """
    try:
        result = await self.delete(object_name, record_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_describe",
    category="salesforce",
    service_class=SalesforceService,
    description="Get metadata about a Salesforce object or all objects"
)
async def sf_describe(self, object_name: str = None) -> str:
    """
    Get metadata about a Salesforce object or all objects

    Parameters:
    - object_name: (Optional) The API name of the Salesforce object, e.g. "Account"
                  If not provided, returns global metadata

    Returns:
    JSON string containing the object metadata
    """
    try:
        result = await self.describe(object_name)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_get_object",
    category="salesforce",
    service_class=SalesforceService,
    description="Get a specific record from Salesforce"
)
async def sf_get_object(self, object_name: str, record_id: str) -> str:
    """
    Get a specific record from Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - record_id: The ID of the record to retrieve

    Returns:
    JSON string containing the record data
    """
    try:
        result = await self.get_object(object_name, record_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_search",
    category="salesforce",
    service_class=SalesforceService,
    description="Execute a SOSL search against Salesforce"
)
async def sf_search(self, sosl_query: str) -> str:
    """
    Execute a SOSL (Salesforce Object Search Language) search

    Parameters:
    - sosl_query: A valid SOSL query string, e.g. "FIND {Smith} IN Name FIELDS RETURNING Account(Id, Name), Contact(Id, Name)"

    Returns:
    JSON string containing the search results
    """
    try:
        result = await self.search(sosl_query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_list_objects",
    category="salesforce",
    service_class=SalesforceService,
    description="List available Salesforce objects"
)
async def sf_list_objects(self) -> str:
    """
    List available Salesforce objects

    Returns:
    JSON string containing the list of available objects
    """
    try:
        result = await self.list_objects()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@register_tool(
    name="sf_authenticate",
    category="salesforce",
    service_class=SalesforceService,
    description="Authenticate with Salesforce using username/password"
)
async def sf_authenticate(self, username: str = None, password: str = None, security_token: str = None) -> str:
    """
    Authenticate with Salesforce using username/password

    Parameters:
    - username: Salesforce username (email)
    - password: Salesforce password
    - security_token: Salesforce security token

    Returns:
    JSON string with authentication status
    """
    try:
        # Update credentials if provided
        if username:
            self.username = username
        if password:
            self.password = password
        if security_token:
            self.security_token = security_token

        # Force re-connection
        self.client = None
        self._ensure_connected()

        return json.dumps({
            "status": "success",
            "message": f"Authenticated as {self.username}",
            "org_id": getattr(self.client, "sf_org_id", "Unknown")
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Authentication failed: {str(e)}"}, indent=2)
