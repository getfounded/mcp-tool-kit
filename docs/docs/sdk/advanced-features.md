---
sidebar_position: 5
---

# Advanced Features

Explore the advanced capabilities of the MCP Tool Kit SDK.

## Middleware System

Middleware allows you to intercept and modify tool parameters before execution.

### Creating Middleware

```python
def logging_middleware(tool_name, params):
    """Log all tool calls."""
    print(f"[{datetime.now()}] Calling {tool_name} with {params}")
    return params

def auth_middleware(tool_name, params):
    """Add authentication to requests."""
    if tool_name in ['fetch', 'web_request']:
        if 'headers' not in params:
            params['headers'] = {}
        params['headers']['Authorization'] = 'Bearer token'
    return params

# Add middleware
sdk.add_middleware(logging_middleware)
sdk.add_middleware(auth_middleware)
```

### Middleware Chain

Middleware is executed in the order it was added:

```python
def middleware_1(tool_name, params):
    params['step1'] = True
    return params

def middleware_2(tool_name, params):
    params['step2'] = True
    return params

sdk.add_middleware(middleware_1)
sdk.add_middleware(middleware_2)

# When calling a tool, params will have both step1 and step2
```

### Conditional Middleware

```python
def rate_limit_middleware(tool_name, params):
    """Add rate limiting to external API calls."""
    if tool_name == 'fetch' and 'api.github.com' in params.get('url', ''):
        import time
        time.sleep(1)  # Rate limit GitHub API calls
    return params

sdk.add_middleware(rate_limit_middleware)
```

## Event System

The SDK emits events during tool execution that you can hook into.

### Available Events

- `before_call`: Fired before tool execution
- `after_call`: Fired after successful execution
- `error`: Fired when an error occurs

### Event Handlers

```python
# Simple handler
sdk.on('before_call', lambda tool, params: print(f"Starting {tool}"))

# Complex handler with state
class EventTracker:
    def __init__(self):
        self.call_count = {}
        self.error_count = {}
    
    def on_before_call(self, tool_name, params):
        self.call_count[tool_name] = self.call_count.get(tool_name, 0) + 1
    
    def on_error(self, tool_name, params, error):
        self.error_count[tool_name] = self.error_count.get(tool_name, 0) + 1
        print(f"Error in {tool_name}: {error}")
    
    def get_stats(self):
        return {
            'calls': self.call_count,
            'errors': self.error_count
        }

tracker = EventTracker()
sdk.on('before_call', tracker.on_before_call)
sdk.on('error', tracker.on_error)
```

### Event-Driven Architecture

```python
class SDKEventBus:
    """Extended event system for SDK."""
    
    def __init__(self, sdk):
        self.sdk = sdk
        self.handlers = {}
        
        # Register SDK events
        sdk.on('before_call', self._emit_before)
        sdk.on('after_call', self._emit_after)
        sdk.on('error', self._emit_error)
    
    def _emit_before(self, tool, params):
        self._emit('tool.start', {'tool': tool, 'params': params})
    
    def _emit_after(self, tool, params, result):
        self._emit('tool.complete', {
            'tool': tool,
            'params': params,
            'result': result
        })
    
    def _emit_error(self, tool, params, error):
        self._emit('tool.error', {
            'tool': tool,
            'params': params,
            'error': error
        })
    
    def _emit(self, event, data):
        if event in self.handlers:
            for handler in self.handlers[event]:
                handler(data)
    
    def subscribe(self, event, handler):
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)

# Usage
bus = SDKEventBus(sdk)
bus.subscribe('tool.error', lambda d: alert_admin(d['error']))
```

## Caching System

The SDK includes built-in caching to improve performance.

### Cache Configuration

```python
# Configure cache TTL (time-to-live)
sdk = MCPToolKitSDK(cache_ttl=600)  # 10 minutes

# Disable cache for specific calls
result = sdk.call_tool("get_current_time", {}, cache=False)

# Clear cache manually
sdk._cache.clear()
```

### Custom Cache Implementation

```python
class RedisCache:
    """Redis-based cache for SDK."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get(self, key):
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    def set(self, key, value, ttl):
        self.redis.setex(key, ttl, json.dumps(value))

class CachedSDK(MCPToolKitSDK):
    """SDK with custom cache backend."""
    
    def __init__(self, redis_client, **kwargs):
        super().__init__(**kwargs)
        self.cache = RedisCache(redis_client)
    
    def call_tool(self, tool_name, params, **kwargs):
        # Check custom cache
        cache_key = f"{tool_name}:{json.dumps(params, sort_keys=True)}"
        
        if kwargs.get('cache', True):
            cached = self.cache.get(cache_key)
            if cached:
                return ToolResult(True, cached, metadata={"cached": True})
        
        # Call tool
        result = super().call_tool(tool_name, params, **kwargs)
        
        # Cache result
        if result.success and kwargs.get('cache', True):
            self.cache.set(cache_key, result.data, self.cache_ttl)
        
        return result
```

## Async Operations

The SDK supports both synchronous and asynchronous operations.

### Async Context Manager

```python
async def process_async():
    async with MCPToolKitSDK(async_mode=True) as sdk:
        # Single async call
        result = await sdk.call_tool_async("list_directory", {"path": "."})
        
        # Concurrent operations
        tasks = [
            sdk.call_tool_async("read_file", {"path": f"file{i}.txt"})
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks)
```

### Async Streaming

