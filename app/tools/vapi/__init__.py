"""
VAPI tools for voice communication and call management.
"""
from app.tools.vapi.tools import *


def get_vapi_tools():
    """Return a dictionary of VAPI tools for registration."""
    return {
        "vapi_make_call": vapi_make_call,
        "vapi_list_calls": vapi_list_calls,
        "vapi_get_call": vapi_get_call,
        "vapi_end_call": vapi_end_call,
        "vapi_get_recordings": vapi_get_recordings,
        "vapi_add_human": vapi_add_human,
        "vapi_pause_call": vapi_pause_call,
        "vapi_resume_call": vapi_resume_call,
        "vapi_send_event": vapi_send_event
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_vapi_service():
    """Initialize the VAPI service."""
    # Implementation can be added as needed
    return True
