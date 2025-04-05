#!/usr/bin/env python3
"""
Tests for the World Bank API service.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import pandas as pd

from app.tools.worldbank.service import WorldBankService


class TestWorldBankService(unittest.TestCase):
    """Test cases for WorldBankService class"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = WorldBankService()
        self.service.initialized = True  # Skip initialization for unit tests

    def test_init(self):
        """Test service initialization"""
        service = WorldBankService()
        self.assertEqual(service.base_url, "https://api.worldbank.org/v2")
        self.assertFalse(service.initialized)
        self.assertIn("worldbank_api", service._rate_limiters)

    @patch('requests.get')
    def test_get_countries(self, mock_get):
        """Test getting countries list"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 2},
            [
                {"id": "USA", "name": "United States"},
                {"id": "CAN", "name": "Canada"}
            ]
        ]
        mock_get.return_value = mock_response

        # Call the service
        result = self.service.get_countries(limit=2)

        # Verify
        mock_get.assert_called_with(
            "https://api.worldbank.org/v2/country?format=json&per_page=2")
        self.assertEqual(len(result[1]), 2)
        self.assertEqual(result[1][0]["id"], "USA")

    @patch('requests.get')
    def test_get_indicators(self, mock_get):
        """Test getting indicators list"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 2},
            [
                {"id": "NY.GDP.MKTP.CD", "name": "GDP (current US$)"},
                {"id": "NY.GDP.PCAP.CD",
                    "name": "GDP per capita (current US$)"}
            ]
        ]
        mock_get.return_value = mock_response

        # Call the service
        result = self.service.get_indicators(limit=2)

        # Verify
        mock_get.assert_called_with(
            "https://api.worldbank.org/v2/indicator?format=json&per_page=2")
        self.assertEqual(len(result[1]), 2)
        self.assertEqual(result[1][0]["id"], "NY.GDP.MKTP.CD")

    @patch('requests.get')
    def test_get_indicator_for_country(self, mock_get):
        """Test getting indicator data for a country"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 2},
            [
                {"country": {"id": "USA"}, "value": 21433225000000, "date": "2019"},
                {"country": {"id": "USA"}, "value": 20611861000000, "date": "2018"}
            ]
        ]
        mock_get.return_value = mock_response

        # Call the service
        result = self.service.get_indicator_for_country(
            "USA", "NY.GDP.MKTP.CD", limit=2)

        # Verify
        mock_get.assert_called_with(
            "https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD?format=json&per_page=2"
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["country"]["id"], "USA")
        self.assertEqual(result[0]["value"], 21433225000000)

    @patch('requests.get')
    def test_get_indicator_metadata(self, mock_get):
        """Test getting indicator metadata"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 1000, "total": 1},
            [
                {
                    "id": "NY.GDP.MKTP.CD",
                    "name": "GDP (current US$)",
                    "sourceNote": "GDP at purchaser's prices is the sum of gross value added by all resident producers in the economy plus any product taxes and minus any subsidies not included in the value of the products.",
                    "source": {"id": "2", "value": "World Development Indicators"}
                }
            ]
        ]
        mock_get.return_value = mock_response

        # Call the service
        result = self.service.get_indicator_metadata("NY.GDP.MKTP.CD")

        # Verify
        mock_get.assert_called_with(
            "https://api.worldbank.org/v2/indicator/NY.GDP.MKTP.CD?format=json"
        )
        self.assertEqual(result["id"], "NY.GDP.MKTP.CD")
        self.assertEqual(result["name"], "GDP (current US$)")

    @patch('requests.get')
    def test_initialize_success(self, mock_get):
        """Test successful initialization"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1, "per_page": 1, "total": 1},
            [{"id": "USA", "name": "United States"}]
        ]
        mock_get.return_value = mock_response

        # Create new instance to test initialization
        service = WorldBankService()
        result = service.initialize()

        # Verify
        self.assertTrue(result)
        self.assertTrue(service.initialized)
        mock_get.assert_called_with(
            "https://api.worldbank.org/v2/country?format=json&per_page=1")

    @patch('requests.get')
    def test_initialize_failure(self, mock_get):
        """Test failed initialization"""
        # Setup mock to raise exception
        mock_get.side_effect = Exception("API error")

        # Create new instance to test initialization
        service = WorldBankService()
        result = service.initialize()

        # Verify
        self.assertFalse(result)
        self.assertFalse(service.initialized)

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        """Test error handling in API calls"""
        # Setup mock to raise exception
        mock_get.side_effect = Exception("API error")

        # Verify exceptions are properly raised
        with self.assertRaises(ValueError) as context:
            self.service.get_countries()
        self.assertIn("Failed to fetch countries", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.service.get_indicators()
        self.assertIn("Failed to fetch indicators", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.service.get_indicator_for_country("USA", "NY.GDP.MKTP.CD")
        self.assertIn("Failed to fetch indicator data", str(context.exception))


if __name__ == '__main__':
    unittest.main()
