"""
Pandas formatter for DataViz service.

This module provides data formatting for pandas DataFrames.
"""

import os
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class PandasFormatter:
    """Handler for pandas DataFrame data sources."""
    
    def __init__(self, service):
        """
        Initialize with parent service reference.
        
        Args:
            service: The parent DataVizService instance
        """
        self.service = service
        logger.debug("PandasFormatter initialized")
    
    def can_handle(self, data):
        """
        Check if this formatter can handle the data.
        
        Args:
            data: The data to be checked
            
        Returns:
            True if the data can be handled, False otherwise
        """
        # Check for DataFrame
        if isinstance(data, pd.DataFrame):
            return True
            
        # Check for file paths
        if isinstance(data, str):
            ext = os.path.splitext(data)[1].lower()
            return ext in ['.csv', '.xlsx', '.xls', '.json', '.parquet']
            
        # Check for dict-like data
        if isinstance(data, dict) and len(data) > 0:
            # Check if it has data-like structure
            if isinstance(list(data.values())[0], (list, np.ndarray, pd.Series)):
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
        logger.debug(f"Processing data with x_column={x_column}, y_columns={y_columns}")
        
        try:
            # Convert data to DataFrame if needed
            df = self._ensure_dataframe(data)
            
            # Auto-detect columns if not specified
            if x_column is None:
                x_column = self._suggest_x_column(df)
                logger.debug(f"Auto-detected x_column: {x_column}")
            
            if y_columns is None:
                y_columns = self._suggest_y_columns(df, x_column)
                logger.debug(f"Auto-detected y_columns: {y_columns}")
                
            # Validate columns
            if x_column not in df.columns:
                raise ValueError(f"Column '{x_column}' not found in data")
            
            for col in y_columns:
                if col not in df.columns:
                    raise ValueError(f"Column '{col}' not found in data")
                    
            # Handle time series data specially
            if pd.api.types.is_datetime64_any_dtype(df[x_column]):
                df = self._prepare_timeseries(df, x_column)
                
            # Detect data type for visualization suggestions
            data_type = self._detect_data_type(df, x_column, y_columns)
            
            return {
                'data': df,
                'x_column': x_column,
                'y_columns': y_columns,
                'data_type': data_type
            }
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise ValueError(f"Failed to process data: {e}")
    
    def _ensure_dataframe(self, data):
        """
        Convert input to DataFrame if needed.
        
        Args:
            data: Input data (DataFrame, path, dict, etc.)
            
        Returns:
            pandas DataFrame
        """
        if isinstance(data, pd.DataFrame):
            return data
            
        elif isinstance(data, str):
            # Handle file path
            ext = os.path.splitext(data)[1].lower()
            
            try:
                if ext == '.csv':
                    return pd.read_csv(data)
                elif ext in ['.xlsx', '.xls']:
                    return pd.read_excel(data)
                elif ext == '.json':
                    return pd.read_json(data)
                elif ext == '.parquet':
                    return pd.read_parquet(data)
                else:
                    raise ValueError(f"Unsupported file extension: {ext}")
            except Exception as e:
                logger.error(f"Error reading file {data}: {e}")
                raise ValueError(f"Failed to read file {data}: {e}")
                
        elif isinstance(data, dict):
            # Convert dictionary to DataFrame
            try:
                return pd.DataFrame(data)
            except Exception as e:
                logger.error(f"Error converting dict to DataFrame: {e}")
                raise ValueError(f"Failed to convert dict to DataFrame: {e}")
                
        elif isinstance(data, (list, tuple)) and len(data) > 0 and isinstance(data[0], dict):
            # Convert list of dictionaries to DataFrame
            try:
                return pd.DataFrame(data)
            except Exception as e:
                logger.error(f"Error converting list to DataFrame: {e}")
                raise ValueError(f"Failed to convert list to DataFrame: {e}")
                
        else:
            raise ValueError(f"Cannot convert data of type {type(data)} to DataFrame")
    
    def _suggest_x_column(self, df):
        """
        Intelligently suggest an x-axis column.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Name of suggested x-axis column
        """
        # Look for date/datetime columns first
        date_cols = df.select_dtypes(include=['datetime64', 'datetime']).columns
        if len(date_cols) > 0:
            return date_cols[0]
            
        # Look for columns with 'date' or 'time' in the name
        date_name_cols = [col for col in df.columns 
                         if any(term in col.lower() for term in ['date', 'time', 'day', 'year'])]
        if date_name_cols:
            # Try to convert to datetime
            for col in date_name_cols:
                try:
                    pd.to_datetime(df[col])
                    return col
                except:
                    continue
            
            # If conversion failed, still use the first date-like column
            return date_name_cols[0]
            
        # Look for common index columns
        index_cols = [col for col in df.columns 
                    if any(term == col.lower() for term in ['id', 'index', 'key', 'name'])]
        if index_cols:
            return index_cols[0]
            
        # Look for categorical or string columns
        cat_cols = df.select_dtypes(include=['category', 'object']).columns
        if len(cat_cols) > 0:
            # Prefer columns with fewer unique values
            n_unique = {col: df[col].nunique() for col in cat_cols}
            sorted_cols = sorted(n_unique.items(), key=lambda x: x[1])
            if sorted_cols and sorted_cols[0][1] < len(df) * 0.5:  # Only if reasonably small number of categories
                return sorted_cols[0][0]
                
        # Default to first column
        return df.columns[0]
    
    def _suggest_y_columns(self, df, x_column):
        """
        Intelligently suggest columns for y-axis values.
        
        Args:
            df: Input DataFrame
            x_column: X-axis column name
            
        Returns:
            List of suggested y-axis column names
        """
        # Get numeric columns except the x_column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != x_column]
        
        if not numeric_cols:
            # If no numeric columns, look for columns that might be convertible
            for col in df.columns:
                if col != x_column:
                    try:
                        pd.to_numeric(df[col])
                        numeric_cols.append(col)
                    except:
                        pass
        
        # If still no numeric columns, raise error
        if not numeric_cols:
            raise ValueError("No numeric columns found for y-axis")
            
        # If too many columns, limit to a reasonable number
        if len(numeric_cols) > 5:
            # Look for columns with names indicating values
            value_cols = [col for col in numeric_cols 
                         if any(term in col.lower() for term in 
                              ['value', 'amount', 'price', 'rate', 'count', 'total', 'sum', 'avg'])]
            
            # If we found value columns, use those
            if value_cols:
                return value_cols[:5]  # Limit to first 5
                
            # Otherwise, use the first 3 numeric columns
            return numeric_cols[:3]
        
        return numeric_cols
    
    def _detect_data_type(self, df, x_column, y_columns):
        """
        Detect the type of data to determine appropriate visualizations.
        
        Args:
            df: Input DataFrame
            x_column: X-axis column name
            y_columns: List of y-axis column names
            
        Returns:
            String describing the data type
        """
        # Detect time series
        if pd.api.types.is_datetime64_any_dtype(df[x_column]):
            return 'time_series'
            
        # Detect categorical x-axis
        if pd.api.types.is_categorical_dtype(df[x_column]) or pd.api.types.is_object_dtype(df[x_column]):
            n_unique = df[x_column].nunique()
            if n_unique < 50:  # Reasonable number of categories
                return 'categorical'
                
        # Detect numeric x and y (scatter-like data)
        if pd.api.types.is_numeric_dtype(df[x_column]) and all(pd.api.types.is_numeric_dtype(df[col]) for col in y_columns):
            return 'numeric'
            
        # Default to general
        return 'general'
    
    def _prepare_timeseries(self, df, time_column):
        """
        Special handling for time series data.
        
        Args:
            df: Input DataFrame
            time_column: Time/date column name
            
        Returns:
            Processed DataFrame
        """
        # Make sure time column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
            try:
                df[time_column] = pd.to_datetime(df[time_column])
            except Exception as e:
                logger.warning(f"Could not convert {time_column} to datetime: {e}")
                return df
        
        # Sort by time
        df = df.sort_values(time_column)
        
        # Check for duplicate times
        if df[time_column].duplicated().any():
            logger.warning(f"Duplicate timestamps found in {time_column}")
            
        # Reset index for consistency
        return df.reset_index(drop=True)
