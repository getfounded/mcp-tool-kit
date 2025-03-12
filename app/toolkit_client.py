import requests
import json
import logging
from typing import Dict, Any, Optional


class MCPClient:
    """Custom client for interacting with MCP (Model Context Protocol) server."""

    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initialize the MCP client.

        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url.rstrip('/')
        self.logger = logging.getLogger("MCPClient")

    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            params: Parameters to pass to the tool

        Returns:
            Tool execution result as a string
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/tools/{tool_name}",
                json=params,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            error_msg = f"Error calling tool {tool_name}: {str(e)}"
            self.logger.error(error_msg)
            return json.dumps({"error": error_msg})
