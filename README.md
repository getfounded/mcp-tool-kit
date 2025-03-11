# MCP Tool Kit

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
- **Browser automation**: Complete browser control via Browserbase and Playwright
- **World Bank API**: Access to economic and development data
- **News API**: Access to global news sources and articles
- **PowerPoint**: Create and manipulate PowerPoint presentations
- **Excel**: Create and manipulate Excel spreadsheets
- **QuickBooks**: Financial and accounting operations
- **Shopify**: E-commerce platform integration
- **Yahoo Finance**: Stock market and financial data
- **FRED**: Federal Reserve Economic Data
- **And many more specialized tools**

# Building Custom Tools for Claude with MCP Toolkit

This guide demonstrates how to create custom tools that Claude can use via the Model Context Protocol (MCP) toolkit.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Implementation Guide](#step-by-step-implementation-guide)
- [Example: Creating a Custom SEO Analysis Tool](#example-creating-a-custom-seo-analysis-tool)
- [Usage with Claude](#usage-with-claude)
- [Troubleshooting](#troubleshooting)

## Overview

The MCP (Model Context Protocol) toolkit allows you to create custom tools that Claude can access and use. This enables Claude to perform specialized actions beyond its built-in capabilities, such as interacting with your specific business systems, analyzing data with custom algorithms, or controlling specialized hardware.

## Prerequisites

- MCP toolkit installed (`pip install mcptoolkit` or Docker setup)
- Access to Claude Desktop app
- Basic Python knowledge
- Docker (recommended)

### Get Started ASAP | Running the Server
Caution: This will grant claude access to every tool without limitation in the main branch of this repository.

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

## Step-by-Step Implementation Guide

### Step 1: Set Up Your MCP Server with the Toolkit

Start by running the MCP server:

```bash
# Using Docker (recommended)
docker run -p 8000:8000 -v ~/documents:/app/documents -v ~/downloads:/app/downloads getfounded/mcp-tool-kit:latest

# Or if installed via pip
mcptoolkit-server
```

### Configure Claude Desktop to Access Your Server

1. Open Claude Desktop app
2. Go to File > Settings > Developer > Edit config
3. Add the 'claude_desktop_configuration.json' file
4. Save the configuration
5. Restart the MCP server with your new tool integrated
6. Restart and Open Claude Desktop app

## Example: Claude Desktop Configuration

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

---

## Other Usage Examples

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
### Sample Claude Prompts

Once set up, you can ask Claude to use the tools with prompts like:

- "Search the web for the latest AI research papers and summarize the findings."
- "Create a PowerPoint presentation about climate change with three slides."
- "Download my QuickBooks invoice data and analyze our revenue for the past quarter."
- "Set up a product on my Shopify store with these details and pricing."
- "Get the current stock price and historical data for Tesla using Yahoo Finance."
- "Analyze inflation trends using FRED economic data for the past 5 years."
- "Use browser automation to fill out this form at [website URL]."
- "Read the text file in my Downloads folder named 'project_notes.txt'."
- "Get the latest news headlines about technology."

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


- **Browser_Automation:**
  - `playwright_launch_browser`: Launch a new browser instance
  - `playwright_navigate`: Navigate to a URL
  - `playwright_screenshot`: Take a screenshot
  - `playwright_click`: Click on an element
  - `playwright_fill`: Fill an input field
  - `playwright_evaluate`: Execute JavaScript
  - `playwright_get_content`: Get the HTML content of a page

### E-Commerce Tools
- **Shopify:**
  - `shopify_get_products`: Get product information
  - `shopify_create_product`: Create a new product
  - `shopify_update_product`: Update an existing product
  - `shopify_get_orders`: Get order information
  - `shopify_create_order`: Create a new order
  - `shopify_get_customers`: Get customer information

### Financial Tools
- **QuickBooks:**
  - `quickbooks_get_accounts`: Get account information
  - `quickbooks_get_invoices`: Get invoice information
  - `quickbooks_create_invoice`: Create an invoice
  - `quickbooks_get_customers`: Get customer information
  - `quickbooks_get_reports`: Generate financial reports

### Financial Data Tools
- **Yahoo Finance:**
  - `yfinance`: Get stock quotes and historical data
  - `yfinance_get_quote`: Get current stock quote
  - `yfinance_get_history`: Get historical stock data
  - `yfinance_get_info`: Get detailed company information
  - `yfinance_get_options`: Get options chain data
  - `yfinance_get_recommendations`: Get analyst recommendations

- **FRED (Federal Reserve Economic Data):**
  - `fred_get_series`: Get economic data series
  - `fred_get_series_info`: Get metadata about a series
  - `fred_search`: Search for economic data series
  - `fred_get_category`: Browse data by category
  - `fred_get_releases`: Get economic data releases
  - `fred_get_sources`: Get data sources

### Time Tools
- `get_current_time`: Get current time in a specified timezone
- `convert_time`: Convert time between timezones

### Sequential Thinking
- `sequentialthinking`: A tool for breaking down complex problems using a step-by-step thinking process

### Brave Search
- `brave_web_search`: Perform web searches
- `brave_local_search`: Search for local businesses and places

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
