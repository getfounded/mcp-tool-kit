"""
MCP Tool Kit SDK Demo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app.sdk import MCPToolKitSDK


def main():
    """Run SDK demo."""
    print("=== MCP Tool Kit SDK Demo ===\n")
    
    # Initialize SDK
    sdk = MCPToolKitSDK()
    print("[OK] SDK initialized\n")
    
    # 1. Basic tool call
    print("1. Basic Tool Call - Reading README.md")
    result = sdk.call_tool("read_file", {"path": "README.md"})
    if result.success:
        print(f"[OK] Successfully read file ({len(str(result.data))} characters)")
        print(f"  First 100 chars: {str(result.data)[:100]}...")
    else:
        print(f"[FAIL] Error: {result.error}")
    print()
    
    # 2. Using convenience methods
    print("2. Convenience Methods - File Operations")
    test_file = "examples/test_output.txt"
    file = sdk.file(test_file)
    
    # Write
    success = file.write("Hello from MCP Tool Kit SDK!\nThis is a test file.")
    print(f"[OK] Write file: {'Success' if success else 'Failed'}")
    
    # Read
    content = file.read()
    print(f"[OK] Read file: {content[:50]}...")
    
    # Append
    success = file.append("\nAppended line at the end.")
    print(f"[OK] Append to file: {'Success' if success else 'Failed'}")
    print()
    
    # 3. Error handling
    print("3. Error Handling - Reading non-existent file")
    result = sdk.call_tool("read_file", {"path": "nonexistent.txt"})
    if not result.success:
        print(f"[OK] Error properly handled: {result.error}")
    print()
    
    # 4. List available tools
    print("4. Available Tools")
    tools = sdk.list_tools()
    if tools:
        print(f"[OK] Found {len(tools)} tools:")
        for tool in tools[:5]:  # Show first 5
            print(f"  - {tool.get('name', 'Unknown')}")
        if len(tools) > 5:
            print(f"  ... and {len(tools) - 5} more")
    print()
    
    # 5. Batch operations
    print("5. Batch Operations - Reading multiple files")
    operations = [
        {"tool": "read_file", "params": {"path": "README.md"}},
        {"tool": "read_file", "params": {"path": "pyproject.toml"}},
        {"tool": "list_directory", "params": {"path": "."}}
    ]
    
    results = sdk.batch_call(operations)
    print(f"[OK] Executed {len(results)} operations:")
    for i, result in enumerate(results):
        status = "Success" if result.success else "Failed"
        print(f"  Operation {i + 1}: {status}")
    print()
    
    # 6. Using middleware
    print("6. Middleware Example")
    
    def logging_middleware(tool_name, params):
        print(f"  [Middleware] Calling {tool_name}")
        return params
    
    sdk.add_middleware(logging_middleware)
    
    # This call will trigger middleware
    sdk.call_tool("list_directory", {"path": "examples"})
    print("[OK] Middleware executed")
    print()
    
    # 7. Event handlers
    print("7. Event Handlers")
    
    events = []
    sdk.on('before_call', lambda tool, params: events.append(f"before:{tool}"))
    sdk.on('after_call', lambda tool, params, result: events.append(f"after:{tool}"))
    
    sdk.call_tool("list_directory", {"path": "."})
    print(f"[OK] Events triggered: {', '.join(events)}")
    print()
    
    # 8. Dynamic methods
    print("8. Dynamic Tool Methods")
    # Instead of sdk.call_tool("read_file", {"path": "..."})
    # You can use sdk.read_file(path="...")
    # Note: This would work with actual server
    print("[OK] Dynamic methods available (e.g., sdk.read_file(path='...'))")
    
    print("\n=== Demo Complete ===")
    print("Check out examples/sdk_usage.py for more advanced examples!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nNote: This demo requires the MCP server to be running.")
        print(f"Error: {e}")
        print("\nTo run the server:")
        print("  python -m app.mcp_unified_server")
        
        # Run a minimal demo without server
        print("\n=== Running minimal demo without server ===")
        sdk = MCPToolKitSDK()
        
        # Show that SDK initializes properly
        print("[OK] SDK initialized successfully")
        
        # Show ToolResult
        from app.sdk import ToolResult
        result = ToolResult(True, "Sample data", metadata={"demo": True})
        print(f"[OK] ToolResult: {result}")
        print(f"  - Success: {result.success}")
        print(f"  - Data: {result.data}")
        print(f"  - Metadata: {result.metadata}")