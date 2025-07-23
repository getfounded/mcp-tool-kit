"""Base class for all MCP tools."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for MCP tool modules.
    
    All tool modules should inherit from this class and implement
    the required methods for automatic registration.
    """
    
    def __init__(self):
        self.mcp: Optional[FastMCP] = None
        self.initialized = False
        
    def set_mcp(self, mcp: FastMCP) -> None:
        """Set the MCP instance for this tool."""
        self.mcp = mcp
        
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this tool module."""
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of this tool module."""
        pass
        
    @abstractmethod
    def get_tools(self) -> Dict[str, Callable]:
        """Return a dictionary of tool_name -> tool_function."""
        pass
        
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return a list of Python package dependencies."""
        pass
        
    def initialize(self, **kwargs) -> None:
        """Initialize the tool with any required configuration.
        
        Override this method if your tool needs initialization.
        """
        self.initialized = True
        
    def cleanup(self) -> None:
        """Cleanup any resources used by the tool.
        
        Override this method if your tool needs cleanup.
        """
        pass
        
    def validate_environment(self) -> bool:
        """Validate that the environment is properly configured for this tool.
        
        Override this method to check for required environment variables,
        API keys, etc. Return False if the tool should not be loaded.
        """
        return True