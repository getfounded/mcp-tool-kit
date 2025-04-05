"""
Project Management tools for MCP Toolkit.
"""
from app.tools.base.registry import register_tool
from app.tools.project_management.service import ProjectManagementService

# Import all tools to ensure they're registered
from app.tools.project_management.tools import *

# For backward compatibility


def initialize():
    """Initialize the Project Management module"""
    return True
