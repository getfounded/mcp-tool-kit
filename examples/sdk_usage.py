"""
Example usage of the MCP Tool Kit SDK
"""
import asyncio
from app.sdk import MCPToolKitSDK, ToolResult


def basic_usage():
    """Basic SDK usage examples."""
    # Initialize SDK
    sdk = MCPToolKitSDK(server_url="http://localhost:8000")
    
    # Simple tool call
    result = sdk.call_tool("read_file", {"path": "README.md"})
    if result.success:
        print(f"File contents: {result.data[:100]}...")
    else:
        print(f"Error: {result.error}")
    
    # Using convenience methods
    file_ops = sdk.file("example.txt")
    file_ops.write("Hello from SDK!")
    content = file_ops.read()
    print(f"File content: {content}")
    
    # Dynamic tool methods
    # sdk.read_file(path="another_file.txt")
    # sdk.list_directory(path=".")


def context_manager_usage():
    """Using SDK with context manager."""
    with MCPToolKitSDK() as sdk:
        # List available tools
        tools = sdk.list_tools()
        print(f"Available tools: {[t['name'] for t in tools]}")
        
        # Get tool info
        tool_info = sdk.get_tool_info("read_file")
        print(f"Tool info: {tool_info}")


def batch_operations():
    """Batch operation examples."""
    sdk = MCPToolKitSDK()
    
    # Batch multiple operations
    operations = [
        {"tool": "read_file", "params": {"path": "file1.txt"}},
        {"tool": "read_file", "params": {"path": "file2.txt"}},
        {"tool": "list_directory", "params": {"path": "."}}
    ]
    
    results = sdk.batch_call(operations)
    for i, result in enumerate(results):
        print(f"Operation {i}: {'Success' if result.success else 'Failed'}")


async def async_usage():
    """Async SDK usage."""
    async with MCPToolKitSDK(async_mode=True) as sdk:
        # Single async call
        result = await sdk.call_tool_async("list_directory", {"path": "."})
        print(f"Directory listing: {result.data}")
        
        # Batch async operations
        operations = [
            {"tool": "read_file", "params": {"path": f"file{i}.txt"}}
            for i in range(5)
        ]
        
        results = await sdk.batch_call_async(operations)
        print(f"Processed {len(results)} files asynchronously")


def middleware_and_events():
    """Using middleware and event handlers."""
    sdk = MCPToolKitSDK()
    
    # Add middleware to log all calls
    def logging_middleware(tool_name, params):
        print(f"Calling {tool_name} with {params}")
        return params  # Can modify params here
    
    sdk.add_middleware(logging_middleware)
    
    # Add event handlers
    def on_before_call(tool_name, params):
        print(f"Before calling {tool_name}")
    
    def on_error(tool_name, params, error):
        print(f"Error in {tool_name}: {error}")
    
    sdk.on('before_call', on_before_call)
    sdk.on('error', on_error)
    
    # Make calls - middleware and events will be triggered
    sdk.call_tool("read_file", {"path": "test.txt"})


def git_operations():
    """Git operations example."""
    sdk = MCPToolKitSDK()
    git = sdk.git(".")
    
    # Check status
    status = git.status()
    print(f"Git status: {status}")
    
    # Make a commit
    success = git.commit("Updated via SDK", files=["README.md"])
    print(f"Commit {'successful' if success else 'failed'}")


def web_operations():
    """Web operations example."""
    sdk = MCPToolKitSDK()
    web = sdk.web()
    
    # GET request
    response = web.get("https://api.github.com/users/github")
    print(f"Response: {response}")
    
    # POST request
    data = {"key": "value"}
    response = web.post("https://httpbin.org/post", data)
    print(f"POST response: {response}")


def custom_integration():
    """Example of custom integration in existing application."""
    
    class MyApplication:
        def __init__(self):
            self.mcp = MCPToolKitSDK()
            
            # Configure SDK for our needs
            self.mcp.add_middleware(self.auth_middleware)
            self.mcp.on('error', self.handle_error)
        
        def auth_middleware(self, tool_name, params):
            # Add authentication to all requests
            params['auth_token'] = 'my-secret-token'
            return params
        
        def handle_error(self, tool_name, params, error):
            # Custom error handling
            self.log_error(f"MCP Error: {tool_name} - {error}")
        
        def process_files(self, file_paths):
            # Use MCP tools in application logic
            results = []
            for path in file_paths:
                result = self.mcp.call_tool("read_file", {"path": path})
                if result.success:
                    # Process file content
                    processed = self.process_content(result.data)
                    results.append(processed)
            return results
        
        def process_content(self, content):
            # Application-specific processing
            return content.upper()
        
        def log_error(self, message):
            print(f"[ERROR] {message}")
    
    # Use in application
    app = MyApplication()
    results = app.process_files(["file1.txt", "file2.txt"])
    print(f"Processed {len(results)} files")


if __name__ == "__main__":
    print("=== Basic Usage ===")
    basic_usage()
    
    print("\n=== Context Manager ===")
    context_manager_usage()
    
    print("\n=== Batch Operations ===")
    batch_operations()
    
    print("\n=== Async Usage ===")
    asyncio.run(async_usage())
    
    print("\n=== Middleware and Events ===")
    middleware_and_events()
    
    print("\n=== Custom Integration ===")
    custom_integration()