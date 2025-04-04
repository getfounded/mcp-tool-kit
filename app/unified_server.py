#!/usr/bin/env python3
"""
Enhanced unified MCP Server with automatic tool registration and monitoring.
"""
import os
import sys
import logging
import argparse
import time
import threading
import signal
import json
from typing import Dict, Any, List, Optional, Set, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UnifiedServer")

# Import tool registry and base classes
from app.tools.base.registry import get_all_tools, get_tool_categories, clear_registry
from app.tools.base.service import ToolServiceBase
from mcp.server.fastmcp import FastMCP

class PerformanceMonitor:
    """Performance monitoring for tool executions"""
    
    def __init__(self):
        """Initialize the performance monitor"""
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_execution(self, tool_name: str, execution_time: float, success: bool):
        """
        Record a tool execution.
        
        Args:
            tool_name: Name of the executed tool
            execution_time: Execution time in seconds
            success: Whether the execution succeeded
        """
        with self.lock:
            if tool_name not in self.metrics:
                self.metrics[tool_name] = {
                    'calls': 0,
                    'successful_calls': 0,
                    'total_time': 0.0,
                    'avg_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0
                }
            
            # Update metrics
            metrics = self.metrics[tool_name]
            metrics['calls'] += 1
            if success:
                metrics['successful_calls'] += 1
            metrics['total_time'] += execution_time
            metrics['avg_time'] = metrics['total_time'] / metrics['calls']
            metrics['min_time'] = min(metrics['min_time'], execution_time)
            metrics['max_time'] = max(metrics['max_time'], execution_time)
    
    def get_metrics(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Args:
            tool_name: Optional tool name to get metrics for
            
        Returns:
            Dictionary of metrics
        """
        with self.lock:
            if tool_name:
                return self.metrics.get(tool_name, {})
            return self.metrics

def create_mcp_server(name: str = "Unified MCP Server", host: str = "0.0.0.0", 
                     port: int = 8000, log_level: str = "info", 
                     enable_monitoring: bool = True):
    """
    Create and configure the MCP server with enhanced features.
    
    Args:
        name: Server name
        host: Host address to bind to
        port: Port to listen on
        log_level: Logging level
        enable_monitoring: Whether to enable performance monitoring
        
    Returns:
        Tuple of (FastMCP instance, PerformanceMonitor)
    """
    # Create MCP server
    mcp = FastMCP(name)
    
    # Configure server
    mcp.config = {
        "host": host,
        "port": port,
        "log_level": log_level
    }
    
    # Create performance monitor if enabled
    monitor = PerformanceMonitor() if enable_monitoring else None
    
    return mcp, monitor

def register_tool_wrapper(mcp: FastMCP, tool_name: str, tool_func: Callable, 
                         monitor: Optional[PerformanceMonitor] = None) -> Callable:
    """
    Create a wrapper for a tool function with monitoring.
    
    Args:
        mcp: FastMCP instance
        tool_name: Name of the tool
        tool_func: Tool function to wrap
        monitor: Optional performance monitor
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        
        try:
            result = tool_func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
        finally:
            execution_time = time.time() - start_time
            
            # Record metrics if monitoring is enabled
            if monitor:
                monitor.record_execution(tool_name, execution_time, success)
    
    # Copy metadata from original function
    wrapper.__name__ = tool_func.__name__
    wrapper.__doc__ = tool_func.__doc__
    
    return wrapper

def register_all_tools(mcp: FastMCP, monitor: Optional[PerformanceMonitor] = None) -> int:
    """
    Register all discovered tools with the MCP server.
    
    Args:
        mcp: FastMCP instance
        monitor: Optional performance monitor
        
    Returns:
        Number of successfully registered tools
    """
    # Get all discovered tools
    tools = get_all_tools()
    
    # Track successful registrations
    success_count = 0
    
    # Register each tool
    for tool_name, tool_info in tools.items():
        try:
            # Create wrapper with monitoring if enabled
            func = tool_info['function']
            wrapped_func = register_tool_wrapper(mcp, tool_name, func, monitor)
            
            # Register the wrapped function
            mcp.tool(name=tool_name)(wrapped_func)
            logger.info(f"Registered tool: {tool_name}")
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to register tool {tool_name}: {e}")
    
    return success_count

def register_admin_tools(mcp: FastMCP, monitor: Optional[PerformanceMonitor] = None) -> None:
    """
    Register administrative tools with the MCP server.
    
    Args:
        mcp: FastMCP instance
        monitor: Optional performance monitor
    """
    @mcp.tool(name="get_tool_categories")
    def get_tool_categories():
        """Get all tool categories"""
        return get_tool_categories()
    
    @mcp.tool(name="get_tools_by_category")
    def get_tools_by_category(category: str):
        """Get all tools in a specific category"""
        return [name for name, info in get_all_tools().items() 
                if info.get('category') == category]
    
    @mcp.tool(name="get_server_status")
    def get_server_status():
        """Get server status and basic information"""
        return {
            "status": "running",
            "tool_count": len(get_all_tools()),
            "categories": get_tool_categories(),
            "uptime": time.time() - server_start_time
        }
    
    if monitor:
        @mcp.tool(name="get_performance_metrics")
        def get_performance_metrics(tool_name: Optional[str] = None):
            """Get performance metrics for tools"""
            return monitor.get_metrics(tool_name)

# Global variables for signal handling
shutdown_event = threading.Event()
server_start_time = time.time()

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info("Received shutdown signal")
    shutdown_event.set()
    
def run_server(mcp: FastMCP):
    """
    Run the MCP server in a separate thread.
    
    Args:
        mcp: FastMCP instance
    """
    def server_thread():
        try:
            mcp.run()
        except Exception as e:
            logger.error(f"Server error: {e}")
            shutdown_event.set()
    
    thread = threading.Thread(target=server_thread)
    thread.daemon = True
    thread.start()
    
    return thread

def main():
    """Main entry point for the enhanced unified server"""
    global server_start_time
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Enhanced Unified MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--name", default="Unified MCP Server", help="Server name")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"],
                       help="Logging level")
    parser.add_argument("--no-monitoring", action="store_true", help="Disable performance monitoring")
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Record server start time
    server_start_time = time.time()
    
    # Create server with monitoring
    mcp, monitor = create_mcp_server(
        args.name, 
        args.host, 
        args.port, 
        args.log_level, 
        not args.no_monitoring
    )
    
    # Import tools (triggers auto-discovery)
    import app.tools
    
    # Register tools
    tool_count = register_all_tools(mcp, monitor)
    logger.info(f"Registered {tool_count} tools")
    
    # Register admin tools
    register_admin_tools(mcp, monitor)
    
    # Run the server in a separate thread
    logger.info(f"Starting MCP server on {args.host}:{args.port}")
    server_thread = run_server(mcp)
    
    # Wait for shutdown signal
    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    
    # Perform cleanup
    logger.info("Shutting down server...")
    # Wait for server to finish (with timeout)
    server_thread.join(timeout=5)
    
    logger.info("Server shutdown complete")

if __name__ == "__main__":
    main()