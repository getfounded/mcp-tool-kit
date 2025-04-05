# MCP Toolkit

A comprehensive collection of tools and services for various integrations including Project Management, QuickBooks, and more.

## Features

- **Modular Architecture**: Easily extendable with new tools and services
- **Service-Based Design**: Consistent patterns for authentication and API interactions
- **Dynamic Tool Discovery**: Automatic registration and discovery of tools
- **Rate Limiting**: Built-in rate limiting for API requests
- **Unified Interface**: Access all tools through a single consistent interface
- **Web Server**: Expose tools through a RESTful API
- **Management GUI**: Web-based interface for managing tools and services

## Installation

### Using pip

```bash
pip install mcp-toolkit
```

### From Source

```bash
git clone https://github.com/mcpteam/mcp-toolkit.git
cd mcp-toolkit
pip install -e .
```

### Using Docker

```bash
docker pull mcpteam/mcp-toolkit:latest
docker run -p 8000:8000 -p 5000:5000 mcpteam/mcp-toolkit:latest
```

## Quick Start

### Running the Server

```bash
# Start the API server
mcp-toolkit server --port 8000

# Start the GUI
mcp-toolkit gui --port 5000
```

### Using the Toolkit in Python

```python
from app.toolkit import Toolkit

# Initialize the toolkit
toolkit = Toolkit()

# Use Project Management tools
projects = await toolkit.pm_get_projects(limit=10)
print(f"Found {len(projects['projects'])} projects")

# Use QuickBooks tools
customers = await toolkit.qb_get_customers(query="DisplayName LIKE '%Client%'")
print(f"Found {len(customers['QueryResponse']['Customer'])} matching customers")
```

## Configuration

The toolkit uses environment variables for configuration. You can set these in your environment or create a `.env` file in the project root:

```
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
MCP_LOG_LEVEL=INFO

# Project Management API Configuration
PM_API_KEY=your_pm_api_key_here
PM_INSTANCE_URL=your_pm_instance_url_here
PM_PROVIDER=asana  # Options: asana, jira

# QuickBooks API Configuration
QB_CLIENT_ID=your_qb_client_id_here
QB_CLIENT_SECRET=your_qb_client_secret_here
QB_REDIRECT_URI=your_qb_redirect_uri_here
QB_REFRESH_TOKEN=your_qb_refresh_token_here
QB_REALM_ID=your_qb_realm_id_here
```

## Tool Categories

The toolkit organizes tools into categories for easier access:

### Project Management

Tools for working with project management systems like Asana and Jira:

- `pm_get_projects`: Get a list of projects
- `pm_get_project`: Get a specific project by ID
- `pm_get_tasks`: Get tasks with optional filtering
- `pm_create_task`: Create a new task
- `pm_update_task`: Update an existing task
- And more...

### QuickBooks

Tools for interacting with QuickBooks accounting:

- `qb_get_company_info`: Get company information
- `qb_get_customers`: Get a list of customers
- `qb_create_invoice`: Create a new invoice
- `qb_get_profit_loss`: Get profit and loss report
- And more...

## Architecture

The toolkit follows a consistent architecture:

1. **Service Classes**: Handle authentication, rate limiting, and API interactions
2. **Tool Functions**: Provide specific functionality through a clean interface
3. **Registry System**: Manages tool registration and discovery
4. **Toolkit Interface**: Provides dynamic access to all tools

## Extending the Toolkit

### Creating a New Service

```python
from app.tools.base.service import ToolServiceBase

class MyService(ToolServiceBase):
    """My custom service"""
    
    def __init__(self):
        super().__init__()
        self.api_key = self.get_env_var("MY_API_KEY")
        
        # Create rate limiter
        self.create_rate_limiter("default", 100, 60)
    
    def initialize(self):
        """Initialize the service"""
        # Perform any initialization
        self.initialized = True
        return True
    
    async def my_api_call(self, param1, param2):
        """Make an API call"""
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60)
        
        # Make the API call
        # ...
        
        return result
```

### Creating Tool Functions

```python
from app.tools.base.registry import register_tool
from app.tools.myservice.service import MyService

@register_tool(
    name="my_tool",
    category="My Category",
    service_class=MyService,
    description="My awesome tool"
)
async def my_tool(self, param1: str, param2: int = 42):
    """My tool function
    
    Parameters:
    - param1: First parameter
    - param2: Second parameter (default: 42)
    """
    result = await self.my_api_call(param1, param2)
    return result
```

## Development

### Setting Up a Development Environment

```bash
# Clone the repository
git clone https://github.com/mcpteam/mcp-toolkit.git
cd mcp-toolkit

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/tools/test_project_management.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
