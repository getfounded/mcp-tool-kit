#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import uvicorn

# MCP SDK imports
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import Tool, TextContent, ImageContent

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

# Initialize MCP server
mcp = FastMCP(
    "Unified MCP Server",
    dependencies=["newsapi-python", "msal", "python-dotenv",
                  "httpx", "pillow", "requests", "pandas", "python-pptx", "nltk"]
)

# Initialize PowerPoint tools
try:
    from tools.ppt import get_ppt_tools, PowerPointTools, set_external_mcp
    # Pass our MCP instance to the ppt module
    set_external_mcp(mcp)
    ppt_available = True

    # Register PowerPoint tools
    ppt_tools = get_ppt_tools()

    for tool_name, tool_func in ppt_tools.items():
        # Register each PowerPoint tool with the main MCP instance
        tool_name_str = tool_name if isinstance(
            tool_name, str) else tool_name.value
        mcp.tool(name=tool_name_str)(tool_func)

    # Add PowerPoint dependencies to MCP dependencies
    mcp.dependencies.extend([
        "python-pptx",
        "nltk",
        "pillow"
    ])

    logging.info("PowerPoint tools registered successfully.")
except ImportError as e:
    ppt_available = False
    logging.warning(f"Could not load PowerPoint tools: {e}")

# Initialize Playwright tools
try:
    from tools.browser_automation import get_playwright_tools, set_external_mcp, initialize

    # Pass our MCP instance to the playwright module
    set_external_mcp(mcp)

    # Initialize playwright tools
    initialize()

    # Register playwright tools
    playwright_tools = get_playwright_tools()
    for tool_name, tool_func in playwright_tools.items():
        # Register each playwright tool with the main MCP instance
        tool_name_str = tool_name if isinstance(
            tool_name, str) else tool_name.value
        mcp.tool(name=tool_name_str)(tool_func)

    # Add Playwright dependencies to MCP dependencies
    mcp.dependencies.extend([
        "playwright"
    ])

    logging.info("Playwright tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load Playwright tools: {e}")

# Initialize Filesystem tools
try:
    from tools.filesystem import get_filesystem_tools, set_external_mcp, initialize_fs_tools

    # Pass our MCP instance to the filesystem module
    set_external_mcp(mcp)

    # Get allowed directories from environment variable
    env_dirs = os.environ.get("MCP_FILESYSTEM_DIRS", "")
    allowed_dirs = [os.path.expanduser(d.strip())
                    for d in env_dirs.split(",") if d.strip()]

    # Default to user's home directory if no dirs specified
    if not allowed_dirs:
        allowed_dirs = [os.path.expanduser("~")]

    initialize_fs_tools(allowed_dirs)

    # Register filesystem tools
    fs_tools = get_filesystem_tools()
    for tool_name, tool_func in fs_tools.items():
        # Register each filesystem tool with the main MCP instance
        mcp.tool(name=tool_name)(tool_func)

    logging.info("Filesystem tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load filesystem tools: {e}")

# Initialize Time tools
try:
    from tools.time_tools import get_time_tools, set_external_mcp, initialize_time_tools

    # Pass our MCP instance to the time tools module
    set_external_mcp(mcp)

    # Initialize time tools
    initialize_time_tools()

    # Register time tools
    time_tools = get_time_tools()
    for tool_name, tool_func in time_tools.items():
        # Register each time tool with the main MCP instance
        tool_name_str = tool_name if isinstance(
            tool_name, str) else tool_name.value
        mcp.tool(name=tool_name_str)(tool_func)

    logging.info("Time tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load time tools: {e}")

# Initialize Sequential Thinking tools
try:
    from tools.sequential_thinking import get_sequential_thinking_tools, set_external_mcp, initialize_thinking_service

    # Pass our MCP instance to the sequential thinking module
    set_external_mcp(mcp)

    # Initialize sequential thinking tools
    initialize_thinking_service()

    # Register sequential thinking tools
    thinking_tools = get_sequential_thinking_tools()
    for tool_name, tool_func in thinking_tools.items():
        # Register each sequential thinking tool with the main MCP instance
        mcp.tool(name=tool_name)(tool_func)

    logging.info("Sequential Thinking tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load Sequential Thinking tools: {e}")

# Initialize FRED API tools
try:
    from tools.fred import get_fred_api_tools, set_external_mcp, initialize_fred_api_service, initialize

    # Pass our MCP instance to the FRED module
    set_external_mcp(mcp)

    # Initialize FRED tools with API key from environment variable
    fred_api_key = os.environ.get("FRED_API_KEY")
    if fred_api_key:
        # Call the module's initialize function
        initialize(mcp)

        # Register FRED tools
        fred_tools = get_fred_api_tools()
        for tool_name, tool_func in fred_tools.items():
            # Register each FRED tool with the main MCP instance
            mcp.tool(name=tool_name)(tool_func)

        logging.info("FRED API tools registered successfully.")
    else:
        logging.warning(
            "FRED API key not configured. FRED API tools will not be available.")
except ImportError as e:
    logging.warning(f"Could not load FRED API tools: {e}")

