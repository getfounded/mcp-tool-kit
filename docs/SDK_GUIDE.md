# MCP Tool Kit SDK Guide

The MCP Tool Kit SDK provides a powerful and flexible way to integrate MCP tools into your Python applications. This guide covers installation, basic usage, and advanced features.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)

## Installation

```bash
pip install mcp-tool-kit
```

Or install from source:
```bash
git clone https://github.com/yourusername/mcp-tool-kit.git
cd mcp-tool-kit
pip install -e .
```

## Quick Start

```python
from mcp_tool_kit import MCPToolKitSDK

# Initialize the SDK
sdk = MCPToolKitSDK(server_url="http://localhost:8000")

# Call a tool
result = sdk.call_tool("read_file", {"path": "example.txt"})
if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")
```

## Core Concepts

### ToolResult
Every tool call returns a `ToolResult` object with:
- `success`: Boolean indicating if the operation succeeded
- `data`: The actual result data
- `error`: Error message if the operation failed
- `metadata`: Additional information about the operation

### Context Managers
The SDK supports both sync and async context managers for proper resource management:

```python
# Sync context manager
with MCPToolKitSDK() as sdk:
    result = sdk.call_tool("list_directory", {"path": "."})

# Async context manager
async with MCPToolKitSDK(async_mode=True) as sdk:
    result = await sdk.call_tool_async("list_directory", {"path": "."})
```

## Basic Usage

### Simple Tool Calls

```python
sdk = MCPToolKitSDK()

# Read a file
result = sdk.call_tool("read_file", {"path": "README.md"})

# Write a file
result = sdk.call_tool("write_file", {
    "path": "output.txt",
    "content": "Hello, World!"
})

# List directory
result = sdk.call_tool("list_directory", {"path": "."})
```

### Using Convenience Classes

The SDK provides convenience classes for common operations:

```python
# File operations
file = sdk.file("example.txt")
file.write("Hello, SDK!")
content = file.read()
exists = file.exists()

# Git operations
git = sdk.git(".")
status = git.status()
git.commit("Updated via SDK")
git.push()

# Web operations
web = sdk.web()
response = web.get("https://api.example.com/data")
result = web.post("https://api.example.com/create", {"name": "test"})
```

### Dynamic Tool Methods

Access tools as methods dynamically:

```python
# Instead of sdk.call_tool("read_file", {"path": "file.txt"})
# You can use:
content = sdk.read_file(path="file.txt")
listing = sdk.list_directory(path=".")
```

## Advanced Features

### Batch Operations

Execute multiple tools efficiently:

```python
# Sync batch
operations = [
    {"tool": "read_file", "params": {"path": "file1.txt"}},
    {"tool": "read_file", "params": {"path": "file2.txt"}},
    {"tool": "list_directory", "params": {"path": "."}}
]
results = sdk.batch_call(operations)

# Async batch (concurrent execution)
async with MCPToolKitSDK(async_mode=True) as sdk:
    results = await sdk.batch_call_async(operations)
```

### Middleware

Add custom processing to all tool calls:

```python
def auth_middleware(tool_name, params):
    # Add authentication token to all requests
    params['auth_token'] = 'your-token'
    return params

def logging_middleware(tool_name, params):
    print(f"Calling {tool_name}")
    return params

sdk.add_middleware(auth_middleware)
sdk.add_middleware(logging_middleware)
```

### Event Handlers

React to tool execution events:

```python
# Register event handlers
sdk.on('before_call', lambda tool, params: print(f"Starting {tool}"))
sdk.on('after_call', lambda tool, params, result: print(f"Completed {tool}"))
sdk.on('error', lambda tool, params, error: print(f"Error in {tool}: {error}"))

# Events are automatically triggered during tool execution
sdk.call_tool("read_file", {"path": "test.txt"})
```

### Caching

The SDK includes built-in caching for improved performance:

```python
# Enable caching with custom TTL
sdk = MCPToolKitSDK(cache_ttl=600)  # 10 minutes

# Disable cache for specific call
result = sdk.call_tool("read_file", {"path": "dynamic.txt"}, cache=False)
```

### Retry Logic

Automatic retry for failed operations:

