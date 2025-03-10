# MCP Tool Kit

A modular server implementation for Claude AI assistants with a variety of integrated tools, enabling Claude to perform actions and access external resources.

[![PyPI version](https://img.shields.io/pypi/v/mcptoolkit.svg)](https://pypi.org/project/mcptoolkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/mcptoolkit.svg)](https://pypi.org/project/mcptoolkit/)
[![License](https://img.shields.io/github/license/getfounded/mcp-tool-kit.svg)](https://github.com/getfounded/mcp-tool-kit/blob/main/LICENSE)
Note that pypi updates may be delayed during the current stages of development.

## MCP Connect | MCP Cloud Tool Kit (Coming Soon)
Connect with a simple api key to access all of the tools. 

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

### Step 2: Create Your Custom Tool

Create a new Python file in the tools directory of the MCP toolkit (e.g., `my_custom_tool.py`):

```python
from mcp import tools

# Store reference to external MCP to be set from mcp_unified_server.py
external_mcp = None

def set_external_mcp(mcp):
    global external_mcp
    external_mcp = mcp

# Create your service class
class MyCustomToolService:
    def __init__(self):
        # Initialize any resources or connections here
        self.some_resource = {}
    
    # Define your tool functionality
    def perform_custom_action(self, parameter1, parameter2):
        # Implement your custom functionality
        result = f"Processed {parameter1} with {parameter2}"
        return result

# Create a service instance
service = MyCustomToolService()

# Define tool wrapper functions
def my_custom_tool(params):
    """
    Performs a custom action.
    
    params:
        parameter1: First parameter description
        parameter2: Second parameter description
    """
    parameter1 = params.get("parameter1", "default")
    parameter2 = params.get("parameter2", "default")
    
    return service.perform_custom_action(parameter1, parameter2)

# Register your tools with MCP
def register_tools(mcp):
    set_external_mcp(mcp)
    mcp.register_tool("my_custom_tool", my_custom_tool)
```

### Step 3: Register Your Tool with the MCP Server

Modify the main MCP server file to import and register your tool:

```python
# Option 1: Update mcp_unified_server.py
from tools import my_custom_tool

# Add to the list of tools to register
tools_modules = [
    # existing tools...
    my_custom_tool,
]

# Option 2: Update tools/__init__.py to include your tool in register_all_tools
def register_all_tools(server):
    # existing tool registrations...
    my_custom_tool.register_tools(server)
```

### Step 4: Configure Claude Desktop to Access Your Tool

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

### Step 5: Create Prompts to Help Claude Use Your Tool

Create example prompts for Claude that demonstrate how to use your custom tool:

```
Claude, I've created a custom tool that can perform [specific action]. 
Here's an example of how to use it:

client.call_tool("my_custom_tool", {
    "parameter1": "value1",
    "parameter2": "value2"
})

Could you please use this tool to [describe what you want Claude to do]?
```

## Example: Creating a Custom SEO Analysis Tool

Here's a complete example of creating an SEO analysis tool:

```python
# seo_tool.py
from mcp import tools
import requests
from bs4 import BeautifulSoup

external_mcp = None

def set_external_mcp(mcp):
    global external_mcp
    external_mcp = mcp

class SEOAnalyzer:
    def analyze_url(self, url):
        try:
            # Fetch the page
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract SEO elements
            title = soup.title.string if soup.title else ""
            meta_desc = soup.find("meta", {"name": "description"})
            meta_desc = meta_desc["content"] if meta_desc else ""
            
            # Count headings
            h1_count = len(soup.find_all('h1'))
            h2_count = len(soup.find_all('h2'))
            
            # Basic analysis
            result = {
                "title": title,
                "title_length": len(title),
                "meta_description": meta_desc,
                "meta_description_length": len(meta_desc),
                "h1_count": h1_count,
                "h2_count": h2_count,
                "issues": []
            }
            
            # Identify issues
            if len(title) < 30 or len(title) > 60:
                result["issues"].append("Title length not optimal (should be 30-60 chars)")
            
            if len(meta_desc) < 120 or len(meta_desc) > 160:
                result["issues"].append("Meta description length not optimal (should be 120-160 chars)")
            
            if h1_count != 1:
                result["issues"].append(f"Page has {h1_count} H1 tags (should have exactly 1)")
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

service = SEOAnalyzer()

def analyze_seo(params):
    """
    Analyzes a URL for basic SEO factors.
    
    params:
        url: The URL to analyze
    """
    url = params.get("url", "")
    if not url:
        return {"error": "URL parameter is required"}
    
    return service.analyze_url(url)

def register_tools(mcp):
    set_external_mcp(mcp)
    mcp.register_tool("analyze_seo", analyze_seo)
```

## Usage with Claude

Once your custom tool is integrated, you can ask Claude to use it:

### Example Prompt for SEO Tool
```
Claude, I've added an SEO analysis tool to your toolkit. Can you please analyze the SEO for my website at https://example.com and provide recommendations for improvement?

The tool can be accessed using:
client.call_tool("analyze_seo", {"url": "https://example.com"})
```

### Example Prompts for Other Custom Tools

1. **Custom Database Tool**:
   ```
   Claude, I've created a tool that can query our product database. Can you use the tool to find all products in the "electronics" category priced under $100?
   
   The tool can be accessed using:
   client.call_tool("query_database", {"category": "electronics", "max_price": 100})
   ```

2. **API Integration Tool**:
   ```
   Claude, I've set up a weather API tool. Can you check the weather forecast for New York for the next 3 days?
   
   The tool can be accessed using:
   client.call_tool("get_weather", {"location": "New York", "days": 3})
   ```

## Troubleshooting

- **Tool Not Found**: Ensure your tool is properly registered and the server is restarted
- **Parameter Errors**: Check that all required parameters are being passed correctly
- **Connection Issues**: Verify the MCP server is running and Claude is properly configured to connect to it
- **Import Errors**: Make sure all dependencies for your custom tool are installed in the environment where the MCP server runs

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

### Browser Automation Tools
- **Browserbase:**
  - `browserbase_create_session`: Create a new browser session
  - `browserbase_close_session`: Close a browser session
  - `browserbase_navigate`: Navigate to a URL
  - `browserbase_screenshot`: Take a screenshot
  - `browserbase_click`: Click an element
  - `browserbase_fill`: Fill a form field
  - `browserbase_evaluate`: Execute JavaScript
  - `browserbase_get_content`: Extract page content

- **Playwright:**
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