```python
async def stream_large_file(sdk, path, chunk_size=1024):
    """Stream a large file in chunks."""
    
    # Get file size
    result = await sdk.call_tool_async("file_info", {"path": path})
    if not result.success:
        return
    
    file_size = result.data['size']
    
    # Read in chunks
    offset = 0
    while offset < file_size:
        result = await sdk.call_tool_async("read_file", {
            "path": path,
            "offset": offset,
            "limit": chunk_size
        })
        
        if result.success:
            yield result.data
            offset += chunk_size
        else:
            break

# Usage
async for chunk in stream_large_file(sdk, "large_file.dat"):
    process_chunk(chunk)
```

## Custom Tool Integration

### Creating Custom Tool Wrappers

```python
class CustomTools:
    """Custom tool implementations."""
    
    def __init__(self, sdk):
        self.sdk = sdk
    
    def search_code(self, pattern, file_type="py"):
        """Search for code patterns."""
        result = self.sdk.call_tool("search", {
            "pattern": pattern,
            "file_pattern": f"*.{file_type}",
            "type": "regex"
        })
        
        if result.success:
            # Parse and format results
            matches = []
            for match in result.data:
                matches.append({
                    'file': match['path'],
                    'line': match['line_number'],
                    'content': match['content']
                })
            return matches
        return []
    
    def bulk_rename(self, pattern, replacement, dry_run=True):
        """Rename multiple files."""
        # Find files matching pattern
        result = self.sdk.call_tool("list_directory", {
            "path": ".",
            "pattern": pattern
        })
        
        if not result.success:
            return []
        
        operations = []
        for old_path in result.data:
            new_path = old_path.replace(pattern, replacement)
            operations.append({
                'old': old_path,
                'new': new_path
            })
        
        if not dry_run:
            # Execute renames
            for op in operations:
                self.sdk.call_tool("rename_file", {
                    "old_path": op['old'],
                    "new_path": op['new']
                })
        
        return operations
```

### Tool Composition

```python
def create_project_structure(sdk, project_name, template="python"):
    """Create a complete project structure."""
    
    templates = {
        "python": {
            "dirs": ["src", "tests", "docs"],
            "files": {
                "README.md": f"# {project_name}\n\nProject description",
                "setup.py": "from setuptools import setup\n\nsetup()",
                ".gitignore": "*.pyc\n__pycache__/\n.env",
                "requirements.txt": "",
                "src/__init__.py": "",
                "tests/__init__.py": ""
            }
        },
        "node": {
            "dirs": ["src", "tests", "public"],
            "files": {
                "README.md": f"# {project_name}\n\nProject description",
                "package.json": json.dumps({
                    "name": project_name,
                    "version": "1.0.0"
                }, indent=2),
                ".gitignore": "node_modules/\n.env",
                "src/index.js": "console.log('Hello World');"
            }
        }
    }
    
    template_config = templates.get(template, templates["python"])
    
    # Create root directory
    sdk.call_tool("create_directory", {"path": project_name})
    
    # Create subdirectories
    for dir_name in template_config["dirs"]:
        sdk.call_tool("create_directory", {
            "path": f"{project_name}/{dir_name}"
        })
    
    # Create files
    for file_path, content in template_config["files"].items():
        sdk.call_tool("write_file", {
            "path": f"{project_name}/{file_path}",
            "content": content
        })
    
    print(f"Created {template} project: {project_name}")
```

## Performance Optimization

### Batch Processing Strategies

```python
def optimized_file_processor(sdk, files, batch_size=10):
    """Process files in optimized batches."""
    
    from itertools import islice
    
    def chunks(iterable, size):
        it = iter(iterable)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                break
            yield chunk
    
    all_results = []
    
    for batch in chunks(files, batch_size):
        # Create batch operations
        operations = [
            {"tool": "read_file", "params": {"path": f}}
            for f in batch
        ]
        
        # Process batch
        results = sdk.batch_call(operations)
        
        # Process results while next batch loads
        for file, result in zip(batch, results):
            if result.success:
                processed = process_content(result.data)
                all_results.append((file, processed))
    
    return all_results
```

### Connection Pooling

```python
class PooledSDK:
    """SDK with connection pooling."""
    
    def __init__(self, pool_size=5, **sdk_kwargs):
        self.pool = [
            MCPToolKitSDK(**sdk_kwargs)
            for _ in range(pool_size)
        ]
        self.current = 0
    
    def get_sdk(self):
        """Get next SDK from pool."""
        sdk = self.pool[self.current]
        self.current = (self.current + 1) % len(self.pool)
        return sdk
    
    def call_tool(self, tool_name, params, **kwargs):
        """Call tool using pooled SDK."""
        return self.get_sdk().call_tool(tool_name, params, **kwargs)
```

## Monitoring and Metrics

### Performance Metrics

```python
class MetricsSDK(MCPToolKitSDK):
    """SDK with built-in metrics collection."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metrics = {
            'calls': 0,
            'errors': 0,
            'cache_hits': 0,
            'total_time': 0
        }
    
    def call_tool(self, tool_name, params, **kwargs):
        import time
        
        start_time = time.time()
        self.metrics['calls'] += 1
        
        result = super().call_tool(tool_name, params, **kwargs)
        
        self.metrics['total_time'] += time.time() - start_time
        
        if not result.success:
            self.metrics['errors'] += 1
        
        if result.metadata.get('cached'):
            self.metrics['cache_hits'] += 1
        
        return result
    
    def get_metrics(self):
        """Get performance metrics."""
        return {
            **self.metrics,
            'avg_time': self.metrics['total_time'] / max(1, self.metrics['calls']),
            'error_rate': self.metrics['errors'] / max(1, self.metrics['calls']),
            'cache_hit_rate': self.metrics['cache_hits'] / max(1, self.metrics['calls'])
        }
```