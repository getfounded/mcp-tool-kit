#!/usr/bin/env python3
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from enum import Enum

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context  # type: ignore
# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Salesforce API tools MCP reference set")


class SalesforceTools(str, Enum):
    """Enum of Salesforce tool names"""
    QUERY = "sf_query"
    CREATE = "sf_create"
    UPDATE = "sf_update"
    DELETE = "sf_delete"
    DESCRIBE = "sf_describe"
    GET_OBJECT = "sf_get_object"
    SEARCH = "sf_search"
    LIST_OBJECTS = "sf_list_objects"


class SalesforceService:
    """Service to handle Salesforce API operations"""

    def __init__(self, username=None, password=None, security_token=None,
                 consumer_key=None, consumer_secret=None, domain=None):
        try:
            from simple_salesforce import Salesforce
            self.sf_module = Salesforce
        except ImportError:
            logging.error(
                "simple_salesforce module not installed. Please install it with 'pip install simple-salesforce'")
            raise ImportError("simple_salesforce module is required")

        # Get credentials from environment variables if not provided
        self.username = username or os.environ.get("SF_USERNAME")
        self.password = password or os.environ.get("SF_PASSWORD")
        self.security_token = security_token or os.environ.get(
            "SF_SECURITY_TOKEN")
        self.consumer_key = consumer_key or os.environ.get("SF_CONSUMER_KEY")
        self.consumer_secret = consumer_secret or os.environ.get(
            "SF_CONSUMER_SECRET")
        self.domain = domain or os.environ.get(
            "SF_DOMAIN", "login")  # Default to login.salesforce.com

        # Connection instance
        self.client = None

        # Check for required credentials
        if not all([self.username, self.password, self.security_token]):
            logging.warning(
                "Salesforce credentials not fully configured. Set SF_USERNAME, SF_PASSWORD, and SF_SECURITY_TOKEN.")

    def _ensure_connected(self):
        """Ensure we have an active Salesforce connection"""
        if self.client is None:
            if not all([self.username, self.password, self.security_token]):
                raise ValueError(
                    "Missing Salesforce credentials. Please set SF_USERNAME, SF_PASSWORD, and SF_SECURITY_TOKEN")

            # Connect to Salesforce
            try:
                # OAuth2 connection if consumer key and secret are provided
                if self.consumer_key and self.consumer_secret:
                    self.client = self.sf_module(
                        username=self.username,
                        password=self.password,
                        security_token=self.security_token,
                        consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret,
                        domain=self.domain
                    )
                # Password-based auth
                else:
                    self.client = self.sf_module(
                        username=self.username,
                        password=self.password,
                        security_token=self.security_token,
                        domain=self.domain
                    )

                logging.info(
                    f"Successfully connected to Salesforce as {self.username}")

            except Exception as e:
                logging.error(f"Failed to connect to Salesforce: {str(e)}")
                raise

    async def query(self, soql_query: str) -> Dict[str, Any]:
        """Execute a SOQL query against Salesforce"""
        try:
            self._ensure_connected()
            result = self.client.query(soql_query)
            return self._format_query_result(result)
        except Exception as e:
            return {"error": str(e)}

    async def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in Salesforce"""
        try:
            self._ensure_connected()

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Create the record
            result = sf_object.create(data)

            return {
                "success": result["success"],
                "id": result["id"] if result["success"] else None,
                "errors": result.get("errors", [])
            }
        except Exception as e:
            return {"error": str(e)}

    async def update(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record in Salesforce"""
        try:
            self._ensure_connected()

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Update the record
            result = sf_object.update(record_id, data)

            return {
                "success": result == 204,  # HTTP 204 means success with no content
                "id": record_id,
                "status_code": result
            }
        except Exception as e:
            return {"error": str(e)}

    async def delete(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Delete a record from Salesforce"""
        try:
            self._ensure_connected()

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Delete the record
            result = sf_object.delete(record_id)

            return {
                "success": result == 204,  # HTTP 204 means success with no content
                "id": record_id,
                "status_code": result
            }
        except Exception as e:
            return {"error": str(e)}

    async def describe(self, object_name: str = None) -> Dict[str, Any]:
        """Get metadata about a Salesforce object or all objects"""
        try:
            self._ensure_connected()

            if object_name:
                # Get metadata for a specific object
                sf_object = getattr(self.client, object_name)
                result = sf_object.describe()
                return self._format_describe_result(result)
            else:
                # Get global metadata for all objects
                result = self.client.describe()
                return self._format_describe_result(result)
        except Exception as e:
            return {"error": str(e)}

    async def get_object(self, object_name: str, record_id: str) -> Dict[str, Any]:
        """Get a specific record from Salesforce"""
        try:
            self._ensure_connected()

            # Get the Salesforce object (Account, Contact, etc.)
            sf_object = getattr(self.client, object_name)

            # Get the record
            result = sf_object.get(record_id)

            # Remove null values for better readability
            cleaned_result = {k: v for k, v in result.items() if v is not None}

            return cleaned_result
        except Exception as e:
            return {"error": str(e)}

    async def search(self, sosl_query: str) -> Dict[str, Any]:
        """Execute a SOSL search against Salesforce"""
        try:
            self._ensure_connected()
            result = self.client.search(sosl_query)
            return self._format_search_result(result)
        except Exception as e:
            return {"error": str(e)}

    async def list_objects(self) -> Dict[str, Any]:
        """List available Salesforce objects"""
        try:
            self._ensure_connected()

            # Get global metadata
            global_describe = self.client.describe()

            # Extract object info
            objects = []
            for obj in global_describe["sobjects"]:
                objects.append({
                    "name": obj["name"],
                    "label": obj["label"],
                    "custom": obj["custom"],
                    "createable": obj["createable"],
                    "updateable": obj["updateable"],
                    "deletable": obj["deletable"],
                    "queryable": obj["queryable"]
                })

            return {
                "objects": objects,
                "count": len(objects)
            }
        except Exception as e:
            return {"error": str(e)}

    def _format_query_result(self, result):
        """Format query results for better readability"""
        if not result:
            return {"records": [], "totalSize": 0, "done": True}

        # For normal query results
        if hasattr(result, "get"):
            return {
                "records": result.get("records", []),
                "totalSize": result.get("totalSize", 0),
                "done": result.get("done", True),
                "nextRecordsUrl": result.get("nextRecordsUrl", None)
            }

        # Fallback for other result types
        return result

    def _format_describe_result(self, result):
        """Format describe results to be more readable"""
        # If it's a list of objects (global describe)
        if isinstance(result, dict) and "sobjects" in result:
            simplified = []
            for obj in result["sobjects"]:
                simplified.append({
                    "name": obj.get("name"),
                    "label": obj.get("label"),
                    "custom": obj.get("custom", False),
                    "keyPrefix": obj.get("keyPrefix")
                })
            return {"objects": simplified}

        # If it's a single object describe
        if isinstance(result, dict) and "fields" in result:
            fields = []
            for field in result["fields"]:
                fields.append({
                    "name": field.get("name"),
                    "label": field.get("label"),
                    "type": field.get("type"),
                    "custom": field.get("custom", False),
                    "nillable": field.get("nillable", True),
                    "picklistValues": field.get("picklistValues", [])
                })

            return {
                "name": result.get("name"),
                "label": result.get("label"),
                "custom": result.get("custom", False),
                "fields": fields
            }

        # Fallback
        return result

    def _format_search_result(self, result):
        """Format search results for better readability"""
        if isinstance(result, list):
            return {"searchRecords": result, "totalSize": len(result)}
        return result


# Tool function definitions that will be registered with MCP

async def sf_query(soql_query: str, ctx: Context = None) -> str:
    """Execute a SOQL (Salesforce Object Query Language) query

    Parameters:
    - soql_query: A valid SOQL query string, e.g. "SELECT Id, Name FROM Account LIMIT 10"

    Returns:
    JSON string containing the query results with records, totalSize, and done status
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.query(soql_query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_create(object_name: str, data: Dict[str, Any], ctx: Context = None) -> str:
    """Create a new record in Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - data: Dictionary containing the field values for the new record

    Returns:
    JSON string containing the creation result with success status and record ID
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.create(object_name, data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_update(object_name: str, record_id: str, data: Dict[str, Any], ctx: Context = None) -> str:
    """Update an existing record in Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - record_id: The ID of the record to update
    - data: Dictionary containing the field values to update

    Returns:
    JSON string containing the update result with success status
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.update(object_name, record_id, data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_delete(object_name: str, record_id: str, ctx: Context = None) -> str:
    """Delete a record from Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - record_id: The ID of the record to delete

    Returns:
    JSON string containing the delete result with success status
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.delete(object_name, record_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_describe(object_name: str = None, ctx: Context = None) -> str:
    """Get metadata about a Salesforce object or all objects

    Parameters:
    - object_name: (Optional) The API name of the Salesforce object, e.g. "Account"
                  If not provided, returns global metadata

    Returns:
    JSON string containing the object metadata
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.describe(object_name)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_get_object(object_name: str, record_id: str, ctx: Context = None) -> str:
    """Get a specific record from Salesforce

    Parameters:
    - object_name: The API name of the Salesforce object, e.g. "Account", "Contact", "Opportunity"
    - record_id: The ID of the record to retrieve

    Returns:
    JSON string containing the record data
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.get_object(object_name, record_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_search(sosl_query: str, ctx: Context = None) -> str:
    """Execute a SOSL (Salesforce Object Search Language) search

    Parameters:
    - sosl_query: A valid SOSL query string, e.g. "FIND {Smith} IN Name FIELDS RETURNING Account(Id, Name), Contact(Id, Name)"

    Returns:
    JSON string containing the search results
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.search(sosl_query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def sf_list_objects(ctx: Context = None) -> str:
    """List available Salesforce objects

    Returns:
    JSON string containing the list of available objects
    """
    sf_service = _get_salesforce_service()
    if not sf_service:
        return "Salesforce API is not configured. Please set the required environment variables."

    try:
        result = await sf_service.list_objects()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# Tool registration and initialization
_salesforce_service = None


def initialize_salesforce_service(username=None, password=None, security_token=None,
                                  consumer_key=None, consumer_secret=None, domain=None):
    """Initialize the Salesforce service with credentials"""
    global _salesforce_service

    # Use environment variables as fallback
    username = username or os.environ.get("SF_USERNAME")
    password = password or os.environ.get("SF_PASSWORD")
    security_token = security_token or os.environ.get("SF_SECURITY_TOKEN")
    consumer_key = consumer_key or os.environ.get("SF_CONSUMER_KEY")
    consumer_secret = consumer_secret or os.environ.get("SF_CONSUMER_SECRET")
    domain = domain or os.environ.get("SF_DOMAIN", "login")

    try:
        _salesforce_service = SalesforceService(
            username=username,
            password=password,
            security_token=security_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            domain=domain
        )
        return _salesforce_service
    except ImportError:
        logging.error(
            "simple_salesforce module is required. Install with 'pip install simple-salesforce'")
        return None
    except Exception as e:
        logging.error(f"Failed to initialize Salesforce service: {str(e)}")
        return None


def _get_salesforce_service():
    """Get or initialize the Salesforce service"""
    global _salesforce_service
    if _salesforce_service is None:
        _salesforce_service = initialize_salesforce_service()
    return _salesforce_service


def get_salesforce_tools():
    """Get a dictionary of all Salesforce tools for registration with MCP"""
    return {
        SalesforceTools.QUERY: sf_query,
        SalesforceTools.CREATE: sf_create,
        SalesforceTools.UPDATE: sf_update,
        SalesforceTools.DELETE: sf_delete,
        SalesforceTools.DESCRIBE: sf_describe,
        SalesforceTools.GET_OBJECT: sf_get_object,
        SalesforceTools.SEARCH: sf_search,
        SalesforceTools.LIST_OBJECTS: sf_list_objects
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the Salesforce module with MCP reference and credentials"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_salesforce_service()
    if service:
        logging.info("Salesforce API service initialized successfully")
    else:
        logging.warning("Failed to initialize Salesforce API service")

    return service is not None


# When running standalone for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a local MCP instance for testing
    local_mcp = FastMCP(
        "Salesforce API Tools",
        dependencies=["simple-salesforce"]
    )

    # Register tools with the local MCP
    sf_tools = get_salesforce_tools()
    for tool_name, tool_func in sf_tools.items():
        local_mcp.tool(name=tool_name)(tool_func)

    print("Salesforce API tools registered with local MCP instance")
    print("Available tools:")
    for tool_name in sf_tools.keys():
        print(f"- {tool_name}")
