"""
JSON formatter for DataViz service.

This module provides data formatting for JSON data sources.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class JsonFormatter:
    """Handler for JSON data sources."""
    
    def __init__(self, service):
        """
        Initialize with parent service reference.
        
        Args:
            service: The parent DataVizService instance
        """
        self.service = service
        self.pandas_formatter = None
        logger.debug("JsonFormatter initialized")
        
    def can_handle(self, data):
        """
        Check if this formatter can handle the data.
        
        Args:
            data: The data to be checked
            
        Returns:
            True if the data can be handled, False otherwise
        """
        # Check if it's a JSON string
        if isinstance(data, str):
            try:
                # Try to parse as JSON
                json_data = json.loads(data)
                return True
            except:
                # Check if it's a path to a JSON file
                ext = os.path.splitext(data)[1].lower()
                return ext == '.json'
        
        # Already parsed JSON (dict or list)
        if isinstance(data, (dict, list)):
            return True
            
        return False
    
    def process(self, data, x_column=None, y_columns=None):
        """
        Process the data into a standardized format for visualization.
        
        Args:
            data: The data to be processed
            x_column: The column to use for x-axis
            y_columns: List of columns to plot as y values
            
        Returns:
            Dictionary with processed data
        """
        logger.debug(f"Processing JSON data with x_column={x_column}, y_columns={y_columns}")
        
        # Parse JSON if needed
        parsed_data = self._parse_json(data)
        
        # Convert to DataFrame
        df = self._json_to_dataframe(parsed_data)
        
        # Once we have a DataFrame, delegate to PandasFormatter
        if self.pandas_formatter is None:
            # Import here to avoid circular imports
            from app.tools.dataviz.formatters.pandas_formatter import PandasFormatter
            self.pandas_formatter = PandasFormatter(self.service)
            
        # Process using PandasFormatter
        return self.pandas_formatter.process(df, x_column, y_columns)
    
    def _parse_json(self, data):
        """
        Parse JSON data if needed.
        
        Args:
            data: JSON data (string, file path, or already parsed)
            
        Returns:
            Parsed JSON data (dict or list)
        """
        if isinstance(data, str):
            try:
                # Try to parse as JSON string first
                return json.loads(data)
            except json.JSONDecodeError:
                # Try to load from file
                try:
                    if os.path.exists(data):
                        with open(data, 'r') as f:
                            return json.load(f)
                except Exception as e:
                    logger.error(f"Error loading JSON from file {data}: {e}")
                    raise ValueError(f"Failed to load JSON from file {data}: {e}")
                    
                # If both parsing as string and loading from file failed
                raise ValueError(f"Could not parse {data} as JSON")
        else:
            # Assume it's already parsed
            return data
    
    def _json_to_dataframe(self, data):
        """
        Convert JSON data to a pandas DataFrame.
        
        Args:
            data: Parsed JSON data (dict or list)
            
        Returns:
            pandas DataFrame
        """
        # Handle different JSON structures
        if isinstance(data, list):
            # List of dictionaries (records)
            if len(data) > 0 and isinstance(data[0], dict):
                return pd.DataFrame(data)
                
            # List of values
            return pd.DataFrame({'value': data})
            
        elif isinstance(data, dict):
            # Dict with arrays
            if any(isinstance(val, list) for val in data.values()):
                # Check if all arrays have the same length
                array_values = {k: v for k, v in data.items() if isinstance(v, list)}
                lengths = [len(v) for v in array_values.values()]
                
                if all(l == lengths[0] for l in lengths):
                    # Clean structure where each key is a column
                    return pd.DataFrame(array_values)
                else:
                    # Uneven arrays, try to handle as best we can
                    logger.warning("JSON has uneven array lengths, normalizing")
                    normalized = {k: pd.Series(v) for k, v in array_values.items()}
                    return pd.DataFrame(normalized)
            
            # Nested dictionaries
            if any(isinstance(val, dict) for val in data.values()):
                # Try to normalize nested structure
                try:
                    # This approach works for some nested structures
                    return pd.json_normalize(data)
                except Exception as e:
                    logger.warning(f"Could not normalize nested JSON: {e}")
                    
                    # Fallback: convert keys to series, values to another series
                    return pd.DataFrame({
                        'key': list(data.keys()),
                        'value': list(data.values())
                    })
            
            # Simple key-value pairs
            return pd.DataFrame({
                'key': list(data.keys()),
                'value': list(data.values())
            })
            
        else:
            raise ValueError(f"Unsupported JSON structure: {type(data)}")
