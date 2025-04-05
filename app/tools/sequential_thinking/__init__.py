"""
Sequential Thinking tools for problem solving.

This module provides tools for dynamic, reflective problem-solving through
sequential thoughts.
"""
from app.tools.sequential_thinking.tools import *


def get_sequential_thinking_tools():
    """Return a dictionary of sequential thinking tools for registration."""
    return {
        "sequentialthinking": sequentialthinking,
        "get_thought_history": get_thought_history,
        "get_branch": get_branch,
        "clear_thought_history": clear_thought_history
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_thinking_service():
    """Initialize the sequential thinking service."""
    # Implementation can be added as needed
    pass
