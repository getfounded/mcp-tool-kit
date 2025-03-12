#!/usr/bin/env python3
import os
import logging
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("FRED API tools MCP reference set")


class FREDAPIService:
    """Service to handle FRED API operations"""

    def __init__(self, api_key):
        self.api_key = api_key
        try:
            from fredapi import Fred
            self.client = Fred(api_key=api_key)
            logging.info("FRED API client initialized successfully")
        except ImportError:
            logging.error(
                "fredapi module not installed. Please install it with 'pip install fredapi'")
            raise ImportError("fredapi module is required")
        except Exception as e:
            logging.error(f"Failed to initialize FRED API client: {str(e)}")
            raise

    def get_series(self, series_id, **kwargs):
        """Get data for a FRED series"""
        try:
            data = self.client.get_series(series_id, **kwargs)
            return self._format_series_data(data, series_id)
        except Exception as e:
            return {"error": str(e)}

    def search(self, search_text, **kwargs):
        """Search for FRED series"""
        try:
            data = self.client.search(search_text, **kwargs)
            return self._format_search_results(data)
        except Exception as e:
            return {"error": str(e)}

    def get_series_info(self, series_id):
        """Get metadata about a FRED series"""
        try:
            info = self.client.get_series_info(series_id)
            return self._format_series_info(info)
        except Exception as e:
            return {"error": str(e)}

    def get_release(self, release_id):
        """Get information about a FRED release"""
        try:
            release = self.client.get_release(release_id)
            return self._format_release(release)
        except Exception as e:
            return {"error": str(e)}

    def get_category(self, category_id=0):
        """Get information about a FRED category"""
        try:
            category = self.client.get_category(category_id)
            return self._format_category(category)
        except Exception as e:
            return {"error": str(e)}

    def _format_series_data(self, data, series_id):
        """Format pandas Series data into a dict for JSON serialization"""
        if isinstance(data, pd.Series):
            # Convert the pandas Series to a list of date/value pairs
            # First reset the index to make the dates a column
            df = data.reset_index()
            # Convert to list of dicts
            data_list = df.to_dict(orient='records')
            # Convert dates to strings
            for item in data_list:
                if 'index' in item and hasattr(item['index'], 'strftime'):
                    item['date'] = item['index'].strftime('%Y-%m-%d')
                    del item['index']
                elif 'DATE' in item and hasattr(item['DATE'], 'strftime'):
                    item['date'] = item['DATE'].strftime('%Y-%m-%d')
                    del item['DATE']

            # Get series info for the title
            try:
                series_info = self.client.get_series_info(series_id)
                title = series_info.get('title', f'Series {series_id}')
            except:
                title = f'Series {series_id}'

            return {
                "series_id": series_id,
                "title": title,
                "observation_start": data.index.min().strftime('%Y-%m-%d') if not data.empty else None,
                "observation_end": data.index.max().strftime('%Y-%m-%d') if not data.empty else None,
                "data": data_list,
                "count": len(data_list)
            }
        return {"error": "Unexpected data format returned from FRED API"}

    def _format_search_results(self, data):
        """Format search results from DataFrame to dict"""
        if isinstance(data, pd.DataFrame):
            results = data.to_dict(orient='records')
            return {
                "results": results,
                "count": len(results)
            }
        return {"error": "Unexpected data format returned from FRED API"}

    def _format_series_info(self, info):
        """Format series info for JSON serialization"""
        if isinstance(info, dict):
            return info
        return {"error": "Unexpected data format returned from FRED API"}

    def _format_release(self, release):
        """Format release info for JSON serialization"""
        if isinstance(release, dict):
            return release
        return {"error": "Unexpected data format returned from FRED API"}

    def _format_category(self, category):
        """Format category info for JSON serialization"""
        if isinstance(category, dict):
            return category
        return {"error": "Unexpected data format returned from FRED API"}


# Tool function definitions that will be registered with MCP

async def fred_get_series(
    series_id: str,
    observation_start: str = None,
    observation_end: str = None,
    frequency: str = None,
    units: str = None,
    ctx: Context = None
) -> str:
    """Get data for a FRED series.

    Retrieves time series data for a specific economic indicator.

    Parameters:
    - series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
    - observation_start: Start date in YYYY-MM-DD format (optional)
    - observation_end: End date in YYYY-MM-DD format (optional)
    - frequency: Data frequency ('d', 'w', 'm', 'q', 'sa', 'a') (optional)
    - units: Units transformation ('lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log') (optional)
    """
    fred_api = _get_fred_api_service()
    if not fred_api:
        return "FRED API key not configured. Please set the FRED_API_KEY environment variable."

    # Build params dict, excluding None values
    params = {}
    if observation_start:
        params['observation_start'] = observation_start
    if observation_end:
        params['observation_end'] = observation_end
    if frequency:
        params['frequency'] = frequency
    if units:
        params['units'] = units

    # Get series data
    response = fred_api.get_series(series_id, **params)

    if "error" in response:
        return f"Error: {response['error']}"

    return json.dumps(response, indent=2)


