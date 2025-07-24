---
sidebar_position: 3
---

# API Reference

Complete API documentation for the MCP Tool Kit SDK.

## MCPToolKitSDK

The main SDK class for interacting with MCP tools.

### Constructor

```python
MCPToolKitSDK(
    server_url: str = "http://localhost:8000",
    async_mode: bool = False,
    retry_count: int = 3,
    timeout: int = 30,
    cache_ttl: int = 300
)
```

**Parameters:**
- `server_url` (str): URL of the MCP server
- `async_mode` (bool): Enable async operations
- `retry_count` (int): Number of retries for failed operations
- `timeout` (int): Request timeout in seconds
- `cache_ttl` (int): Cache time-to-live in seconds

### Methods

#### call_tool

Execute a single tool with parameters.

```python
call_tool(tool_name: str, params: Dict[str, Any], **kwargs) -> ToolResult
```

**Parameters:**
- `tool_name` (str): Name of the tool to execute
- `params` (dict): Parameters to pass to the tool
- `**kwargs`: Additional options
  - `cache` (bool): Enable/disable caching (default: True)
  - `retry` (int): Override retry count for this call

**Returns:** `ToolResult` object

**Example:**
```python
result = sdk.call_tool("read_file", {"path": "example.txt"})
```

#### call_tool_async

Async version of `call_tool`.

```python
async call_tool_async(tool_name: str, params: Dict[str, Any], **kwargs) -> ToolResult
```

**Example:**
```python
result = await sdk.call_tool_async("read_file", {"path": "example.txt"})
```

#### batch_call

Execute multiple tool calls sequentially.

```python
batch_call(operations: List[Dict[str, Any]]) -> List[ToolResult]
```

**Parameters:**
- `operations` (list): List of operation dictionaries

**Operation format:**
```python
{
    "tool": "tool_name",
    "params": {"param": "value"},
    "options": {"cache": False}  # Optional
}
```

**Example:**
```python
operations = [
    {"tool": "read_file", "params": {"path": "file1.txt"}},
    {"tool": "read_file", "params": {"path": "file2.txt"}}
]
results = sdk.batch_call(operations)
```

#### batch_call_async

Execute multiple tool calls concurrently.

```python
async batch_call_async(operations: List[Dict[str, Any]]) -> List[ToolResult]
```

#### list_tools

Get a list of available tools.

```python
list_tools() -> List[Dict[str, Any]]
```

**Returns:** List of tool definitions

**Example:**
```python
tools = sdk.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")
```

#### get_tool_info

Get detailed information about a specific tool.

```python
get_tool_info(tool_name: str) -> Optional[Dict[str, Any]]
```

**Example:**
```python
info = sdk.get_tool_info("read_file")
if info:
    print(f"Parameters: {info['parameters']}")
```

#### add_middleware

Add middleware to process parameters before tool calls.

```python
add_middleware(middleware: Callable[[str, Dict], Dict])
```

**Example:**
```python
def auth_middleware(tool_name, params):
    params['auth_token'] = 'secret-token'
    return params

sdk.add_middleware(auth_middleware)
```

#### on

Register an event handler.

```python
on(event: str, handler: Callable)
```

**Events:**
- `before_call`: Fired before tool execution
- `after_call`: Fired after successful execution
- `error`: Fired when an error occurs

**Example:**
```python
sdk.on('error', lambda tool, params, error: print(f"Error: {error}"))
```

### Convenience Method Factories

#### file

Get a `FileOperations` instance for a specific path.

```python
file(path: str) -> FileOperations
```

#### git

Get a `GitOperations` instance for a repository.

```python
git(repo_path: str = ".") -> GitOperations
```

#### web

Get a `WebOperations` instance.

```python
web() -> WebOperations
```

## ToolResult

Result object returned by tool executions.

### Attributes

- `success` (bool): Whether the operation succeeded
- `data` (Any): The result data
- `error` (Optional[str]): Error message if failed
- `metadata` (Dict[str, Any]): Additional information

### Methods

#### to_dict

Convert to dictionary representation.

```python
to_dict() -> Dict[str, Any]
```

## FileOperations

Simplified file operations.

### Constructor

```python
FileOperations(sdk: MCPToolKitSDK, base_path: str = ".")
```

### Methods

#### read

Read file contents.

```python
read(path: Optional[str] = None) -> str
```

#### write

Write content to file.

```python
write(content: str, path: Optional[str] = None) -> bool
```

#### append

Append content to file.

```python
append(content: str, path: Optional[str] = None) -> bool
```

#### exists

Check if file exists.

```python
exists(path: Optional[str] = None) -> bool
```

**Example:**
```python
file = sdk.file("data.txt")
file.write("Initial content")
file.append("\nMore content")
if file.exists():
    content = file.read()
```

## GitOperations

Git repository operations.

### Constructor

```python
GitOperations(sdk: MCPToolKitSDK, repo_path: str = ".")
```

### Methods

#### status

Get git status.

```python
status() -> str
```

#### commit

Create a commit.

```python
commit(message: str, files: Optional[List[str]] = None) -> bool
```

#### push

Push to remote.

```python
push(branch: Optional[str] = None) -> bool
```

**Example:**
```python
git = sdk.git(".")
status = git.status()
if "modified" in status:
    git.commit("Update files", files=["file1.py", "file2.py"])
    git.push("main")
```

## WebOperations

HTTP operations.

### Constructor

```python
WebOperations(sdk: MCPToolKitSDK)
```

### Methods

#### get

Make a GET request.

```python
get(url: str, headers: Optional[Dict] = None) -> Union[str, Dict]
```

#### post

Make a POST request.

```python
post(url: str, data: Any, headers: Optional[Dict] = None) -> Union[str, Dict]
```

**Example:**
```python
web = sdk.web()

# GET request
data = web.get("https://api.example.com/users")

# POST request
response = web.post(
    "https://api.example.com/users",
    {"name": "John", "email": "john@example.com"},
    headers={"Authorization": "Bearer token"}
)
```

## Dynamic Methods

The SDK supports dynamic method generation for direct tool access:

```python
# Instead of:
result = sdk.call_tool("read_file", {"path": "file.txt"})

# You can use:
result = sdk.read_file(path="file.txt")
result = sdk.list_directory(path=".")
result = sdk.write_file(path="output.txt", content="data")
```

Any tool name becomes a callable method with parameters as keyword arguments.