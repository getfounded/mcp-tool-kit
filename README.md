# MCP Unified Server

A modular server implementation for Claude AI assistants with a variety of integrated tools, enabling Claude to perform actions and access external resources.

[![PyPI version](https://img.shields.io/pypi/v/mcptoolkit.svg)](https://pypi.org/project/mcptoolkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/mcptoolkit.svg)](https://pypi.org/project/mcptoolkit/)
[![License](https://img.shields.io/github/license/getfounded/mcp-tool-kit.svg)](https://github.com/getfounded/mcp-tool-kit/blob/main/LICENSE)

## Quick Install

```bash
pip install mcptoolkit
```

## Overview

The MCP Unified Server provides a unified interface for Claude to interact with various external systems and tools including:

- **File system operations**: Read, write, and manipulate files
- **Time tools**: Get current time in different timezones, convert between timezones
- **Sequential thinking**: A tool for dynamic and reflective problem-solving
- **Brave Search**: Web and local search capabilities
- **Browserbase**: Browser automation for web interactions
- **World Bank API**: Access to economic and development data
- **News API**: Access to global news sources and articles
- **PowerPoint**: Create and manipulate PowerPoint presentations
- **Excel**: Create and manipulate Excel spreadsheets

## Usage Examples

### Example 1: Running the Server

```python
# Method 1: Using command-line entry point
mcptoolkit-server

# Method 2: Using Python module
from mcptoolkit import mcp_unified_server

# Create and run the server
server = mcp_unified_server.create_server()
server.start()
```

### Example 2: Using the Client 

```python
from mcp.client import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Use file operations
client.call_tool("write_file", {"path": "~/data/timestamp.txt", "content": "File created at:"})

# Get current time
time_result = client.call_tool("get_current_time", {"timezone": "America/New_York"})

# Append time to file
client.call_tool("edit_file", {
    "path": "~/data/timestamp.txt", 
    "edits": [{"oldText": "File created at:", "newText": f"File created at: {time_result}"}]
})
```

## Architecture

The server is built with a modular architecture:

```
mcptoolkit/
├── __init__.py             # Package initialization
├── mcp_unified_server.py   # Main server implementation
├── config_loader.py        # Configuration loader
├── config_ui.py            # Web UI for configuration
├── launcher.py             # Helper script
├── ms_graph_auth.py        # Microsoft Graph authentication
└── tools/                  # Tool modules
    ├── __init__.py         # Package initialization
    ├── brave_search.py     # Brave Search API integration
    ├── browserbase.py      # Browserbase browser automation
    ├── filesystem.py       # File system operations
    ├── news_api.py         # News API integration
    ├── ppt.py              # PowerPoint tools
    ├── sequential_thinking.py # Sequential thinking tools
    ├── time_tools.py       # Time-related tools
    ├── worldbank.py        # World Bank API integration
    └── ... (other tools)
```

Each tool module follows a consistent pattern:
- External MCP reference
- Service class implementation
- Tool function definitions
- Registration functions

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install mcptoolkit
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/getfounded/mcp-tool-kit.git
cd mcp-tool-kit

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Configuration

The server can be configured using environment variables. Create a `.env` file in the project root with the following variables:

```env
# MCP Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_LOG_LEVEL=info  # debug, info, warning, error

# Tool API Keys
BRAVE_API_KEY=your_brave_api_key
BROWSERBASE_API_KEY=your_browserbase_api_key
BROWSERBASE_PROJECT_ID=your_browserbase_project_id
NEWS_API_KEY=your_news_api_key

# File System Configuration
MCP_FILESYSTEM_DIRS=~/documents,~/downloads  # Comma-separated list of allowed directories
```

### Configuration UI

The package includes a web-based configuration UI:

```bash
# Run the configuration UI
mcptoolkit-config
```

Access the UI in your web browser at http://localhost:8501

## Available Tools

### File System Tools
- `read_file`: Read contents of a file
- `read_multiple_files`: Read multiple files simultaneously
- `write_file`: Create or overwrite a file
- `edit_file`: Make line-based edits to a file
- `create_directory`: Create a new directory
- `list_directory`: Get directory contents
- `directory_tree`: Get a recursive tree view
- `move_file`: Move or rename files/directories
- `search_files`: Search for files matching a pattern
- `get_file_info`: Get file metadata
- `list_allowed_directories`: List allowed directories

### Time Tools
- `get_current_time`: Get current time in a specified timezone
- `convert_time`: Convert time between timezones

### Sequential Thinking
- `sequentialthinking`: A tool for breaking down complex problems using a step-by-step thinking process

### Brave Search
- `brave_web_search`: Perform web searches
- `brave_local_search`: Search for local businesses and places

### Browserbase
- `browserbase_create_session`: Create a new browser session
- `browserbase_close_session`: Close a browser session
- `browserbase_navigate`: Navigate to a URL
- `browserbase_screenshot`: Take a screenshot
- `browserbase_click`: Click an element
- `browserbase_fill`: Fill a form field
- `browserbase_evaluate`: Execute JavaScript
- `browserbase_get_content`: Extract page content

### World Bank API
- `worldbank_get_indicator`: Get indicator data for a country

### News API
- `news_top_headlines`: Get top news headlines
- `news_search`: Search for news articles
- `news_sources`: List available news sources

### PowerPoint Tools
- `ppt_create_presentation`: Create a new PowerPoint presentation
- `ppt_open_presentation`: Open an existing presentation
- `ppt_save_presentation`: Save a presentation
- `ppt_add_slide`: Add a new slide
- `ppt_add_text`: Add text to a slide
- `ppt_add_image`: Add an image to a slide
- `ppt_add_chart`: Add a chart to a slide
- `ppt_add_table`: Add a table to a slide
- `ppt_analyze_presentation`: Analyze presentation structure
- `ppt_enhance_presentation`: Suggest enhancements
- `ppt_generate_presentation`: Generate a presentation from text
- `ppt_command`: Process natural language commands

For a complete list of available tools, see the documentation or browse the tools directory.

## Development

### Adding a New Tool Module

1. Create a new file in the `tools` directory (e.g., `my_tool.py`)
2. Follow the existing module pattern:
   - Create service class
   - Define tool functions
   - Implement registration functions
3. Update `mcp_unified_server.py` to import and register your new module

### Extending an Existing Tool Module

1. Add new methods to the service class
2. Add new tool functions
3. Update the registration function to include your new tools

## Troubleshooting

- **Module not loading**: Check the import path and dependencies
- **API key errors**: Verify your API keys in the `.env` file
- **Permission errors**: Check the allowed directories in `MCP_FILESYSTEM_DIRS`
- **Connection errors**: Ensure the server is running and the port is accessible

## License

The MCP Unified Server is licensed under the MIT License.

## Acknowledgements

This project uses several open-source libraries and APIs:
- MCP SDK for Claude AI assistants
- NewsAPI for news access
- Brave Search API for web search
- World Bank API for economic data
- python-pptx for PowerPoint manipulation
- XlsxWriter for Excel spreadsheets