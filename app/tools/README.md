# MCP Tool Kit - Tools Documentation

## Overview
The MCP Tool Kit provides a flexible framework for creating and using tools that can interact with various services and APIs. This documentation covers the architecture, development patterns, and usage of the tools in the MCP Tool Kit.

## Architecture

### Core Components

#### Tool Registry
The tool registry (`app/tools/base/registry.py`) provides a system for registering and discovering tools. Tools are registered with metadata that describes their functionality, parameters, and categories.

#### Services
Services (`app/tools/base/service.py`) provide the underlying functionality for tools, handling:
- Authentication
- API communication
- Rate limiting
- Error handling
- Configuration

#### Tool Functions
Tool functions are Python functions that are decorated with the `@register_tool` decorator to register them with the MCP system. These functions expose the service functionality to users in a standardized way.

### Directory Structure
Each tool follows a standardized directory structure:
```
app/tools/
├── base/                 # Base classes and utilities
│   ├── registry.py       # Tool registration system
│   ├── service.py        # Base service class
├── [tool_name]/          # Tool-specific directory
│   ├── __init__.py       # Tool initialization and imports
│   ├── service.py        # Service implementation
│   ├── tools.py          # Tool functions
│   └── README.md         # Tool-specific documentation
```

## Developing New Tools

### 1. Create the Service
Create a new service class that extends `ToolServiceBase`:

```python
from app.tools.base.service import ToolServiceBase

class MyNewService(ToolServiceBase):
    """Service to handle interactions with [API/Service]"""
    
    def __init__(self, param1=None, param2=None):
        """Initialize the service with parameters"""
        super().__init__()
        self.param1 = param1 or self.get_env_var("ENV_PARAM1")
        self.param2 = param2 or self.get_env_var("ENV_PARAM2")
    
    def initialize(self) -> bool:
        """Initialize the service (required override)"""
        try:
            # Initialize connections, check credentials, etc.
            self.initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize: {str(e)}")
            return False
    
    # Implement service-specific methods
    async def do_something(self, arg1, arg2):
        """Implement a service operation"""
        self._is_initialized()  # Ensure service is initialized
        
        # Implementation
        return {"result": "success"}

# Singleton instance pattern
_service_instance = None

def get_service() -> MyNewService:
    """Get or initialize the service singleton"""
    global _service_instance
    if _service_instance is None:
        _service_instance = MyNewService()
        _service_instance.initialize()
    return _service_instance
```

### 2. Create Tool Functions
Create tool functions that use the service:

```python
from app.tools.base.registry import register_tool
from app.tools.mynew.service import get_service

@register_tool(category="mynew_category")
async def mynew_do_something(
    arg1: str,
    arg2: int = 42,
    ctx: Context = None
) -> str:
    """Do something with the new tool.
    
    Detailed description of what this tool does.
    
    Parameters:
    - arg1: Description of arg1
    - arg2: Description of arg2 (default: 42)
    
    Returns:
    - JSON string with the result
    """
    service = get_service()
    
    try:
        result = await service.do_something(arg1, arg2)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})
```

### 3. Create the __init__.py
Create an initialization file to import and register your tools:

```python
"""
My New tools for MCP toolkit.
"""

# Import the tools to ensure they are registered
from app.tools.mynew.tools import (
    mynew_do_something,
    # other tools...
)
```

### 4. Document Your Tool
Create a README.md file for your tool explaining:
- Purpose and functionality
- Configuration requirements
- Usage examples
- API documentation

## Best Practices

### Service Development
- Extend `ToolServiceBase` for consistent functionality
- Implement proper initialization and validation
- Use the built-in logging and error handling
- Implement rate limiting for API services
- Use async/await for potentially slow operations
- Implement singleton pattern for service instances

### Tool Function Development
- Use the `@register_tool` decorator with appropriate categories
- Include detailed docstrings
- Use type hints for parameters
- Handle exceptions and return consistent JSON responses
- Follow naming conventions: `toolname_action` for function names

### Documentation
- Include a README.md for each tool
- Document all parameters, return values, and possible errors
- Provide usage examples
- Explain configuration requirements

## Using Tools

### From Python
```python
from app.toolkit import MCPToolKit

# Create the toolkit instance
toolkit = MCPToolKit("http://localhost:8000")

# Call a tool
result = await toolkit.mynew_do_something("arg1_value", arg2=123)
print(result)
```

### From Command Line
```bash
# List available tools
python main.py list

# Run a specific tool
python main.py run mynew_do_something --params '{"arg1": "value", "arg2": 123}'

# Start interactive client
python main.py client
```

### From the MCP Server API
```
POST /tool/mynew_do_something
Content-Type: application/json

{
  "arg1": "value",
  "arg2": 123
}
```

## Available Tools
The MCP Tool Kit includes various tool categories:
- `brave_search`: Web and local search tools
- `dataviz`: Data visualization tools
- `document_management`: Document processing and manipulation
- `excel`: Excel file manipulation
- `filesystem`: File system operations
- `fred`: Federal Reserve Economic Data tools
- `news_api`: News API integration
- `pdf`: PDF file operations
- `powerpoint`: PowerPoint file creation and manipulation
- `project_management`: Project management tools
- `salesforce`: Salesforce CRM integration
- `sharepoint`: SharePoint integration
- `time`: Time-related utilities
- `worldbank`: World Bank data access
- `yfinance`: Yahoo Finance data access

Refer to each tool's specific README for detailed information.
