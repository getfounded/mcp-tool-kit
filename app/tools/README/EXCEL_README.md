# XlsxWriter Tool for MCP

A comprehensive tool for integrating the XlsxWriter library with MCP Unified Server, enabling Claude to create and manipulate Excel files programmatically.

## Overview

The XlsxWriter Tool provides a set of functions to create Excel spreadsheets with features including:

- Creating workbooks and worksheets
- Writing data to cells and ranges
- Applying formatting to cells
- Adding charts, images, and formulas
- Creating tables with headers and styling
- Closing and saving workbooks

This tool maintains state between function calls, allowing for complex Excel file creation across multiple requests.

## Installation

1. Add the `xlsxwriter.py` file to your `tools` directory in the MCP Unified Server
2. Install the required dependency with `pip install XlsxWriter`
3. Update your `requirements.txt` file to include `XlsxWriter>=3.1.0`
4. Update the `mcp_unified_server.py` file to import and register the XlsxWriter module

### Adding to mcp_unified_server.py

Add the following code to your `mcp_unified_server.py` file:

```python
# Initialize XlsxWriter tools
try:
    from tools.xlsxwriter import get_xlsx_tools, set_external_mcp, initialize_xlsx_service

    # Pass our MCP instance to the xlsxwriter module
    set_external_mcp(mcp)

    # Initialize xlsxwriter tools
    initialize_xlsx_service()

    # Register xlsxwriter tools
    xlsx_tools = get_xlsx_tools()
    for tool_name, tool_func in xlsx_tools.items():
        # Register each xlsxwriter tool with the main MCP instance
        mcp.tool(name=tool_name)(tool_func)

    # Add XlsxWriter dependencies to MCP dependencies
    mcp.dependencies.extend([
        "XlsxWriter"
    ])

    logging.info("XlsxWriter tools registered successfully.")
except ImportError as e:
    logging.warning(f"Could not load XlsxWriter tools: {e}")
```

## Available Tools

### xlsx_create_workbook

Creates a new Excel workbook.

```python
xlsx_create_workbook(filename: str)
```

Parameters:
- `filename`: Path to save the Excel file

### xlsx_add_worksheet

Adds a worksheet to the workbook.

```python
xlsx_add_worksheet(filename: str, name: str = None)
```

Parameters:
- `filename`: Path to the Excel file
- `name`: (Optional) Name for the worksheet

### xlsx_write_data

Writes data to a cell in a worksheet.

```python
xlsx_write_data(filename: str, worksheet: str, row: int, col: int, data: Any, format: str = None)
```

Parameters:
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `row`: Row number (0-based)
- `col`: Column number (0-based)
- `data`: Data to write (string, number, boolean, etc.)
- `format`: (Optional) Name of a predefined format

### xlsx_write_matrix

Writes a matrix of data to a worksheet.

```python
xlsx_write_matrix(filename: str, worksheet: str, start_row: int, start_col: int, data: List[List[Any]], formats: List[List[str]] = None)
```

Parameters:
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `start_row`: Starting row number (0-based)
- `start_col`: Starting column number (0-based)
- `data`: 2D list of data to write
- `formats`: (Optional) 2D list of format names corresponding to data

### xlsx_add_format

Creates a cell format.

```python
xlsx_add_format(filename: str, format_name: str, properties: Dict[str, Any])
```

Parameters:
- `filename`: Path to the Excel file
- `format_name`: Name to identify the format
- `properties`: Dictionary of format properties (e.g., `{'bold': True, 'font_color': 'red'}`)

### xlsx_add_chart

Adds a chart to a worksheet.

```python
xlsx_add_chart(filename: str, worksheet: str, chart_type: str, data_range: List[Dict[str, Any]], position: Dict[str, int], options: Dict[str, Any] = None)
```

Parameters:
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `chart_type`: Type of chart (e.g., 'column', 'line', 'pie')
- `data_range`: List of data series specifications
- `position`: Dictionary with 'row' and 'col' keys specifying chart position
- `options`: (Optional) Additional chart options

### xlsx_add_image

