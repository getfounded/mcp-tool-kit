# Excel Tool

## Overview
The Excel Tool provides comprehensive functionality for working with Excel and CSV files. It enables spreadsheet creation, data manipulation, analysis, and visualization directly from MCP.

## Features
- Workbook and worksheet management
- Cell data writing and formatting
- Table, chart, and image insertion
- Formula support
- Excel and CSV file reading/writing
- Pandas DataFrame integration
- Data analysis operations (filtering, sorting, grouping)
- Statistical functions

## Requirements
- Pandas for data manipulation and analysis
- XlsxWriter for Excel file creation
- Openpyxl for Excel file reading and modification

## Usage Examples

### Spreadsheet Creation
```python
# Create a new workbook
result = await xlsx_create_workbook(filename="/path/to/new_workbook.xlsx")

# Add a worksheet
result = await xlsx_add_worksheet(
    filename="/path/to/new_workbook.xlsx",
    name="Sales Data"
)

# Write data to cells
result = await xlsx_write_data(
    filename="/path/to/new_workbook.xlsx",
    worksheet="Sales Data",
    row=0,
    col=0,
    data="Product"
)

# Write a matrix of data
data_matrix = [
    ["Product", "Q1", "Q2", "Q3", "Q4"],
    ["Widgets", 5200, 5500, 4900, 6100],
    ["Gadgets", 4100, 4300, 4700, 5200]
]

result = await xlsx_write_matrix(
    filename="/path/to/new_workbook.xlsx",
    worksheet="Sales Data",
    start_row=0,
    start_col=0,
    data=data_matrix
)

# Save and close the workbook
result = await xlsx_close_workbook(filename="/path/to/new_workbook.xlsx")
```

### Cell Formatting
```python
# Create a format for headers
result = await xlsx_add_format(
    filename="/path/to/workbook.xlsx",
    format_name="header_format",
    properties={
        "bold": True,
        "font_color": "white",
        "bg_color": "#4F81BD",
        "align": "center"
    }
)

# Write formatted data
result = await xlsx_write_data(
    filename="/path/to/workbook.xlsx",
    worksheet="Sheet1",
    row=0,
    col=0,
    data="Quarter",
    format="header_format"
)
```

### Adding Charts and Formulas
```python
# Add a formula
result = await xlsx_add_formula(
    filename="/path/to/workbook.xlsx",
    worksheet="Sheet1",
    row=10,
    col=1,
    formula="=SUM(B2:B9)"
)

# Add a chart
result = await xlsx_add_chart(
    filename="/path/to/workbook.xlsx",
    worksheet="Sheet1",
    chart_type="column",
    data_range=[
        {
            "categories": "=Sheet1!$A$2:$A$7",
            "values": "=Sheet1!$B$2:$B$7",
            "name": "Sales"
        }
    ],
    position={"row": 15, "col": 1}
)
```

### Data Analysis
```python
# Read an Excel file into a DataFrame
result = await xlsx_read_excel(
    filename="/path/to/data.xlsx",
    sheet_name="Sales",
    output_id="sales_data"
)

# Get information about the DataFrame
info = await xlsx_dataframe_info(dataframe_id="sales_data")

# Filter data
filtered = await xlsx_filter_dataframe(
    dataframe_id="sales_data",
    query="Revenue > 5000 and Region == 'North'"
)

# Group and aggregate data
grouped = await xlsx_group_dataframe(
    dataframe_id="sales_data",
    by=["Region", "Product"],
    agg_func={"Revenue": "sum", "Units": "mean"}
)

# Get statistical description
stats = await xlsx_describe_dataframe(dataframe_id="sales_data")

# Get correlation matrix
corr = await xlsx_get_correlation(
    dataframe_id="sales_data",
    method="pearson"
)

# Export results to new Excel file
result = await xlsx_dataframe_to_excel(
    dataframe_id="sales_data_grouped",
    filename="/path/to/export.xlsx"
)
```

## API Reference

### Workbook Creation and Management

#### xlsx_create_workbook
Create a new Excel workbook.

**Parameters:**
- `filename`: Path to save the Excel file

