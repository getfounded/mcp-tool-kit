"""
Streamlit tools for creating and managing Streamlit applications.
"""
from app.tools.streamlit.tools import *


def get_streamlit_tools():
    """Return a dictionary of Streamlit tools for registration."""
    return {
        "streamlit_create_app": streamlit_create_app,
        "streamlit_run_app": streamlit_run_app,
        "streamlit_stop_app": streamlit_stop_app,
        "streamlit_list_apps": streamlit_list_apps,
        "streamlit_get_app_url": streamlit_get_app_url,
        "streamlit_modify_app": streamlit_modify_app,
        "streamlit_check_deps": streamlit_check_deps
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_streamlit_service():
    """Initialize the Streamlit service."""
    # Implementation can be added as needed
    pass