Adds an image to a worksheet.

```python
xlsx_add_image(filename: str, worksheet: str, image_path: str, position: Dict[str, int], options: Dict[str, Any] = None)
```

Parameters:
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `image_path`: Path to the image file
- `position`: Dictionary with 'row' and 'col' keys specifying image position
- `options`: (Optional) Additional image options

### xlsx_add_formula

Adds a formula to a cell.

```python
xlsx_add_formula(filename: str, worksheet: str, row: int, col: int, formula: str, format: str = None)
```

Parameters:
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `row`: Row number (0-based)
- `col`: Column number (0-based)
- `formula`: Excel formula (e.g., '=SUM(A1:A10)')
- `format`: (Optional) Name of a predefined format

### xlsx_add_table

Adds a table to a worksheet.

```python
xlsx_add_table(filename: str, worksheet: str, start_row: int, start_col: int, end_row: int, end_col: int, options: Dict[str, Any] = None)
```

Parameters:
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `start_row`: Starting row number (0-based)
- `start_col`: Starting column number (0-based)
- `end_row`: Ending row number (0-based)
- `end_col`: Ending column number (0-based)
- `options`: (Optional) Table options (e.g., `{'header_row': True, 'columns': [{'header': 'Name'}]}`)

### xlsx_close_workbook

Closes and saves the workbook.

```python
xlsx_close_workbook(filename: str)
```

Parameters:
- `filename`: Path to the Excel file

## Usage Examples

### Basic Example: Creating a Simple Spreadsheet

```python
# Create a new workbook
result = await mcp.call_tool("xlsx_create_workbook", {"filename": "example.xlsx"})

# Add a worksheet
result = await mcp.call_tool("xlsx_add_worksheet", {"filename": "example.xlsx", "name": "Data"})

# Write headers with bold formatting
result = await mcp.call_tool("xlsx_add_format", {
    "filename": "example.xlsx", 
    "format_name": "header_format", 
    "properties": {"bold": True, "bg_color": "#DDDDDD"}
})

headers = ["ID", "Name", "Value"]
for i, header in enumerate(headers):
    result = await mcp.call_tool("xlsx_write_data", {
        "filename": "example.xlsx", 
        "worksheet": "Data", 
        "row": 0, 
        "col": i, 
        "data": header, 
        "format": "header_format"
    })

# Write data
data = [
    [1, "Apple", 100],
    [2, "Banana", 150],
    [3, "Cherry", 200]
]

result = await mcp.call_tool("xlsx_write_matrix", {
    "filename": "example.xlsx", 
    "worksheet": "Data", 
    "start_row": 1, 
    "start_col": 0, 
    "data": data
})

# Add a formula for the sum
result = await mcp.call_tool("xlsx_add_formula", {
    "filename": "example.xlsx", 
    "worksheet": "Data", 
    "row": 4, 
    "col": 2, 
    "formula": "=SUM(C2:C4)"
})

# Close and save the workbook
result = await mcp.call_tool("xlsx_close_workbook", {"filename": "example.xlsx"})
```

### Advanced Example: Creating a Report with Chart