```python
# Configure default retry count
sdk = MCPToolKitSDK(retry_count=5)

# Override for specific call
result = sdk.call_tool("fetch", {"url": "https://api.example.com"}, retry=10)
```

## Best Practices

### 1. Use Context Managers
Always use context managers to ensure proper cleanup:

```python
with MCPToolKitSDK() as sdk:
    # Your operations here
    pass
```

### 2. Handle Errors Gracefully
Always check the `success` field:

```python
result = sdk.call_tool("read_file", {"path": "maybe-exists.txt"})
if result.success:
    process_data(result.data)
else:
    handle_error(result.error)
```

### 3. Use Appropriate Methods
Choose the right method for your use case:
- Use `call_tool` for single operations
- Use `batch_call` for multiple operations
- Use convenience classes for cleaner code
- Use async methods for I/O-heavy operations

### 4. Configure for Your Environment
Adjust settings based on your needs:

```python
sdk = MCPToolKitSDK(
    server_url="http://your-server:8000",
    retry_count=3,
    timeout=60,
    cache_ttl=300
)
```

### 5. Implement Custom Error Handling

```python
class MyApp:
    def __init__(self):
        self.sdk = MCPToolKitSDK()
        self.sdk.on('error', self.handle_mcp_error)
    
    def handle_mcp_error(self, tool_name, params, error):
        # Log to your monitoring system
        self.logger.error(f"MCP error in {tool_name}: {error}")
        # Send alerts if critical
        if tool_name in ['critical_tool']:
            self.send_alert(f"Critical tool failed: {tool_name}")
```

## API Reference

### MCPToolKitSDK

#### Constructor
```python
MCPToolKitSDK(
    server_url: str = "http://localhost:8000",
    async_mode: bool = False,
    retry_count: int = 3,
    timeout: int = 30,
    cache_ttl: int = 300
)
```

#### Methods

**call_tool(tool_name: str, params: Dict[str, Any], **kwargs) -> ToolResult**
- Execute a single tool
- Returns: ToolResult object

**call_tool_async(tool_name: str, params: Dict[str, Any], **kwargs) -> ToolResult**
- Async version of call_tool
- Returns: ToolResult object (awaitable)

**batch_call(operations: List[Dict[str, Any]]) -> List[ToolResult]**
- Execute multiple tools sequentially
- Returns: List of ToolResult objects

**batch_call_async(operations: List[Dict[str, Any]]) -> List[ToolResult]**
- Execute multiple tools concurrently
- Returns: List of ToolResult objects (awaitable)

**list_tools() -> List[Dict[str, Any]]**
- Get available tools
- Returns: List of tool definitions

**get_tool_info(tool_name: str) -> Optional[Dict[str, Any]]**
- Get detailed tool information
- Returns: Tool definition or None

**add_middleware(middleware: Callable)**
- Add parameter processing middleware

**on(event: str, handler: Callable)**
- Register event handler
- Events: 'before_call', 'after_call', 'error'

### ToolResult

#### Attributes
- `success: bool` - Operation success status
- `data: Any` - Result data
- `error: Optional[str]` - Error message if failed
- `metadata: Dict[str, Any]` - Additional information

#### Methods
**to_dict() -> Dict[str, Any]**
- Convert to dictionary representation

### Convenience Classes

#### FileOperations
- `read(path: Optional[str]) -> str`
- `write(content: str, path: Optional[str]) -> bool`
- `append(content: str, path: Optional[str]) -> bool`
- `exists(path: Optional[str]) -> bool`

#### GitOperations
- `status() -> str`
- `commit(message: str, files: Optional[List[str]]) -> bool`
- `push(branch: Optional[str]) -> bool`

#### WebOperations
- `get(url: str, headers: Optional[Dict]) -> Union[str, Dict]`
- `post(url: str, data: Any, headers: Optional[Dict]) -> Union[str, Dict]`

## Examples

See the [examples directory](../examples/) for complete working examples:
- `sdk_usage.py` - Comprehensive SDK usage examples
- `async_example.py` - Async operations
- `integration_example.py` - Integration patterns

## Support

For issues and feature requests, please visit our [GitHub repository](https://github.com/yourusername/mcp-tool-kit).