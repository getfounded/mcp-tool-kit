"""
News API tools for accessing news articles and headlines.
"""
from app.tools.news_api.tools import *


def get_news_api_tools():
    """Return a dictionary of News API tools for registration."""
    return {
        "news_top_headlines": news_top_headlines,
        "news_search": news_search,
        "news_sources": news_sources
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_news_api_service(api_key=None):
    """Initialize the News API service with an API key."""
    # Implementation can be added as needed
    pass