```python
# Create workbook and worksheet
await mcp.call_tool("xlsx_create_workbook", {"filename": "sales_report.xlsx"})
await mcp.call_tool("xlsx_add_worksheet", {"filename": "sales_report.xlsx", "name": "Sales"})

# Add formats
await mcp.call_tool("xlsx_add_format", {
    "filename": "sales_report.xlsx", 
    "format_name": "title", 
    "properties": {"bold": True, "font_size": 16}
})

await mcp.call_tool("xlsx_add_format", {
    "filename": "sales_report.xlsx", 
    "format_name": "header", 
    "properties": {"bold": True, "bg_color": "#D7E4BC", "border": 1}
})

# Add title
await mcp.call_tool("xlsx_write_data", {
    "filename": "sales_report.xlsx", 
    "worksheet": "Sales", 
    "row": 0, 
    "col": 0, 
    "data": "Quarterly Sales Report", 
    "format": "title"
})

# Add headers
headers = ["Quarter", "North", "South", "East", "West"]
for i, header in enumerate(headers):
    await mcp.call_tool("xlsx_write_data", {
        "filename": "sales_report.xlsx", 
        "worksheet": "Sales", 
        "row": 2, 
        "col": i, 
        "data": header, 
        "format": "header"
    })

# Add data
data = [
    ["Q1", 10000, 8000, 12000, 9000],
    ["Q2", 12000, 9500, 14000, 8500],
    ["Q3", 14500, 10000, 15500, 9500],
    ["Q4", 16000, 12000, 17000, 10000]
]

await mcp.call_tool("xlsx_write_matrix", {
    "filename": "sales_report.xlsx", 
    "worksheet": "Sales", 
    "start_row": 3, 
    "start_col": 0, 
    "data": data
})

# Add chart
chart_data = [
    {
        "name": "North",
        "categories": "=Sales!$A$4:$A$7",
        "values": "=Sales!$B$4:$B$7"
    },
    {
        "name": "South",
        "categories": "=Sales!$A$4:$A$7",
        "values": "=Sales!$C$4:$C$7"
    },
    {
        "name": "East",
        "categories": "=Sales!$A$4:$A$7",
        "values": "=Sales!$D$4:$D$7"
    },
    {
        "name": "West",
        "categories": "=Sales!$A$4:$A$7",
        "values": "=Sales!$E$4:$E$7"
    }
]

chart_options = {
    "title": "Quarterly Sales by Region",
    "x_axis": {"name": "Quarter"},
    "y_axis": {"name": "Sales ($)"},
    "style": 10
}

await mcp.call_tool("xlsx_add_chart", {
    "filename": "sales_report.xlsx", 
    "worksheet": "Sales", 
    "chart_type": "column", 
    "data_range": chart_data, 
    "position": {"row": 8, "col": 1}, 
    "options": chart_options
})

# Add table format
await mcp.call_tool("xlsx_add_table", {
    "filename": "sales_report.xlsx", 
    "worksheet": "Sales", 
    "start_row": 2, 
    "start_col": 0, 
    "end_row": 7, 
    "end_col": 4, 
    "options": {
        "name": "SalesTable",
        "style": "Table Style Medium 2",
        "total_row": True
    }
})

# Close and save
await mcp.call_tool("xlsx_close_workbook", {"filename": "sales_report.xlsx"})
```

## Important Notes

1. XlsxWriter can only **create new files**, not modify existing ones. This is a limitation of the underlying library.

2. Workbooks must be closed with `xlsx_close_workbook()` to be properly saved. Until then, they exist only in memory.

3. The tool maintains state between API calls, allowing for complex operations across multiple requests.

4. Row and column indices are 0-based (as in Python), not 1-based (as in Excel).

5. All functions return JSON strings containing the result or error information.

## Troubleshooting

- **"Workbook not found" error**: Make sure you've created the workbook and are using the correct filename.

- **"Worksheet not found" error**: Ensure the worksheet has been added to the workbook.

- **Error during format application**: Check that the format name has been defined with `xlsx_add_format`.

- **Missing data in saved file**: Ensure you've called `xlsx_close_workbook` to properly save the file.

- **Installation issues**: Verify that the XlsxWriter library is installed with `pip install XlsxWriter`.

## License

This tool is provided under the same license as the MCP Unified Server.

# Enhanced Excel Tool Documentation

The Enhanced Excel Tool extends the existing MCP Excel functionality to include comprehensive support for reading, manipulating, and analyzing Excel and CSV files using pandas. This tool bridges the gap between Excel file management and powerful data analysis capabilities.

## New Features

1. **File Reading Capabilities**
   - Read Excel files (XLSX, XLS) with customizable options
   - Read CSV files with delimiter and encoding support
   - List available sheets in Excel files

2. **DataFrame Management**
   - Store DataFrame objects in memory for multi-step operations
   - List, inspect, and clear DataFrames
   - Convert between DataFrames and Excel/CSV files

