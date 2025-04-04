"""
DataViz Service Implementation.

This module provides the core DataViz service implementation with tools
for creating various types of data visualizations.
"""

import os
import tempfile
import importlib
import logging
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import numpy as np

# Import base service and registry decorators
from app.tools.base.service import BaseService
from app.tools.base.registry import tool, category

# Configure logging
logger = logging.getLogger(__name__)


class DataVizService(BaseService):
    """Service for data visualization capabilities."""
    
    def initialize(self):
        """Initialize the visualization service."""
        logger.info("Initializing DataViz service")
        
        # Initialize storage for renderers and formatters
        self.renderers = {}
        self.formatters = {}
        
        # Load available renderers and formatters
        self._load_renderers()
        self._load_formatters()
        
        # Configure data storage
        self.temp_dir = self.get_env_var('DATAVIZ_TEMP_DIR', 
                                         tempfile.gettempdir())
        
        logger.info(f"DataViz service initialized with temp dir: {self.temp_dir}")
    
    def _load_renderers(self):
        """Dynamically load available renderers."""
        logger.debug("Loading DataViz renderers")
        
        # List of supported renderers to try loading
        renderer_modules = ['matplotlib', 'plotly', 'bokeh']
        
        for renderer_name in renderer_modules:
            try:
                # Construct the module path
                module_path = f"app.tools.dataviz.renderers.{renderer_name}"
                
                # Try to import the module
                module = importlib.import_module(module_path)
                
                # Get the renderer class (assume it follows naming convention)
                class_name = f"{renderer_name.capitalize()}Renderer"
                if hasattr(module, class_name):
                    renderer_class = getattr(module, class_name)
                    
                    # Initialize the renderer
                    self.renderers[renderer_name] = renderer_class(self)
                    logger.debug(f"Loaded renderer: {renderer_name}")
                else:
                    logger.warning(f"Could not find {class_name} in {module_path}")
                    
            except ImportError as e:
                logger.debug(f"Renderer {renderer_name} not available: {e}")
                # Skip unavailable renderers
                continue
                
        logger.info(f"Loaded renderers: {list(self.renderers.keys())}")
    
    def _load_formatters(self):
        """Dynamically load available data formatters."""
        logger.debug("Loading DataViz formatters")
        
        # List of supported formatters to try loading
        formatter_modules = ['pandas_formatter', 'json_formatter']
        
        for formatter_name in formatter_modules:
            try:
                # Construct the module path
                module_path = f"app.tools.dataviz.formatters.{formatter_name}"
                
                # Try to import the module
                module = importlib.import_module(module_path)
                
                # Get the formatter class (assume it follows naming convention)
                class_name = formatter_name.split('_')[0].capitalize() + 'Formatter'
                if hasattr(module, class_name):
                    formatter_class = getattr(module, class_name)
                    
                    # Initialize the formatter
                    formatter = formatter_class(self)
                    self.formatters[formatter_name] = formatter
                    logger.debug(f"Loaded formatter: {formatter_name}")
                else:
                    logger.warning(f"Could not find {class_name} in {module_path}")
                    
            except ImportError as e:
                logger.debug(f"Formatter {formatter_name} not available: {e}")
                # Skip unavailable formatters
                continue
                
        logger.info(f"Loaded formatters: {list(self.formatters.keys())}")
    
    def _get_formatter(self, data):
        """
        Select the appropriate formatter for the data type.
        
        Args:
            data: The data to be formatted
            
        Returns:
            A formatter instance that can handle the data
        """
        # Try each formatter to see if it can handle the data
        for formatter_name, formatter in self.formatters.items():
            if hasattr(formatter, 'can_handle') and formatter.can_handle(data):
                logger.debug(f"Using formatter: {formatter_name} for data")
                return formatter
                
        # Default to pandas formatter if available
        if 'pandas_formatter' in self.formatters:
            logger.debug("No suitable formatter found, defaulting to pandas_formatter")
            return self.formatters['pandas_formatter']
            
        raise ValueError(f"No suitable formatter found for data of type {type(data)}")
    
    def _get_renderer(self, renderer_name):
        """
        Get the specified renderer instance.
        
        Args:
            renderer_name: Name of the renderer to use
            
        Returns:
            A renderer instance
        """
        if renderer_name not in self.renderers:
            available = list(self.renderers.keys())
            if not available:
                raise ValueError("No renderers available")
                
            # Default to first available renderer
            logger.warning(
                f"Renderer '{renderer_name}' not available. Using {available[0]}"
            )
            renderer_name = available[0]
            
        return self.renderers[renderer_name]
    
    def _generate_output_path(self, title=None, output_format='png'):
        """
        Generate a path for the output file.
        
        Args:
            title: The visualization title (for filename)
            output_format: The file format
            
        Returns:
            Path to the output file
        """
        # Create a safe filename from the title
        if title:
            # Replace spaces and unsafe characters with underscores
            safe_title = ''.join([c if c.isalnum() else '_' for c in title])
            filename = f"viz_{safe_title}"
        else:
            # Create a timestamp-based filename
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"visualization_{timestamp}"
            
        # Ensure temp dir exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Create the full path
        return os.path.join(self.temp_dir, f"{filename}.{output_format}")
    
    @tool
    @category('visualization')
    def create_line_chart(self, data, x_column=None, y_columns=None, title=None, 
                         renderer='matplotlib', output_format='png'):
        """
        Create a line chart visualization from provided data.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            x_column: The column to use for x-axis
            y_columns: List of columns to plot as y values
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating line chart with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data
        processed_data = formatter.process(data, x_column, y_columns)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.line_chart(
            data=processed_data,
            x_column=processed_data['x_column'],
            y_columns=processed_data['y_columns'],
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_bar_chart(self, data, x_column=None, y_columns=None, 
                        stacked=False, title=None, renderer='matplotlib',
                        output_format='png'):
        """
        Create a bar chart visualization from provided data.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            x_column: The column to use for x-axis
            y_columns: List of columns to plot as y values
            stacked: Whether to create a stacked bar chart
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating bar chart with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data
        processed_data = formatter.process(data, x_column, y_columns)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.bar_chart(
            data=processed_data,
            x_column=processed_data['x_column'],
            y_columns=processed_data['y_columns'],
            stacked=stacked,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_scatter_plot(self, data, x_column=None, y_column=None, 
                           size_column=None, color_column=None, title=None,
                           renderer='matplotlib', output_format='png'):
        """
        Create a scatter plot visualization.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            x_column: Column for x-axis values
            y_column: Column for y-axis values
            size_column: Column to determine point sizes
            color_column: Column to determine point colors
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating scatter plot with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # For scatter plot, we need exactly one y-column
        y_columns = [y_column] if y_column else None
        
        # Process the data
        processed_data = formatter.process(data, x_column, y_columns)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.scatter_plot(
            data=processed_data,
            x_column=processed_data['x_column'],
            y_column=processed_data['y_columns'][0],
            size_column=size_column,
            color_column=color_column,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_pie_chart(self, data, value_column, label_column=None,
                        title=None, renderer='matplotlib', output_format='png'):
        """
        Create a pie chart visualization from provided data.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            value_column: Column with values to determine slice sizes
            label_column: Column with labels for slices
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating pie chart with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data - we don't need x/y columns for pie charts
        processed_data = formatter.process(data)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.pie_chart(
            data=processed_data,
            value_column=value_column,
            label_column=label_column,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_heatmap(self, data, x_column=None, y_column=None, value_column=None,
                      colormap='viridis', title=None, renderer='matplotlib',
                      output_format='png'):
        """
        Create a heatmap visualization from provided data.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            x_column: Column for x-axis categories
            y_column: Column for y-axis categories
            value_column: Column for cell values
            colormap: Name of the colormap to use
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating heatmap with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data - provide x and y columns so formatter can pivot if needed
        processed_data = formatter.process(data, x_column, None)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.heatmap(
            data=processed_data,
            x_column=x_column or processed_data['x_column'],
            y_column=y_column,
            value_column=value_column,
            colormap=colormap,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_histogram(self, data, column, bins=10, density=False,
                        title=None, renderer='matplotlib', output_format='png'):
        """
        Create a histogram visualization from provided data.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            column: Column to plot the distribution of
            bins: Number of bins or list of bin edges
            density: Whether to normalize the histogram
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating histogram with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data
        processed_data = formatter.process(data)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.histogram(
            data=processed_data,
            column=column,
            bins=bins,
            density=density,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_boxplot(self, data, value_columns, group_column=None,
                      title=None, renderer='matplotlib', output_format='png'):
        """
        Create a boxplot visualization from provided data.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            value_columns: Columns to show distributions for
            group_column: Column to group boxplots by (optional)
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating boxplot with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data
        processed_data = formatter.process(data)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.boxplot(
            data=processed_data,
            value_columns=value_columns,
            group_column=group_column,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_correlation_matrix(self, data, columns=None,
                                method='pearson', title=None,
                                renderer='matplotlib', output_format='png'):
        """
        Create a correlation matrix visualization.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            columns: List of columns to include in correlation calculation
            method: Correlation method ('pearson', 'kendall', 'spearman')
            title: Chart title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating correlation matrix with {renderer} renderer")
        
        # Get the formatter for this data
        formatter = self._get_formatter(data)
        
        # Process the data
        processed_data = formatter.process(data)
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # Create the chart
        fig = renderer_instance.correlation_matrix(
            data=processed_data,
            columns=columns,
            method=method,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    @tool
    @category('visualization')
    def create_multiple_charts(self, data, chart_configs, layout=None,
                             title=None, renderer='plotly', output_format='html'):
        """
        Create multiple charts in a single visualization.
        
        Args:
            data: The dataset to visualize (DataFrame, dict, or path to file)
            chart_configs: List of chart configurations
            layout: Layout configuration for the charts (rows, cols)
            title: Overall title
            renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
            output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
            
        Returns:
            Path to the generated visualization or the visualization object
        """
        logger.debug(f"Creating multiple charts with {renderer} renderer")
        
        # Only certain renderers support multiple charts
        if renderer not in ['plotly', 'matplotlib']:
            logger.warning(f"Renderer {renderer} may not support multiple charts")
        
        # Get the renderer
        renderer_instance = self._get_renderer(renderer)
        
        # If data is provided, process it
        processed_data = None
        if data is not None:
            formatter = self._get_formatter(data)
            processed_data = formatter.process(data)
        
        # Create the chart
        fig = renderer_instance.multiple_charts(
            data=processed_data,
            chart_configs=chart_configs,
            layout=layout,
            title=title
        )
        
        # Generate output path
        output_path = self._generate_output_path(title, output_format)
        
        # Export the visualization
        return renderer_instance.export(fig, output_format, output_path)
    
    # Integration with other services
    
    @tool
    @category('integrations')
    def visualize_fred_series(self, series_id, start_date=None, end_date=None,
                             title=None, renderer='plotly', output_format='html'):
        """
        Visualize a FRED economic data series.
        
        Args:
            series_id: FRED series identifier (e.g., 'GDP', 'UNRATE')
            start_date: Start date for data (YYYY-MM-DD)
            end_date: End date for data (YYYY-MM-DD)
            title: Chart title
            renderer: Visualization backend
            output_format: Output format
            
        Returns:
            Visualization of the FRED time series
        """
        logger.debug(f"Visualizing FRED series {series_id}")
        
        try:
            # Get the FRED service
            fred_service = self.toolkit.get_service('fred')
            
            # Fetch the series data
            series_data = fred_service.get_series(
                series_id=series_id, 
                observation_start=start_date,
                observation_end=end_date
            )
            
            # Convert to DataFrame
            if isinstance(series_data, dict) and 'data' in series_data:
                # Handle API response format
                df = pd.DataFrame(series_data['data'])
            elif isinstance(series_data, (list, dict)):
                # Handle other possible formats
                df = pd.DataFrame(series_data)
            else:
                raise ValueError(f"Unexpected format from FRED service: {type(series_data)}")
            
            # Ensure we have date and value columns
            if 'date' not in df.columns or len(df.columns) < 2:
                raise ValueError(f"FRED data does not have expected columns: {df.columns}")
            
            # Get the value column name
            value_col = [col for col in df.columns if col != 'date'][0]
            
            # Get series info for the title if not provided
            if not title:
                try:
                    series_info = fred_service.get_series_info(series_id=series_id)
                    if isinstance(series_info, dict) and 'title' in series_info:
                        title = f"{series_info['title']} ({series_id})"
                    else:
                        title = f"FRED Series: {series_id}"
                except Exception as e:
                    logger.warning(f"Could not get FRED series info: {e}")
                    title = f"FRED Series: {series_id}"
            
            # Create visualization
            return self.create_line_chart(
                data=df,
                x_column='date',
                y_columns=[value_col],
                title=title,
                renderer=renderer,
                output_format=output_format
            )
            
        except Exception as e:
            logger.error(f"Error visualizing FRED series: {e}")
            raise ValueError(f"Failed to visualize FRED series: {e}")
    
    @tool
    @category('integrations')
    def visualize_stock_data(self, ticker_symbol, period="1y", interval="1d",
                           chart_type='line', title=None, include_volume=False,
                           renderer='plotly', output_format='html'):
        """
        Visualize stock price data from YFinance.
        
        Args:
            ticker_symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            chart_type: Type of chart ('line', 'candlestick', 'ohlc')
            title: Chart title
            include_volume: Whether to include volume data
            renderer: Visualization backend
            output_format: Output format
            
        Returns:
            Visualization of the stock data
        """
        logger.debug(f"Visualizing stock data for {ticker_symbol}")
        
        try:
            # Get the YFinance service
            yfinance_service = self.toolkit.get_service('yfinance')
            
            # Fetch the historical data
            historical_data = yfinance_service.get_historical_data(
                ticker_symbol=ticker_symbol,
                period=period,
                interval=interval
            )
            
            # Convert to DataFrame if needed
            if not isinstance(historical_data, pd.DataFrame):
                if isinstance(historical_data, dict) and 'data' in historical_data:
                    df = pd.DataFrame(historical_data['data'])
                else:
                    df = pd.DataFrame(historical_data)
            else:
                df = historical_data
            
            # Auto-generate title if not provided
            if not title:
                title = f"{ticker_symbol} Stock Price"
                if period != '1d':
                    title += f" ({period})"
            
            # Handle different chart types
            if chart_type == 'line':
                # For line chart, we just need the closing price
                return self.create_line_chart(
                    data=df,
                    x_column='Date',
                    y_columns=['Close'] + (['Volume'] if include_volume else []),
                    title=title,
                    renderer=renderer,
                    output_format=output_format
                )
                
            elif chart_type in ('candlestick', 'ohlc'):
                # Get the renderer instance
                renderer_instance = self._get_renderer(renderer)
                
                # Special handling for OHLC/candlestick charts
                if hasattr(renderer_instance, f"{chart_type}_chart"):
                    # Format the data
                    formatter = self._get_formatter(df)
                    processed_data = formatter.process(df)
                    
                    # Create the chart
                    fig = getattr(renderer_instance, f"{chart_type}_chart")(
                        data=processed_data,
                        open_col='Open',
                        high_col='High',
                        low_col='Low',
                        close_col='Close',
                        volume_col='Volume' if include_volume else None,
                        title=title
                    )
                    
                    # Generate output path
                    output_path = self._generate_output_path(title, output_format)
                    
                    # Export the visualization
                    return renderer_instance.export(fig, output_format, output_path)
                else:
                    logger.warning(
                        f"Renderer {renderer} doesn't support {chart_type} charts. Using line chart."
                    )
                    return self.create_line_chart(
                        data=df,
                        x_column='Date',
                        y_columns=['Close'],
                        title=title,
                        renderer=renderer,
                        output_format=output_format
                    )
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
                
        except Exception as e:
            logger.error(f"Error visualizing stock data: {e}")
            raise ValueError(f"Failed to visualize stock data: {e}")
