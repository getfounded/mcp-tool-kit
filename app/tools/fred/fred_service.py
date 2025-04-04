#!/usr/bin/env python3
"""
FRED (Federal Reserve Economic Data) API service.
"""
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase

class FREDService(ToolServiceBase):
    """Service to handle FRED API operations"""

    def __init__(self):
        """Initialize the FRED service."""
        super().__init__()
        self.client = None
        self.api_key = None
    
    def initialize(self) -> bool:
        """
        Initialize the FRED service with API key.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        # Get API key from environment
        self.api_key = self.get_env_var("FRED_API_KEY", required=True)
        
        try:
            # Import the fredapi module
            from fredapi import Fred
            
            # Initialize the client
            self.client = Fred(api_key=self.api_key)
            
            # Set up rate limiting (10 calls per 5 seconds)
            self.create_rate_limiter("fred_api", calls=10, period=5.0)
            
            self.logger.info("FRED API client initialized successfully")
            self.initialized = True
            return True
        except ImportError:
            self.logger.error(
                "fredapi module not installed. Please install it with 'pip install fredapi'")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize FRED API client: {e}")
            return False
    
    def get_series(self, series_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get data for a FRED series.
        
        Args:
            series_id: The FRED series ID
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with series data
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("fred_api", calls=10, period=5.0)
        
        try:
            data = self.client.get_series(series_id, **kwargs)
            return self._format_series_data(data, series_id)
        except Exception as e:
            self.logger.error(f"FRED API error: {e}")
            return {"error": str(e)}

    def search(self, search_text: str, **kwargs) -> Dict[str, Any]:
        """
        Search for FRED series.
        
        Args:
            search_text: Text to search for
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Dictionary with search results
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("fred_api", calls=10, period=5.0)
        
        try:
            data = self.client.search(search_text, **kwargs)
            return self._format_search_results(data)
        except Exception as e:
            self.logger.error(f"FRED API error: {e}")
            return {"error": str(e)}

    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """
        Get metadata about a FRED series.
        
        Args:
            series_id: The FRED series ID
            
        Returns:
            Dictionary with series metadata
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("fred_api", calls=10, period=5.0)
        
        try:
            info = self.client.get_series_info(series_id)
            return self._format_series_info(info)
        except Exception as e:
            self.logger.error(f"FRED API error: {e}")
            return {"error": str(e)}

    def get_category(self, category_id: int = 0) -> Dict[str, Any]:
        """
        Get information about a FRED category.
        
        Args:
            category_id: The FRED category ID
            
        Returns:
            Dictionary with category information
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("fred_api", calls=10, period=5.0)
        
        try:
            category = self.client.get_category(category_id)
            return self._format_category(category)
        except Exception as e:
            self.logger.error(f"FRED API error: {e}")
            return {"error": str(e)}

    def _format_series_data(self, data: pd.Series, series_id: str) -> Dict[str, Any]:
        """
        Format pandas Series data into a dict for JSON serialization.
        
        Args:
            data: Series data from FRED API
            series_id: The FRED series ID
            
        Returns:
            Formatted dictionary
        """
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
                series_info = self.get_series_info(series_id)
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

    def _format_search_results(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Format search results from DataFrame to dict.
        
        Args:
            data: DataFrame from FRED API
            
        Returns:
            Formatted dictionary
        """
        if isinstance(data, pd.DataFrame):
            results = data.to_dict(orient='records')
            return {
                "results": results,
                "count": len(results)
            }
            
        return {"error": "Unexpected data format returned from FRED API"}

    def _format_series_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format series info for JSON serialization.
        
        Args:
            info: Series info from FRED API
            
        Returns:
            Formatted dictionary
        """
        if isinstance(info, dict):
            return info
            
        return {"error": "Unexpected data format returned from FRED API"}

    def _format_category(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format category info for JSON serialization.
        
        Args:
            category: Category info from FRED API
            
        Returns:
            Formatted dictionary
        """
        if isinstance(category, dict):
            return category
            
        return {"error": "Unexpected data format returned from FRED API"}
