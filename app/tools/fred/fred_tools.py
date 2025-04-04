#!/usr/bin/env python3
"""
FRED (Federal Reserve Economic Data) API tools.
"""
import json
from typing import Dict, Any, Optional

from app.tools.base.registry import register_tool
from app.tools.fred.fred_service import FREDService

@register_tool(
    category="economic_data",
    service_class=FREDService,
    description="Get data for a FRED economic time series"
)
def fred_get_series(
    self,
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
    frequency: Optional[str] = None,
    units: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get data for a FRED series.

    Retrieves time series data for a specific economic indicator.

    Args:
        series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
        observation_start: Start date in YYYY-MM-DD format (optional)
        observation_end: End date in YYYY-MM-DD format (optional)
        frequency: Data frequency ('d', 'w', 'm', 'q', 'sa', 'a') (optional)
        units: Units transformation ('lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log') (optional)
    
    Returns:
        Dictionary with series data
    """
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

    # Get series data using the service
    return self.get_series(series_id, **params)

@register_tool(
    category="economic_data",
    service_class=FREDService,
    description="Search for economic data series by keywords"
)
def fred_search(
    self,
    search_text: str,
    limit: int = 10,
    order_by: str = 'search_rank',
    sort_order: str = 'desc'
) -> Dict[str, Any]:
    """
    Search for FRED series.

    Searches for economic data series by keywords/text.

    Args:
        search_text: The words to match against economic data series
        limit: Maximum number of results to return (default: 10)
        order_by: Order results by values of the specified attribute (default: 'search_rank')
        sort_order: Sort results in ascending or descending order ('asc' or 'desc', default: 'desc')
    
    Returns:
        Dictionary with search results
    """
    # Build params dict
    params = {
        'limit': limit,
        'order_by': order_by,
        'sort_order': sort_order
    }

    # Get search results using the service
    return self.search(search_text, **params)

@register_tool(
    category="economic_data",
    service_class=FREDService,
    description="Get detailed information about a FRED data series"
)
def fred_get_series_info(
    self,
    series_id: str
) -> Dict[str, Any]:
    """
    Get metadata about a FRED series.

    Retrieves detailed information about a specific economic data series.

    Args:
        series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
    
    Returns:
        Dictionary with series metadata
    """
    # Get series info using the service
    return self.get_series_info(series_id)

@register_tool(
    category="economic_data",
    service_class=FREDService,
    description="Get information about a FRED data category"
)
def fred_get_category(
    self,
    category_id: int = 0
) -> Dict[str, Any]:
    """
    Get information about a FRED category.

    Retrieves details about a category of economic data series.

    Args:
        category_id: The FRED category ID (default: 0, which is the root category)
    
    Returns:
        Dictionary with category information
    """
    # Get category using the service
    return self.get_category(category_id)
