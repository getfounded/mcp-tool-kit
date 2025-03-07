#!/usr/bin/env python3
import requests
import pandas as pd
import logging

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("World Bank tools MCP reference set")


class WorldBankService:
    """Service to handle World Bank API operations"""

    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"

    def get_countries(self):
        """Get list of countries from World Bank API"""
        try:
            url = f"{self.base_url}/country?format=json&per_page=1000"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_indicators(self):
        """Get list of indicators from World Bank API"""
        try:
            url = f"{self.base_url}/indicator?format=json&per_page=50000"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_indicator_for_country(self, country_id, indicator_id):
        """Get values for an indicator for a specific country"""
        try:
            url = f"{self.base_url}/country/{country_id}/indicator/{indicator_id}?format=json&per_page=20000"
            response = requests.get(url)
            data = response.json()

            # Handle case where API returns error
            if not isinstance(data, list) or len(data) < 2:
                return {"error": "Invalid API response format"}

            indicator_values = data[1]
            return pd.json_normalize(indicator_values).to_csv()
        except Exception as e:
            return {"error": str(e)}

# Resource function definitions


def get_worldbank_countries():
    """Get list of countries from World Bank API"""
    wb_service = _get_worldbank_service()
    countries = wb_service.get_countries()

    if "error" in countries:
        return f"Error fetching countries: {countries['error']}"

    try:
        if isinstance(countries, list) and len(countries) >= 2:
            country_data = countries[1]
            return pd.json_normalize(country_data).to_csv()
        return "No country data available"
    except Exception as e:
        return f"Error processing country data: {str(e)}"


def get_worldbank_indicators():
    """Get list of indicators from World Bank API"""
    wb_service = _get_worldbank_service()
    indicators = wb_service.get_indicators()

    if "error" in indicators:
        return f"Error fetching indicators: {indicators['error']}"

    try:
        if isinstance(indicators, list) and len(indicators) >= 2:
            indicator_data = indicators[1]
            return pd.json_normalize(indicator_data).to_csv()
        return "No indicator data available"
    except Exception as e:
        return f"Error processing indicator data: {str(e)}"

# Tool function definitions that will be registered with MCP


async def worldbank_get_indicator(country_id: str, indicator_id: str, ctx: Context = None) -> str:
    """Get indicator data for a specific country from the World Bank API."""
    if not country_id:
        return "Error: country_id is required"

    if not indicator_id:
        return "Error: indicator_id is required"

    try:
        import httpx

        url = f"https://api.worldbank.org/v2/country/{country_id}/indicator/{indicator_id}?format=json&per_page=20000"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            # Handle non-200 responses
            if response.status_code != 200:
                return f"Error: API returned status code {response.status_code}: {response.text}"

            data = response.json()

            # Check data structure
            if not isinstance(data, list) or len(data) < 2:
                return f"Error: Unexpected API response format: {data}"

            # Get the actual data records
            indicator_values = data[1]

            # If no data was returned
            if not indicator_values:
                return "No data available for the specified country and indicator"

            # Convert to CSV
            csv_data = pd.json_normalize(indicator_values).to_csv()
            return csv_data

    except Exception as e:
        return f"Error processing request: {str(e)}"

# Tool registration and initialization
_worldbank_service = None


def initialize_worldbank_service():
    """Initialize the World Bank service"""
    global _worldbank_service
    _worldbank_service = WorldBankService()
    return _worldbank_service


def _get_worldbank_service():
    """Get or initialize the World Bank service"""
    global _worldbank_service
    if _worldbank_service is None:
        _worldbank_service = initialize_worldbank_service()
    return _worldbank_service


def get_worldbank_tools():
    """Get a dictionary of all World Bank tools for registration with MCP"""
    return {
        "worldbank_get_indicator": worldbank_get_indicator
    }


def get_worldbank_resources():
    """Get a dictionary of all World Bank resources for registration with MCP"""
    return {
        "worldbank://countries": get_worldbank_countries,
        "worldbank://indicators": get_worldbank_indicators
    }