3. **Data Manipulation and Analysis**
   - Filter DataFrames by query or column conditions
   - Sort DataFrames by one or multiple columns
   - Group DataFrames and apply aggregation functions
   - Generate statistical descriptions and correlations

## Tool Reference

### Reading Files

#### `xlsx_read_excel`
Read an Excel file into a pandas DataFrame.

```python
xlsx_read_excel(
    filename: str,                            # Path to the Excel file
    sheet_name: Union[str, int] = 0,          # Sheet name or index
    output_id: str = None,                    # ID to store the DataFrame (default: filename)
    header: Union[int, List[int], None] = 0,  # Row(s) to use as column names
    names: List[str] = None,                  # List of custom column names
    skiprows: Union[int, List[int]] = None    # Row indices to skip
)
```

Example:
```
xlsx_read_excel("financial_data.xlsx", sheet_name="Q1_Results", output_id="q1_data")
```

#### `xlsx_read_csv`
Read a CSV file into a pandas DataFrame.

```python
xlsx_read_csv(
    filename: str,                            # Path to the CSV file
    output_id: str = None,                    # ID to store the DataFrame (default: filename)
    delimiter: str = ",",                     # Delimiter to use
    header: Union[int, List[int], None] = 0,  # Row(s) to use as column names
    names: List[str] = None,                  # List of custom column names
    skiprows: Union[int, List[int]] = None,   # Row indices to skip
    encoding: str = None                      # File encoding
)
```

Example:
```
xlsx_read_csv("sales_data.csv", delimiter=";", encoding="utf-8", output_id="sales")
```

#### `xlsx_get_sheet_names`
Get sheet names from an Excel file.

```python
xlsx_get_sheet_names(
    filename: str  # Path to the Excel file
)
```

Example:
```
xlsx_get_sheet_names("financial_data.xlsx")
```

### DataFrame Management

#### `xlsx_dataframe_info`
Get information about a DataFrame.

```python
xlsx_dataframe_info(
    dataframe_id: str  # ID of the DataFrame in memory
)
```

Example:
```
xlsx_dataframe_info("sales_data")
```

#### `xlsx_list_dataframes`
List all DataFrames currently in memory.

```python
xlsx_list_dataframes()
```

#### `xlsx_clear_dataframe`
Remove a DataFrame from memory.

```python
xlsx_clear_dataframe(
    dataframe_id: str  # ID of the DataFrame to clear
)
```

Example:
```
xlsx_clear_dataframe("old_data")
```

#### `xlsx_get_column_values`
Get values from a specific column in a DataFrame.

```python
xlsx_get_column_values(
    dataframe_id: str,  # ID of the DataFrame
    column: str,        # Name of the column
    unique: bool = False,  # Whether to return only unique values
    count: bool = False    # Whether to count occurrences of each value
)
```

Example:
```
xlsx_get_column_values("customer_data", "country", unique=True, count=True)
```

### Data Manipulation

#### `xlsx_filter_dataframe`
Filter a DataFrame by query or column condition.

```python
xlsx_filter_dataframe(
    dataframe_id: str,     # ID of the DataFrame to filter
    query: str = None,     # Query string for filtering
    column: str = None,    # Column name to filter by (alternative to query)
    value: Any = None,     # Value to compare with
    operator: str = "==",  # Comparison operator
    output_id: str = None  # ID to store the filtered DataFrame
)
```

Examples:
```
xlsx_filter_dataframe("sales", query="revenue > 1000 and region == 'North'")
xlsx_filter_dataframe("customers", column="age", value=30, operator=">")
```

#### `xlsx_sort_dataframe`
Sort a DataFrame by columns.

```python
xlsx_sort_dataframe(
    dataframe_id: str,                    # ID of the DataFrame to sort
    by: Union[str, List[str]],            # Column name(s) to sort by
    ascending: Union[bool, List[bool]] = True,  # Sort order
    output_id: str = None                 # ID to store the sorted DataFrame
)
```

Example:
```
xlsx_sort_dataframe("products", by=["category", "price"], ascending=[True, False])
```

#### `xlsx_group_dataframe`
Group a DataFrame and apply aggregation.

