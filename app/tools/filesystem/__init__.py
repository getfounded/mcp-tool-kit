"""
Filesystem tools for secure file operations.
"""
from app.tools.filesystem.tools import *

# Export filesystem tools for the MCP server


def get_filesystem_tools():
    """Return a dictionary of filesystem tools for registration."""
    return {
        "read_file": read_file,
        "read_multiple_files": read_multiple_files,
        "write_file": write_file,
        "edit_file": edit_file,
        "create_directory": create_directory,
        "list_directory": list_directory,
        "directory_tree": directory_tree,
        "move_file": move_file,
        "search_files": search_files,
        "get_file_info": get_file_info,
        "list_allowed_directories": list_allowed_directories
    }

# For MCP integration


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_fs_tools(allowed_directories=None):
    """Initialize filesystem tools with allowed directories."""
    # Implementation can be added as needed
    pass
