# Data Visualization Tool

## Overview
The Data Visualization tool provides capabilities for creating various types of charts and visualizations from data sources. It supports multiple rendering backends and output formats to meet different visualization needs.

## Features
- Line charts for time series and trend analysis
- Bar charts for comparison between categories (regular and stacked)
- Scatter plots for relationship analysis
- Pie charts for showing composition
- Multiple rendering backends (matplotlib, plotly)
- Various output formats (png, svg, pdf, html, json)
- Flexible data input formats

## Requirements
- Python data visualization libraries based on the renderer you choose:
  - Matplotlib (default)
  - Plotly
- Pandas for data manipulation

## Usage Examples

### Creating a Line Chart
```python
# Basic line chart from a DataFrame
result = await dataviz_create_line_chart(
    data=my_dataframe,
    x_column="date",
    y_columns=["sales", "profit"],
    title="Monthly Sales and Profit"
)

# Line chart specifying renderer and output format
result = await dataviz_create_line_chart(
    data=my_dataframe,
    x_column="date",
    y_columns=["temperature"],
    title="Temperature Over Time",
    renderer="plotly",
    output_format="html"
)
```

### Creating a Bar Chart
```python
# Basic bar chart
result = await dataviz_create_bar_chart(
    data=my_dataframe,
    x_column="category",
    y_columns=["count"],
    title="Count by Category"
)

# Stacked bar chart
result = await dataviz_create_bar_chart(
    data=my_dataframe,
    x_column="month",
    y_columns=["product_a", "product_b", "product_c"],
    stacked=True,
    title="Monthly Sales by Product"
)
```

### Creating a Scatter Plot
```python
# Basic scatter plot
result = await dataviz_create_scatter_plot(
    data=my_dataframe,
    x_column="height",
    y_column="weight",
    title="Height vs. Weight"
)

# Advanced scatter plot with size and color
result = await dataviz_create_scatter_plot(
    data=my_dataframe,
    x_column="income",
    y_column="spending",
    size_column="savings",
    color_column="age_group",
    title="Income vs. Spending by Age Group"
)
```

### Creating a Pie Chart
```python
# Basic pie chart
result = await dataviz_create_pie_chart(
    data=my_dataframe,
    value_column="revenue",
    label_column="product",
    title="Revenue by Product"
)
```

## API Reference

### dataviz_create_line_chart
Create a line chart visualization from provided data.

**Parameters:**
- `data`: The dataset to visualize (DataFrame, dict, or path to file)
- `x_column`: The column to use for x-axis
- `y_columns`: List of columns to plot as y values
- `title`: Chart title
- `renderer`: Visualization backend to use ('matplotlib', 'plotly')
- `output_format`: Output format ('png', 'svg', 'pdf', 'html', 'json')

**Returns:**
- JSON string with result containing the visualization

### dataviz_create_bar_chart
Create a bar chart visualization from provided data.

**Parameters:**
- `data`: The dataset to visualize (DataFrame, dict, or path to file)
- `x_column`: The column to use for x-axis
- `y_columns`: List of columns to plot as y values
- `stacked`: Whether to create a stacked bar chart
- `title`: Chart title
- `renderer`: Visualization backend to use ('matplotlib', 'plotly')
- `output_format`: Output format ('png', 'svg', 'pdf', 'html', 'json')

**Returns:**
- JSON string with result containing the visualization

### dataviz_create_scatter_plot
Create a scatter plot visualization.

**Parameters:**
- `data`: The dataset to visualize (DataFrame, dict, or path to file)
- `x_column`: Column for x-axis values
- `y_column`: Column for y-axis values
- `size_column`: Column to determine point sizes
- `color_column`: Column to determine point colors
- `title`: Chart title
- `renderer`: Visualization backend to use ('matplotlib', 'plotly')
- `output_format`: Output format ('png', 'svg', 'pdf', 'html', 'json')

**Returns:**
- JSON string with result containing the visualization

### dataviz_create_pie_chart
Create a pie chart visualization from provided data.

**Parameters:**
- `data`: The dataset to visualize (DataFrame, dict, or path to file)
- `value_column`: Column with values to determine slice sizes
- `label_column`: Column with labels for slices
- `title`: Chart title
- `renderer`: Visualization backend to use ('matplotlib', 'plotly')
- `output_format`: Output format ('png', 'svg', 'pdf', 'html', 'json')

**Returns:**
- JSON string with result containing the visualization

## Data Input Formats
The tool accepts several input formats:
- Pandas DataFrame objects
- Python dictionaries (will be converted to DataFrames)
- File paths to supported data formats (CSV, Excel, JSON)

## Renderers
The tool supports multiple visualization backends:
- `matplotlib`: The default renderer, good for static images
- `plotly`: Interactive visualizations, especially good for HTML output

## Output Formats
- `png`: Portable Network Graphics (static image)
- `svg`: Scalable Vector Graphics (vector image)
- `pdf`: Portable Document Format (print-ready)
- `html`: HTML with interactive elements (for plotly)
- `json`: JSON representation of the chart

## Error Handling
The tool will return a JSON object with an error message if visualization fails. Always check the response for error messages.

## Limitations
- Large datasets may cause performance issues
- Some visualization features may only be available with specific renderers
- Complex visualizations might require custom code
