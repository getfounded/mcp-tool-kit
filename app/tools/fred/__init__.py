"""
FRED API tools for accessing Federal Reserve Economic Data.
"""
from app.tools.fred.tools import *


def get_fred_api_tools():
    """Return a dictionary of FRED API tools for registration."""
    return {
        "fred_get_series": fred_get_series,
        "fred_search": fred_search,
        "fred_get_series_info": fred_get_series_info,
        "fred_get_category": fred_get_category
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_fred_api_service(api_key=None):
    """Initialize the FRED API service with an API key."""
    # Implementation can be added as needed
    pass


def initialize(mcp_instance):
    """Initialize the FRED module with MCP instance."""
    set_external_mcp(mcp_instance)
    return True
