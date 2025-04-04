#!/usr/bin/env python3
"""
Enhanced MCP Toolkit main entry point with improved configuration and features.
"""
import os
import sys
import logging
import argparse
import json
import textwrap
from typing import Dict, Any, List, Optional

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MCPToolkit")

def start_server(args):
    """
    Start the MCP Unified Server with the specified configuration.
    
    Args:
        args: Command-line arguments
    """
    # Convert arguments to the format expected by unified_server
    sys.argv = [
        sys.argv[0],
        f"--host={args.host}",
        f"--port={args.port}",
        f"--log-level={args.log_level}"
    ]
    
    # Add optional arguments
    if args.name:
        sys.argv.append(f"--name={args.name}")
    
    if args.no_monitoring:
        sys.argv.append("--no-monitoring")
    
    # Start the server
    from app.unified_server import main
    main()

def display_tool_info(toolkit, tool_name: str):
    """
    Display detailed information about a specific tool.
    
    Args:
        toolkit: MCPToolKit instance
        tool_name: Name of the tool to display info for
    """
    tool_info = toolkit.get_tool_details(tool_name)
    
    if not tool_info:
        print(f"Tool '{tool_name}' not found")
        return
    
    # Display tool information
    print(f"\n=== {tool_info['name']} ===")
    print(f"Category: {tool_info.get('category', 'Uncategorized')}")
    
    if tool_info.get('description'):
        print(f"Description: {tool_info['description']}")
    
    # Format and display docstring
    if tool_info.get('doc'):
        print("\nDocumentation:")
        # Format docstring
        doc = textwrap.dedent(tool_info['doc']).strip()
        for line in doc.split('\n'):
            print(f"  {line}")
    
    # Display parameters
    if tool_info.get('parameters'):
        print("\nParameters:")
        for param_name, param_info in tool_info['parameters'].items():
            required = "required" if param_info.get('required') else "optional"
            param_type = f", {param_info.get('type')}" if param_info.get('type') else ""
            default = f", default={param_info.get('default')}" if param_info.get('default') is not None else ""
            print(f"  {param_name}: {required}{param_type}{default}")
    
    print(f"\nSignature: {tool_info['signature']}")

def start_client(args):
    """
    Start an interactive client session with improved features.
    
    Args:
        args: Command-line arguments
    """
    from app.toolkit import MCPToolKit
    
    # Create toolkit instance
    toolkit = MCPToolKit(args.server, log_level=args.log_level)
    
    print("=== MCP Toolkit Interactive Client ===")
    print(f"Connected to server: {args.server}")
    
    # Display available categories
    print("\nAvailable tool categories:")
    categories = toolkit.list_categories()
    for category in categories:
        print(f"- {category}")
    
    print("\nCommands:")
    print("  help                 - Show this help message")
    print("  list                 - List all available tools")
    print("  category:<name>      - List tools in a category")
    print("  info:<tool>          - Show detailed information about a tool")
    print("  search:<query>       - Search for tools")
    print("  exit, quit           - Exit the client")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ["exit", "quit"]:
                break
            
            elif command.lower() == "help":
                print("\nCommands:")
                print("  help                 - Show this help message")
                print("  list                 - List all available tools")
                print("  category:<name>      - List tools in a category")
                print("  info:<tool>          - Show detailed information about a tool")
                print("  search:<query>       - Search for tools")
                print("  exit, quit           - Exit the client")
            
            elif command.lower() == "list":
                tools = toolkit.list_available_tools()
                print("\nAll available tools:")
                current_category = None
                
                # Sort tools by category
                tools.sort(key=lambda t: (t.get('category', 'ZZZ'), t['name']))
                
                for tool in tools:
                    category = tool.get('category', 'Uncategorized')
                    
                    # Print category header if changed
                    if category != current_category:
                        print(f"\n[{category}]")
                        current_category = category
                    
                    # Print tool info
                    description = tool.get('description', '')
                    if description:
                        print(f"- {tool['name']}: {description}")
                    else:
                        print(f"- {tool['name']}")
            
            elif command.startswith("category:"):
                category = command[9:].strip()
                tools = toolkit.list_tools_by_category(category)
                
                if not tools:
                    print(f"No tools found in category '{category}'")
                    continue
                
                print(f"\nTools in category '{category}':")
                for tool in tools:
                    # Print tool info with description
                    description = tool.get('description', '')
                    if description:
                        print(f"- {tool['name']}: {description}")
                    else:
                        print(f"- {tool['name']}")
            
            elif command.startswith("info:"):
                tool_name = command[5:].strip()
                display_tool_info(toolkit, tool_name)
            
            elif command.startswith("search:"):
                query = command[7:].strip()
                results = toolkit.search_tools(query)
                
                if not results:
                    print(f"No tools found matching '{query}'")
                    continue
                
                print(f"\nSearch results for '{query}':")
                for tool in results:
                    category = tool.get('category', 'Uncategorized')
                    description = tool.get('description', '')
                    if description:
                        print(f"- {tool['name']} [{category}]: {description}")
                    else:
                        print(f"- {tool['name']} [{category}]")
            
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def list_tools(args):
    """
    List available tools with optional filtering.
    
    Args:
        args: Command-line arguments
    """
    from app.toolkit import MCPToolKit
    
    # Create toolkit instance
    toolkit = MCPToolKit(args.server, log_level=args.log_level)
    
    # Filter by category if specified
    if args.category:
        tools = toolkit.list_tools_by_category(args.category)
        print(f"Tools in category '{args.category}':")
    else:
        tools = toolkit.list_available_tools()
        print("All available tools:")
    
    # Display tools
    for tool in tools:
        description = tool.get('description', '')
        if description:
            print(f"- {tool['name']}: {description}")
        else:
            print(f"- {tool['name']}")

