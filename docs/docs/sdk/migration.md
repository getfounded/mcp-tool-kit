---
sidebar_position: 6
---

# Migration Guide

This guide helps you migrate from the legacy `MCPToolKit` class to the new `MCPToolKitSDK`.

## Overview

The new SDK provides a more robust and feature-rich interface while maintaining ease of use. Key improvements include:

- Structured error handling with `ToolResult` objects
- Built-in retry logic and caching
- Async/await support
- Middleware and event hooks
- Better type hints and IDE support

## Quick Migration

### 1. Update Imports

```python
# Old
from mcp_tool_kit import MCPToolKit

# New
from mcp_tool_kit import MCPToolKitSDK
```

### 2. Update Initialization

```python
# Old
client = MCPToolKit("http://localhost:8000")

# New
sdk = MCPToolKitSDK("http://localhost:8000")

# With additional options
sdk = MCPToolKitSDK(
    server_url="http://localhost:8000",
    retry_count=3,
    cache_ttl=300
)
```

### 3. Update Method Calls

The new SDK returns `ToolResult` objects instead of raw strings:

```python
# Old
try:
    content = client.read_file("/path/to/file.txt")
    # Parse content for errors manually
except Exception as e:
    print(f"Error: {e}")

# New
result = sdk.call_tool("read_file", {"path": "/path/to/file.txt"})
if result.success:
    content = result.data
else:
    print(f"Error: {result.error}")
```

## Detailed Migration Examples

### File Operations

#### Reading Files

```python
# Old
content = client.read_file("/path/to/file.txt")

# New - Option 1: Direct tool call
result = sdk.call_tool("read_file", {"path": "/path/to/file.txt"})
if result.success:
    content = result.data

# New - Option 2: Convenience method
file = sdk.file("/path/to/file.txt")
content = file.read()
```

#### Writing Files

```python
# Old
client.write_file("/path/to/file.txt", "content")

# New - Option 1: Direct tool call
result = sdk.call_tool("write_file", {
    "path": "/path/to/file.txt",
    "content": "content"
})

# New - Option 2: Convenience method
file = sdk.file("/path/to/file.txt")
success = file.write("content")
```

#### Multiple File Operations

```python
# Old
files = client.read_multiple_files(["/file1.txt", "/file2.txt"])

# New - Using batch operations
operations = [
    {"tool": "read_file", "params": {"path": "/file1.txt"}},
    {"tool": "read_file", "params": {"path": "/file2.txt"}}
]
results = sdk.batch_call(operations)

for result in results:
    if result.success:
        print(result.data)
```

### Directory Operations

```python
# Old
files = client.list_directory("/path")
client.create_directory("/new/path")

# New
# List directory
result = sdk.call_tool("list_directory", {"path": "/path"})
if result.success:
    files = result.data

# Create directory
result = sdk.call_tool("create_directory", {"path": "/new/path"})
```

### Git Operations

```python
# Old
status = client.git_status(".")
client.git_commit(".", "commit message")
client.git_push(".")

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
git.push()
```

### Error Handling

The new SDK provides better error handling:

```python
# Old - Error handling was inconsistent
try:
    result = client.some_operation()
    if isinstance(result, dict) and "error" in result:
        # Handle error
        pass
except Exception as e:
    # Handle exception
    pass

# New - Consistent error handling
result = sdk.call_tool("some_operation", params)
if result.success:
    # Process result.data
    pass
else:
    # Handle result.error
    logging.error(f"Operation failed: {result.error}")
```

## Advanced Migration

### Adding Retry Logic

```python
# Old - No built-in retry
def retry_read(client, path, attempts=3):
    for i in range(attempts):
        try:
            return client.read_file(path)
        except Exception as e:
            if i == attempts - 1:
                raise
            time.sleep(1)

# New - Built-in retry
sdk = MCPToolKitSDK(retry_count=3)
result = sdk.call_tool("read_file", {"path": path})
# Or override for specific call
result = sdk.call_tool("read_file", {"path": path}, retry=5)
```

### Batch Operations

```python
# Old - Sequential operations
results = []
for file in file_list:
    try:
        content = client.read_file(file)
        results.append(content)
    except Exception as e:
        results.append(None)

# New - Batch operations
operations = [
    {"tool": "read_file", "params": {"path": file}}
    for file in file_list
]
results = sdk.batch_call(operations)

# Or async for better performance
async with MCPToolKitSDK(async_mode=True) as sdk:
    results = await sdk.batch_call_async(operations)
```

### Custom Processing

```python
# Old - Limited extensibility
class CustomClient(MCPToolKit):
    def read_and_process(self, path):
        content = self.read_file(path)
        return content.upper()

# New - Multiple extension points
# Using middleware
def uppercase_middleware(tool_name, params):
    if tool_name == "read_file":
        params["process"] = "uppercase"
    return params

sdk.add_middleware(uppercase_middleware)

# Using events
def process_read_results(tool_name, params, result):
    if tool_name == "read_file" and isinstance(result, str):
        result = result.upper()

sdk.on("after_call", process_read_results)
```

## Migration Checklist

- [ ] Update all imports from `MCPToolKit` to `MCPToolKitSDK`
- [ ] Update initialization code
- [ ] Replace direct method calls with `call_tool` or convenience methods
- [ ] Update error handling to use `result.success` and `result.error`
- [ ] Consider using batch operations for multiple similar calls
- [ ] Add middleware for cross-cutting concerns
- [ ] Implement event handlers for monitoring
- [ ] Enable caching where appropriate
- [ ] Consider async operations for I/O-heavy workloads

## Gradual Migration

You can migrate gradually by using both APIs:

```python
from mcp_tool_kit import MCPToolKit, MCPToolKitSDK

class MigrationWrapper:
    def __init__(self):
        self.legacy = MCPToolKit()  # For old code
        self.sdk = MCPToolKitSDK()  # For new code
    
    # Keep old methods working
    def read_file(self, path):
        return self.legacy.read_file(path)
    
    # Add new SDK methods
    def read_file_safe(self, path):
        result = self.sdk.call_tool("read_file", {"path": path})
        return result.data if result.success else None
```

## Common Patterns

### Pattern 1: Safe File Operations

```python
# Old
def safe_read(client, path, default=""):
    try:
        return client.read_file(path)
    except:
        return default

# New
def safe_read(sdk, path, default=""):
    result = sdk.call_tool("read_file", {"path": path})
    return result.data if result.success else default
```

### Pattern 2: Logging All Operations

```python
# Old - Manual logging
def logged_read(client, path):
    logger.info(f"Reading {path}")
    try:
        result = client.read_file(path)
        logger.info(f"Successfully read {path}")
        return result
    except Exception as e:
        logger.error(f"Failed to read {path}: {e}")
        raise

# New - Automatic with events
sdk.on("before_call", lambda t, p: logger.info(f"Calling {t} with {p}"))
sdk.on("after_call", lambda t, p, r: logger.info(f"{t} succeeded"))
sdk.on("error", lambda t, p, e: logger.error(f"{t} failed: {e}"))
```

## Getting Help

If you encounter issues during migration:

1. Check the [API Reference](./api-reference) for detailed documentation
2. Review [Examples](./examples) for common patterns
3. Consult the [FAQ](#) for common questions
4. Report issues on our [GitHub repository](https://github.com/yourusername/mcp-tool-kit)