"""
MCP Toolkit Tools
================

This package contains the various tools and integrations that can be used
with the MCP Unified Server.

Each module in this package provides specific functionality that can be
registered with an MCP server to enable Claude AI assistants to interact
with external systems.
"""

# Import all tools to make them accessible from mcptoolkit.tools
from . import (
    brave_search,
    browserbase,
    data_analysis,
    digital_marketing,
    document_management,
    filesystem,
    fred,
    gui_rpa,
    linkedin,
    news_api,
    outlook,
    ppt,
    project_management,
    salesforce,
    sequential_thinking,
    streamlit,
    teams,
    time_tools,
    worldbank,
    yfinance,
)

# Function to register all tools with an MCP server


def register_all_tools(server):
    """
    Register all available tools with the provided MCP server.

    Args:
        server: The MCP server instance

    Returns:
        None
    """
    # Register each tool module
    brave_search.register_tools(server)
    browserbase.register_tools(server)
    data_analysis.register_tools(server)
    digital_marketing.register_tools(server)
    document_management.register_tools(server)
    filesystem.register_tools(server)
    fred.register_tools(server)
    gui_rpa.register_tools(server)
    linkedin.register_tools(server)
    news_api.register_tools(server)
    outlook.register_tools(server)
    ppt.register_tools(server)
    project_management.register_tools(server)
    salesforce.register_tools(server)
    sequential_thinking.register_tools(server)
    streamlit.register_tools(server)
    teams.register_tools(server)
    time_tools.register_tools(server)
    worldbank.register_tools(server)
    yfinance.register_tools(server)
