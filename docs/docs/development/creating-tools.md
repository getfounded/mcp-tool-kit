---
sidebar_position: 1
---

# Creating Tools

This guide will walk you through creating a new tool for the MCP Tool Kit using the standardized base class system.

## Overview

All tools in MCP Tool Kit inherit from the `BaseTool` class, which provides a consistent interface for tool registration and management.

## Basic Tool Structure

Here's a minimal example of a new tool:

```python
from app.tools.base_tool import BaseTool
from typing import Dict, List, Callable
from mcp.server.fastmcp import Context

class MyCustomTool(BaseTool):
    """A custom tool that does something useful."""
    
    def __init__(self):
        super().__init__()
        
    def get_name(self) -> str:
        return "My Custom Tool"
        
    def get_description(self) -> str:
        return "A tool that performs custom operations"
        
    def get_dependencies(self) -> List[str]:
        return ["requests", "pandas"]  # List your pip dependencies
        
    def get_tools(self) -> Dict[str, Callable]:
        return {
            "my_function": self.my_function,
            "another_function": self.another_function
        }
        
    async def my_function(self, param1: str, param2: int, ctx: Context = None) -> str:
        """Your tool function implementation."""
        # Your logic here
        return f"Processed {param1} with value {param2}"
        
    async def another_function(self, data: str, ctx: Context = None) -> str:
        """Another tool function."""
        # Your logic here
        return f"Processed: {data}"
```

## Required Methods

Every tool must implement these methods:

### `get_name() -> str`
Returns the display name of your tool.

### `get_description() -> str`
Returns a description of what your tool does.

### `get_dependencies() -> List[str]`
Returns a list of Python package dependencies required by your tool.

### `get_tools() -> Dict[str, Callable]`
Returns a dictionary mapping tool function names to their implementations.

## Optional Methods

You can override these methods for additional functionality:

### `initialize(**kwargs) -> None`
Called when the tool is registered. Use this for setup tasks.

```python
def initialize(self, api_key: str = None, **kwargs) -> None:
    """Initialize the tool with configuration."""
    self.api_key = api_key or os.environ.get("MY_API_KEY")
    if not self.api_key:
        raise ValueError("API key is required")
    super().initialize(**kwargs)
```

### `validate_environment() -> bool`
Check if the environment is properly configured for your tool.

```python
def validate_environment(self) -> bool:
    """Check if required environment variables are set."""
    return bool(os.environ.get("MY_API_KEY"))
```

### `cleanup() -> None`
Called when the server shuts down. Use this to clean up resources.

```python
def cleanup(self) -> None:
    """Clean up resources."""
    if hasattr(self, 'connection'):
        self.connection.close()
```

## Tool Function Guidelines

Tool functions should follow these patterns:

1. **Async Functions**: All tool functions should be async
2. **Context Parameter**: Include `ctx: Context = None` as the last parameter
3. **Return Strings**: Return results as strings (JSON for complex data)
4. **Error Handling**: Return error messages as strings, don't raise exceptions

```python
async def process_data(self, 
                      input_data: str, 
                      format: str = "json",
                      ctx: Context = None) -> str:
    """Process data in the specified format.
    
    Args:
        input_data: The data to process
        format: Output format (json, csv, xml)
        ctx: MCP context (optional)
        
    Returns:
        Processed data as a string
    """
    try:
        # Your processing logic
        result = self._process(input_data, format)
        
        if format == "json":
            return json.dumps(result, indent=2)
        else:
            return str(result)
            
    except Exception as e:
        return f"Error processing data: {str(e)}"
```

## Configuration Support

Tools can receive configuration from `config.yaml`:

```yaml
tool_config:
  my_custom_tool:
    api_endpoint: "https://api.example.com"
    timeout: 30
    max_retries: 3
```

Access configuration in your `initialize` method:

```python
def initialize(self, api_endpoint: str = None, timeout: int = 30, **kwargs) -> None:
    """Initialize with configuration."""
    self.api_endpoint = api_endpoint or "https://default.api.com"
    self.timeout = timeout
    super().initialize(**kwargs)
```

## Best Practices

1. **Naming**: Use descriptive names for your tool and functions
2. **Documentation**: Add docstrings to all methods and functions
3. **Error Handling**: Always handle errors gracefully
4. **Logging**: Use the logging module for debugging
5. **Type Hints**: Use type hints for better code clarity
6. **Async/Await**: Make functions async even if they don't need it currently

## Example: Weather Tool

Here's a complete example of a weather tool:

```python
import os
import json
import httpx
from typing import Dict, List, Callable
from app.tools.base_tool import BaseTool
from mcp.server.fastmcp import Context
import logging

logger = logging.getLogger(__name__)


class WeatherTool(BaseTool):
    """Tool for getting weather information."""
    
    def __init__(self):
        super().__init__()
        self.api_key = None
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_name(self) -> str:
        return "Weather Tool"
        
    def get_description(self) -> str:
        return "Get current weather and forecasts for any location"
        
    def get_dependencies(self) -> List[str]:
        return ["httpx"]
        
    def get_tools(self) -> Dict[str, Callable]:
        return {
            "get_weather": self.get_weather,
            "get_forecast": self.get_forecast
        }
        
    def validate_environment(self) -> bool:
        """Check if OpenWeather API key is available."""
        return bool(os.environ.get("OPENWEATHER_API_KEY"))
        
    def initialize(self, **kwargs) -> None:
        """Initialize with API key."""
        self.api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable is required")
        super().initialize(**kwargs)
        
    async def get_weather(self, city: str, country_code: str = None, ctx: Context = None) -> str:
        """Get current weather for a city.
        
        Args:
            city: City name
            country_code: Optional 2-letter country code
            ctx: MCP context
            
        Returns:
            JSON string with weather data
        """
        try:
            location = f"{city},{country_code}" if country_code else city
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                
            data = response.json()
            
            result = {
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
            
            return json.dumps(result, indent=2)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting weather: {e}")
            return f"Error fetching weather data: {str(e)}"
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return f"Error processing weather request: {str(e)}"
            
    async def get_forecast(self, city: str, days: int = 5, ctx: Context = None) -> str:
        """Get weather forecast for a city."""
        # Implementation here
        pass
```

## Testing Your Tool

1. Place your tool file in the `app/tools/` directory
2. Enable it in `config.yaml`:
   ```yaml
   enabled_tools:
     weather_tool: true
   ```
3. Start the server and check if your tool is registered
4. Test your tool functions

## Next Steps

- Learn about the [BaseTool class](base-tool-class) in detail
- Understand [tool registration](tool-registration) process
- Follow [best practices](best-practices) for tool development