async def fred_search(
    search_text: str,
    limit: int = 10,
    order_by: str = 'search_rank',
    sort_order: str = 'desc',
    ctx: Context = None
) -> str:
    """Search for FRED series.

    Searches for economic data series by keywords/text.

    Parameters:
    - search_text: The words to match against economic data series
    - limit: Maximum number of results to return (default: 10)
    - order_by: Order results by values of the specified attribute (default: 'search_rank')
    - sort_order: Sort results in ascending or descending order ('asc' or 'desc', default: 'desc')
    """
    fred_api = _get_fred_api_service()
    if not fred_api:
        return "FRED API key not configured. Please set the FRED_API_KEY environment variable."

    # Build params dict
    params = {
        'limit': limit,
        'order_by': order_by,
        'sort_order': sort_order
    }

    # Get search results
    response = fred_api.search(search_text, **params)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format the response
    result_count = response.get("count", 0)
    results = response.get("results", [])

    formatted_results = []
    for result in results:
        formatted_results.append(f"""ID: {result.get('id', 'N/A')}
Title: {result.get('title', 'N/A')}
Units: {result.get('units', 'N/A')}
Frequency: {result.get('frequency', 'N/A')}
Seasonal Adjustment: {result.get('seasonal_adjustment', 'N/A')}
Last Updated: {result.get('last_updated', 'N/A')}
""")

    if not formatted_results:
        return "No series found matching your search criteria."

    return f"Found {result_count} series. Showing top {len(formatted_results)} results:\n\n" + "\n---\n".join(formatted_results)


async def fred_get_series_info(
    series_id: str,
    ctx: Context = None
) -> str:
    """Get metadata about a FRED series.

    Retrieves detailed information about a specific economic data series.

    Parameters:
    - series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
    """
    fred_api = _get_fred_api_service()
    if not fred_api:
        return "FRED API key not configured. Please set the FRED_API_KEY environment variable."

    # Get series info
    response = fred_api.get_series_info(series_id)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format the response
    info = {}
    for key, value in response.items():
        if value is not None:
            info[key] = value

    return json.dumps(info, indent=2)


async def fred_get_category(
    category_id: int = 0,
    ctx: Context = None
) -> str:
    """Get information about a FRED category.

    Retrieves details about a category of economic data series.

    Parameters:
    - category_id: The FRED category ID (default: 0, which is the root category)
    """
    fred_api = _get_fred_api_service()
    if not fred_api:
        return "FRED API key not configured. Please set the FRED_API_KEY environment variable."

    # Get category
    response = fred_api.get_category(category_id)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format the response
    return json.dumps(response, indent=2)


# Tool registration and initialization
_fred_api_service = None


def initialize_fred_api_service(api_key=None):
    """Initialize the FRED API service"""
    global _fred_api_service

    if api_key is None:
        api_key = os.environ.get("FRED_API_KEY")

    if not api_key:
        logging.warning(
            "FRED API key not configured. Please set the FRED_API_KEY environment variable.")
        return None

    try:
        _fred_api_service = FREDAPIService(api_key=api_key)
        return _fred_api_service
    except ImportError:
        logging.error(
            "fredapi module is required. Install with 'pip install fredapi'")
        return None
    except Exception as e:
        logging.error(f"Failed to initialize FRED API service: {str(e)}")
        return None


def _get_fred_api_service():
    """Get or initialize the FRED API service"""
    global _fred_api_service
    if _fred_api_service is None:
        _fred_api_service = initialize_fred_api_service()
    return _fred_api_service


def get_fred_api_tools():
    """Get a dictionary of all FRED API tools for registration with MCP"""
    return {
        "fred_get_series": fred_get_series,
        "fred_search": fred_search,
        "fred_get_series_info": fred_get_series_info,
        "fred_get_category": fred_get_category
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the FRED API module with MCP reference and API key"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_fred_api_service()
    if service:
        logging.info("FRED API service initialized successfully")
    else:
        logging.warning("Failed to initialize FRED API service")

    return service is not None


# When running standalone for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create a local MCP instance for testing
    local_mcp = FastMCP(
        "FRED API Tools",
        dependencies=["fredapi", "pandas"]
    )

    # Register tools with the local MCP
    fred_tools = get_fred_api_tools()
    for tool_name, tool_func in fred_tools.items():
        local_mcp.tool(name=tool_name)(tool_func)

    print("FRED API tools registered with local MCP instance")
    print("Available tools:")
    for tool_name in fred_tools.keys():
        print(f"- {tool_name}")
