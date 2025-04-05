#!/usr/bin/env python3
"""
Enhanced dynamic client wrapper for the MCP Toolkit.
"""
import logging
import inspect
import json
from typing import Any, Dict, List, Optional, Callable, Union, Type

from app.toolkit_client import MCPClient
from app.tools.base.registry import get_all_tools, get_tool_categories, get_tools_by_category
from app.tools.base.service import ToolServiceBase


class Toolkit:
    """Enhanced client wrapper for the MCP Tool Kit providing dynamic access to all tools."""

    def __init__(self, server_url: str = "http://localhost:8000", log_level: str = "INFO"):
        """
        Initialize the MCP Tool Kit client.

        Args:
            server_url: URL of the MCP Tool Kit server
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.client = MCPClient(server_url)
        self.logger = logging.getLogger("MCPToolKit")

        # Set up logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Set log level
        log_level_enum = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level_enum)

        # Cache available tools
        self._tools_info = get_all_tools()
        self._tool_methods = {}

        self.logger.info(
            f"Initialized MCPToolKit with {len(self._tools_info)} available tools")

    def __getattr__(self, name: str) -> Callable:
        """
        Dynamically handle method calls for tools.

        Args:
            name: Name of the attribute/method to get

        Returns:
            Callable method for the specified tool

        Raises:
            AttributeError: If the requested name doesn't match any tool
        """
        # Return cached method if available
        if name in self._tool_methods:
            return self._tool_methods[name]

        # Check if the name matches a tool
        if name in self._tools_info:
            # Create a dynamic method
            def method(*args, **kwargs):
                # Build parameters from args and kwargs based on signature
                tool_info = self._tools_info[name]
                signature = tool_info['signature']
                parameters = {}

                # Map positional args to named parameters
                param_names = list(signature.parameters.keys())
                # Skip 'self', 'cls', and 'ctx' parameters if present
                for skip_param in ('self', 'cls', 'ctx'):
                    if skip_param in param_names:
                        param_names.remove(skip_param)

                # Convert positional args to kwargs
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        parameters[param_names[i]] = arg

                # Add keyword args
                parameters.update(kwargs)

                # Call the tool
                result = self.client.call_tool(name, parameters)

                # Log any errors
                if isinstance(result, dict) and 'error' in result:
                    self.logger.error(
                        f"Error calling {name}: {result['error']}")

                return result

            # Add docstring from original function
            method.__doc__ = self._tools_info[name].get('doc')

            # Cache the method
            self._tool_methods[name] = method
            return method

        # Not a tool, raise AttributeError
        raise AttributeError(
            f"'{self.__class__.__name__}' has no attribute '{name}'")

    def list_available_tools(self, include_parameters: bool = False) -> List[Dict[str, Any]]:
        """
        List all available tools with their documentation.

        Args:
            include_parameters: Whether to include detailed parameter information

        Returns:
            List of dictionaries with tool information
        """
        tools = []
        for name, info in self._tools_info.items():
            tool_info = {
                'name': name,
                'category': info.get('category'),
                'description': info.get('description', ''),
                'doc': info.get('doc', '').strip(),
                'signature': str(info.get('signature'))
            }

            # Add detailed parameter info if requested
            if include_parameters and 'parameters' in info:
                tool_info['parameters'] = info['parameters']

            tools.append(tool_info)

        return tools

    def list_categories(self) -> List[str]:
        """
        List all available tool categories.

        Returns:
            List of category names
        """
        return get_tool_categories()

    def list_tools_by_category(self, category: str, include_parameters: bool = False) -> List[Dict[str, Any]]:
        """
        List all tools in a specific category.

        Args:
            category: Category name
            include_parameters: Whether to include detailed parameter information

        Returns:
            List of dictionaries with tool information
        """
        tools = []
        category_tools = get_tools_by_category(category)

        for name, info in category_tools.items():
            tool_info = {
                'name': name,
                'description': info.get('description', ''),
                'doc': info.get('doc', '').strip(),
                'signature': str(info.get('signature'))
            }

            # Add detailed parameter info if requested
            if include_parameters and 'parameters' in info:
                tool_info['parameters'] = info['parameters']

            tools.append(tool_info)

        return tools

    def get_tool_details(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool details or None if not found
        """
        if tool_name not in self._tools_info:
            return None

        info = self._tools_info[tool_name]
        return {
            'name': tool_name,
            'category': info.get('category'),
            'description': info.get('description', ''),
            'doc': info.get('doc', '').strip(),
            'signature': str(info.get('signature')),
            'parameters': info.get('parameters', {})
        }

    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for tools by name or description.

        Args:
            query: Search query

        Returns:
            List of tool information dictionaries
        """
        results = []
        query = query.lower()

        for name, info in self._tools_info.items():
            # Check if query matches tool name
            if query in name.lower():
                results.append({
                    'name': name,
                    'category': info.get('category'),
                    'description': info.get('description', ''),
                    'doc': info.get('doc', '').strip()
                })
                continue

            # Check if query matches description
            description = info.get('description', '').lower()
            if query in description:
                results.append({
                    'name': name,
                    'category': info.get('category'),
                    'description': info.get('description', ''),
                    'doc': info.get('doc', '').strip()
                })
                continue

            # Check if query matches docstring
            doc = info.get('doc', '').lower()
            if query in doc:
                results.append({
                    'name': name,
                    'category': info.get('category'),
                    'description': info.get('description', ''),
                    'doc': info.get('doc', '').strip()
                })

        return results
