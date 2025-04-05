#!/usr/bin/env python3
"""
Tool functions for data visualization operations.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.dataviz.service import get_service


@register_tool(category="dataviz")
async def dataviz_create_line_chart(
    data: Any,
    x_column: Optional[str] = None,
    y_columns: Optional[List[str]] = None,
    title: Optional[str] = None,
    renderer: str = 'matplotlib',
    output_format: str = 'png'
) -> str:
    """Create a line chart visualization from provided data.

    Parameters:
    - data: The dataset to visualize (DataFrame, dict, or path to file)
    - x_column: The column to use for x-axis
    - y_columns: List of columns to plot as y values
    - title: Chart title
    - renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
    - output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
    """
    dataviz_service = get_service()
    result = dataviz_service.create_line_chart(
        data=data,
        x_column=x_column,
        y_columns=y_columns,
        title=title,
        renderer=renderer,
        output_format=output_format
    )
    return json.dumps({"status": "success", "result": result}, indent=2)


@register_tool(category="dataviz")
async def dataviz_create_bar_chart(
    data: Any,
    x_column: Optional[str] = None,
    y_columns: Optional[List[str]] = None,
    stacked: bool = False,
    title: Optional[str] = None,
    renderer: str = 'matplotlib',
    output_format: str = 'png'
) -> str:
    """Create a bar chart visualization from provided data.

    Parameters:
    - data: The dataset to visualize (DataFrame, dict, or path to file)
    - x_column: The column to use for x-axis
    - y_columns: List of columns to plot as y values
    - stacked: Whether to create a stacked bar chart
    - title: Chart title
    - renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
    - output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
    """
    dataviz_service = get_service()
    result = dataviz_service.create_bar_chart(
        data=data,
        x_column=x_column,
        y_columns=y_columns,
        stacked=stacked,
        title=title,
        renderer=renderer,
        output_format=output_format
    )
    return json.dumps({"status": "success", "result": result}, indent=2)


@register_tool(category="dataviz")
async def dataviz_create_scatter_plot(
    data: Any,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    size_column: Optional[str] = None,
    color_column: Optional[str] = None,
    title: Optional[str] = None,
    renderer: str = 'matplotlib',
    output_format: str = 'png'
) -> str:
    """Create a scatter plot visualization.

    Parameters:
    - data: The dataset to visualize (DataFrame, dict, or path to file)
    - x_column: Column for x-axis values
    - y_column: Column for y-axis values
    - size_column: Column to determine point sizes
    - color_column: Column to determine point colors
    - title: Chart title
    - renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
    - output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
    """
    dataviz_service = get_service()
    result = dataviz_service.create_scatter_plot(
        data=data,
        x_column=x_column,
        y_column=y_column,
        size_column=size_column,
        color_column=color_column,
        title=title,
        renderer=renderer,
        output_format=output_format
    )
    return json.dumps({"status": "success", "result": result}, indent=2)


@register_tool(category="dataviz")
async def dataviz_create_pie_chart(
    data: Any,
    value_column: str,
    label_column: Optional[str] = None,
    title: Optional[str] = None,
    renderer: str = 'matplotlib',
    output_format: str = 'png'
) -> str:
    """Create a pie chart visualization from provided data.

    Parameters:
    - data: The dataset to visualize (DataFrame, dict, or path to file)
    - value_column: Column with values to determine slice sizes
    - label_column: Column with labels for slices
    - title: Chart title
    - renderer: Visualization backend to use ('matplotlib', 'plotly', 'bokeh')
    - output_format: Output format ('png', 'svg', 'pdf', 'html', 'json')
    """
    dataviz_service = get_service()
    result = dataviz_service.create_pie_chart(
        data=data,
        value_column=value_column,
        label_column=label_column,
        title=title,
        renderer=renderer,
        output_format=output_format
    )
    return json.dumps({"status": "success", "result": result}, indent=2)
