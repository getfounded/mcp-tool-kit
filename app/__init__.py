"""
MCP Tool Kit - Model Context Protocol Tools
"""

# Import main classes for easy access
from .sdk import MCPToolKitSDK, ToolResult, FileOperations, GitOperations, WebOperations
from .toolkit import MCPToolKit  # Legacy, for backward compatibility

__version__ = "1.0.0"
__all__ = [
    "MCPToolKitSDK",
    "ToolResult", 
    "FileOperations",
    "GitOperations",
    "WebOperations",
    "MCPToolKit"  # Legacy
]

# Convenience imports
SDK = MCPToolKitSDK  # Alias for shorter imports