def show_categories(args):
    """
    Show available tool categories.
    
    Args:
        args: Command-line arguments
    """
    from app.toolkit import MCPToolKit
    
    # Create toolkit instance
    toolkit = MCPToolKit(args.server, log_level=args.log_level)
    
    # Get and display categories
    categories = toolkit.list_categories()
    print("Available tool categories:")
    for category in categories:
        print(f"- {category}")

def run_tool(args):
    """
    Run a specific tool with provided parameters.
    
    Args:
        args: Command-line arguments
    """
    from app.toolkit import MCPToolKit
    import json
    
    # Create toolkit instance
    toolkit = MCPToolKit(args.server, log_level=args.log_level)
    
    # Get tool details
    tool_info = toolkit.get_tool_details(args.tool)
    
    if not tool_info:
        print(f"Tool '{args.tool}' not found")
        return 1
    
    # Parse parameters
    params = {}
    if args.params:
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError:
            print("Error: Invalid JSON parameters")
            return 1
    
    # Get the tool method
    tool_method = getattr(toolkit, args.tool)
    
    # Call the tool
    try:
        result = tool_method(**params)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error executing tool: {e}")
        return 1

def main():
    """Enhanced main entry point with improved command-line interface"""
    parser = argparse.ArgumentParser(
        description="MCP Toolkit - A dynamic toolkit for various tools and services"
    )
    
    # Common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--server", default="http://localhost:8000", 
        help="MCP server URL"
    )
    common_parser.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        default="INFO", help="Logging level"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command", 
        help="Command to run",
        required=True
    )
    
    # Server command
    server_parser = subparsers.add_parser(
        "server", 
        help="Start the MCP server",
        parents=[common_parser]
    )
    server_parser.add_argument(
        "--host", default="0.0.0.0", 
        help="Host to bind to"
    )
    server_parser.add_argument(
        "--port", type=int, default=8000, 
        help="Port to listen on"
    )
    server_parser.add_argument(
        "--name", default=None, 
        help="Server name"
    )
    server_parser.add_argument(
        "--no-monitoring", action="store_true",
        help="Disable performance monitoring"
    )
    server_parser.set_defaults(func=start_server)
    
    # Client command
    client_parser = subparsers.add_parser(
        "client", 
        help="Start an interactive client",
        parents=[common_parser]
    )
    client_parser.set_defaults(func=start_client)
    
    # List tools command
    list_parser = subparsers.add_parser(
        "list", 
        help="List available tools",
        parents=[common_parser]
    )
    list_parser.add_argument(
        "--category", "-c", 
        help="Filter by category"
    )
    list_parser.set_defaults(func=list_tools)
    
    # Show categories command
    categories_parser = subparsers.add_parser(
        "categories", 
        help="Show available tool categories",
        parents=[common_parser]
    )
    categories_parser.set_defaults(func=show_categories)
    
    # Run tool command
    run_parser = subparsers.add_parser(
        "run", 
        help="Run a specific tool",
        parents=[common_parser]
    )
    run_parser.add_argument(
        "tool", 
        help="Name of the tool to run"
    )
    run_parser.add_argument(
        "--params", "-p", 
        help="Tool parameters in JSON format"
    )
    run_parser.set_defaults(func=run_tool)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Call the appropriate function
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main() or 0)