**Returns:**
- Dictionary with operation result

#### xlsx_add_worksheet
Add a worksheet to the workbook.

**Parameters:**
- `filename`: Path to the Excel file
- `name`: (Optional) Name for the worksheet

**Returns:**
- Dictionary with operation result

#### xlsx_close_workbook
Close and save the workbook.

**Parameters:**
- `filename`: Path to the Excel file

**Returns:**
- Dictionary with operation result

### Cell and Data Operations

#### xlsx_write_data
Write data to a cell in a worksheet.

**Parameters:**
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `row`: Row number (0-based)
- `col`: Column number (0-based)
- `data`: Data to write
- `format`: (Optional) Name of a predefined format

**Returns:**
- Dictionary with operation result

#### xlsx_write_matrix
Write a matrix of data to a worksheet.

**Parameters:**
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `start_row`: Starting row number (0-based)
- `start_col`: Starting column number (0-based)
- `data`: 2D list of data to write
- `formats`: (Optional) 2D list of format names corresponding to data

**Returns:**
- Dictionary with operation result

#### xlsx_add_format
Create a cell format.

**Parameters:**
- `filename`: Path to the Excel file
- `format_name`: Name to identify the format
- `properties`: Dictionary of format properties (e.g., {'bold': True, 'font_color': 'red'})

**Returns:**
- Dictionary with operation result

#### xlsx_add_formula
Add a formula to a cell.

**Parameters:**
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `row`: Row number (0-based)
- `col`: Column number (0-based)
- `formula`: Excel formula (e.g., '=SUM(A1:A10)')
- `format`: (Optional) Name of a predefined format

**Returns:**
- Dictionary with operation result

### Visual Elements

#### xlsx_add_chart
Add a chart to a worksheet.

**Parameters:**
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `chart_type`: Type of chart (e.g., 'column', 'line', 'pie')
- `data_range`: List of data series specifications
- `position`: Dictionary with 'row' and 'col' keys specifying chart position
- `options`: (Optional) Additional chart options

**Returns:**
- Dictionary with operation result

#### xlsx_add_image
Add an image to a worksheet.

**Parameters:**
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `image_path`: Path to the image file
- `position`: Dictionary with 'row' and 'col' keys specifying image position
- `options`: (Optional) Additional image options

**Returns:**
- Dictionary with operation result

#### xlsx_add_table
Add a table to a worksheet.

**Parameters:**
- `filename`: Path to the Excel file
- `worksheet`: Name of the worksheet
- `start_row`: Starting row number (0-based)
- `start_col`: Starting column number (0-based)
- `end_row`: Ending row number (0-based)
- `end_col`: Ending column number (0-based)
- `options`: (Optional) Table options

**Returns:**
- Dictionary with operation result

### Data Import

#### xlsx_read_excel
Read an Excel file into a pandas DataFrame.

**Parameters:**
- `filename`: Path to the Excel file
- `sheet_name`: Sheet name or index (default: 0)
- `output_id`: ID to store the DataFrame in memory (default: filename)
- `header`: Row(s) to use as column names (default: 0)
- `names`: List of custom column names (default: None)
- `skiprows`: Row indices to skip or number of rows to skip (default: None)

**Returns:**
- Dictionary with DataFrame information

#### xlsx_read_csv
Read a CSV file into a pandas DataFrame.

**Parameters:**
- `filename`: Path to the CSV file
- `output_id`: ID to store the DataFrame in memory (default: filename)
- `delimiter`: Delimiter to use (default: ",")
- `header`: Row(s) to use as column names (default: 0)
- `names`: List of custom column names (default: None)
- `skiprows`: Row indices to skip or number of rows to skip (default: None)
- `encoding`: File encoding (default: None, pandas will try to detect)

**Returns:**
- Dictionary with DataFrame information

#### xlsx_get_sheet_names
Get sheet names from an Excel file.

**Parameters:**
- `filename`: Path to the Excel file

**Returns:**
- Dictionary with sheet names

### DataFrame Management

#### xlsx_dataframe_info
Get information about a DataFrame.

**Parameters:**
- `dataframe_id`: ID of the DataFrame in memory

