#!/usr/bin/env python3
"""
Tool functions for FRED (Federal Reserve Economic Data) API.
"""
import json
from typing import Dict, List, Any, Optional, Union

from mcp.server.fastmcp import Context

from app.tools.base.registry import register_tool
from app.tools.fred.service import get_service

@register_tool(category="fred")
async def fred_get_series(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
    frequency: Optional[str] = None,
    units: Optional[str] = None,
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
    fred_api = get_service()

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


@register_tool(category="fred")
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
    fred_api = get_service()

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


@register_tool(category="fred")
async def fred_get_series_info(
    series_id: str,
    ctx: Context = None
) -> str:
    """Get metadata about a FRED series.

    Retrieves detailed information about a specific economic data series.

    Parameters:
    - series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
    """
    fred_api = get_service()

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


@register_tool(category="fred")
async def fred_get_category(
    category_id: int = 0,
    ctx: Context = None
) -> str:
    """Get information about a FRED category.

    Retrieves details about a category of economic data series.

    Parameters:
    - category_id: The FRED category ID (default: 0, which is the root category)
    """
    fred_api = get_service()

    # Get category
    response = fred_api.get_category(category_id)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format the response
    return json.dumps(response, indent=2)