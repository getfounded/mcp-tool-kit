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

The MCP Tool Kit provides a unified interface for Claude to interact with various external systems and tools including:

- **File system operations**: Read, write, and manipulate files
- **Time tools**: Get current time in different timezones, convert between timezones
- **Sequential thinking**: A tool for dynamic and reflective problem-solving
- **Brave Search**: Web and local search capabilities
- **Browser automation**: Complete browser control via Browserbase and Playwright
- **World Bank API**: Access to economic and development data
- **News API**: Access to global news sources and articles
- **PowerPoint**: Create and manipulate PowerPoint presentations
- **Excel**: Create and manipulate Excel spreadsheets
- **Yahoo Finance**: Stock market and financial data
- **FRED**: Federal Reserve Economic Data
- **And many more specialized tools**

## Using the MCP Tool Kit

The toolkit offers two ways to interact with the various tools:

### Option 1: Server Approach

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

### Option 2: MCPToolKit Class

The `MCPToolKit` class provides a clean, structured interface to all MCP tools. This approach makes it easier to integrate with your existing Python code and provides better IDE auto-completion support.

```python
from mcptoolkit import MCPToolKit

# Initialize the toolkit with the server URL
toolkit = MCPToolKit(server_url="http://localhost:8000")

# Now you can use any tool through the toolkit
# Example: Read a file
content = toolkit.read_file("path/to/file.txt")

# Example: Perform a web search
search_results = toolkit.web_search("artificial intelligence trends")
```

## Client Usage Examples

### Example 1: Basic Operations with MCPToolKit

```python
from mcptoolkit import MCPToolKit

# Initialize the toolkit
toolkit = MCPToolKit()

# Read a file
file_content = toolkit.read_file("README.md")
print(f"File content length: {len(file_content)}")

# Create a directory
toolkit.create_directory("analysis_results")

# Write data to a file
toolkit.write_file("analysis_results/report.md", "# Analysis Report\n\nThis is an automated report.")

# Get current time in different timezone
time_info = toolkit.get_current_time("America/New_York")
print(f"Current time in New York: {time_info}")

# Perform a web search
search_results = toolkit.web_search("latest AI research papers", count=5)
print("Search results:", search_results)
```

### Example 2: Practical Tool Examples

```python
from mcptoolkit import MCPToolKit

# Initialize the toolkit
toolkit = MCPToolKit()

# --- File System Operations ---
# Read file content
readme = toolkit.read_file("README.md")

# Write to a file
toolkit.write_file(
    "analysis_results.txt", 
    "# Analysis Results\n\nThis file contains the output of our data analysis."
)

# --- Web Search and Information Retrieval ---
# Search the web
search_results = toolkit.web_search("latest AI research papers")

# Get news headlines
news = toolkit.news_top_headlines(category="technology", page_size=5)

# --- Data Analysis and Visualization ---
# Analyze stock market data
stock_data = toolkit.yfinance_get_historical_data("MSFT", period="1mo")

# --- Document Generation ---
# Create a PowerPoint presentation
toolkit.ppt_create_presentation(session_id="quarterly_report")
toolkit.ppt_add_slide(session_id="quarterly_report", title="Q3 Financial Results")
toolkit.ppt_add_chart(
    session_id="quarterly_report",
    slide_index=1,
    chart_type="bar",
    chart_title="Revenue by Department",
    categories=["Marketing", "Sales", "R&D", "Support"],
    series_names=["Q3 2024"],
    series_values=[[125000, 240000, 175000, 98000]]
)
toolkit.ppt_save_presentation(session_id="quarterly_report")

# --- Browser Automation ---
# Create browser session and navigate
browser_id = toolkit.browser_launch(browser_type="chromium", headless=True)
page_id = toolkit.browser_new_page(browser_id=browser_id)
toolkit.browser_navigate(page_id=page_id, url="https://example.com")
content = toolkit.browser_get_content(page_id=page_id)
```

### Example 3: Building a Complete Workflow

