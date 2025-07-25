---
sidebar_position: 2
---

# Quick Start

Get up and running with MCP Tool Kit in minutes!

## Starting the Server

### Using the Launcher (Easiest)

1. **Windows**: Double-click `launch.bat`
2. **Mac/Linux**: Run `./launch.sh`
3. Select option 1 for Claude Desktop or option 2 for web access

### Manual Start

```bash
# For stdio mode (Claude Desktop)
docker-compose up -d
docker exec -it mcp-server python mcp_server_v2.py

# For SSE mode (web access)
docker-compose up -d
docker exec -it mcp-server python mcp_server_v2.py --transport sse
```

## Connecting to Claude Desktop

### 1. Locate Claude Desktop Config

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add MCP Server Configuration

Edit the config file and add:

```json
{
  "mcpServers": {
    "mcp-tool-kit": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "mcp_server_v2.py"]
    }
  }
}
```

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

### 4. Verify Connection

In Claude Desktop, you should see the available tools. Try:
- "What tools are available?"
- "Check the health status"

## Using SSE Mode

### 1. Start the Server

```bash
./launch.sh  # Choose option 2
```

### 2. Access the Server

Open http://localhost:8080 in your browser.

### 3. Test the Connection

Use curl to test:
```bash
# Get server info
curl http://localhost:8080/

# Connect to SSE stream
curl http://localhost:8080/sse
```

## Testing Tools

### File System Tool
```
"List files in the current directory"
"Read the README.md file"
```

### Time Tools
```
"What time is it in Tokyo?"
"Convert 3:00 PM EST to PST"
```

### Web Search (requires API key)
```
"Search for recent news about AI"
```

## Common Issues

### Tools not showing in Claude Desktop
1. Check Docker is running: `docker ps`
2. Verify server is running: `docker logs mcp-server`
3. Restart Claude Desktop

### SSE connection refused
1. Check port 8080 is not in use
2. Verify firewall settings
3. Try `localhost` instead of `127.0.0.1`

## Using the SDK

For programmatic access to MCP tools in your Python applications:

```python
from mcp_tool_kit import MCPToolKitSDK

# Initialize SDK
sdk = MCPToolKitSDK()

# Call a tool
result = sdk.call_tool("read_file", {"path": "example.txt"})
if result.success:
    print(result.data)

# Use convenience methods
file = sdk.file("output.txt")
file.write("Hello from SDK!")
```

See the [SDK Quick Start](../sdk/quick-start) for more details.

## Next Steps

- [Configuration Guide](configuration) - Enable/disable tools
- [SDK Documentation](../sdk/overview) - Use tools in your applications
- [Available Tools](../tools/overview) - Explore all tools
- [Creating Tools](../development/creating-tools) - Build your own