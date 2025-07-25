# Migration Guide: MCPToolKit to MCPToolKitSDK

This guide helps you migrate from the legacy `MCPToolKit` class to the new `MCPToolKitSDK`.

## Why Migrate?

The new SDK offers:
- 🚀 Better performance with caching and batch operations
- 🔄 Async/await support
- 🎯 Cleaner API with convenience methods
- 🛡️ Enhanced error handling with ToolResult objects
- 🔌 Middleware and event hooks
- 📦 Context managers for resource management

## Quick Comparison

### Old Way (MCPToolKit)
```python
from app.toolkit import MCPToolKit

client = MCPToolKit()
result = client.read_file("/path/to/file.txt")
# Returns raw string, need to parse for errors
```

### New Way (MCPToolKitSDK)
```python
from app.sdk import MCPToolKitSDK

sdk = MCPToolKitSDK()
result = sdk.call_tool("read_file", {"path": "/path/to/file.txt"})
if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")
```

## Migration Steps

### 1. Update Imports

```python
# Old
from app.toolkit import MCPToolKit

# New
from app.sdk import MCPToolKitSDK
```

### 2. Update Initialization

```python
# Old
client = MCPToolKit("http://localhost:8000")

# New
sdk = MCPToolKitSDK("http://localhost:8000")

# Or with additional options
sdk = MCPToolKitSDK(
    server_url="http://localhost:8000",
    retry_count=3,
    cache_ttl=300
)
```

### 3. Update Method Calls

#### File Operations

```python
# Old
content = client.read_file("/path/to/file.txt")
client.write_file("/path/to/file.txt", "content")

# New - Option 1: Direct tool calls
result = sdk.call_tool("read_file", {"path": "/path/to/file.txt"})
if result.success:
    content = result.data

result = sdk.call_tool("write_file", {
    "path": "/path/to/file.txt",
    "content": "content"
})

# New - Option 2: Convenience methods
file = sdk.file("/path/to/file.txt")
content = file.read()
file.write("content")
```

#### Directory Operations

```python
# Old
files = client.list_directory("/path")
client.create_directory("/new/path")

# New
result = sdk.call_tool("list_directory", {"path": "/path"})
if result.success:
    files = result.data

result = sdk.call_tool("create_directory", {"path": "/new/path"})
```

#### Git Operations

```python
# Old
status = client.git_status(".")
client.git_commit(".", "commit message")

# New - Option 1: Direct calls
result = sdk.call_tool("git_status", {"repo_path": "."})
result = sdk.call_tool("git_commit", {
    "repo_path": ".",
    "message": "commit message"
})

# New - Option 2: Convenience methods
git = sdk.git(".")
status = git.status()
git.commit("commit message")
```

### 4. Error Handling

The new SDK returns `ToolResult` objects instead of raw strings:

```python
# Old - Need to parse response for errors
try:
    result = client.read_file("/path/to/file.txt")
    # Check if result contains error
    if "error" in result:
        handle_error(result)
except Exception as e:
    handle_error(str(e))

# New - Structured error handling
result = sdk.call_tool("read_file", {"path": "/path/to/file.txt"})
if result.success:
    process_data(result.data)
else:
    handle_error(result.error)
```

### 5. Batch Operations

The new SDK supports efficient batch operations:

```python
# Old - Sequential calls
results = []
for path in file_paths:
    content = client.read_file(path)
    results.append(content)

# New - Batch operations
operations = [
    {"tool": "read_file", "params": {"path": path}}
    for path in file_paths
]
results = sdk.batch_call(operations)

# Or async for better performance
async with MCPToolKitSDK(async_mode=True) as sdk:
    results = await sdk.batch_call_async(operations)
```

## Advanced Features

### Context Managers

```python
# Old - Manual cleanup
client = MCPToolKit()
try:
    # operations
finally:
    # no cleanup method

# New - Automatic cleanup
with MCPToolKitSDK() as sdk:
    # operations
    pass  # cleanup handled automatically
```

### Middleware

```python
# Old - No middleware support

# New - Add custom processing
def auth_middleware(tool_name, params):
    params['auth_token'] = 'your-token'
    return params

sdk.add_middleware(auth_middleware)
```

### Event Handlers

```python
# Old - No event support

# New - React to events
sdk.on('before_call', lambda tool, params: print(f"Calling {tool}"))
sdk.on('error', lambda tool, params, error: log_error(error))
```

## Complete Migration Example

### Old Code
```python
from app.toolkit import MCPToolKit

class FileProcessor:
    def __init__(self):
        self.client = MCPToolKit()
    
    def process_files(self, paths):
        results = []
        for path in paths:
            try:
                content = self.client.read_file(path)
                processed = self.process_content(content)
                self.client.write_file(f"{path}.processed", processed)
                results.append({"path": path, "status": "success"})
            except Exception as e:
                results.append({"path": path, "status": "error", "error": str(e)})
        return results
    
    def process_content(self, content):
        return content.upper()
```

### New Code
```python
from app.sdk import MCPToolKitSDK

class FileProcessor:
    def __init__(self):
        self.sdk = MCPToolKitSDK(retry_count=3, cache_ttl=300)
        self.sdk.on('error', self.log_error)
    
    def process_files(self, paths):
        # Use batch operations for better performance
        read_ops = [
            {"tool": "read_file", "params": {"path": path}}
            for path in paths
        ]
        
        read_results = self.sdk.batch_call(read_ops)
        
        results = []
        write_ops = []
        
        for path, result in zip(paths, read_results):
            if result.success:
                processed = self.process_content(result.data)
                write_ops.append({
                    "tool": "write_file",
                    "params": {
                        "path": f"{path}.processed",
                        "content": processed
                    }
                })
                results.append({"path": path, "status": "success"})
            else:
                results.append({
                    "path": path,
                    "status": "error",
                    "error": result.error
                })
        
        # Batch write operations
        if write_ops:
            self.sdk.batch_call(write_ops)
        
        return results
    
    def process_content(self, content):
        return content.upper()
    
    def log_error(self, tool_name, params, error):
        print(f"Error in {tool_name}: {error}")
```

## Gradual Migration

You can migrate gradually by using both APIs during transition:

```python
from app.toolkit import MCPToolKit
from app.sdk import MCPToolKitSDK

class HybridApp:
    def __init__(self):
        self.legacy_client = MCPToolKit()  # For old code
        self.sdk = MCPToolKitSDK()  # For new code
    
    def old_method(self):
        # Keep using legacy client
        return self.legacy_client.read_file("file.txt")
    
    def new_method(self):
        # Use new SDK features
        result = self.sdk.call_tool("read_file", {"path": "file.txt"})
        return result.data if result.success else None
```

## Need Help?

- Check the [SDK Guide](SDK_GUIDE.md) for detailed documentation
- See [examples](../examples/) for working code samples
- Report issues on our [GitHub repository](https://github.com/yourusername/mcp-tool-kit)