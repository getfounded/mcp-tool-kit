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

```bash
# Method 1: Using Docker (recommended)
docker run -p 8000:8000 -v ~/documents:/app/documents getfounded/mcp-tool-kit:latest

# Method 2: Using docker-compose
docker-compose up

# Method 3: Using command-line entry point (if installed via pip)
mcptoolkit-server

# Method 4: Launch both server and configuration UI
mcptoolkit-launcher
```

```python
# Method 5: Using Python module
from mcptoolkit import mcp_unified_server

# Create and run the server with default settings
server = mcp_unified_server.create_server()
server.start()
```

### Example 2: Practical Tool Examples

```python
from mcp.client import MCPClient

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# --- File System Operations ---
# Read file content
readme = client.call_tool("read_file", {"path": "README.md"})

# Write to a file
client.call_tool("write_file", {
    "path": "analysis_results.txt", 
    "content": "# Analysis Results\n\nThis file contains the output of our data analysis."
})

# --- Web Search and Information Retrieval ---
# Search the web
search_results = client.call_tool("brave_web_search", {"query": "latest AI research papers"})

# Get news headlines
news = client.call_tool("news_top_headlines", {"category": "technology", "page_size": 5})

# --- Data Analysis and Visualization ---
# Analyze stock market data
stock_data = client.call_tool("yfinance", {"symbol": "MSFT", "period": "1mo"})

# --- Document Generation ---
# Create a PowerPoint presentation
client.call_tool("ppt_create_presentation", {"session_id": "quarterly_report"})
client.call_tool("ppt_add_slide", {"session_id": "quarterly_report", "title": "Q3 Financial Results"})
client.call_tool("ppt_add_chart", {
    "session_id": "quarterly_report",
    "slide_index": 1,
    "chart_type": "bar",
    "chart_title": "Revenue by Department",
    "categories": ["Marketing", "Sales", "R&D", "Support"],
    "series_names": ["Q3 2024"],
    "series_values": [[125000, 240000, 175000, 98000]]
})
client.call_tool("ppt_save_presentation", {"session_id": "quarterly_report"})

# --- Browser Automation ---
# Create browser session and navigate
session_id = client.call_tool("browserbase_create_session", {"sessionId": "browser1"})
client.call_tool("browserbase_navigate", {"sessionId": "browser1", "url": "https://example.com"})
content = client.call_tool("browserbase_get_content", {"sessionId": "browser1"})
client.call_tool("browserbase_close_session", {"sessionId": "browser1"})

# --- Advanced Problem-Solving ---
# Use sequential thinking to break down a complex problem
client.call_tool("sequentialthinking", {
    "thought": "First, we need to identify the key variables in this optimization problem",
    "thoughtNumber": 1,
    "totalThoughts": 5,
    "nextThoughtNeeded": True
})
```

### Example 3: Building a Complete Workflow

```python
from mcp.client import MCPClient
import json

# Connect to the MCP server
client = MCPClient("http://localhost:8000")

# Scenario: Market research assistant that gathers data, analyzes it, and prepares a report

def run_market_research(company_name, market_sector):
    """Perform comprehensive market research using various MCP tools"""
    
    print(f"Beginning market research for {company_name} in the {market_sector} sector...")
    
    # 1. Gather information about the company and market
    company_search = client.call_tool("brave_web_search", {
        "query": f"{company_name} company profile financial information",
        "count": 5
    })
    
    market_news = client.call_tool("news_search", {
        "q": f"{market_sector} market trends analysis",
        "page_size": 10
    })
    
    # 2. Get economic indicators relevant to the sector
    if market_sector.lower() in ["tech", "technology"]:
        indicator = "GB.XPD.RSDV.GD.ZS"  # R&D expenditure
    elif market_sector.lower() in ["finance", "banking"]:
        indicator = "FM.LBL.BMNY.GD.ZS"  # Broad money to GDP
    else:
        indicator = "NY.GDP.MKTP.KD.ZG"  # GDP growth
        
    economic_data = client.call_tool("worldbank_get_indicator", {
        "country_id": "WLD",  # World
        "indicator_id": indicator
    })
    
    # 3. Create a report directory and save gathered information
    client.call_tool("create_directory", {"path": f"{company_name}_research"})
    
    client.call_tool("write_file", {
        "path": f"{company_name}_research/company_info.json",
        "content": json.dumps(company_search, indent=2)
    })
    
    client.call_tool("write_file", {
        "path": f"{company_name}_research/market_news.json",
        "content": json.dumps(market_news, indent=2)
    })
    
    client.call_tool("write_file", {
        "path": f"{company_name}_research/economic_indicators.json",
        "content": json.dumps(economic_data, indent=2)
    })
    
    # 4. Generate a PowerPoint presentation with the findings
    client.call_tool("ppt_create_presentation", {"session_id": "market_report"})
    
    # Add title slide
    client.call_tool("ppt_add_slide", {
        "session_id": "market_report",
        "title": f"{company_name}: Market Analysis",
        "content": f"An overview of {company_name} in the {market_sector} sector"
    })
    
    # Add company overview
    client.call_tool("ppt_add_slide", {
        "session_id": "market_report",
        "title": "Company Overview",
        "layout_index": 2
    })
    
    # Add market trends
    client.call_tool("ppt_add_slide", {
        "session_id": "market_report",
        "title": f"{market_sector} Market Trends",
        "layout_index": 2
    })
    
    # Add economic indicators chart
    client.call_tool("ppt_add_slide", {
        "session_id": "market_report",
        "title": "Economic Indicators",
        "layout_index": 5
    })
    
    # Save the presentation
    client.call_tool("ppt_save_presentation", {
        "session_id": "market_report", 
        "file_path": f"{company_name}_research/market_report.pptx"
    })
    
    print(f"Market research completed. Results saved to {company_name}_research/")
    return f"{company_name}_research/"

# Execute the research function
research_folder = run_market_research("Acme Corp", "technology")
```

