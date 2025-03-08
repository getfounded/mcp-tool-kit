# MCP Toolkit

A modular server implementation for Claude AI assistants with integrated tools, enabling Claude to perform actions and access external resources.

## Overview

The MCP Toolkit provides a unified interface for Claude to interact with various external systems and tools including:

- **File system operations**: Read, write, and manipulate files
- **Time tools**: Get current time in different timezones, convert between timezones
- **Sequential thinking**: A tool for dynamic and reflective problem-solving
- **Brave Search**: Web and local search capabilities
- **Browserbase**: Browser automation for web interactions
- **World Bank API**: Access to economic and development data
- **News API**: Access to global news sources and articles
- **PowerPoint**: Create and manipulate PowerPoint presentations
- **Excel**: Create and manipulate Excel spreadsheets
- **Multiple other integrations**: MS Graph, Outlook, Teams, Salesforce, and more

## Installation

```bash
pip install mcptoolkit
```

## Quick Start

```python
from mcptoolkit.mcp_unified_server import create_server
from mcptoolkit.tools import register_all_tools

# Create a new MCP server
server = create_server()

# Register all available tools
register_all_tools(server)

# Start the server
server.start()
```

## Running the Server

You can also run the server directly using the included command-line utility:

```bash
mcptoolkit-server
```

Configure the server using a `.env` file or environment variables.

## Documentation

For complete documentation, please visit the [GitHub repository](https://github.com/getfounded/mcp-tool-kit).

## License

MIT License