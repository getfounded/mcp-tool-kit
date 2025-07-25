---
sidebar_position: 7
---

# Best Practices

Follow these best practices to get the most out of the MCP Tool Kit SDK.

## Initialization

### Use Context Managers

Always use context managers to ensure proper cleanup:

```python
# Good
with MCPToolKitSDK() as sdk:
    result = sdk.call_tool("read_file", {"path": "file.txt"})

# Also good for async
async with MCPToolKitSDK(async_mode=True) as sdk:
    result = await sdk.call_tool_async("read_file", {"path": "file.txt"})

# Avoid
sdk = MCPToolKitSDK()
# ... operations without cleanup
```

### Configure Appropriately

Set configuration based on your use case:

```python
# For production with external APIs
sdk = MCPToolKitSDK(
    retry_count=5,      # More retries for network issues
    timeout=60,         # Longer timeout for slow operations
    cache_ttl=3600      # Longer cache for stable data
)

# For development/testing
sdk = MCPToolKitSDK(
    retry_count=1,      # Fail fast during development
    timeout=10,         # Quick feedback
    cache_ttl=0         # No caching while testing
)

# For high-throughput applications
sdk = MCPToolKitSDK(
    async_mode=True,    # Enable async operations
    cache_ttl=300       # Moderate caching
)
```

## Error Handling

### Always Check Success

Never assume operations succeed:

```python
# Bad
result = sdk.call_tool("read_file", {"path": "file.txt"})
data = result.data  # Could be None if failed!

# Good
result = sdk.call_tool("read_file", {"path": "file.txt"})
if result.success:
    data = result.data
else:
    # Handle error appropriately
    logger.error(f"Failed to read file: {result.error}")
    return None
```

### Implement Graceful Degradation

```python
def get_config(sdk, primary_path, fallback_path):
    """Get configuration with fallback."""
    
    # Try primary location
    result = sdk.call_tool("read_file", {"path": primary_path})
    if result.success:
        return json.loads(result.data)
    
    # Try fallback
    logger.warning(f"Primary config not found: {result.error}")
    result = sdk.call_tool("read_file", {"path": fallback_path})
    if result.success:
        return json.loads(result.data)
    
    # Use defaults
    logger.warning("Using default configuration")
    return {"version": "1.0", "settings": {}}
```

### Use Specific Error Handling

```python
def safe_file_operation(sdk, path):
    """Handle specific error conditions."""
    
    result = sdk.call_tool("read_file", {"path": path})
    
    if result.success:
        return result.data
    
    # Handle specific errors
    error = result.error.lower()
    
    if "not found" in error:
        raise FileNotFoundError(f"File {path} does not exist")
    elif "permission" in error:
        raise PermissionError(f"No permission to read {path}")
    elif "timeout" in error:
        raise TimeoutError(f"Operation timed out for {path}")
    else:
        raise Exception(f"Unknown error: {result.error}")
```

## Performance

### Use Batch Operations

For multiple similar operations, use batching:

```python
# Bad - Sequential calls
results = []
for file in files:
    result = sdk.call_tool("read_file", {"path": file})
    results.append(result)

# Good - Batch call
operations = [
    {"tool": "read_file", "params": {"path": file}}
    for file in files
]
results = sdk.batch_call(operations)

# Better - Async batch for I/O operations
async with MCPToolKitSDK(async_mode=True) as sdk:
    results = await sdk.batch_call_async(operations)
```

### Leverage Caching

Use caching for expensive or frequently accessed data:

```python
# Configure appropriate cache TTL
sdk = MCPToolKitSDK(cache_ttl=3600)  # 1 hour

# Disable cache for dynamic data
current_time = sdk.call_tool("get_current_time", {}, cache=False)

# Force cache refresh when needed
def get_user_data(sdk, user_id, force_refresh=False):
    return sdk.call_tool(
        "fetch_user",
        {"user_id": user_id},
        cache=not force_refresh
    )
```

### Optimize Large Operations

```python
def process_large_dataset(sdk, data_files):
    """Process large dataset efficiently."""
    
    # Process in chunks to avoid memory issues
    chunk_size = 100
    results = []
    
    for i in range(0, len(data_files), chunk_size):
        chunk = data_files[i:i + chunk_size]
        
        # Batch process chunk
        operations = [
            {"tool": "process_data", "params": {"file": f}}
            for f in chunk
        ]
        
        chunk_results = sdk.batch_call(operations)
        results.extend(chunk_results)
        
        # Allow garbage collection between chunks
        import gc
        gc.collect()
    
    return results
```

## Code Organization

### Create Service Classes

Organize related operations into service classes:

```python
class FileService:
    """File operations service."""
    
    def __init__(self, sdk):
        self.sdk = sdk
    
    def read_json(self, path):
        """Read and parse JSON file."""
        result = self.sdk.call_tool("read_file", {"path": path})
        if result.success:
            try:
                return json.loads(result.data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path}: {e}")
        raise FileNotFoundError(f"Cannot read {path}: {result.error}")
    
    def write_json(self, path, data, pretty=True):
        """Write data as JSON."""
        content = json.dumps(data, indent=2 if pretty else None)
        result = self.sdk.call_tool("write_file", {
            "path": path,
            "content": content
        })
        return result.success
    
    def backup_file(self, path):
        """Create backup of file."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup_{timestamp}"
        
        # Read original
        result = self.sdk.call_tool("read_file", {"path": path})
        if not result.success:
            return False
        
        # Write backup
        result = self.sdk.call_tool("write_file", {
            "path": backup_path,
            "content": result.data
        })
        return result.success
```

