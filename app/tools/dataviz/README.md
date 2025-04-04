# DataViz Service for MCP Toolkit

## Overview

The DataViz service provides data visualization capabilities for the MCP Toolkit, enabling users to create various types of visualizations from different data sources. It's designed to integrate seamlessly with other data services like FRED, YFinance, and Excel/XLSX.

## Features

- Multiple visualization types (line charts, bar charts, scatter plots, etc.)
- Support for different rendering backends (Matplotlib, Plotly, Bokeh)
- Intelligent data formatting and column selection
- Multiple export formats (PNG, SVG, PDF, HTML, JSON)
- Integration with data services (FRED, YFinance)
- Dashboard creation capability

## Directory Structure

```
app/tools/dataviz/
├── __init__.py           # Package initialization with tool discovery
├── service.py            # DataViz service implementation
├── renderers/            # Specialized visualization renderers
│   ├── __init__.py
│   ├── matplotlib.py     # Matplotlib-based renderer
│   └── plotly.py         # Plotly-based renderer
├── formatters/           # Data format handlers
│   ├── __init__.py
│   ├── pandas_formatter.py
│   └── json_formatter.py
└── tests/                # Unit tests
    ├── __init__.py
    ├── test_service.py
    ├── test_renderers.py
    └── test_formatters.py
```

## Installation

The DataViz service is included in the MCP Toolkit. Make sure you have the required dependencies:

```bash
pip install matplotlib pandas plotly
```

Optional dependencies:

```bash
pip install bokeh seaborn kaleido
```

## Usage Examples

### Basic Line Chart

```python
from app.toolkit import toolkit

# Create line chart from a DataFrame
chart_path = toolkit.dataviz.create_line_chart(
    data=my_dataframe,
    x_column='Date',
    y_columns=['Revenue', 'Expenses'],
    title='Monthly Financial Performance',
    renderer='matplotlib',
    output_format='png'
)

print(f"Chart created at: {chart_path}")
```

### Bar Chart

```python
# Create a bar chart
chart_path = toolkit.dataviz.create_bar_chart(
    data=my_dataframe,
    x_column='Category',
    y_columns=['Count'],
    stacked=False,
    title='Count by Category',
    renderer='plotly',
    output_format='html'
)
```

### FRED Data Visualization

```python
# Visualize GDP data from FRED
chart_path = toolkit.dataviz.visualize_fred_series(
    series_id='GDP',
    start_date='2010-01-01',
    title='US Gross Domestic Product',
    renderer='plotly',
    output_format='html'
)
```

### Stock Price Visualization

```python
# Visualize Apple stock price
chart_path = toolkit.dataviz.visualize_stock_data(
    ticker_symbol='AAPL',
    period='1y',
    chart_type='candlestick',
    title='Apple Inc. Stock Price',
    include_volume=True,
    renderer='plotly',
    output_format='html'
)
```

### Creating a Dashboard

```python
# Create multiple charts
gdp_chart = toolkit.dataviz.visualize_fred_series(
    series_id='GDP',
    start_date='2010-01-01',
    title='US GDP',
    renderer='plotly'
)

unemployment_chart = toolkit.dataviz.visualize_fred_series(
    series_id='UNRATE',
    start_date='2010-01-01',
    title='US Unemployment Rate',
    renderer='plotly'
)

# Create a dashboard with both charts
dashboard_path = toolkit.dataviz.create_multiple_charts(
    data=None,
    chart_configs=[
        {'chart': gdp_chart, 'title': 'GDP'},
        {'chart': unemployment_chart, 'title': 'Unemployment'}
    ],
    layout={'rows': 2, 'cols': 1},
    title='US Economic Indicators',
    renderer='plotly',
    output_format='html'
)
```

## Available Visualization Types

| Method | Description |
|--------|-------------|
| `create_line_chart` | Create a line chart visualization |
| `create_bar_chart` | Create a bar chart (grouped or stacked) |
| `create_scatter_plot` | Create a scatter plot with optional size/color dimensions |
| `create_pie_chart` | Create a pie chart |
| `create_heatmap` | Create a heatmap visualization |
| `create_histogram` | Create a histogram of data distribution |
| `create_boxplot` | Create boxplots for data distributions |
| `create_correlation_matrix` | Create a correlation matrix heatmap |
| `create_multiple_charts` | Create a dashboard with multiple charts |

## Integration Methods

| Method | Description |
|--------|-------------|
| `visualize_fred_series` | Visualize an economic data series from FRED |
| `visualize_stock_data` | Visualize stock price data with various chart types |

## Renderer Options

- `matplotlib`: Static, publication-quality visualizations
- `plotly`: Interactive, web-friendly visualizations

## Export Formats

- `png`: Standard image format
- `svg`: Vector graphics format
- `pdf`: Document format
- `html`: Interactive web visualization (Plotly only)
- `json`: Serialized visualization data (Plotly only)

## Custom Data Handling

The service automatically detects appropriate columns for visualization, but you can always specify them explicitly:

```python
# Auto-detection
chart_path = toolkit.dataviz.create_line_chart(
    data=my_dataframe,
    title='Auto-detected Columns'
)

# Explicit specification
chart_path = toolkit.dataviz.create_line_chart(
    data=my_dataframe,
    x_column='Date',
    y_columns=['Revenue', 'Expenses'],
    title='Explicit Columns'
)
```

## Testing

Run the tests using pytest:

```bash
pytest app/tools/dataviz/tests/
```

## Dependencies

- Core: pandas, numpy, matplotlib
- Optional: plotly, bokeh, seaborn, kaleido

## License

This service is part of the MCP Toolkit and is subject to the same licensing terms.
