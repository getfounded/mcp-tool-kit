# MCP Unified Server

A modular server implementation for Claude AI assistants with a variety of integrated tools, enabling Claude to perform actions and access external resources.

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

## Architecture

The server is built with a modular architecture:

```
mcp_unified_server/
├── mcp_unified_server.py     # Main server implementation
├── .env                      # Environment variables 
└── tools/                    # Tool modules
    ├── __init__.py           # Package initialization
    ├── brave_search.py       # Brave Search API integration
    ├── browserbase.py        # Browserbase browser automation
    ├── filesystem.py         # File system operations
    ├── news_api.py           # News API integration
    ├── ppt.py                # PowerPoint tools
    ├── sequential_thinking.py # Sequential thinking tools
    ├── time_tools.py         # Time-related tools
    └── worldbank.py          # World Bank API integration
```

Each tool module follows a consistent pattern:
- External MCP reference
- Service class implementation
- Tool function definitions
- Registration functions

## Installation

### Prerequisites

- Python 3.9+
- Required Python packages (automatically installed with pip)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/mcp_unified_server.git
   cd mcp_unified_server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables by creating a `.env` file (see Configuration section)

5. Run the server:
   ```bash
   python mcp_unified_server.py
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

### API Keys

To use all features of the MCP Unified Server, you'll need to obtain API keys for the following services:

- **Brave Search API**: Get an API key from [Brave Search API](https://brave.com/search/api/)
- **Browserbase**: Sign up at [Browserbase](https://browserbase.com) to get API key and project ID
- **News API**: Get an API key from [News API](https://newsapi.org)

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

## Usage Examples

### Example 1: Using File Operations with Time Tools

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

### Example 2: News Search and Analysis

```python
from mcp.client import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Search for news about a topic
news_results = client.call_tool("news_search", {"q": "artificial intelligence", "page_size": 10})

# Create a directory for results
client.call_tool("create_directory", {"path": "~/news_analysis"})

# Save results to a file
client.call_tool("write_file", {"path": "~/news_analysis/ai_news.txt", "content": news_results})
```

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

[MIT License](LICENSE)

## Acknowledgements

This project uses several open-source libraries and APIs:
- MCP SDK for Claude AI assistants
- NewsAPI for news access
- Brave Search API for web search
- World Bank API for economic data
- python-pptx for PowerPoint manipulation
