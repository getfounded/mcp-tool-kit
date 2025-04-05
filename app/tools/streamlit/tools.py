#!/usr/bin/env python3
"""
Streamlit tools implementation using the decorator pattern.
"""
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from app.tools.base.registry import register_tool
from app.tools.streamlit.service import StreamlitService


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="Create a new Streamlit app with the provided code"
)
async def streamlit_create_app(
    self,
    app_id: str,
    code: str,
    overwrite: bool = False
) -> str:
    """
    Create a new Streamlit app with the provided code

    Creates a Python file with the given code that can be run as a Streamlit application.

    Args:
        app_id: Unique identifier for the app (letters, numbers, underscores, and hyphens only)
        code: Python code for the Streamlit app
        overwrite: Whether to overwrite an existing app with the same ID

    Returns:
        JSON string with creation result
    """
    try:
        result = await self.create_app(app_id, code, overwrite)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="Run a Streamlit app as a background process"
)
async def streamlit_run_app(
    self,
    app_id: str,
    port: Optional[int] = None,
    browser: bool = False
) -> str:
    """
    Run a Streamlit app as a background process

    Starts the Streamlit app in the background and makes it accessible via HTTP.

    Args:
        app_id: Identifier of the app to run
        port: Optional port number (if not specified, an available port will be used)
        browser: Whether to open the app in a browser window

    Returns:
        JSON string with run result including URL
    """
    try:
        result = await self.run_app(app_id, port, browser)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="Stop a running Streamlit app"
)
async def streamlit_stop_app(self, app_id: str) -> str:
    """
    Stop a running Streamlit app

    Terminates a running Streamlit application process.

    Args:
        app_id: Identifier of the app to stop

    Returns:
        JSON string with stop result
    """
    try:
        result = await self.stop_app(app_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="List all available Streamlit apps"
)
async def streamlit_list_apps(self) -> str:
    """
    List all available Streamlit apps

    Returns information about all Streamlit apps created in the system.

    Returns:
        JSON string with list of apps and their status
    """
    try:
        result = await self.list_apps()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="Get the URL for a running Streamlit app"
)
async def streamlit_get_app_url(self, app_id: str) -> str:
    """
    Get the URL for a running Streamlit app

    Retrieves the access URL for a running Streamlit application.

    Args:
        app_id: Identifier of the app

    Returns:
        JSON string with URL information
    """
    try:
        result = await self.get_app_url(app_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="Modify an existing Streamlit app"
)
async def streamlit_modify_app(
    self,
    app_id: str,
    code_updates: Optional[List[Tuple[str, str]]] = None,
    append_code: Optional[str] = None
) -> str:
    """
    Modify an existing Streamlit app

    Updates the code of an existing Streamlit application. Can replace specific parts
    of the code or append new code to the end.

    Args:
        app_id: Identifier of the app to modify
        code_updates: List of tuples (old_text, new_text) for text replacements
        append_code: Code to append to the end of the app

    Returns:
        JSON string with modification result
    """
    try:
        result = await self.modify_app(app_id, code_updates, append_code)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


@register_tool(
    category="app_development",
    service_class=StreamlitService,
    description="Check if Streamlit and required dependencies are installed"
)
async def streamlit_check_deps(self) -> str:
    """
    Check if Streamlit and required dependencies are installed

    Verifies that Streamlit and common supporting libraries are available on the system.

    Returns:
        JSON string with dependency status information
    """
    try:
        result = await self.check_dependencies()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)
