# MCP Tool Kit SDK

The MCP Tool Kit SDK provides a powerful, flexible Python interface for integrating MCP tools into your applications.

## Features

- 🚀 **Easy Integration** - Simple API for calling MCP tools
- 🔄 **Async/Sync Support** - Use synchronous or asynchronous operations
- 📦 **Batch Operations** - Execute multiple tools efficiently
- 🛡️ **Robust Error Handling** - Structured results with success/error states
- 🔌 **Middleware & Hooks** - Customize behavior with middleware and event handlers
- 💾 **Built-in Caching** - Automatic caching for improved performance
- 🔁 **Retry Logic** - Configurable retry for failed operations
- 🎯 **Convenience Classes** - Simplified interfaces for common operations

## Quick Start

```python
from app.sdk import MCPToolKitSDK

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

## Installation

The SDK is included with the MCP Tool Kit. No separate installation needed.

## Key Components

### MCPToolKitSDK
The main SDK class providing:
- Tool execution
- Batch operations
- Middleware support
- Event handling
- Caching and retry logic

### ToolResult
Structured result object with:
- `success`: Boolean indicating operation success
- `data`: The actual result data
- `error`: Error message if operation failed
- `metadata`: Additional information

### Convenience Classes
- **FileOperations**: Simplified file operations
- **GitOperations**: Git repository management
- **WebOperations**: HTTP requests

## Documentation

- [SDK Guide](docs/SDK_GUIDE.md) - Comprehensive documentation
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Upgrade from legacy API
- [Examples](examples/) - Working code samples

## Example Usage

### Basic Operations
```python
# File operations
sdk.call_tool("write_file", {"path": "test.txt", "content": "Hello"})
sdk.call_tool("read_file", {"path": "test.txt"})

# Directory operations
sdk.call_tool("list_directory", {"path": "."})
sdk.call_tool("create_directory", {"path": "new_folder"})
```

### Advanced Features
```python
# Batch operations
results = sdk.batch_call([
    {"tool": "read_file", "params": {"path": "file1.txt"}},
    {"tool": "read_file", "params": {"path": "file2.txt"}}
])

# Middleware
def auth_middleware(tool_name, params):
    params['auth'] = 'token'
    return params

sdk.add_middleware(auth_middleware)

# Event handlers
sdk.on('error', lambda tool, params, error: print(f"Error in {tool}: {error}"))
```

## Testing

Run tests with:
```bash
python -m unittest tests.test_sdk -v
```

## Support

For issues and questions, please visit our [GitHub repository](https://github.com/yourusername/mcp-tool-kit).