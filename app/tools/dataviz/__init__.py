"""
DataViz service module for MCP toolkit.

This package provides tools for creating data visualizations from various
data sources, supporting multiple rendering backends and data formats.
"""

# Version information
__version__ = '0.1.0'

# Import for module discovery
from app.tools.dataviz.service import DataVizService
from app.tools.dataviz.tools import *


def get_dataviz_tools():
    """
    Get a list of all dataviz tools.

    Returns:
        List of tool functions
    """
    from app.tools.dataviz.tools import (
        dataviz_create_line_chart,
        dataviz_create_bar_chart,
        dataviz_create_scatter_plot,
        dataviz_create_pie_chart
    )

    return [
        dataviz_create_line_chart,
        dataviz_create_bar_chart,
        dataviz_create_scatter_plot,
        dataviz_create_pie_chart
    ]


# Define default services
default_services = ['DataVizService']
