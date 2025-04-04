#!/usr/bin/env python3
"""
Service implementation for FRED (Federal Reserve Economic Data) API.
"""
import os
import logging
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase

class FREDAPIService(ToolServiceBase):
    """Service to handle FRED API operations"""

    def __init__(self, api_key=None):
        """
        Initialize the FRED API service.
        
        Args:
            api_key: Optional API key (will use environment variable if not provided)
        """
        super().__init__()
        self.api_key = api_key or self.get_env_var("FRED_API_KEY")
        self.client = None
    
    def initialize(self) -> bool:
        """
        Initialize the FRED API client.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            from fredapi import Fred
            self.client = Fred(api_key=self.api_key)
            self.initialized = True
            self.logger.info("FRED API client initialized successfully")
            return True
        except ImportError:
            self.logger.error(
                "fredapi module not installed. Please install it with 'pip install fredapi'")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize FRED API client: {str(e)}")
            return False

    def get_series(self, series_id, **kwargs):
        """
        Get data for a FRED series.
        
        Args:
            series_id: The FRED series ID
            **kwargs: Additional parameters for the FRED API
            
        Returns:
            Dictionary with series data
        """
        try:
            self._is_initialized()
            data = self.client.get_series(series_id, **kwargs)
            return self._format_series_data(data, series_id)
        except Exception as e:
            return {"error": str(e)}

    def search(self, search_text, **kwargs):
        """
        Search for FRED series.
        
        Args:
            search_text: Text to search for
            **kwargs: Additional parameters for the FRED API
            
        Returns:
            Dictionary with search results
        """
        try:
            self._is_initialized()
            data = self.client.search(search_text, **kwargs)
            return self._format_search_results(data)
        except Exception as e:
            return {"error": str(e)}

    def get_series_info(self, series_id):
        """
        Get metadata about a FRED series.
        
        Args:
            series_id: The FRED series ID
            
        Returns:
            Dictionary with series information
        """
        try:
            self._is_initialized()
            info = self.client.get_series_info(series_id)
            return self._format_series_info(info)
        except Exception as e:
            return {"error": str(e)}

    def get_category(self, category_id=0):
        """
        Get information about a FRED category.
        
        Args:
            category_id: The FRED category ID
            
        Returns:
            Dictionary with category information
        """
        try:
            self._is_initialized()
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

    def _format_category(self, category):
        """Format category info for JSON serialization"""
        if isinstance(category, dict):
            return category
        return {"error": "Unexpected data format returned from FRED API"}


# Singleton instance
_service_instance = None

def get_service() -> FREDAPIService:
    """
    Get or initialize the FRED API service singleton.
    
    Returns:
        FREDAPIService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = FREDAPIService()
        _service_instance.initialize()
    return _service_instance