# Initialize YFinance tools
try:
    from tools.yfinance import get_yfinance_tools, set_external_mcp, initialize

    # Pass our MCP instance to the yfinance module
    set_external_mcp(mcp)

    # Initialize YFinance tools
    if initialize(mcp):
        # Register YFinance tools
        yfinance_tools = get_yfinance_tools()
        for tool_name, tool_func in yfinance_tools.items():
            # Register each YFinance tool with the main MCP instance
            tool_name_str = tool_name if isinstance(
                tool_name, str) else tool_name.value
            mcp.tool(name=tool_name_str)(tool_func)

        # Add YFinance dependencies to MCP dependencies
        mcp.dependencies.extend(["yfinance", "pandas", "numpy"])

        logging.info("YFinance tools registered successfully.")
    else:
        logging.warning("Failed to initialize YFinance tools.")
except ImportError as e:
    logging.warning(f"Could not load YFinance tools: {e}")

# Initialize Streamlit tools
try:
    from tools.streamlit import get_streamlit_tools, set_external_mcp, initialize

    # Pass our MCP instance to the streamlit module
    set_external_mcp(mcp)

    # Initialize Streamlit tools
    # Get custom apps directory from environment variable if set
    apps_dir = os.environ.get("STREAMLIT_APPS_DIR")

    if initialize(mcp):
        # Register Streamlit tools
        streamlit_tools = get_streamlit_tools()
        for tool_name, tool_func in streamlit_tools.items():
            # Register each Streamlit tool with the main MCP instance
            tool_name_str = tool_name if isinstance(
                tool_name, str) else tool_name.value
            mcp.tool(name=tool_name_str)(tool_func)

        # Add Streamlit dependencies to MCP dependencies
        mcp.dependencies.extend(
            ["streamlit", "pandas", "numpy", "matplotlib", "plotly"])

        logging.info("Streamlit tools registered successfully.")
    else:
        logging.warning(
            "Failed to initialize Streamlit tools. Make sure streamlit is installed.")
except ImportError as e:
    logging.warning(f"Could not load Streamlit tools: {e}")


# Initialize Brave Search tools
try:
    from tools.brave_search import get_brave_search_tools, set_external_mcp, initialize_brave_search

    # Pass our MCP instance to the brave search module
    set_external_mcp(mcp)

    # Initialize brave search tools with API key from environment variable
    brave_api_key = os.environ.get("BRAVE_API_KEY")
    if brave_api_key:
        initialize_brave_search(brave_api_key)

        # Register brave search tools
        brave_tools = get_brave_search_tools()
        for tool_name, tool_func in brave_tools.items():
            # Register each brave search tool with the main MCP instance
            mcp.tool(name=tool_name)(tool_func)

        logging.info("Brave Search tools registered successfully.")
    else:
        logging.warning(
            "Brave Search API key not configured. Brave Search tools will not be available.")
except ImportError as e:
    logging.warning(f"Could not load Brave Search tools: {e}")

# Initialize World Bank tools
try:
    from tools.worldbank import get_worldbank_tools, get_worldbank_resources, set_external_mcp, initialize_worldbank_service

    # Pass our MCP instance to the world bank module
    set_external_mcp(mcp)

    # Initialize world bank tools
    initialize_worldbank_service()

    # Register world bank tools
    worldbank_tools = get_worldbank_tools()
    for tool_name, tool_func in worldbank_tools.items():
        # Register each world bank tool with the main MCP instance
        mcp.tool(name=tool_name)(tool_func)

    # Register world bank resources
    worldbank_resources = get_worldbank_resources()
    for resource_path, resource_func in worldbank_resources.items():
        # Register each world bank resource with the main MCP instance
        mcp.resource(resource_path)(resource_func)

    logging.info("World Bank tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load World Bank tools: {e}")

# Initialize News API tools
try:
    from tools.news_api import get_news_api_tools, set_external_mcp, initialize_news_api_service

    # Pass our MCP instance to the news api module
    set_external_mcp(mcp)

    # Initialize news api tools with API key from environment variable
    news_api_key = os.environ.get("NEWS_API_KEY")
    if news_api_key:
        initialize_news_api_service(news_api_key)

        # Register news api tools
        news_api_tools = get_news_api_tools()
        for tool_name, tool_func in news_api_tools.items():
            # Register each news api tool with the main MCP instance
            mcp.tool(name=tool_name)(tool_func)

        logging.info("News API tools registered successfully.")
    else:
        logging.warning(
            "News API key not configured. News API tools will not be available.")
except ImportError as e:
    logging.warning(f"Could not load News API tools: {e}")

# Validate required environment variables
REQUIRED_ENV_VARS = {
    "BRAVE_API_KEY": "For Brave Search functionality",
    "BROWSERBASE_API_KEY": "For browser automation functionality",
    "BROWSERBASE_PROJECT_ID": "For browser automation functionality",
    "NEWS_API_KEY": "For NewsAPI functionality"
}

missing_vars = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
if missing_vars:
    logging.warning("The following environment variables are missing:")
    for var in missing_vars:
        logging.warning(f"  - {var}: {REQUIRED_ENV_VARS[var]}")
    logging.warning("Some functionality may be limited.")

# Server Lifespan and Startup


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Server lifespan manager - initialize and cleanup resources"""
    try:
        # Log startup message
        logging.info("Starting Unified MCP Server...")

        # Initialize any services that need async initialization
        # (none in our current implementation)

        # Pass any shared context to the request handlers
        yield {
            "startup_time": datetime.now().isoformat()
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

    # Import uvicorn to run the ASGI application
    import uvicorn

    # Run the server using uvicorn instead of mcp.run()
    logging.info(f"Starting server at http://{host}:{port}")
    uvicorn.run(mcp.app, host=host, port=port, log_level=log_level.lower())