### Use Dependency Injection

```python
class Application:
    """Main application with injected SDK."""
    
    def __init__(self, sdk=None):
        self.sdk = sdk or MCPToolKitSDK()
        self.file_service = FileService(self.sdk)
        self.git_service = GitService(self.sdk)
    
    def process_project(self, project_path):
        """Process a project."""
        # Use services
        config = self.file_service.read_json(f"{project_path}/config.json")
        
        # Process based on config
        # ...
        
        # Commit changes
        self.git_service.commit_all("Updated project configuration")
```

## Monitoring and Logging

### Implement Comprehensive Logging

```python
import logging

def setup_sdk_logging(sdk):
    """Set up comprehensive SDK logging."""
    
    logger = logging.getLogger("mcp_sdk")
    
    # Log all operations
    def log_before(tool_name, params):
        logger.info(f"Starting {tool_name}", extra={
            "tool": tool_name,
            "params": params
        })
    
    def log_after(tool_name, params, result):
        logger.info(f"Completed {tool_name}", extra={
            "tool": tool_name,
            "success": True,
            "cached": result.get("cached", False)
        })
    
    def log_error(tool_name, params, error):
        logger.error(f"Failed {tool_name}: {error}", extra={
            "tool": tool_name,
            "params": params,
            "error": error
        })
    
    sdk.on("before_call", log_before)
    sdk.on("after_call", log_after)
    sdk.on("error", log_error)
```

### Add Metrics Collection

```python
class MetricsCollector:
    """Collect SDK usage metrics."""
    
    def __init__(self, sdk):
        self.sdk = sdk
        self.metrics = defaultdict(lambda: {
            "calls": 0,
            "errors": 0,
            "total_time": 0
        })
        
        sdk.on("before_call", self._start_timer)
        sdk.on("after_call", self._record_success)
        sdk.on("error", self._record_error)
        
        self._timers = {}
    
    def _start_timer(self, tool_name, params):
        import time
        key = f"{tool_name}_{id(params)}"
        self._timers[key] = time.time()
    
    def _record_success(self, tool_name, params, result):
        self._record_call(tool_name, params, success=True)
    
    def _record_error(self, tool_name, params, error):
        self._record_call(tool_name, params, success=False)
    
    def _record_call(self, tool_name, params, success):
        import time
        key = f"{tool_name}_{id(params)}"
        
        if key in self._timers:
            elapsed = time.time() - self._timers[key]
            del self._timers[key]
        else:
            elapsed = 0
        
        self.metrics[tool_name]["calls"] += 1
        self.metrics[tool_name]["total_time"] += elapsed
        
        if not success:
            self.metrics[tool_name]["errors"] += 1
    
    def get_report(self):
        """Get metrics report."""
        report = {}
        for tool, data in self.metrics.items():
            report[tool] = {
                **data,
                "avg_time": data["total_time"] / max(1, data["calls"]),
                "error_rate": data["errors"] / max(1, data["calls"])
            }
        return report
```

## Security

### Validate Inputs

```python
def safe_file_read(sdk, path, allowed_dirs=None):
    """Read file with path validation."""
    
    # Normalize path
    import os
    abs_path = os.path.abspath(path)
    
    # Check allowed directories
    if allowed_dirs:
        allowed = False
        for allowed_dir in allowed_dirs:
            if abs_path.startswith(os.path.abspath(allowed_dir)):
                allowed = True
                break
        
        if not allowed:
            raise ValueError(f"Access denied: {path}")
    
    # Check for path traversal
    if ".." in path:
        raise ValueError(f"Path traversal detected: {path}")
    
    return sdk.call_tool("read_file", {"path": abs_path})
```

### Use Middleware for Authentication

```python
def create_authenticated_sdk(api_key):
    """Create SDK with authentication."""
    
    sdk = MCPToolKitSDK()
    
    def auth_middleware(tool_name, params):
        # Add authentication to external calls
        if tool_name in ["fetch", "api_call"]:
            if "headers" not in params:
                params["headers"] = {}
            params["headers"]["Authorization"] = f"Bearer {api_key}"
        return params
    
    sdk.add_middleware(auth_middleware)
    return sdk
```

## Testing

### Mock SDK for Testing

```python
class MockSDK:
    """Mock SDK for testing."""
    
    def __init__(self):
        self.responses = {}
        self.calls = []
    
    def set_response(self, tool_name, response, error=None):
        """Set mock response for tool."""
        self.responses[tool_name] = (response, error)
    
    def call_tool(self, tool_name, params, **kwargs):
        """Mock tool call."""
        self.calls.append((tool_name, params))
        
        if tool_name in self.responses:
            response, error = self.responses[tool_name]
            if error:
                return ToolResult(False, None, error=error)
            return ToolResult(True, response)
        
        return ToolResult(False, None, error="Tool not mocked")

# Usage in tests
def test_file_processor():
    mock_sdk = MockSDK()
    mock_sdk.set_response("read_file", "test content")
    
    processor = FileProcessor(mock_sdk)
    result = processor.process("test.txt")
    
    assert result == "TEST CONTENT"
    assert mock_sdk.calls[0] == ("read_file", {"path": "test.txt"})
```

## Summary

Key best practices:

1. **Always use context managers** for resource cleanup
2. **Check result.success** before using data
3. **Use batch operations** for multiple similar calls
4. **Enable caching** for performance
5. **Implement proper error handling** with specific exceptions
6. **Organize code** into service classes
7. **Add logging and monitoring** for production
8. **Validate inputs** for security
9. **Use middleware** for cross-cutting concerns
10. **Write tests** with proper mocking