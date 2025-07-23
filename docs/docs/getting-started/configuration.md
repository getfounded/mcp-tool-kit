---
sidebar_position: 3
---

# Configuration

MCP Tool Kit uses a YAML configuration file to control which tools are enabled and their settings.

## Configuration File

The main configuration file is `config.yaml` in the root directory.

### Basic Structure

```yaml
# Enable/disable tools
enabled_tools:
  filesystem: true
  time_tools: true
  brave_search: false  # Disabled

# Tool-specific settings
tool_config:
  filesystem:
    allowed_directories:
      - "~/Documents"
      - "~/Downloads"
    
  brave_search:
    max_results: 10

# Server settings
server:
  default_transport: "stdio"
  log_level: "INFO"
```

## Enabling/Disabling Tools

### Enable a Tool
```yaml
enabled_tools:
  my_tool: true
```

### Disable a Tool
```yaml
enabled_tools:
  my_tool: false
```

### Enable All Tools
Remove the `enabled_tools` section entirely - all tools are enabled by default.

## Tool-Specific Configuration

Each tool can have its own configuration section:

### File System Tool
```yaml
tool_config:
  filesystem:
    allowed_directories:
      - "~/Documents"
      - "~/Projects"
      - "/tmp"
    allow_file_deletion: false
```

### Browser Automation
```yaml
tool_config:
  browser_automation:
    headless: true
    timeout: 30000
    viewport:
      width: 1920
      height: 1080
```

### News API
```yaml
tool_config:
  news_api:
    default_language: "en"
    default_country: "us"
    page_size: 20
```

## Environment Variables

API keys and sensitive data should be stored in `.env`:

```env
# API Keys
BRAVE_SEARCH_API_KEY=your_brave_key
NEWS_API_KEY=your_news_api_key
FRED_API_KEY=your_fred_key
OPENWEATHER_API_KEY=your_weather_key

# Server Configuration
MCP_LOG_LEVEL=INFO
MCP_FILESYSTEM_DIRS=~/Documents,~/Downloads
```

### Environment Variable Priority

Environment variables override config.yaml settings:
1. Environment variable (highest priority)
2. config.yaml setting
3. Default value (lowest priority)

## Server Configuration

### Logging
```yaml
server:
  log_level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

### Transport Settings
```yaml
server:
  default_transport: "stdio"  # or "sse"
  
  sse:
    host: "0.0.0.0"
    port: 8080
```

### Performance
```yaml
server:
  max_concurrent_tools: 10
  tool_timeout: 300  # seconds
```

## Advanced Configuration

### Custom Tool Directories
```yaml
server:
  tool_directories:
    - "./app/tools"
    - "./custom_tools"
```

### Tool Aliases
```yaml
tool_aliases:
  fs: filesystem
  browser: browser_automation
```

## Configuration Examples

### Minimal Configuration
```yaml
# All tools enabled with defaults
enabled_tools: {}
```

### Development Configuration
```yaml
enabled_tools:
  filesystem: true
  time_tools: true
  sequential_thinking: true

server:
  log_level: "DEBUG"
  
tool_config:
  filesystem:
    allowed_directories:
      - "."  # Current directory
```

### Production Configuration
```yaml
enabled_tools:
  # Only enable production-ready tools
  filesystem: true
  time_tools: true
  brave_search: true
  
server:
  log_level: "WARNING"
  
tool_config:
  filesystem:
    allowed_directories:
      - "/app/data"
    allow_file_deletion: false
```

## Reloading Configuration

Configuration is loaded when the server starts. To apply changes:

```bash
# Restart the server
docker-compose restart

# Or stop and start
docker-compose down
docker-compose up -d
```

## Validating Configuration

Check your configuration is valid:

```bash
# Inside the container
python -c "from config_loader import load_config; print(load_config())"
```

## Next Steps

- [Available Tools](../tools/overview) - See all available tools
- [Tool Development](../development/creating-tools) - Create custom tools