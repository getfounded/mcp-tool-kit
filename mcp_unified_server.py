#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import importlib
import traceback

# MCP SDK imports
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import Tool, TextContent, ImageContent

# Import configuration loader
from config_loader import load_config, is_tool_enabled, get_tool_config, create_default_config

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get(
        "MCP_LOG_LEVEL", "").lower() == "debug" else logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)

# Add tools directory to path to import modules
tools_path = Path(__file__).parent / "tools"
sys.path.append(str(tools_path))

# Load environment variables
load_dotenv()

# Load configuration
config_path = Path(__file__).parent / "config.yaml"
create_default_config(config_path)  # Create default config if it doesn't exist
config = load_config(config_path)

# Initialize MCP server
mcp = FastMCP(
    "Unified MCP Server",
    dependencies=["newsapi-python", "msal", "python-dotenv",
                  "httpx", "pillow", "requests", "pandas", "python-pptx", "nltk"]
)

# Function to dynamically load and register tool modules


def load_tool_module(module_name):
    """Dynamically load a tool module if it's enabled in configuration"""
    if not is_tool_enabled(config, module_name):
        logging.info(
            f"Tool '{module_name}' is disabled in configuration, skipping")
        return False

    try:
        # Import the module
        module = importlib.import_module(f"tools.{module_name}")

        # Set external MCP instance if the module has this function
        if hasattr(module, "set_external_mcp"):
            module.set_external_mcp(mcp)

        # Get module-specific config
        module_config = get_tool_config(config, module_name)

        # Initialize the module if it has an initialize function
        initialization_successful = True
        if hasattr(module, "initialize"):
            try:
                # Pass MCP instance and any module-specific config
                initialization_successful = module.initialize(
                    mcp, **module_config)
            except TypeError:
                # Fall back to just passing MCP if module doesn't accept config
                initialization_successful = module.initialize(mcp)

        if not initialization_successful:
            logging.warning(
                f"Module '{module_name}' initialization returned False, skipping registration")
            return False

        # Register tools through different methods depending on module structure
        tools_registered = False

        # Method 1: Use get_X_tools() function (most modules)
        tools_getter_name = f"get_{module_name}_tools"
        if hasattr(module, tools_getter_name):
            tools_getter = getattr(module, tools_getter_name)
            tools = tools_getter()

            for tool_name, tool_func in tools.items():
                tool_name_str = tool_name if isinstance(
                    tool_name, str) else tool_name.value
                mcp.tool(name=tool_name_str)(tool_func)

            tools_registered = True
            logging.info(
                f"Registered {len(tools)} tools from '{module_name}' using {tools_getter_name}()")

        # Method 2: Direct tool definition in module
        elif hasattr(module, "tools"):
            tools = module.tools
            for tool_name, tool_func in tools.items():
                tool_name_str = tool_name if isinstance(
                    tool_name, str) else tool_name.value
                mcp.tool(name=tool_name_str)(tool_func)

            tools_registered = True
            logging.info(
                f"Registered {len(tools)} tools from '{module_name}' using module.tools")

        # Register resources if the module has them
        resources_registered = False
        resources_getter_name = f"get_{module_name}_resources"
        if hasattr(module, resources_getter_name):
            resources_getter = getattr(module, resources_getter_name)
            resources = resources_getter()

            for resource_path, resource_func in resources.items():
                mcp.resource(resource_path)(resource_func)

            resources_registered = True
            logging.info(
                f"Registered {len(resources)} resources from '{module_name}'")

        if tools_registered or resources_registered:
            logging.info(f"Successfully loaded module '{module_name}'")
            return True
        else:
            logging.warning(
                f"No tools or resources found to register in module '{module_name}'")
            return False

    except ImportError as e:
        logging.warning(f"Could not load '{module_name}' tools: {e}")
        return False
    except Exception as e:
        logging.error(f"Error loading '{module_name}' tools: {str(e)}")
        logging.debug(traceback.format_exc())
        return False


# Define available tool modules - this helps with discovery
AVAILABLE_TOOLS = [
    "ppt",
    "filesystem",
    "time_tools",
    "sequential_thinking",
    "brave_search",
    "browserbase",
    "worldbank",
    "news_api",
    "data_analysis",
    "document_management",
    "outlook",
    "salesforce",
    "linkedin",
    "shopify",
    "yfinance"
]

# Server Lifespan and Startup


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Server lifespan manager - initialize and cleanup resources"""
    try:
        # Log startup message
        logging.info("Starting Unified MCP Server...")

        # Load tool modules
        loaded_modules = []
        for module_name in AVAILABLE_TOOLS:
            if load_tool_module(module_name):
                loaded_modules.append(module_name)

        logging.info(
            f"Loaded {len(loaded_modules)} tool modules: {', '.join(loaded_modules)}")

        # Initialize any services that need async initialization
        # (none in our current implementation)

        # Pass any shared context to the request handlers
        yield {
            "startup_time": datetime.now().isoformat(),
            "loaded_modules": loaded_modules
        }
    finally:
        # Cleanup on shutdown
        logging.info("Shutting down Unified MCP Server...")
        # Close any open resources or connections

# Set lifespan context manager
mcp.lifespan = server_lifespan

# Main execution
if __name__ == "__main__":
    # Add debugging info
    logging.info("Starting MCP Unified Server...")
    logging.debug(f"Python version: {sys.version}")

    # Use configuration from environment variables if available
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    log_level = os.environ.get("MCP_LOG_LEVEL", "debug")

    # Update configuration
    mcp.config = {
        "host": host,
        "port": port,
        "log_level": log_level
    }

    # Run the server with configuration from mcp.config
    mcp.run()
