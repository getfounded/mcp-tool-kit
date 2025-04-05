"""
QuickBooks tools for MCP Toolkit.
"""
from app.tools.base.registry import register_tool
from app.tools.quickbooks.service import QuickBooksService

# Import all tools to ensure they're registered
from app.tools.quickbooks.tools import *

# For backward compatibility


def initialize():
    """Initialize the QuickBooks module"""
    return True
