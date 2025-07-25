---
sidebar_position: 2
---

# Quick Start

Get started with the MCP Tool Kit SDK in minutes.

## Installation

The SDK is included with the MCP Tool Kit. If you're using the tool kit, you already have access to the SDK.

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-tool-kit.git
cd mcp-tool-kit

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Initialize the SDK

```python
from mcp_tool_kit import MCPToolKitSDK

# Basic initialization
sdk = MCPToolKitSDK()

# With custom configuration
sdk = MCPToolKitSDK(
    server_url="http://localhost:8000",
    retry_count=3,
    timeout=30,
    cache_ttl=300
)
```

### 2. Call Tools

```python
# Call a tool with parameters
result = sdk.call_tool("read_file", {"path": "README.md"})

# Check the result
if result.success:
    print(f"File contents: {result.data}")
else:
    print(f"Error: {result.error}")
```

### 3. Use Convenience Methods

The SDK provides convenience classes for common operations:

```python
# File operations
file = sdk.file("example.txt")
file.write("Hello from SDK!")
content = file.read()
file.append("\nAppended text")

# Git operations
git = sdk.git(".")
status = git.status()
git.commit("Updated files")
git.push()

# Web operations
web = sdk.web()
data = web.get("https://api.example.com/data")
response = web.post("https://api.example.com/create", {"name": "test"})
```

## Context Managers

Use context managers for proper resource cleanup:

```python
# Synchronous
with MCPToolKitSDK() as sdk:
    result = sdk.call_tool("list_directory", {"path": "."})
    # SDK cleanup happens automatically

# Asynchronous
async with MCPToolKitSDK(async_mode=True) as sdk:
    result = await sdk.call_tool_async("list_directory", {"path": "."})
```

## Error Handling

The SDK provides structured error handling:

```python
result = sdk.call_tool("read_file", {"path": "nonexistent.txt"})

if result.success:
    # Process the data
    data = result.data
    print(f"File size: {len(data)} bytes")
else:
    # Handle the error
    print(f"Failed to read file: {result.error}")
    
    # You can also access metadata
    if result.metadata.get("retry_count"):
        print(f"Retried {result.metadata['retry_count']} times")
```

## Batch Operations

Process multiple operations efficiently:

```python
# Define operations
operations = [
    {"tool": "read_file", "params": {"path": "file1.txt"}},
    {"tool": "read_file", "params": {"path": "file2.txt"}},
    {"tool": "write_file", "params": {"path": "output.txt", "content": "data"}}
]

# Execute batch
results = sdk.batch_call(operations)

# Process results
for i, result in enumerate(results):
    if result.success:
        print(f"Operation {i} succeeded")
    else:
        print(f"Operation {i} failed: {result.error}")
```

## Complete Example

Here's a complete example that demonstrates various SDK features:

```python
from mcp_tool_kit import MCPToolKitSDK

def process_project_files():
    """Example: Process all Python files in a project."""
    
    with MCPToolKitSDK() as sdk:
        # List all Python files
        result = sdk.call_tool("list_directory", {"path": ".", "recursive": True})
        
        if not result.success:
            print(f"Failed to list directory: {result.error}")
            return
        
        # Filter Python files
        python_files = [f for f in result.data if f.endswith('.py')]
        print(f"Found {len(python_files)} Python files")
        
        # Read and process each file
        for file_path in python_files[:5]:  # Process first 5 files
            file = sdk.file(file_path)
            content = file.read()
            
            if content:
                # Count lines
                lines = content.split('\n')
                print(f"{file_path}: {len(lines)} lines")
                
                # Create a backup
                backup_path = f"{file_path}.backup"
                backup = sdk.file(backup_path)
                backup.write(content)
        
        print("Processing complete!")

if __name__ == "__main__":
    process_project_files()
```

## Next Steps

- Explore [API Reference](./api-reference) for detailed documentation
- Check out [Examples](./examples) for more usage patterns
- Learn about [Advanced Features](./advanced-features) like middleware and caching
- Read the [Best Practices](./best-practices) guide