## Using with Claude Desktop App

The mcptoolkit can be easily integrated with the Claude desktop application to enhance Claude's capabilities with external tools.

### Quick Setup for Claude Desktop (Docker Method - Recommended)

1. **Run using Docker** (easiest and recommended):
   ```bash
   # Pull and run the Docker image
   docker run -p 8000:8000 -v ~/documents:/app/documents -v ~/downloads:/app/downloads getfounded/mcp-tool-kit:latest
   ```
   
   This will start the server and expose it on port 8000. The `-v` flags mount your local directories to make them accessible to the toolkit.

2. **Configure Claude Desktop**:
   - Open the Claude desktop app
   - Go to Settings > Tools
   - Click "Add Tool"
   - Add the MCP server URL: `http://localhost:8000`
   - Save the configuration

3. **Start chatting with Claude**:
   - Claude will now have access to all the tools provided by mcptoolkit
   - You can ask Claude to search the web, create presentations, analyze data, and more

### Alternative: Setup without Docker

If you prefer not to use Docker, you can install and run the toolkit directly:

1. **Install the toolkit**:
   ```bash
   pip install mcptoolkit
   ```

2. **Start the MCP server**:
   ```bash
   mcptoolkit-server
   ```
   
   By default, the server will run on `http://localhost:8000`.

3. Then continue with the Claude Desktop configuration as described above.

### Sample Claude Prompts

Once set up, you can ask Claude to use the tools with prompts like:

- "Search the web for the latest AI research papers and summarize the findings."
- "Create a PowerPoint presentation about climate change with three slides."
- "What's the current stock price of Microsoft?"
- "Read the text file in my Downloads folder named 'project_notes.txt'."
- "Get the latest news headlines about technology."

### Example: Claude Desktop Configuration

The repository includes a sample Claude desktop configuration file (`claude_desktop_config.json`) that you can use:

```json
{
  "tools": [
    {
      "name": "MCP Toolkit",
      "url": "http://localhost:8000"
    }
  ],
  "settings": {
    "allowed_directories": ["~/Documents", "~/Downloads"],
    "default_tools": ["MCP Toolkit"]
  }
}
```

You can import this configuration in the Claude desktop app or use it as a reference to create your own.

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

### Method 1: Docker (Recommended)

The easiest way to get started is using Docker, which requires no Python or dependency installation:

```bash
# Pull the Docker image
docker pull getfounded/mcp-tool-kit:latest

# Run the container
docker run -p 8000:8000 -v ~/documents:/app/documents -v ~/downloads:/app/downloads getfounded/mcp-tool-kit:latest
```

You can also use docker-compose:

```bash
# Using the provided docker-compose.yml
docker-compose up
```

This will:
- Start the server on port 8000
- Mount your local directories to make them accessible to the toolkit
- Configure the server with sensible defaults

### Method 2: Install from PyPI

```bash
pip install mcptoolkit
```

### Method 3: Install from Source

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

### Docker Configuration

When running with Docker, you can configure the container using environment variables:

```bash
# Run with custom configuration
docker run -p 8000:8000 \
    -e BRAVE_API_KEY=your_brave_api_key \
    -e NEWS_API_KEY=your_news_api_key \
    -e MCP_LOG_LEVEL=debug \
    -v ~/documents:/app/documents \
    -v ~/downloads:/app/downloads \
    getfounded/mcp-tool-kit:latest
```

Alternatively, you can modify the `docker-compose.yml` file:

```yaml
version: '3'
services:
  mcp-server:
    image: getfounded/mcp-tool-kit:latest
    ports:
      - "8000:8000"
    environment:
      - BRAVE_API_KEY=your_brave_api_key
      - NEWS_API_KEY=your_news_api_key
      - MCP_LOG_LEVEL=info
    volumes:
      - ~/documents:/app/documents
      - ~/downloads:/app/downloads
```

### Local Configuration

If running locally, the server can be configured using environment variables or a `.env` file in the project root:

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

### Development with Docker

You can use Docker for development to ensure a consistent environment:

```bash
# Build a development image
docker build -t mcp-tool-kit:dev .

# Run with source code mounted for development
docker run -p 8000:8000 \
    -v $(pwd):/app \
    -v ~/documents:/app/documents \
    mcp-tool-kit:dev
```

This mounts your local repository into the container, so changes to the code are reflected immediately (for most files).

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