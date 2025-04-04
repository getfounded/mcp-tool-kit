"""
Unit tests for DataViz renderers.

This module contains tests for the visualization renderers.
"""

import os
import unittest
import pandas as pd
import numpy as np
import tempfile
from unittest.mock import MagicMock, patch

# Import renderers for testing
try:
    from app.tools.dataviz.renderers.matplotlib import MatplotlibRenderer
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from app.tools.dataviz.renderers.plotly import PlotlyRenderer
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@unittest.skipIf(not MATPLOTLIB_AVAILABLE, "Matplotlib not available")
class TestMatplotlibRenderer(unittest.TestCase):
    """Test cases for MatplotlibRenderer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock service
        self.mock_service = MagicMock()
        
        # Create renderer
        self.renderer = MatplotlibRenderer(self.mock_service)
        
        # Create test data
        self.test_data = {
            'data': pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
                'Revenue': [100, 120, 140, 160, 180, 200, 210, 205, 215, 230, 240, 250],
                'Expenses': [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135],
                'Profit': [20, 35, 50, 65, 80, 95, 100, 90, 95, 105, 110, 115],
                'Category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
            }),
            'x_column': 'Date',
            'y_columns': ['Revenue', 'Expenses'],
            'data_type': 'time_series'
        }
    
    def test_line_chart(self):
        """Test line chart creation."""
        # Create chart
        fig = self.renderer.line_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'],
            title='Test Line Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_line.png')
        
        result = self.renderer.export(fig, 'png', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_bar_chart(self):
        """Test bar chart creation."""
        # Create chart
        fig = self.renderer.bar_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'],
            stacked=False,
            title='Test Bar Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Create stacked chart
        fig_stacked = self.renderer.bar_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'],
            stacked=True,
            title='Test Stacked Bar Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig_stacked)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_bar.png')
        
        result = self.renderer.export(fig, 'png', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_scatter_plot(self):
        """Test scatter plot creation."""
        # Create chart
        fig = self.renderer.scatter_plot(
            data=self.test_data,
            x_column='Revenue',
            y_column='Profit',
            title='Test Scatter Plot'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_scatter.png')
        
        result = self.renderer.export(fig, 'png', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_pie_chart(self):
        """Test pie chart creation."""
        # Create chart
        fig = self.renderer.pie_chart(
            data=self.test_data,
            value_column='Revenue',
            label_column='Category',
            title='Test Pie Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_pie.png')
        
        result = self.renderer.export(fig, 'png', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_export_formats(self):
        """Test exporting in different formats."""
        # Create a simple chart
        fig = self.renderer.line_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'][0:1],
            title='Test Export Formats'
        )
        
        # Test PNG format
        temp_dir = tempfile.mkdtemp()
        png_file = os.path.join(temp_dir, 'test.png')
        
        result = self.renderer.export(fig, 'png', png_file)
        self.assertTrue(os.path.exists(result))
        
        # Test SVG format
        svg_file = os.path.join(temp_dir, 'test.svg')
        
        result = self.renderer.export(fig, 'svg', svg_file)
        self.assertTrue(os.path.exists(result))
        
        # Test PDF format
        pdf_file = os.path.join(temp_dir, 'test.pdf')
        
        result = self.renderer.export(fig, 'pdf', pdf_file)
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        for file in [png_file, svg_file, pdf_file]:
            if os.path.exists(file):
                os.remove(file)


@unittest.skipIf(not PLOTLY_AVAILABLE, "Plotly not available")
class TestPlotlyRenderer(unittest.TestCase):
    """Test cases for PlotlyRenderer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock service
        self.mock_service = MagicMock()
        
        # Create renderer
        self.renderer = PlotlyRenderer(self.mock_service)
        
        # Create test data
        self.test_data = {
            'data': pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=12, freq='M'),
                'Revenue': [100, 120, 140, 160, 180, 200, 210, 205, 215, 230, 240, 250],
                'Expenses': [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135],
                'Profit': [20, 35, 50, 65, 80, 95, 100, 90, 95, 105, 110, 115],
                'Category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
            }),
            'x_column': 'Date',
            'y_columns': ['Revenue', 'Expenses'],
            'data_type': 'time_series'
        }
    
    def test_line_chart(self):
        """Test line chart creation."""
        # Create chart
        fig = self.renderer.line_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'],
            title='Test Line Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_line.html')
        
        result = self.renderer.export(fig, 'html', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_bar_chart(self):
        """Test bar chart creation."""
        # Create chart
        fig = self.renderer.bar_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'],
            stacked=False,
            title='Test Bar Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Create stacked chart
        fig_stacked = self.renderer.bar_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'],
            stacked=True,
            title='Test Stacked Bar Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig_stacked)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_bar.html')
        
        result = self.renderer.export(fig, 'html', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_scatter_plot(self):
        """Test scatter plot creation."""
        # Create chart
        fig = self.renderer.scatter_plot(
            data=self.test_data,
            x_column='Revenue',
            y_column='Profit',
            title='Test Scatter Plot'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_scatter.html')
        
        result = self.renderer.export(fig, 'html', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_candlestick_chart(self):
        """Test candlestick chart creation."""
        # Create stock data
        stock_data = {
            'data': pd.DataFrame({
                'Date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
                'Open': np.random.rand(30) * 100 + 100,
                'High': np.random.rand(30) * 100 + 110,
                'Low': np.random.rand(30) * 100 + 90,
                'Close': np.random.rand(30) * 100 + 105,
                'Volume': np.random.randint(1000, 100000, 30)
            }),
            'x_column': 'Date',
            'y_columns': ['Open', 'High', 'Low', 'Close'],
            'data_type': 'time_series'
        }
        
        # Create chart
        fig = self.renderer.candlestick_chart(
            data=stock_data,
            open_col='Open',
            high_col='High',
            low_col='Low',
            close_col='Close',
            volume_col='Volume',
            title='Test Candlestick Chart'
        )
        
        # Check figure was created
        self.assertIsNotNone(fig)
        
        # Export chart
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_candlestick.html')
        
        result = self.renderer.export(fig, 'html', temp_file)
        
        # Check file was created
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        os.remove(result)
    
    def test_export_formats(self):
        """Test exporting in different formats."""
        # Create a simple chart
        fig = self.renderer.line_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'][0:1],
            title='Test Export Formats'
        )
        
        # Test HTML format
        temp_dir = tempfile.mkdtemp()
        html_file = os.path.join(temp_dir, 'test.html')
        
        result = self.renderer.export(fig, 'html', html_file)
        self.assertTrue(os.path.exists(result))
        
        # Test JSON format
        json_file = os.path.join(temp_dir, 'test.json')
        
        result = self.renderer.export(fig, 'json', json_file)
        self.assertTrue(os.path.exists(result))
        
        # Cleanup
        for file in [html_file, json_file]:
            if os.path.exists(file):
                os.remove(file)
    
    @patch('plotly.graph_objects.Figure.write_image')
    def test_image_export(self, mock_write_image):
        """Test exporting as images."""
        # Mock write_image to avoid kaleido dependency
        mock_write_image.return_value = None
        
        # Create a simple chart
        fig = self.renderer.line_chart(
            data=self.test_data,
            x_column=self.test_data['x_column'],
            y_columns=self.test_data['y_columns'][0:1],
            title='Test Export Images'
        )
        
        # Test PNG format
        temp_dir = tempfile.mkdtemp()
        png_file = os.path.join(temp_dir, 'test.png')
        
        self.renderer.export(fig, 'png', png_file)
        mock_write_image.assert_called_once()


if __name__ == '__main__':
    unittest.main()
