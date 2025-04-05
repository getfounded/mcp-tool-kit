#!/usr/bin/env python3
"""
World Bank API tools implementations.
"""
import pandas as pd
from typing import Optional, Dict, Any, List

from app.tools.base.registry import register_tool
from .service import WorldBankService


@register_tool(
    name="worldbank_get_indicator",
    category="world_bank",
    service_class=WorldBankService,
    description="Get indicator data for a specific country from the World Bank API"
)
def get_indicator(self, country_id: str, indicator_id: str) -> str:
    """
    Get indicator data for a specific country from the World Bank API.

    Args:
        country_id: The 3-letter ISO 3166-1 code or numeric code of the country
        indicator_id: The indicator code (e.g., 'NY.GDP.MKTP.CD' for GDP)

    Returns:
        CSV data containing the indicator values
    """
    if not country_id:
        raise ValueError("country_id is required")

    if not indicator_id:
        raise ValueError("indicator_id is required")

    try:
        # Get data from service
        indicator_values = self.get_indicator_for_country(
            country_id, indicator_id)

        # If no data was returned
        if not indicator_values:
            return "No data available for the specified country and indicator"

        # Convert to CSV
        csv_data = pd.json_normalize(indicator_values).to_csv()
        return csv_data
    except Exception as e:
        return f"Error processing request: {str(e)}"


@register_tool(
    name="worldbank_get_countries",
    category="world_bank",
    service_class=WorldBankService,
    description="Get a list of countries from the World Bank API"
)
def get_countries(self) -> str:
    """
    Get a list of countries from the World Bank API.

    Returns:
        CSV data containing country information
    """
    try:
        countries = self.get_countries()

        if isinstance(countries, list) and len(countries) >= 2:
            country_data = countries[1]
            return pd.json_normalize(country_data).to_csv()
        return "No country data available"
    except Exception as e:
        return f"Error fetching countries: {str(e)}"


@register_tool(
    name="worldbank_get_indicators",
    category="world_bank",
    service_class=WorldBankService,
    description="Get a list of indicators from the World Bank API"
)
def get_indicators(self) -> str:
    """
    Get a list of indicators from the World Bank API.

    Returns:
        CSV data containing indicator information
    """
    try:
        indicators = self.get_indicators()

        if isinstance(indicators, list) and len(indicators) >= 2:
            indicator_data = indicators[1]
            return pd.json_normalize(indicator_data).to_csv()
        return "No indicator data available"
    except Exception as e:
        return f"Error fetching indicators: {str(e)}"


@register_tool(
    name="worldbank_get_indicator_metadata",
    category="world_bank",
    service_class=WorldBankService,
    description="Get metadata for a specific indicator from the World Bank API"
)
def get_indicator_metadata(self, indicator_id: str) -> str:
    """
    Get metadata for a specific indicator from the World Bank API.

    Args:
        indicator_id: The indicator code (e.g., 'NY.GDP.MKTP.CD' for GDP)

    Returns:
        JSON data containing indicator metadata
    """
    if not indicator_id:
        raise ValueError("indicator_id is required")

    try:
        # Get metadata from service
        metadata = self.get_indicator_metadata(indicator_id)

        # Convert to JSON string
        import json
        return json.dumps(metadata, indent=2)
    except Exception as e:
        return f"Error fetching indicator metadata: {str(e)}"


@register_tool(
    name="worldbank_search_indicators",
    category="world_bank",
    service_class=WorldBankService,
    description="Search for indicators by keyword from the World Bank API"
)
def search_indicators(self, query: str) -> str:
    """
    Search for indicators by keyword from the World Bank API.

    Args:
        query: Search query for indicators

    Returns:
        CSV data containing matching indicator information
    """
    if not query:
        raise ValueError("query is required")

    try:
        # Get all indicators
        indicators = self.get_indicators()

        if not isinstance(indicators, list) or len(indicators) < 2:
            return "No indicator data available"

        indicator_data = indicators[1]

        # Filter indicators by query
        query = query.lower()
        matching_indicators = [
            indicator for indicator in indicator_data
            if query in indicator.get('name', '').lower() or
            query in indicator.get('id', '').lower() or
            query in indicator.get('sourceNote', '').lower()
        ]

        # If no matches found
        if not matching_indicators:
            return "No indicators found matching the query"

        # Convert to CSV
        return pd.json_normalize(matching_indicators).to_csv()
    except Exception as e:
        return f"Error searching indicators: {str(e)}"