```python
xlsx_group_dataframe(
    dataframe_id: str,                         # ID of the DataFrame to group
    by: Union[str, List[str]],                 # Column name(s) to group by
    agg_func: Union[str, Dict[str, str]] = "mean",  # Aggregation function(s)
    output_id: str = None                      # ID to store the grouped DataFrame
)
```

Examples:
```
xlsx_group_dataframe("sales", by="region", agg_func="sum")
xlsx_group_dataframe("orders", by=["product", "region"], 
                    agg_func={"quantity": "sum", "price": "mean"})
```

#### `xlsx_describe_dataframe`
Get statistical description of a DataFrame.

```python
xlsx_describe_dataframe(
    dataframe_id: str,                    # ID of the DataFrame to describe
    include: Union[str, List[str]] = None,  # Types of columns to include
    exclude: Union[str, List[str]] = None,  # Types of columns to exclude
    percentiles: List[float] = None       # List of percentiles to include
)
```

Example:
```
xlsx_describe_dataframe("measurements", include=["number"])
```

#### `xlsx_get_correlation`
Get correlation matrix for a DataFrame.

```python
xlsx_get_correlation(
    dataframe_id: str,     # ID of the DataFrame
    method: str = "pearson"  # Correlation method
)
```

Example:
```
xlsx_get_correlation("stock_prices", method="spearman")
```

### Exporting Data

#### `xlsx_dataframe_to_excel`
Export a DataFrame to an Excel file.

```python
xlsx_dataframe_to_excel(
    dataframe_id: str,        # ID of the DataFrame in memory
    filename: str,            # Path to save the Excel file
    sheet_name: str = "Sheet1",  # Name of the sheet
    index: bool = True        # Whether to include the DataFrame index
)
```

Example:
```
xlsx_dataframe_to_excel("filtered_sales", "filtered_sales_report.xlsx")
```

#### `xlsx_dataframe_to_csv`
Export a DataFrame to a CSV file.

```python
xlsx_dataframe_to_csv(
    dataframe_id: str,     # ID of the DataFrame in memory
    filename: str,         # Path to save the CSV file
    index: bool = True,    # Whether to include the DataFrame index
    encoding: str = "utf-8",  # File encoding
    sep: str = ","         # Delimiter to use
)
```

Example:
```
xlsx_dataframe_to_csv("quarterly_data", "quarterly_report.csv", sep=";")
```

## Common Workflows

### Reading and Analyzing Sales Data

```
# Read the Excel file
xlsx_read_excel("sales_data.xlsx", sheet_name="2023", output_id="sales_2023")

# Get information about the DataFrame
xlsx_dataframe_info("sales_2023")

# Filter to specific region
xlsx_filter_dataframe("sales_2023", column="region", value="North", output_id="north_sales")

# Group by product category and calculate total sales
xlsx_group_dataframe("north_sales", by="category", 
                    agg_func={"revenue": "sum", "units": "sum"},
                    output_id="north_by_category")

# Export the grouped data
xlsx_dataframe_to_excel("north_by_category", "north_region_sales_by_category.xlsx")
```

### Reading CSV and Finding Correlations

```
# Read the CSV file
xlsx_read_csv("stock_prices.csv", output_id="stocks")

# Calculate correlation between stock prices
xlsx_get_correlation("stocks", method="pearson")

# Filter to relevant time period
xlsx_filter_dataframe("stocks", query="date >= '2023-01-01' and date <= '2023-12-31'", 
                     output_id="stocks_2023")

# Calculate new correlation on filtered data
xlsx_get_correlation("stocks_2023")
```

## Dependencies

This tool requires the following Python packages:
- xlsxwriter (required for Excel writing)
- pandas (required for all functionality)
- openpyxl (recommended for Excel reading)
- xlrd (recommended for reading older Excel formats)

## Technical Notes

- DataFrames are stored in memory with a unique ID for reference in subsequent operations
- File paths should be absolute or relative to the current working directory
- Large DataFrames will be kept in memory until explicitly cleared with `xlsx_clear_dataframe`
