#!/usr/bin/env python3
"""
Tests for the World Bank API tools.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import pandas as pd

from app.tools.base.registry import clear_registry, get_all_tools
from app.tools.worldbank.service import WorldBankService
from app.tools.worldbank.tools import (
    get_indicator,
    get_countries,
    get_indicators,
    get_indicator_metadata,
    search_indicators
)


class TestWorldBankTools(unittest.TestCase):
    """Test cases for World Bank tools"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = WorldBankService()
        self.service.initialized = True  # Skip initialization for unit tests

    def tearDown(self):
        """Clean up after tests"""
        clear_registry()

    def test_tool_registration(self):
        """Test that tools are properly registered"""
        # Get all registered tools
        tools = get_all_tools()

        # Check that our tools are registered
        self.assertIn("worldbank_get_indicator", tools)
        self.assertIn("worldbank_get_countries", tools)
        self.assertIn("worldbank_get_indicators", tools)
        self.assertIn("worldbank_get_indicator_metadata", tools)
        self.assertIn("worldbank_search_indicators", tools)

        # Check tool metadata
        indicator_tool = tools["worldbank_get_indicator"]
        self.assertEqual(indicator_tool["category"], "world_bank")
        self.assertEqual(indicator_tool["service_class"], WorldBankService)
        self.assertIn("indicator data", indicator_tool["description"].lower())

    def test_get_indicator_validation(self):
        """Test parameter validation for get_indicator"""
        # Test with missing country_id
        with self.assertRaises(ValueError) as context:
            get_indicator(self.service, "", "NY.GDP.MKTP.CD")
        self.assertIn("country_id is required", str(context.exception))

        # Test with missing indicator_id
        with self.assertRaises(ValueError) as context:
            get_indicator(self.service, "USA", "")
        self.assertIn("indicator_id is required", str(context.exception))

    @patch.object(WorldBankService, 'get_indicator_for_country')
    def test_get_indicator(self, mock_get_indicator):
        """Test get_indicator tool"""
        # Setup mock response
        mock_get_indicator.return_value = [
            {"country": {"id": "USA"}, "value": 21433225000000, "date": "2019"},
            {"country": {"id": "USA"}, "value": 20611861000000, "date": "2018"}
        ]

        # Call the tool
        result = get_indicator(self.service, "USA", "NY.GDP.MKTP.CD")

        # Verify
        mock_get_indicator.assert_called_with("USA", "NY.GDP.MKTP.CD")
        self.assertIsInstance(result, str)
        # Check that CSV contains expected data
        self.assertIn("USA", result)
        self.assertIn("21433225000000", result)

    @patch.object(WorldBankService, 'get_countries')
    def test_get_countries(self, mock_get_countries):
        """Test get_countries tool"""
        # Setup mock response
        mock_get_countries.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 2},
            [
                {"id": "USA", "name": "United States"},
                {"id": "CAN", "name": "Canada"}
            ]
        ]

        # Call the tool
        result = get_countries(self.service)

        # Verify
        mock_get_countries.assert_called_once()
        self.assertIsInstance(result, str)
        # Check that CSV contains expected data
        self.assertIn("USA", result)
        self.assertIn("United States", result)
        self.assertIn("CAN", result)
        self.assertIn("Canada", result)

    @patch.object(WorldBankService, 'get_indicators')
    def test_get_indicators(self, mock_get_indicators):
        """Test get_indicators tool"""
        # Setup mock response
        mock_get_indicators.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 2},
            [
                {"id": "NY.GDP.MKTP.CD", "name": "GDP (current US$)"},
                {"id": "NY.GDP.PCAP.CD",
                    "name": "GDP per capita (current US$)"}
            ]
        ]

        # Call the tool
        result = get_indicators(self.service)

        # Verify
        mock_get_indicators.assert_called_once()
        self.assertIsInstance(result, str)
        # Check that CSV contains expected data
        self.assertIn("NY.GDP.MKTP.CD", result)
        self.assertIn("GDP (current US$)", result)

    @patch.object(WorldBankService, 'get_indicator_metadata')
    def test_get_indicator_metadata(self, mock_get_metadata):
        """Test get_indicator_metadata tool"""
        # Setup mock response
        mock_metadata = {
            "id": "NY.GDP.MKTP.CD",
            "name": "GDP (current US$)",
            "sourceNote": "GDP at purchaser's prices...",
            "source": {"id": "2", "value": "World Development Indicators"}
        }
        mock_get_metadata.return_value = mock_metadata

        # Call the tool
        result = get_indicator_metadata(self.service, "NY.GDP.MKTP.CD")

        # Verify
        mock_get_metadata.assert_called_with("NY.GDP.MKTP.CD")
        self.assertIsInstance(result, str)
        # Parse the JSON result
        parsed_result = json.loads(result)
        self.assertEqual(parsed_result["id"], "NY.GDP.MKTP.CD")
        self.assertEqual(parsed_result["name"], "GDP (current US$)")

    @patch.object(WorldBankService, 'get_indicators')
    def test_search_indicators(self, mock_get_indicators):
        """Test search_indicators tool"""
        # Setup mock response with indicators
        indicators = [
            {"id": "NY.GDP.MKTP.CD",
                "name": "GDP (current US$)", "sourceNote": "GDP measures..."},
            {"id": "NY.GDP.PCAP.CD",
                "name": "GDP per capita (current US$)", "sourceNote": "Per capita GDP..."},
            {"id": "FP.CPI.TOTL.ZG",
                "name": "Inflation, consumer prices (annual %)", "sourceNote": "Inflation..."}
        ]
        mock_get_indicators.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 3},
            indicators
        ]

        # Call the tool with search query "gdp"
        result = search_indicators(self.service, "gdp")

        # Verify
        mock_get_indicators.assert_called_once()
        self.assertIsInstance(result, str)
        # Check that only GDP indicators are included
        self.assertIn("NY.GDP.MKTP.CD", result)
        self.assertIn("NY.GDP.PCAP.CD", result)
        self.assertNotIn("FP.CPI.TOTL.ZG", result)

        # Test with no results
        result = search_indicators(self.service, "xyz123")
        self.assertIn("No indicators found", result)


if __name__ == '__main__':
    unittest.main()