```python
from mcptoolkit import MCPToolKit
import json

# Initialize the toolkit
toolkit = MCPToolKit()

def run_market_research(company_name, market_sector):
    """Perform comprehensive market research using various MCP tools"""
    
    print(f"Beginning market research for {company_name} in the {market_sector} sector...")
    
    # 1. Gather information about the company and market
    company_search = toolkit.web_search(
        query=f"{company_name} company profile financial information",
        count=5
    )
    
    market_news = toolkit.news_search(
        q=f"{market_sector} market trends analysis",
        page_size=10
    )
    
    # 2. Get economic indicators relevant to the sector
    if market_sector.lower() in ["tech", "technology"]:
        indicator = "GB.XPD.RSDV.GD.ZS"  # R&D expenditure
    elif market_sector.lower() in ["finance", "banking"]:
        indicator = "FM.LBL.BMNY.GD.ZS"  # Broad money to GDP
    else:
        indicator = "NY.GDP.MKTP.KD.ZG"  # GDP growth
        
    economic_data = toolkit.worldbank_get_indicator(
        country_id="WLD",  # World
        indicator_id=indicator
    )
    
    # 3. Create a report directory and save gathered information
    toolkit.create_directory(path=f"{company_name}_research")
    
    toolkit.write_file(
        path=f"{company_name}_research/company_info.json",
        content=json.dumps(company_search, indent=2)
    )
    
    toolkit.write_file(
        path=f"{company_name}_research/market_news.json",
        content=json.dumps(market_news, indent=2)
    )
    
    toolkit.write_file(
        path=f"{company_name}_research/economic_indicators.json",
        content=json.dumps(economic_data, indent=2)
    )
    
    # 4. Generate a PowerPoint presentation with the findings
    toolkit.ppt_create_presentation(session_id="market_report")
    
    # Add title slide
    toolkit.ppt_add_slide(
        session_id="market_report",
        title=f"{company_name}: Market Analysis",
        content=f"An overview of {company_name} in the {market_sector} sector"
    )
    
    # Add company overview
    toolkit.ppt_add_slide(
        session_id="market_report",
        title="Company Overview",
        layout_index=2
    )
    
    # Add market trends
    toolkit.ppt_add_slide(
        session_id="market_report",
        title=f"{market_sector} Market Trends",
        layout_index=2
    )
    
    # Add economic indicators chart
    toolkit.ppt_add_slide(
        session_id="market_report",
        title="Economic Indicators",
        layout_index=5
    )
    
    # Save the presentation
    toolkit.ppt_save_presentation(
        session_id="market_report", 
        file_path=f"{company_name}_research/market_report.pptx"
    )
    
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

The MCP Tool Kit follows a client-server architecture:

```
mcptoolkit/
├── __init__.py             # Package initialization
├── mcp_unified_server.py   # Main server implementation
├── config_loader.py        # Configuration loader
├── config_ui.py            # Web UI for configuration
├── launcher.py             # Helper script
├── ms_graph_auth.py        # Microsoft Graph authentication
├── toolkit.py              # MCPToolKit client interface class
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

The architecture consists of two main components:

1. **Server**: The MCP Unified Server that hosts all the tools and provides a JSON-RPC interface for Claude to interact with.

2. **Client Interface**: The `MCPToolKit` class provides a clean, structured Python interface to interact with the server's tools, making it easier to use the tools programmatically.

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
  - `browser_launch`: Launch a new browser instance
  - `browser_navigate`: Navigate to a URL
  - `browser_screenshot`: Take a screenshot
  - `browser_click`: Click on an element
  - `browser_fill`: Fill an input field
  - `browser_evaluate`: Execute JavaScript
  - `browser_get_content`: Get the HTML content of a page

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
  - `yfinance_get_ticker_info`: Get detailed company information
  - `yfinance_get_historical_data`: Get historical stock data
  - `yfinance_get_financials`: Get financial statements
  - `yfinance_get_balance_sheet`: Get balance sheet data
  - `yfinance_get_cashflow`: Get cash flow statements
  - `yfinance_get_earnings`: Get earnings data
  - `yfinance_get_options`: Get options chain data
  - `yfinance_get_news`: Get company news
  - `yfinance_download_data`: Download data for multiple tickers

- **FRED (Federal Reserve Economic Data):**
  - `fred_get_series`: Get economic data series
  - `fred_get_series_info`: Get metadata about a series
  - `fred_search`: Search for economic data series
  - `fred_get_category`: Browse data by category

### Time Tools
- `get_current_time`: Get current time in a specified timezone
- `convert_time`: Convert time between timezones

### Sequential Thinking
- `sequential_thinking`: A tool for breaking down complex problems using a step-by-step thinking process

### Brave Search
- `web_search`: Perform web searches
- `local_search`: Search for local businesses and places

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

For a complete list of available tools, see the documentation or browse the tools directory.

## Development

### Adding a New Tool Module

1. Create a new file in the `tools` directory (e.g., `my_tool.py`)
2. Follow the existing module pattern:
   - Create service class
   - Define tool functions
   - Implement registration functions
3. Update `mcp_unified_server.py` to import and register your new module
4. Add methods to the `MCPToolKit` class to provide a clean interface

### Extending an Existing Tool Module

1. Add new methods to the service class
2. Add new tool functions
3. Update the registration function to include your new tools
4. Add corresponding methods to the `MCPToolKit` class

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

The MCP Tool Kit is licensed under the MIT License.

## Acknowledgements

This project uses several open-source libraries and APIs:
- MCP SDK for Claude AI assistants
- NewsAPI for news access
- Brave Search API for web search
- World Bank API for economic data
- python-pptx for PowerPoint manipulation
- XlsxWriter for Excel spreadsheets

The `MCPToolKit` class provides a simplified client interface to the MCP server, inspired by other API client libraries.
