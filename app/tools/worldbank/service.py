#!/usr/bin/env python3
"""
World Bank API service implementation for MCP toolkit.
"""
import logging
import requests
import pandas as pd
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase


class WorldBankService(ToolServiceBase):
    """Service to handle World Bank API operations"""

    def __init__(self):
        """Initialize the World Bank service"""
        super().__init__()
        self.base_url = "https://api.worldbank.org/v2"
        # Initialize rate limiter (10 calls per second is generous,
        # but World Bank API doesn't specify exact limits)
        self.create_rate_limiter("worldbank_api", 10, 1.0)

    def initialize(self) -> bool:
        """
        Initialize the service by testing API connectivity.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Test API connectivity with a simple request
            self.get_countries(limit=1)
            self.initialized = True
            self.logger.info("World Bank service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize World Bank service: {e}")
            return False

    def get_countries(self, limit: int = 1000) -> Dict:
        """
        Get list of countries from World Bank API.

        Args:
            limit: Maximum number of countries to return

        Returns:
            Dict containing country data

        Raises:
            ValueError: If API request fails
        """
        self._is_initialized()

        # Apply rate limiting
        self.apply_rate_limit("worldbank_api", 10, 1.0)

        try:
            url = f"{self.base_url}/country?format=json&per_page={limit}"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching countries: {e}")
            raise ValueError(f"Failed to fetch countries: {e}")

    def get_indicators(self, limit: int = 1000) -> Dict:
        """
        Get list of indicators from World Bank API.

        Args:
            limit: Maximum number of indicators to return

        Returns:
            Dict containing indicator data

        Raises:
            ValueError: If API request fails
        """
        self._is_initialized()

        # Apply rate limiting
        self.apply_rate_limit("worldbank_api", 10, 1.0)

        try:
            url = f"{self.base_url}/indicator?format=json&per_page={limit}"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching indicators: {e}")
            raise ValueError(f"Failed to fetch indicators: {e}")

    def get_indicator_for_country(self, country_id: str, indicator_id: str, limit: int = 20000) -> List[Dict]:
        """
        Get values for an indicator for a specific country.

        Args:
            country_id: The country identifier (ISO code or ID)
            indicator_id: The indicator code
            limit: Maximum number of data points to return

        Returns:
            List of indicator values

        Raises:
            ValueError: If API request fails or returns invalid data
        """
        self._is_initialized()

        # Apply rate limiting
        self.apply_rate_limit("worldbank_api", 10, 1.0)

        try:
            url = f"{self.base_url}/country/{country_id}/indicator/{indicator_id}?format=json&per_page={limit}"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()

            # Handle case where API returns error
            if not isinstance(data, list) or len(data) < 2:
                raise ValueError("Invalid API response format")

            # Return the actual data records
            return data[1]
        except Exception as e:
            self.logger.error(f"Error fetching indicator data: {e}")
            raise ValueError(f"Failed to fetch indicator data: {e}")

    def get_indicator_metadata(self, indicator_id: str) -> Dict:
        """
        Get metadata for a specific indicator.

        Args:
            indicator_id: The indicator code

        Returns:
            Dict containing indicator metadata

        Raises:
            ValueError: If API request fails
        """
        self._is_initialized()

        # Apply rate limiting
        self.apply_rate_limit("worldbank_api", 10, 1.0)

        try:
            url = f"{self.base_url}/indicator/{indicator_id}?format=json"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()

            # Handle case where API returns error
            if not isinstance(data, list) or len(data) < 2 or not data[1]:
                raise ValueError(
                    "Invalid API response format or indicator not found")

            # Return the indicator metadata (first item in data array)
            return data[1][0]
        except Exception as e:
            self.logger.error(f"Error fetching indicator metadata: {e}")
            raise ValueError(f"Failed to fetch indicator metadata: {e}")
