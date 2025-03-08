# MCP Tools Configuration System

This system provides an easy way to enable and disable tools in the MCP Unified Server through a web-based user interface. The configuration system consists of three main components:

1. **Configuration UI**: A Streamlit web application for easy tool management
2. **Configuration Loader**: A Python module to load configuration settings
3. **MCP Unified Server Integration**: Modified server that respects configuration settings

## Quick Start

1. Install requirements:
   ```bash
   pip install streamlit pyyaml python-dotenv
   ```

2. Start both the server and configuration UI:
   ```bash
   python launcher.py
   ```

3. Or start them separately:
   ```bash
   # Start just the server
   python launcher.py --server-only
   
   # Start just the configuration UI
   python launcher.py --ui-only
   ```

4. Access the Configuration UI in your web browser at http://localhost:8501

## Configuration System Overview

### Configuration File Structure

The system uses a YAML-based configuration file (`config.yaml`) with the following structure:

```yaml
enabled_tools:
  filesystem: true
  time_tools: true
  sequential_thinking: true
  brave_search: true
  # ... other tools here

tool_config:
  brave_search:
    rate_limit: 100
    max_results: 10
  filesystem:
    allowed_directories:
      - "~/documents"
      - "~/downloads"
    allow_file_deletion: false
  # ... other tool-specific configurations
```

### Configuration UI Features

The Streamlit-based configuration UI provides the following features:

- **Enable/Disable Tools**: Easily toggle tools on or off
- **Tool Configuration**: Configure specific settings for each tool
- **Environment Variables**: View and edit environment variables
- **Server Control**: Start, stop, and restart the MCP server
- **Advanced Settings**: Edit raw configuration YAML

### Files in this System

- `mcp_unified_server.py`: Main MCP server with configuration integration
- `config_loader.py`: Module for loading and parsing configuration
- `config_ui.py`: Streamlit web application for configuration management
- `launcher.py`: Helper script to start both server and UI
- `config.yaml`: Configuration file (created automatically if not present)

## Extending the Configuration System

### Adding a New Tool

1. Create your tool module in the `tools` directory
2. Make sure it follows the standard MCP tool module pattern:
   - Has a `set_external_mcp()` function
   - Has a `get_<toolname>_tools()` function that returns a dictionary of tools
   - Optionally has an `initialize()` function
3. Add the tool name to the `AVAILABLE_TOOLS` list in `mcp_unified_server.py`
4. Restart the server and it will be available in the configuration UI

### Adding Tool-Specific Configuration Options

For each tool, you can add custom configuration options:

1. Update the UI in `config_ui.py` to include form fields for the tool's settings
2. Access the configuration in your tool using the `get_tool_config()` function

## Troubleshooting

- **UI can't connect to server**: Make sure the server is running and check the ports
- **Tool not appearing in UI**: Ensure it's in the `AVAILABLE_TOOLS` list and follows the module pattern
- **Configuration changes not taking effect**: Make sure to save changes and restart the server

## Security Considerations

- The configuration UI doesn't include authentication by default
- Consider adding authentication or only running it on localhost
- Be careful with environment variables containing sensitive credentials
