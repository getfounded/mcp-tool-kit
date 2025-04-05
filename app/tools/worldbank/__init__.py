"""
World Bank API tools for accessing economic indicators and country data.
"""
from app.tools.worldbank.tools import *


def get_worldbank_tools():
    """Return a dictionary of World Bank API tools for registration."""
    return {
        "worldbank_get_indicator": get_indicator,
        "worldbank_get_countries": get_countries,
        "worldbank_get_indicators": get_indicators,
        "worldbank_get_indicator_metadata": get_indicator_metadata,
        "worldbank_search_indicators": search_indicators
    }


def get_worldbank_resources():
    """Return a dictionary of World Bank API resources for registration."""
    return {}


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_worldbank_service():
    """Initialize the World Bank API service."""
    # Implementation can be added as needed
    pass