**Returns:**
- Dictionary with DataFrame information

#### xlsx_list_dataframes
List all DataFrames currently in memory.

**Returns:**
- Dictionary with list of DataFrame IDs and basic info

#### xlsx_clear_dataframe
Remove a DataFrame from memory.

**Parameters:**
- `dataframe_id`: ID of the DataFrame to clear

**Returns:**
- Dictionary with operation result

#### xlsx_get_column_values
Get values from a specific column in a DataFrame.

**Parameters:**
- `dataframe_id`: ID of the DataFrame
- `column`: Name of the column to get values from
- `unique`: Whether to return only unique values (default: False)
- `count`: Whether to count occurrences of each value (default: False)

**Returns:**
- Dictionary with column values or counts

### Data Analysis

#### xlsx_filter_dataframe
Filter a DataFrame by query or column condition.

**Parameters:**
- `dataframe_id`: ID of the DataFrame to filter
- `query`: Query string for filtering (e.g., "column > 5 and column2 == 'value'")
- `column`: Column name to filter by (alternative to query)
- `value`: Value to compare with (used with column and operator)
- `operator`: Comparison operator (used with column and value): ==, !=, >, >=, <, <=, in, contains
- `output_id`: ID to store the filtered DataFrame (default: dataframe_id + "_filtered")

**Returns:**
- Dictionary with filter operation result

#### xlsx_sort_dataframe
Sort a DataFrame by columns.

**Parameters:**
- `dataframe_id`: ID of the DataFrame to sort
- `by`: Column name(s) to sort by (string or list of strings)
- `ascending`: Whether to sort in ascending order (boolean or list of booleans)
- `output_id`: ID to store the sorted DataFrame (default: dataframe_id + "_sorted")

**Returns:**
- Dictionary with sort operation result

#### xlsx_group_dataframe
Group a DataFrame and apply aggregation.

**Parameters:**
- `dataframe_id`: ID of the DataFrame to group
- `by`: Column name(s) to group by (string or list of strings)
- `agg_func`: Aggregation function(s) to apply (string or dict of column->function)
- `output_id`: ID to store the grouped DataFrame (default: dataframe_id + "_grouped")

**Returns:**
- Dictionary with group operation result

#### xlsx_describe_dataframe
Get statistical description of a DataFrame.

**Parameters:**
- `dataframe_id`: ID of the DataFrame to describe
- `include`: Types of columns to include (None, 'all', or list of dtypes)
- `exclude`: Types of columns to exclude (None or list of dtypes)
- `percentiles`: List of percentiles to include in output (default: [0.25, 0.5, 0.75])

**Returns:**
- Dictionary with statistical description

#### xlsx_get_correlation
Get correlation matrix for a DataFrame.

**Parameters:**
- `dataframe_id`: ID of the DataFrame
- `method`: Correlation method ('pearson', 'kendall', or 'spearman')

**Returns:**
- Dictionary with correlation matrix

### Data Export

#### xlsx_dataframe_to_excel
Export a DataFrame to an Excel file.

**Parameters:**
- `dataframe_id`: ID of the DataFrame in memory
- `filename`: Path to save the Excel file
- `sheet_name`: Name of the sheet (default: "Sheet1")
- `index`: Whether to include the DataFrame index (default: True)

**Returns:**
- Dictionary with export operation result

#### xlsx_dataframe_to_csv
Export a DataFrame to a CSV file.

**Parameters:**
- `dataframe_id`: ID of the DataFrame in memory
- `filename`: Path to save the CSV file
- `index`: Whether to include the DataFrame index (default: True)
- `encoding`: File encoding (default: "utf-8")
- `sep`: Delimiter to use (default: ",")

**Returns:**
- Dictionary with export operation result

## Error Handling
All functions return JSON objects with error information when operations fail. Common errors include:
- File not found
- Invalid worksheet name
- Cell or format not found
- Invalid data types
- DataFrame operations failing due to incompatible types

## Limitations
- Memory usage can be high when working with large DataFrames
- Some Excel features might not be fully supported
- Performance may be impacted when working with very large spreadsheets
