"""
MCP Tool Kit SDK - Easy integration for Python applications
"""
import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional, List, Callable, Union
from concurrent.futures import ThreadPoolExecutor
import json
from functools import wraps
from app.toolkit_client import MCPClient


class ToolResult:
    """Wrapper for tool execution results with status and metadata."""
    
    def __init__(self, success: bool, data: Any, error: Optional[str] = None, metadata: Optional[Dict] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"ToolResult(success={self.success}, data={self.data[:100] if isinstance(self.data, str) else self.data}...)"
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }


class MCPToolKitSDK:
    """
    Enhanced SDK for integrating MCP tools into Python applications.
    
    Features:
    - Simplified tool discovery and usage
    - Async/sync support
    - Context managers for resource management
    - Batch operations
    - Event hooks and middleware
    - Built-in caching and retry logic
    """
    
    def __init__(
        self, 
        server_url: str = "http://localhost:8000",
        async_mode: bool = False,
        retry_count: int = 3,
        timeout: int = 30,
        cache_ttl: int = 300
    ):
        """
        Initialize the SDK with enhanced configuration options.
        
        Args:
            server_url: MCP server URL
            async_mode: Enable async operations
            retry_count: Number of retries for failed operations
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self.client = MCPClient(server_url)
        self.async_mode = async_mode
        self.retry_count = retry_count
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._middleware = []
        self._event_handlers = {}
        self._executor = ThreadPoolExecutor(max_workers=10) if async_mode else None
        
        self.logger = logging.getLogger("MCPToolKitSDK")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if self._executor:
            self._executor.shutdown(wait=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._executor:
            self._executor.shutdown(wait=True)
    
    # Core tool execution
    def call_tool(self, tool_name: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        """
        Call a tool with enhanced error handling and result wrapping.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            **kwargs: Additional options (cache, retry, etc.)
        
        Returns:
            ToolResult object with execution results
        """
        # Check cache
        cache_key = f"{tool_name}:{json.dumps(params, sort_keys=True)}"
        if kwargs.get('cache', True) and cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if timestamp + self.cache_ttl > time.time():
                return ToolResult(True, cached_data, metadata={"cached": True})
        
        # Apply middleware
        for middleware in self._middleware:
            params = middleware(tool_name, params)
        
        # Execute with retry logic
        retry_count = kwargs.get('retry', self.retry_count)
        last_error = None
        
        for attempt in range(retry_count):
            try:
                # Emit before event
                self._emit_event('before_call', tool_name, params)
                
                # Execute tool
                result = self.client.call_tool(tool_name, params)
                
                # Parse result
                try:
                    data = json.loads(result) if isinstance(result, str) else result
                    if isinstance(data, dict) and 'error' in data:
                        raise Exception(data['error'])
                except json.JSONDecodeError:
                    data = result
                
                # Cache successful result
                if kwargs.get('cache', True):
                    self._cache[cache_key] = (data, time.time())
                
                # Emit after event
                self._emit_event('after_call', tool_name, params, data)
                
                return ToolResult(True, data)
                
            except Exception as e:
                last_error = str(e)
                if attempt < retry_count - 1:
                    self.logger.warning(f"Retry {attempt + 1}/{retry_count} for {tool_name}: {e}")
                    continue
        
        # All retries failed
        self._emit_event('error', tool_name, params, last_error)
        return ToolResult(False, None, error=last_error)
    
    async def call_tool_async(self, tool_name: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        """Async version of call_tool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.call_tool,
            tool_name,
            params,
            **kwargs
        )
    
    # Batch operations
    def batch_call(self, operations: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Execute multiple tool calls in batch.
        
        Args:
            operations: List of dicts with 'tool', 'params', and optional 'options'
        
        Returns:
            List of ToolResult objects
        """
        results = []
        for op in operations:
            result = self.call_tool(
                op['tool'],
                op['params'],
                **op.get('options', {})
            )
            results.append(result)
        return results
    
    async def batch_call_async(self, operations: List[Dict[str, Any]]) -> List[ToolResult]:
        """Async batch execution with concurrency."""
        tasks = [
            self.call_tool_async(
                op['tool'],
                op['params'],
                **op.get('options', {})
            )
            for op in operations
        ]
        return await asyncio.gather(*tasks)
    
    # Tool discovery
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with metadata."""
        result = self.call_tool("list_tools", {})
        return result.data if result.success else []
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool."""
        tools = self.list_tools()
        for tool in tools:
            if tool.get('name') == tool_name:
                return tool
        return None
    
    # Middleware and hooks
    def add_middleware(self, middleware: Callable):
        """Add middleware to process parameters before tool calls."""
        self._middleware.append(middleware)
    
    def on(self, event: str, handler: Callable):
        """Register event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def _emit_event(self, event: str, *args, **kwargs):
        """Emit event to registered handlers."""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Event handler error: {e}")
    
    # Convenience methods for common tools
    def file(self, path: str) -> 'FileOperations':
        """Get file operations helper for a specific path."""
        return FileOperations(self, path)
    
    def git(self, repo_path: str = ".") -> 'GitOperations':
        """Get git operations helper."""
        return GitOperations(self, repo_path)
    
    def web(self) -> 'WebOperations':
        """Get web operations helper."""
        return WebOperations(self)
    
    # Dynamic tool method generation
    def __getattr__(self, name: str):
        """Dynamically generate tool methods."""
        def tool_method(**params):
            return self.call_tool(name, params)
        return tool_method


class FileOperations:
    """Simplified file operations using MCP tools."""
    
    def __init__(self, sdk: MCPToolKitSDK, base_path: str = "."):
        self.sdk = sdk
        self.base_path = base_path
    
    def read(self, path: Optional[str] = None) -> str:
        """Read file contents."""
        full_path = path or self.base_path
        result = self.sdk.call_tool("read_file", {"path": full_path})
        return result.data if result.success else ""
    
    def write(self, content: str, path: Optional[str] = None) -> bool:
        """Write content to file."""
        full_path = path or self.base_path
        result = self.sdk.call_tool("write_file", {"path": full_path, "content": content})
        return result.success
    
    def append(self, content: str, path: Optional[str] = None) -> bool:
        """Append content to file."""
        full_path = path or self.base_path
        current = self.read(full_path)
        return self.write(current + content, full_path)
    
    def exists(self, path: Optional[str] = None) -> bool:
        """Check if file exists."""
        full_path = path or self.base_path
        result = self.sdk.call_tool("list_directory", {"path": os.path.dirname(full_path)})
        if result.success:
            filename = os.path.basename(full_path)
            return filename in result.data
        return False


class GitOperations:
    """Simplified git operations."""
    
    def __init__(self, sdk: MCPToolKitSDK, repo_path: str = "."):
        self.sdk = sdk
        self.repo_path = repo_path
    
    def status(self) -> str:
        """Get git status."""
        result = self.sdk.call_tool("git_status", {"repo_path": self.repo_path})
        return result.data if result.success else ""
    
    def commit(self, message: str, files: Optional[List[str]] = None) -> bool:
        """Create a git commit."""
        params = {"repo_path": self.repo_path, "message": message}
        if files:
            params["files"] = files
        result = self.sdk.call_tool("git_commit", params)
        return result.success
    
    def push(self, branch: Optional[str] = None) -> bool:
        """Push to remote."""
        params = {"repo_path": self.repo_path}
        if branch:
            params["branch"] = branch
        result = self.sdk.call_tool("git_push", params)
        return result.success


class WebOperations:
    """Simplified web operations."""
    
    def __init__(self, sdk: MCPToolKitSDK):
        self.sdk = sdk
    
    def get(self, url: str, headers: Optional[Dict] = None) -> Union[str, Dict]:
        """Make GET request."""
        params = {"url": url, "method": "GET"}
        if headers:
            params["headers"] = headers
        result = self.sdk.call_tool("fetch", params)
        return result.data if result.success else None
    
    def post(self, url: str, data: Any, headers: Optional[Dict] = None) -> Union[str, Dict]:
        """Make POST request."""
        params = {"url": url, "method": "POST", "body": data}
        if headers:
            params["headers"] = headers
        result = self.sdk.call_tool("fetch", params)
        return result.data if result.success else None


# Export main classes
__all__ = ['MCPToolKitSDK', 'ToolResult', 'FileOperations', 'GitOperations', 'WebOperations']