#!/usr/bin/env python3
"""
Tests for the FRED API tools.
"""
import os
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import json

from app.tools.base.registry import get_all_tools, clear_registry
from app.tools.fred.fred_service import FREDService
from app.tools.fred.fred_tools import fred_get_series, fred_search, fred_get_series_info, fred_get_category

class TestFREDTools(unittest.TestCase):
    """Test case for FRED API tools."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Set up mock environment variables
        os.environ["FRED_API_KEY"] = "test_api_key"
        
        # Initialize service
        cls.service = FREDService()
        
        # Mock the Fred client
        cls.mock_client = MagicMock()
        cls.service.client = cls.mock_client
        cls.service.initialized = True
        
        # Set up rate limiter
        cls.service.create_rate_limiter("fred_api", calls=10, period=5.0)
    
    def test_fred_get_series(self):
        """Test fred_get_series function."""
        # Create mock data
        mock_series = pd.Series([1.0, 2.0, 3.0], index=pd.date_range(start='2020-01-01', periods=3))
        mock_series_info = {"title": "Test Series"}
        
        # Configure mocks
        self.mock_client.get_series.return_value = mock_series
        self.mock_client.get_series_info.return_value = mock_series_info
        
        # Call the function
        result = fred_get_series(self.service, "TEST")
        
        # Check the result
        self.assertEqual(result["series_id"], "TEST")
        self.assertEqual(result["title"], "Test Series")
        self.assertEqual(len(result["data"]), 3)
        
        # Verify mocks called
        self.mock_client.get_series.assert_called_once_with("TEST")
    
    def test_fred_search(self):
        """Test fred_search function."""
        # Create mock data
        mock_df = pd.DataFrame({
            'id': ['TEST1', 'TEST2'],
            'title': ['Test Series 1', 'Test Series 2']
        })
        
        # Configure mocks
        self.mock_client.search.return_value = mock_df
        
        # Call the function
        result = fred_search(self.service, "test")
        
        # Check the result
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["id"], "TEST1")
        
        # Verify mocks called
        self.mock_client.search.assert_called_once_with(
            "test", limit=10, order_by='search_rank', sort_order='desc'
        )
    
    def test_fred_get_series_info(self):
        """Test fred_get_series_info function."""
        # Create mock data
        mock_info = {"id": "TEST", "title": "Test Series", "units": "Percent"}
        
        # Configure mocks
        self.mock_client.get_series_info.return_value = mock_info
        
        # Call the function
        result = fred_get_series_info(self.service, "TEST")
        
        # Check the result
        self.assertEqual(result["id"], "TEST")
        self.assertEqual(result["title"], "Test Series")
        
        # Verify mocks called
        self.mock_client.get_series_info.assert_called_once_with("TEST")
    
    def test_fred_get_category(self):
        """Test fred_get_category function."""
        # Create mock data
        mock_category = {"id": 0, "name": "Root", "parent_id": None, "children": [1, 2, 3]}
        
        # Configure mocks
        self.mock_client.get_category.return_value = mock_category
        
        # Call the function
        result = fred_get_category(self.service)
        
        # Check the result
        self.assertEqual(result["id"], 0)
        self.assertEqual(result["name"], "Root")
        
        # Verify mocks called
        self.mock_client.get_category.assert_called_once_with(0)

if __name__ == "__main__":
    unittest.main()
