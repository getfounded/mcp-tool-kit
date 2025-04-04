"""
Unit tests for DataViz service.

This module contains tests for the core DataViz service functionality.
"""

import os
import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

# Import service for testing
from app.tools.dataviz.service import DataVizService


class TestDataVizService(unittest.TestCase):
    """Test cases for DataVizService."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create service instance
        self.service = DataVizService()
        
        # Mock the toolkit
        self.service.toolkit = MagicMock()
        
        # Initialize service
        self.service.initialize()
        
        # Create test data
        self.test_data = {
            'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
            'Revenue': [100, 120, 140, 160, 180, 200, 210, 205, 215, 230, 240, 250],
            'Expenses': [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135],
            'Profit': [20, 35, 50, 65, 80, 95, 100, 90, 95, 105, 110, 115],
            'Category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        }
        self.test_df = pd.DataFrame(self.test_data)
    
    def test_initialization(self):
        """Test service initialization."""
        # Check formatters were loaded
        self.assertTrue(len(self.service.formatters) > 0)
        
        # Check renderers were loaded
        self.assertTrue(len(self.service.renderers) > 0)
    
    def test_get_formatter(self):
        """Test formatter selection."""
        # Test with DataFrame
        formatter = self.service._get_formatter(self.test_df)
        self.assertIsNotNone(formatter)
        
        # Test with dict
        formatter = self.service._get_formatter(self.test_data)
        self.assertIsNotNone(formatter)
    
    def test_get_renderer(self):
        """Test renderer selection."""
        # Test with valid renderer
        if 'matplotlib' in self.service.renderers:
            renderer = self.service._get_renderer('matplotlib')
            self.assertIsNotNone(renderer)
        
        # Test with invalid renderer
        if len(self.service.renderers) > 0:
            first_renderer = list(self.service.renderers.keys())[0]
            renderer = self.service._get_renderer('invalid_renderer')
            self.assertEqual(renderer, self.service.renderers[first_renderer])
    
    def test_generate_output_path(self):
        """Test output path generation."""
        # Test with title
        path = self.service._generate_output_path('Test Title', 'png')
        self.assertTrue(path.endswith('.png'))
        self.assertIn('viz_Test_Title', path)
        
        # Test without title
        path = self.service._generate_output_path(None, 'html')
        self.assertTrue(path.endswith('.html'))
        self.assertIn('visualization_', path)
    
    def test_create_line_chart(self):
        """Test line chart creation."""
        # Mock renderer export method
        mock_renderer = MagicMock()
        mock_renderer.line_chart.return_value = 'test_fig'
        mock_renderer.export.return_value = '/tmp/test.png'
        self.service.renderers = {'matplotlib': mock_renderer}
        
        # Test with explicit columns
        result = self.service.create_line_chart(
            data=self.test_df,
            x_column='Date',
            y_columns=['Revenue', 'Expenses'],
            title='Test Chart',
            renderer='matplotlib',
            output_format='png'
        )
        
        # Check renderer methods were called
        mock_renderer.line_chart.assert_called_once()
        mock_renderer.export.assert_called_once_with('test_fig', 'png', mock_renderer.export.call_args[0][2])
        
        # Check result
        self.assertEqual(result, '/tmp/test.png')
    
    def test_create_bar_chart(self):
        """Test bar chart creation."""
        # Mock renderer export method
        mock_renderer = MagicMock()
        mock_renderer.bar_chart.return_value = 'test_fig'
        mock_renderer.export.return_value = '/tmp/test.png'
        self.service.renderers = {'matplotlib': mock_renderer}
        
        # Test with explicit columns
        result = self.service.create_bar_chart(
            data=self.test_df,
            x_column='Category',
            y_columns=['Revenue'],
            stacked=False,
            title='Test Bar Chart',
            renderer='matplotlib',
            output_format='png'
        )
        
        # Check renderer methods were called
        mock_renderer.bar_chart.assert_called_once()
        mock_renderer.export.assert_called_once_with('test_fig', 'png', mock_renderer.export.call_args[0][2])
        
        # Check result
        self.assertEqual(result, '/tmp/test.png')
    
    def test_create_scatter_plot(self):
        """Test scatter plot creation."""
        # Mock renderer export method
        mock_renderer = MagicMock()
        mock_renderer.scatter_plot.return_value = 'test_fig'
        mock_renderer.export.return_value = '/tmp/test.png'
        self.service.renderers = {'matplotlib': mock_renderer}
        
        # Test with explicit columns
        result = self.service.create_scatter_plot(
            data=self.test_df,
            x_column='Revenue',
            y_column='Profit',
            title='Test Scatter Plot',
            renderer='matplotlib',
            output_format='png'
        )
        
        # Check renderer methods were called
        mock_renderer.scatter_plot.assert_called_once()
        mock_renderer.export.assert_called_once_with('test_fig', 'png', mock_renderer.export.call_args[0][2])
        
        # Check result
        self.assertEqual(result, '/tmp/test.png')
    
    @patch('app.tools.dataviz.service.DataVizService._get_formatter')
    def test_create_pie_chart(self, mock_get_formatter):
        """Test pie chart creation."""
        # Mock formatter
        mock_formatter = MagicMock()
        mock_formatter.process.return_value = {'data': self.test_df, 'x_column': 'Category'}
        mock_get_formatter.return_value = mock_formatter
        
        # Mock renderer export method
        mock_renderer = MagicMock()
        mock_renderer.pie_chart.return_value = 'test_fig'
        mock_renderer.export.return_value = '/tmp/test.png'
        self.service.renderers = {'matplotlib': mock_renderer}
        
        # Test with explicit columns
        result = self.service.create_pie_chart(
            data=self.test_df,
            value_column='Revenue',
            label_column='Category',
            title='Test Pie Chart',
            renderer='matplotlib',
            output_format='png'
        )
        
        # Check renderer methods were called
        mock_renderer.pie_chart.assert_called_once()
        mock_renderer.export.assert_called_once_with('test_fig', 'png', mock_renderer.export.call_args[0][2])
        
        # Check result
        self.assertEqual(result, '/tmp/test.png')
    
    @patch('app.tools.dataviz.service.DataVizService._get_formatter')
    def test_integration_with_fred(self, mock_get_formatter):
        """Test FRED integration."""
        # Mock formatter
        mock_formatter = MagicMock()
        mock_formatter.process.return_value = {'data': self.test_df, 'x_column': 'date', 'y_columns': ['value']}
        mock_get_formatter.return_value = mock_formatter
        
        # Mock renderer export method
        mock_renderer = MagicMock()
        mock_renderer.line_chart.return_value = 'test_fig'
        mock_renderer.export.return_value = '/tmp/test.html'
        self.service.renderers = {'plotly': mock_renderer}
        
        # Mock FRED service
        mock_fred = MagicMock()
        mock_fred.get_series.return_value = {'data': [
            {'date': '2023-01-01', 'value': 100},
            {'date': '2023-02-01', 'value': 101},
            {'date': '2023-03-01', 'value': 102}
        ]}
        mock_fred.get_series_info.return_value = {'title': 'GDP', 'id': 'GDP'}
        self.service.toolkit.get_service.return_value = mock_fred
        
        # Test FRED visualization
        result = self.service.visualize_fred_series(
            series_id='GDP',
            start_date='2023-01-01',
            end_date='2023-03-01',
            title=None,
            renderer='plotly',
            output_format='html'
        )
        
        # Check FRED service was called
        self.service.toolkit.get_service.assert_called_once_with('fred')
        mock_fred.get_series.assert_called_once()
        mock_fred.get_series_info.assert_called_once()
        
        # Check renderer methods were called
        mock_renderer.line_chart.assert_called_once()
        mock_renderer.export.assert_called_once()
        
        # Check result
        self.assertEqual(result, '/tmp/test.html')
    
    @patch('app.tools.dataviz.service.DataVizService._get_formatter')
    def test_integration_with_yfinance(self, mock_get_formatter):
        """Test YFinance integration."""
        # Mock formatter
        mock_formatter = MagicMock()
        mock_formatter.process.return_value = {'data': self.test_df, 'x_column': 'Date', 'y_columns': ['Close']}
        mock_get_formatter.return_value = mock_formatter
        
        # Mock renderer export method
        mock_renderer = MagicMock()
        mock_renderer.line_chart.return_value = 'test_fig'
        mock_renderer.export.return_value = '/tmp/test.html'
        self.service.renderers = {'plotly': mock_renderer}
        
        # Mock YFinance service
        mock_yfinance = MagicMock()
        mock_yfinance.get_historical_data.return_value = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
            'Open': np.random.rand(30) * 100 + 100,
            'High': np.random.rand(30) * 100 + 110,
            'Low': np.random.rand(30) * 100 + 90,
            'Close': np.random.rand(30) * 100 + 105,
            'Volume': np.random.randint(1000, 100000, 30)
        })
        self.service.toolkit.get_service.return_value = mock_yfinance
        
        # Test stock visualization
        result = self.service.visualize_stock_data(
            ticker_symbol='AAPL',
            period='1mo',
            chart_type='line',
            title=None,
            renderer='plotly',
            output_format='html'
        )
        
        # Check YFinance service was called
        self.service.toolkit.get_service.assert_called_once_with('yfinance')
        mock_yfinance.get_historical_data.assert_called_once()
        
        # Check renderer methods were called
        mock_renderer.line_chart.assert_called_once()
        mock_renderer.export.assert_called_once()
        
        # Check result
        self.assertEqual(result, '/tmp/test.html')


if __name__ == '__main__':
    unittest.main()
