#!/usr/bin/env python3
"""Dynamic MCP Server with automatic tool registration."""
import sys
import os
from pathlib import Path
import json
from datetime import datetime
from dotenv import load_dotenv
import logging
import asyncio
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.models import InitializationOptions
from mcp import stdio_server, sse_server

# Add app/tools directory to path
tools_path = Path(__file__).parent / "app" / "tools"
sys.path.append(str(tools_path))

from app.tools.tool_registry import ToolRegistry
from config_loader import load_config, is_tool_enabled, get_tool_config, create_default_config

# Load environment variables
load_dotenv()

# Load configuration
config = load_config()
if not config.get("enabled_tools"):
    create_default_config()
    config = load_config()

# Configure logging
log_level = config.get("server", {}).get("log_level", 
                                         os.environ.get("MCP_LOG_LEVEL", "INFO")).upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "Dynamic MCP Server",
    dependencies=[]  # Dependencies will be added dynamically
)

# Store startup time for health checks
mcp.startup_time = datetime.now().isoformat()


@mcp.tool(name="health_check")
async def health_check(ctx: Context):
    """Check the health status of the MCP server."""
    try:
        registry_status = registry.get_status() if 'registry' in globals() else {}
        
        status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(mcp.startup_time)).total_seconds(),
            "tools": registry_status
        }
        
        return status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool(name="list_tools")
async def list_tools(ctx: Context):
    """List all registered tools and their status."""
    if 'registry' not in globals():
        return {"error": "Tool registry not initialized"}
        
    status = registry.get_status()
    
    # Get detailed tool information
    tool_details = {}
    for tool_name, tool in registry.tools.items():
        tool_details[tool_name] = {
            "description": tool.get_description(),
            "functions": list(tool.get_tools().keys()),
            "dependencies": tool.get_dependencies()
        }
    
    return {
        "registered_tools": tool_details,
        "failed_tools": status["failed"],
        "total_functions": status["total_tools"],
        "total_dependencies": status["total_dependencies"]
    }


def initialize_tools():
    """Initialize and register all tools."""
    global registry
    
    logger.info("Initializing tool registry...")
    registry = ToolRegistry(mcp)
    
    # Get tool-specific initialization parameters from environment
    init_params = {
        "filesystem": {
            "allowed_dirs": [os.path.expanduser(d.strip()) 
                           for d in os.environ.get("MCP_FILESYSTEM_DIRS", "~").split(",") 
                           if d.strip()]
        }
    }
    
    # Register all tools with configuration
    tools_dir = Path(__file__).parent / "app" / "tools"
    results = registry.register_all_tools(tools_dir, config=config, **init_params)
    
    # Log results
    successful = [name for name, success in results.items() if success]
    failed = [name for name, success in results.items() if not success]
    
    logger.info(f"Successfully registered {len(successful)} tools: {', '.join(successful)}")
    if failed:
        logger.warning(f"Failed to register {len(failed)} tools: {', '.join(failed)}")
    
    # Log final status
    status = registry.get_status()
    logger.info(f"Total functions registered: {status['total_tools']}")
    logger.info(f"Total dependencies: {status['total_dependencies']}")


async def run_stdio():
    """Run the server using stdio transport."""
    logger.info("Starting MCP server with stdio transport...")
    
    # Initialize tools before starting the server
    initialize_tools()
    
    # Run the stdio server
    async with stdio_server(
        mcp.get_handler()
    ) as server:
        await server.wait()


async def run_sse(host: str = "0.0.0.0", port: int = 8080):
    """Run the server using SSE transport."""
    logger.info(f"Starting MCP server with SSE transport on {host}:{port}...")
    
    # Initialize tools before starting the server
    initialize_tools()
    
    # Create SSE server
    from mcp.server.sse import SseServerTransport
    from aiohttp import web
    
    # Create the SSE transport
    sse_transport = SseServerTransport(mcp.get_handler())
    
    # Create web app
    app = web.Application()
    
    # Add SSE endpoint
    app.router.add_get("/sse", sse_transport.handle_sse)
    app.router.add_post("/messages", sse_transport.handle_messages)
    
    # Add a simple index page
    async def index(request):
        return web.Response(text="""
        <html>
        <head><title>MCP Server (SSE)</title></head>
        <body>
            <h1>MCP Server is running</h1>
            <p>SSE endpoint: /sse</p>
            <p>Messages endpoint: /messages</p>
            <p>Use the health_check tool to verify server status.</p>
        </body>
        </html>
        """, content_type='text/html')
    
    app.router.add_get("/", index)
    
    # Run the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    
    logger.info(f"SSE server listening on http://{host}:{port}")
    await site.start()
    
    # Keep the server running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down SSE server...")
    finally:
        await runner.cleanup()


def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic MCP Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse"], 
        default="stdio",
        help="Transport mechanism to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind SSE server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind SSE server to (default: 8080)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.transport == "stdio":
            asyncio.run(run_stdio())
        else:
            asyncio.run(run_sse(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        if 'registry' in globals():
            registry.cleanup()


if __name__ == "__main__":
    main()