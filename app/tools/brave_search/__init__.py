"""
Brave Search API tools for web and local search.
"""
from app.tools.brave_search.tools import *


def get_brave_search_tools():
    """Return a dictionary of Brave Search tools for registration."""
    return {
        "brave_web_search": brave_web_search,
        "brave_local_search": brave_local_search
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_brave_search(api_key=None):
    """Initialize the Brave Search service with an API key."""
    # Implementation can be added as needed
    pass
