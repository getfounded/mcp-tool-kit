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
from app.tools.base.service import ToolServiceBase
from app.tools.base.registry import register_tool

# Configure logging
logger = logging.getLogger(__name__)


class DataVizService(ToolServiceBase):
    """Service for data visualization capabilities."""

    def __init__(self):
        """Initialize the visualization service."""
        super().__init__()

        # Initialize storage for renderers and formatters
        self.renderers = {}
        self.formatters = {}
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize the visualization service."""
        logger.info("Initializing DataViz service")

        # Load available renderers and formatters
        self._load_renderers()
        self._load_formatters()

        # Configure data storage
        self.temp_dir = self.get_env_var('DATAVIZ_TEMP_DIR',
                                         default=tempfile.gettempdir())

        logger.info(
            f"DataViz service initialized with temp dir: {self.temp_dir}")
        self.initialized = True
        return True

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
                    logger.warning(
                        f"Could not find {class_name} in {module_path}")

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
                class_name = formatter_name.split(
                    '_')[0].capitalize() + 'Formatter'
                if hasattr(module, class_name):
                    formatter_class = getattr(module, class_name)

                    # Initialize the formatter
                    formatter = formatter_class(self)
                    self.formatters[formatter_name] = formatter
                    logger.debug(f"Loaded formatter: {formatter_name}")
                else:
                    logger.warning(
                        f"Could not find {class_name} in {module_path}")

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
            logger.debug(
                "No suitable formatter found, defaulting to pandas_formatter")
            return self.formatters['pandas_formatter']

        raise ValueError(
            f"No suitable formatter found for data of type {type(data)}")

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
        self._is_initialized()
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
        self._is_initialized()
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
        self._is_initialized()
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
        self._is_initialized()
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


# Singleton instance
_service_instance = None


def get_service() -> DataVizService:
    """
    Get or initialize the DataViz service singleton.

    Returns:
        DataVizService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = DataVizService()
        _service_instance.initialize()
    return _service_instance
