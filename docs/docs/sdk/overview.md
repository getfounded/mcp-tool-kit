---
sidebar_position: 1
---

# SDK Overview

The MCP Tool Kit SDK provides a powerful, flexible Python interface for integrating MCP tools into your applications.

## Key Features

- 🚀 **Easy Integration** - Simple API for calling MCP tools
- 🔄 **Async/Sync Support** - Use synchronous or asynchronous operations
- 📦 **Batch Operations** - Execute multiple tools efficiently
- 🛡️ **Robust Error Handling** - Structured results with success/error states
- 🔌 **Middleware & Hooks** - Customize behavior with middleware and event handlers
- 💾 **Built-in Caching** - Automatic caching for improved performance
- 🔁 **Retry Logic** - Configurable retry for failed operations
- 🎯 **Convenience Classes** - Simplified interfaces for common operations

## Quick Example

```python
from mcp_tool_kit import MCPToolKitSDK

# Initialize SDK
sdk = MCPToolKitSDK()

# Call a tool
result = sdk.call_tool("read_file", {"path": "example.txt"})
if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")

# Use convenience methods
file = sdk.file("output.txt")
file.write("Hello, World!")
content = file.read()
```

## Why Use the SDK?

### 1. Simplified Error Handling

Instead of parsing raw responses and checking for errors, the SDK provides structured `ToolResult` objects:

```python
# Without SDK
response = client.call_tool("read_file", {"path": "file.txt"})
# Need to parse response and check for errors manually

# With SDK
result = sdk.call_tool("read_file", {"path": "file.txt"})
if result.success:
    process_data(result.data)
else:
    handle_error(result.error)
```

### 2. Built-in Best Practices

The SDK includes:
- Automatic retries for transient failures
- Request caching to reduce server load
- Proper resource cleanup with context managers
- Consistent error handling patterns

### 3. Enhanced Developer Experience

- Type hints for better IDE support
- Convenience methods for common operations
- Batch operations for efficiency
- Event hooks for monitoring and debugging

## Components

### MCPToolKitSDK

The main SDK class that provides:
- Tool execution methods
- Configuration options
- Middleware and event handling
- Resource management

### ToolResult

A structured result object containing:
- `success`: Boolean indicating if the operation succeeded
- `data`: The actual result data
- `error`: Error message if the operation failed
- `metadata`: Additional information about the operation

### Convenience Classes

Pre-built helpers for common operations:
- `FileOperations`: File reading, writing, and manipulation
- `GitOperations`: Git repository management
- `WebOperations`: HTTP requests and web interactions

## Next Steps

- [Quick Start Guide](./quick-start) - Get up and running quickly
- [API Reference](./api-reference) - Detailed API documentation
- [Examples](./examples) - Code examples and patterns
- [Migration Guide](./migration) - Upgrade from the legacy API