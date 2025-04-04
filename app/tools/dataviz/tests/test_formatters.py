"""
Unit tests for DataViz formatters.

This module contains tests for the data formatters.
"""

import os
import json
import unittest
import pandas as pd
import numpy as np
import tempfile
from unittest.mock import MagicMock, patch

# Import formatters for testing
try:
    from app.tools.dataviz.formatters.pandas_formatter import PandasFormatter
    PANDAS_FORMATTER_AVAILABLE = True
except ImportError:
    PANDAS_FORMATTER_AVAILABLE = False

try:
    from app.tools.dataviz.formatters.json_formatter import JsonFormatter
    JSON_FORMATTER_AVAILABLE = True
except ImportError:
    JSON_FORMATTER_AVAILABLE = False


@unittest.skipIf(not PANDAS_FORMATTER_AVAILABLE, "PandasFormatter not available")
class TestPandasFormatter(unittest.TestCase):
    """Test cases for PandasFormatter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock service
        self.mock_service = MagicMock()
        
        # Create formatter
        self.formatter = PandasFormatter(self.mock_service)
        
        # Create test data
        self.test_df = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
            'Revenue': [100, 120, 140, 160, 180, 200, 210, 205, 215, 230, 240, 250],
            'Expenses': [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135],
            'Profit': [20, 35, 50, 65, 80, 95, 100, 90, 95, 105, 110, 115],
            'Category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })
    
    def test_can_handle(self):
        """Test data type recognition."""
        # Test with DataFrame
        self.assertTrue(self.formatter.can_handle(self.test_df))
        
        # Test with file paths
        self.assertTrue(self.formatter.can_handle('data.csv'))
        self.assertTrue(self.formatter.can_handle('data.xlsx'))
        self.assertTrue(self.formatter.can_handle('data.json'))
        
        # Test with dict
        test_dict = {
            'Revenue': [100, 120, 140],
            'Expenses': [80, 85, 90]
        }
        self.assertTrue(self.formatter.can_handle(test_dict))
        
        # Test with invalid data
        self.assertFalse(self.formatter.can_handle("invalid string"))
        self.assertFalse(self.formatter.can_handle(123))
    
    def test_ensure_dataframe(self):
        """Test conversion to DataFrame."""
        # Test with DataFrame
        df = self.formatter._ensure_dataframe(self.test_df)
        self.assertIs(df, self.test_df)
        
        # Test with dict
        test_dict = {
            'Revenue': [100, 120, 140],
            'Expenses': [80, 85, 90]
        }
        df = self.formatter._ensure_dataframe(test_dict)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 2))
        
        # Test with list of dicts
        test_list = [
            {'Revenue': 100, 'Expenses': 80},
            {'Revenue': 120, 'Expenses': 85},
            {'Revenue': 140, 'Expenses': 90}
        ]
        df = self.formatter._ensure_dataframe(test_list)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 2))
        
        # Test with invalid data
        with self.assertRaises(ValueError):
            self.formatter._ensure_dataframe("invalid string")
    
    def test_suggest_x_column(self):
        """Test X column suggestion."""
        # Test with datetime index
        x_col = self.formatter._suggest_x_column(self.test_df)
        self.assertEqual(x_col, 'Date')
        
        # Test with categorical data
        df = pd.DataFrame({
            'ID': range(1, 11),
            'Category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
            'Value': np.random.rand(10) * 100
        })
        x_col = self.formatter._suggest_x_column(df)
        self.assertEqual(x_col, 'Category')
        
        # Test with only numeric data
        df = pd.DataFrame({
            'X': range(1, 11),
            'Y': np.random.rand(10) * 100,
            'Z': np.random.rand(10) * 50
        })
        x_col = self.formatter._suggest_x_column(df)
        self.assertEqual(x_col, 'X')
    
    def test_suggest_y_columns(self):
        """Test Y columns suggestion."""
        # Test with standard data
        y_cols = self.formatter._suggest_y_columns(self.test_df, 'Date')
        self.assertIn('Revenue', y_cols)
        self.assertIn('Expenses', y_cols)
        self.assertIn('Profit', y_cols)
        
        # Test with mostly categorical data
        df = pd.DataFrame({
            'ID': range(1, 11),
            'Category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
            'Subcategory': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'X', 'Y', 'Z', 'X'],
            'Value': np.random.rand(10) * 100
        })
        y_cols = self.formatter._suggest_y_columns(df, 'Category')
        self.assertEqual(y_cols, ['Value'])
        
        # Test with many numeric columns
        df = pd.DataFrame({
            'ID': range(1, 11),
            'A': np.random.rand(10) * 10,
            'B': np.random.rand(10) * 20,
            'C': np.random.rand(10) * 30,
            'D': np.random.rand(10) * 40,
            'E': np.random.rand(10) * 50,
            'F': np.random.rand(10) * 60,
            'G': np.random.rand(10) * 70,
        })
        y_cols = self.formatter._suggest_y_columns(df, 'ID')
        self.assertTrue(len(y_cols) <= 5)  # Should limit to 5 or fewer
    
    def test_detect_data_type(self):
        """Test data type detection."""
        # Test time series
        data_type = self.formatter._detect_data_type(self.test_df, 'Date', ['Revenue', 'Expenses'])
        self.assertEqual(data_type, 'time_series')
        
        # Test categorical
        df = pd.DataFrame({
            'Category': ['A', 'B', 'C', 'D', 'E'],
            'Value': [10, 20, 30, 40, 50]
        })
        data_type = self.formatter._detect_data_type(df, 'Category', ['Value'])
        self.assertEqual(data_type, 'categorical')
        
        # Test numeric
        df = pd.DataFrame({
            'X': [1, 2, 3, 4, 5],
            'Y': [10, 20, 30, 40, 50]
        })
        data_type = self.formatter._detect_data_type(df, 'X', ['Y'])
        self.assertEqual(data_type, 'numeric')
    
    def test_process(self):
        """Test data processing."""
        # Test with explicit columns
        result = self.formatter.process(
            data=self.test_df,
            x_column='Date',
            y_columns=['Revenue', 'Expenses']
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        self.assertIn('x_column', result)
        self.assertIn('y_columns', result)
        self.assertIn('data_type', result)
        
        self.assertEqual(result['x_column'], 'Date')
        self.assertEqual(result['y_columns'], ['Revenue', 'Expenses'])
        self.assertEqual(result['data_type'], 'time_series')
        
        # Test with auto-detected columns
        result = self.formatter.process(data=self.test_df)
        
        self.assertIsInstance(result, dict)
        self.assertIn('data', result)
        self.assertIn('x_column', result)
        self.assertIn('y_columns', result)
        self.assertIn('data_type', result)
        
        self.assertEqual(result['x_column'], 'Date')
        self.assertTrue(len(result['y_columns']) > 0)
        self.assertEqual(result['data_type'], 'time_series')
    
    def test_prepare_timeseries(self):
        """Test time series preparation."""
        # Create unsorted time series
        df = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=5, freq='D').tolist()[::-1],  # Reversed
            'Value': [50, 40, 30, 20, 10]  # Reversed values
        })
        
        # Process time series
        result_df = self.formatter._prepare_timeseries(df, 'Date')
        
        # Check sorting
        self.assertTrue(result_df['Date'].is_monotonic_increasing)
        
        # Check values are reordered
        self.assertEqual(result_df['Value'].iloc[0], 10)
        self.assertEqual(result_df['Value'].iloc[-1], 50)


@unittest.skipIf(not JSON_FORMATTER_AVAILABLE, "JsonFormatter not available")
class TestJsonFormatter(unittest.TestCase):
    """Test cases for JsonFormatter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock service
        self.mock_service = MagicMock()
        
        # Create formatter
        self.formatter = JsonFormatter(self.mock_service)
        
        # Create test data
        self.test_dict = {
            'data': [
                {'date': '2023-01-01', 'revenue': 100, 'expenses': 80, 'category': 'A'},
                {'date': '2023-02-01', 'revenue': 120, 'expenses': 85, 'category': 'B'},
                {'date': '2023-03-01', 'revenue': 140, 'expenses': 90, 'category': 'A'}
            ]
        }
        
        self.test_array_dict = {
            'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
            'revenue': [100, 120, 140],
            'expenses': [80, 85, 90],
            'category': ['A', 'B', 'A']
        }
    
    def test_can_handle(self):
        """Test data type recognition."""
        # Test with JSON string
        json_str = json.dumps(self.test_dict)
        self.assertTrue(self.formatter.can_handle(json_str))
        
        # Test with file path
        self.assertTrue(self.formatter.can_handle('data.json'))
        
        # Test with dict
        self.assertTrue(self.formatter.can_handle(self.test_dict))
        
        # Test with list
        self.assertTrue(self.formatter.can_handle(self.test_dict['data']))
        
        # Test with invalid data
        self.assertFalse(self.formatter.can_handle(123))
    
    def test_parse_json(self):
        """Test JSON parsing."""
        # Test with JSON string
        json_str = json.dumps(self.test_dict)
        result = self.formatter._parse_json(json_str)
        self.assertEqual(result, self.test_dict)
        
        # Test with dict (already parsed)
        result = self.formatter._parse_json(self.test_dict)
        self.assertEqual(result, self.test_dict)
        
        # Test with invalid JSON
        with self.assertRaises(ValueError):
            self.formatter._parse_json('{invalid json}')
    
    @patch('app.tools.dataviz.formatters.json_formatter.JsonFormatter._parse_json')
    def test_process(self, mock_parse_json):
        """Test data processing."""
        # Mock parse_json to return test dict
        mock_parse_json.return_value = self.test_dict
        
        # Mock pandas_formatter
        mock_pandas_formatter = MagicMock()
        expected_result = {
            'data': pd.DataFrame(self.test_dict['data']),
            'x_column': 'date',
            'y_columns': ['revenue', 'expenses'],
            'data_type': 'time_series'
        }
        mock_pandas_formatter.process.return_value = expected_result
        
        # Set mock formatter
        self.formatter.pandas_formatter = mock_pandas_formatter
        
        # Process data
        result = self.formatter.process(
            data=self.test_dict,
            x_column='date',
            y_columns=['revenue', 'expenses']
        )
        
        # Check result
        self.assertEqual(result, expected_result)
        
        # Check mock calls
        mock_parse_json.assert_called_once_with(self.test_dict)
        mock_pandas_formatter.process.assert_called_once()
    
    def test_json_to_dataframe(self):
        """Test converting JSON to DataFrame."""
        # Test with list of dictionaries
        df = self.formatter._json_to_dataframe(self.test_dict['data'])
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 4))
        
        # Test with dictionary of arrays
        df = self.formatter._json_to_dataframe(self.test_array_dict)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 4))
        
        # Test with simple key-value pairs
        simple_dict = {'A': 1, 'B': 2, 'C': 3}
        df = self.formatter._json_to_dataframe(simple_dict)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (3, 2))
        
        # Test with list of values
        values_list = [1, 2, 3, 4, 5]
        df = self.formatter._json_to_dataframe(values_list)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (5, 1))


if __name__ == '__main__':
    unittest.main()
