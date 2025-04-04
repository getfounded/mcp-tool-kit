#!/usr/bin/env python3
"""
Excel tools implementation using the decorator pattern.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.excel.excel_service import ExcelService

# Workbook Creation and Manipulation Tools

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Create a new Excel workbook"
)
def xlsx_create_workbook(self, filename: str) -> Dict[str, Any]:
    """
    Create a new Excel workbook.

    Creates an empty Excel file at the specified location.

    Args:
        filename: Path to save the Excel file

    Returns:
        Dictionary with operation result
    """
    return self.create_workbook(filename)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Add a worksheet to an Excel workbook"
)
def xlsx_add_worksheet(self, filename: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a worksheet to the workbook.

    Creates a new worksheet in the specified Excel file.

    Args:
        filename: Path to the Excel file
        name: (Optional) Name for the worksheet

    Returns:
        Dictionary with operation result
    """
    return self.add_worksheet(filename, name)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Write data to a cell in a worksheet"
)
def xlsx_write_data(
    self, 
    filename: str, 
    worksheet: str, 
    row: int, 
    col: int,
    data: Any, 
    format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Write data to a cell in a worksheet.

    Adds content to a specific cell in an Excel worksheet.

    Args:
        filename: Path to the Excel file
        worksheet: Name of the worksheet
        row: Row number (0-based)
        col: Column number (0-based)
        data: Data to write
        format: (Optional) Name of a predefined format

    Returns:
        Dictionary with operation result
    """
    return self.write_data(filename, worksheet, row, col, data, format)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Write a matrix of data to a worksheet"
)
def xlsx_write_matrix(
    self,
    filename: str, 
    worksheet: str, 
    start_row: int, 
    start_col: int,
    data: List[List[Any]], 
    formats: Optional[List[List[str]]] = None
) -> Dict[str, Any]:
    """
    Write a matrix of data to a worksheet.

    Adds a 2D array of data to an Excel worksheet, starting at a specific location.

    Args:
        filename: Path to the Excel file
        worksheet: Name of the worksheet
        start_row: Starting row number (0-based)
        start_col: Starting column number (0-based)
        data: 2D list of data to write
        formats: (Optional) 2D list of format names corresponding to data

    Returns:
        Dictionary with operation result
    """
    return self.write_matrix(filename, worksheet, start_row, start_col, data, formats)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Create a cell format for Excel"
)
def xlsx_add_format(
    self,
    filename: str, 
    format_name: str, 
    properties: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a cell format.

    Defines a reusable format for cells in an Excel workbook.

    Args:
        filename: Path to the Excel file
        format_name: Name to identify the format
        properties: Dictionary of format properties (e.g., {'bold': True, 'font_color': 'red'})

    Returns:
        Dictionary with operation result
    """
    return self.add_format(filename, format_name, properties)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Add a chart to an Excel worksheet"
)
def xlsx_add_chart(
    self,
    filename: str, 
    worksheet: str, 
    chart_type: str, 
    data_range: List[Dict[str, Any]],
    position: Dict[str, int], 
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add a chart to a worksheet.

    Creates a chart in an Excel worksheet using specified data series.

    Args:
        filename: Path to the Excel file
        worksheet: Name of the worksheet
        chart_type: Type of chart (e.g., 'column', 'line', 'pie')
        data_range: List of data series specifications
        position: Dictionary with 'row' and 'col' keys specifying chart position
        options: (Optional) Additional chart options

    Returns:
        Dictionary with operation result
    """
    return self.add_chart(filename, worksheet, chart_type, data_range, position, options)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Add an image to an Excel worksheet"
)
def xlsx_add_image(
    self,
    filename: str, 
    worksheet: str, 
    image_path: str,
    position: Dict[str, int], 
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add an image to a worksheet.

    Inserts an image into an Excel worksheet at the specified position.

    Args:
        filename: Path to the Excel file
        worksheet: Name of the worksheet
        image_path: Path to the image file
        position: Dictionary with 'row' and 'col' keys specifying image position
        options: (Optional) Additional image options

    Returns:
        Dictionary with operation result
    """
    return self.add_image(filename, worksheet, image_path, position, options)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Add a formula to a cell in an Excel worksheet"
)
def xlsx_add_formula(
    self,
    filename: str, 
    worksheet: str, 
    row: int, 
    col: int,
    formula: str, 
    format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a formula to a cell.

    Inserts an Excel formula into a specific cell.

    Args:
        filename: Path to the Excel file
        worksheet: Name of the worksheet
        row: Row number (0-based)
        col: Column number (0-based)
        formula: Excel formula (e.g., '=SUM(A1:A10)')
        format: (Optional) Name of a predefined format

    Returns:
        Dictionary with operation result
    """
    return self.add_formula(filename, worksheet, row, col, formula, format)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Add a table to an Excel worksheet"
)
def xlsx_add_table(
    self,
    filename: str, 
    worksheet: str, 
    start_row: int, 
    start_col: int,
    end_row: int, 
    end_col: int, 
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add a table to a worksheet.

    Creates a formatted table in an Excel worksheet from a range of cells.

    Args:
        filename: Path to the Excel file
        worksheet: Name of the worksheet
        start_row: Starting row number (0-based)
        start_col: Starting column number (0-based)
        end_row: Ending row number (0-based)
        end_col: Ending column number (0-based)
        options: (Optional) Table options (e.g., {'header_row': True, 'columns': [{'header': 'Name'}]})

    Returns:
        Dictionary with operation result
    """
    return self.add_table(filename, worksheet, start_row, start_col, end_row, end_col, options)

@register_tool(
    category="spreadsheets",
    service_class=ExcelService,
    description="Close and save an Excel workbook"
)
def xlsx_close_workbook(self, filename: str) -> Dict[str, Any]:
    """
    Close and save the workbook.

    Saves changes and closes an Excel workbook.

    Args:
        filename: Path to the Excel file

    Returns:
        Dictionary with operation result
    """
    return self.close_workbook(filename)

# Excel File Reading Tools

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Read an Excel file into a DataFrame"
)
def xlsx_read_excel(
    self,
    filename: str, 
    sheet_name: Union[str, int] = 0,
    output_id: Optional[str] = None, 
    header: Union[int, List[int], None] = 0,
    names: Optional[List[str]] = None, 
    skiprows: Union[int, List[int], None] = None
) -> Dict[str, Any]:
    """
    Read an Excel file into a pandas DataFrame.

    Imports Excel data into a DataFrame for analysis.

    Args:
        filename: Path to the Excel file
        sheet_name: Sheet name or index (default: 0)
        output_id: ID to store the DataFrame in memory (default: filename)
        header: Row(s) to use as column names (default: 0)
        names: List of custom column names (default: None)
        skiprows: Row indices to skip or number of rows to skip (default: None)

    Returns:
        Dictionary with DataFrame information
    """
    # Set default output_id to filename without extension
    if not output_id:
        import os
        output_id = os.path.splitext(os.path.basename(filename))[0]

    # Read the Excel file
    result = self.read_excel(
        filename, 
        sheet_name=sheet_name, 
        header=header,
        names=names, 
        skiprows=skiprows
    )

    # Handle both single sheet and multiple sheets
    if isinstance(result, dict) and "error" in result:
        return result

    elif isinstance(result, dict) and "sheets" in result:
        # Multiple sheets returned
        sheet_info = {}
        for sheet_name, df in result["dataframes"].items():
            sheet_id = f"{output_id}_{sheet_name}"
            self.store_dataframe(sheet_id, df)
            info = self.dataframe_info(df)
            sheet_info[sheet_name] = {
                "dataframe_id": sheet_id,
                "shape": info["shape"],
                "columns": info["columns"]
            }

        return {
            "filename": filename,
            "sheets": result["sheets"],
            "sheet_info": sheet_info,
            "status": "read",
            "message": f"Multiple sheets read. Access individual DataFrames using their IDs."
        }

    else:
        # Single sheet returned
        self.store_dataframe(output_id, result)
        info = self.dataframe_info(result)

        return {
            "filename": filename,
            "dataframe_id": output_id,
            "shape": info["shape"],
            "columns": info["columns"],
            "dtypes": info["dtypes"],
            "has_nulls": info["has_nulls"],
            "head": info["head"],
            "status": "read"
        }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Read a CSV file into a DataFrame"
)
def xlsx_read_csv(
    self,
    filename: str, 
    output_id: Optional[str] = None, 
    delimiter: str = ",",
    header: Union[int, List[int], None] = 0, 
    names: Optional[List[str]] = None,
    skiprows: Union[int, List[int], None] = None, 
    encoding: Optional[str] = None
) -> Dict[str, Any]:
    """
    Read a CSV file into a pandas DataFrame.

    Imports CSV data into a DataFrame for analysis.

    Args:
        filename: Path to the CSV file
        output_id: ID to store the DataFrame in memory (default: filename)
        delimiter: Delimiter to use (default: ",")
        header: Row(s) to use as column names (default: 0)
        names: List of custom column names (default: None)
        skiprows: Row indices to skip or number of rows to skip (default: None)
        encoding: File encoding (default: None, pandas will try to detect)

    Returns:
        Dictionary with DataFrame information
    """
    # Set default output_id to filename without extension
    if not output_id:
        import os
        output_id = os.path.splitext(os.path.basename(filename))[0]

    # Read the CSV file
    kwargs = {
        "delimiter": delimiter,
        "header": header,
        "skiprows": skiprows
    }

    if names:
        kwargs["names"] = names

    if encoding:
        kwargs["encoding"] = encoding

    result = self.read_csv(filename, **kwargs)

    if isinstance(result, dict) and "error" in result:
        return result

    # Store DataFrame in memory
    self.store_dataframe(output_id, result)

    # Get DataFrame info
    info = self.dataframe_info(result)

    return {
        "filename": filename,
        "dataframe_id": output_id,
        "shape": info["shape"],
        "columns": info["columns"],
        "dtypes": info["dtypes"],
        "has_nulls": info["has_nulls"],
        "head": info["head"],
        "status": "read"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Get sheet names from an Excel file"
)
def xlsx_get_sheet_names(self, filename: str) -> Dict[str, Any]:
    """
    Get sheet names from an Excel file.

    Retrieves a list of all worksheet names in an Excel file.

    Args:
        filename: Path to the Excel file

    Returns:
        Dictionary with sheet names
    """
    result = self.get_excel_sheet_names(filename)

    if isinstance(result, dict) and "error" in result:
        return result

    return {
        "filename": filename,
        "sheet_names": result,
        "count": len(result),
        "status": "success"
    }

# DataFrame Management Tools

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Get information about a DataFrame"
)
def xlsx_dataframe_info(self, dataframe_id: str) -> Dict[str, Any]:
    """
    Get information about a DataFrame.

    Retrieves metadata and basic statistics about a stored DataFrame.

    Args:
        dataframe_id: ID of the DataFrame in memory

    Returns:
        Dictionary with DataFrame information
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Get DataFrame info
    info = self.dataframe_info(df)

    if isinstance(info, dict) and "error" in info:
        return info

    return {
        "dataframe_id": dataframe_id,
        "shape": info["shape"],
        "columns": info["columns"],
        "dtypes": info["dtypes"],
        "has_nulls": info["has_nulls"],
        "memory_usage": info["memory_usage"],
        "info": info["info"],
        "head": info["head"],
        "status": "success"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="List all DataFrames in memory"
)
def xlsx_list_dataframes(self) -> Dict[str, Any]:
    """
    List all DataFrames currently in memory.

    Returns a list of all stored DataFrames with basic information.

    Returns:
        Dictionary with list of DataFrame IDs and basic info
    """
    dataframe_ids = self.list_dataframes()

    # Get basic info for each DataFrame
    dataframes_info = {}
    
    for df_id in dataframe_ids:
        df = self.get_dataframe(df_id)
        if df is not None:
            dataframes_info[df_id] = {
                "shape": df.shape,
                "columns": list(df.columns)
            }

    return {
        "dataframe_ids": dataframe_ids,
        "count": len(dataframe_ids),
        "dataframes_info": dataframes_info,
        "status": "success"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Remove a DataFrame from memory"
)
def xlsx_clear_dataframe(self, dataframe_id: str) -> Dict[str, Any]:
    """
    Remove a DataFrame from memory.

    Deletes a stored DataFrame to free up memory.

    Args:
        dataframe_id: ID of the DataFrame to clear

    Returns:
        Dictionary with operation result
    """
    result = self.clear_dataframe(dataframe_id)

    if result:
        return {
            "dataframe_id": dataframe_id,
            "status": "cleared",
            "message": f"DataFrame with ID '{dataframe_id}' has been removed from memory"
        }
    else:
        return {
            "error": f"DataFrame with ID '{dataframe_id}' not found",
            "status": "not_found"
        }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Get values from a specific column in a DataFrame"
)
def xlsx_get_column_values(
    self,
    dataframe_id: str, 
    column: str, 
    unique: bool = False,
    count: bool = False
) -> Dict[str, Any]:
    """
    Get values from a specific column in a DataFrame.

    Retrieves values or counts from a column for analysis.

    Args:
        dataframe_id: ID of the DataFrame
        column: Name of the column to get values from
        unique: Whether to return only unique values (default: False)
        count: Whether to count occurrences of each value (default: False)

    Returns:
        Dictionary with column values or counts
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Get column values
    result = self.get_column_values(df, column, unique, count)
    
    if "error" in result:
        return result
        
    result["dataframe_id"] = dataframe_id
    return result

# Data Analysis Tools

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Filter a DataFrame by query or column condition"
)
def xlsx_filter_dataframe(
    self,
    dataframe_id: str, 
    query: Optional[str] = None, 
    column: Optional[str] = None,
    value: Any = None, 
    operator: str = "==",
    output_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filter a DataFrame by query or column condition.

    Selects rows from a DataFrame that match specified criteria.

    Args:
        dataframe_id: ID of the DataFrame to filter
        query: Query string for filtering (e.g., "column > 5 and column2 == 'value'")
        column: Column name to filter by (alternative to query)
        value: Value to compare with (used with column and operator)
        operator: Comparison operator (used with column and value): ==, !=, >, >=, <, <=, in, contains
        output_id: ID to store the filtered DataFrame (default: dataframe_id + "_filtered")

    Returns:
        Dictionary with filter operation result
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Set default output ID if not provided
    if not output_id:
        output_id = f"{dataframe_id}_filtered"

    # Filter the DataFrame
    if query:
        # Filter by query string
        filtered_df = self.filter_dataframe(df, query=query)
    elif column and value is not None:
        # Filter by column and value
        filtered_df = self.filter_dataframe(df, column=column, value=value, operator=operator)
    else:
        return {"error": "Either query or column+value must be provided"}

    if isinstance(filtered_df, dict) and "error" in filtered_df:
        return filtered_df

    # Store filtered DataFrame
    self.store_dataframe(output_id, filtered_df)

    # Get DataFrame info
    info = self.dataframe_info(filtered_df)

    return {
        "original_id": dataframe_id,
        "filtered_id": output_id,
        "original_rows": df.shape[0],
        "filtered_rows": filtered_df.shape[0],
        "columns": info["columns"],
        "head": info["head"],
        "status": "filtered"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Sort a DataFrame by columns"
)
def xlsx_sort_dataframe(
    self,
    dataframe_id: str, 
    by: Union[str, List[str]],
    ascending: Union[bool, List[bool]] = True,
    output_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sort a DataFrame by columns.

    Orders the rows of a DataFrame according to values in specified columns.

    Args:
        dataframe_id: ID of the DataFrame to sort
        by: Column name(s) to sort by (string or list of strings)
        ascending: Whether to sort in ascending order (boolean or list of booleans)
        output_id: ID to store the sorted DataFrame (default: dataframe_id + "_sorted")

    Returns:
        Dictionary with sort operation result
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Set default output ID if not provided
    if not output_id:
        output_id = f"{dataframe_id}_sorted"

    # Sort the DataFrame
    sorted_df = self.sort_dataframe(df, by=by, ascending=ascending)

    if isinstance(sorted_df, dict) and "error" in sorted_df:
        return sorted_df

    # Store sorted DataFrame
    self.store_dataframe(output_id, sorted_df)

    # Get DataFrame info
    info = self.dataframe_info(sorted_df)

    return {
        "original_id": dataframe_id,
        "sorted_id": output_id,
        "sorted_by": by if isinstance(by, str) else list(by),
        "ascending": ascending if isinstance(ascending, bool) else list(ascending),
        "rows": sorted_df.shape[0],
        "head": info["head"],
        "status": "sorted"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Group a DataFrame and apply aggregation"
)
def xlsx_group_dataframe(
    self,
    dataframe_id: str, 
    by: Union[str, List[str]],
    agg_func: Union[str, Dict[str, str]] = "mean",
    output_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Group a DataFrame and apply aggregation.

    Groups data by specified columns and calculates aggregate statistics.

    Args:
        dataframe_id: ID of the DataFrame to group
        by: Column name(s) to group by (string or list of strings)
        agg_func: Aggregation function(s) to apply (string or dict of column->function)
        output_id: ID to store the grouped DataFrame (default: dataframe_id + "_grouped")

    Returns:
        Dictionary with group operation result
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Set default output ID if not provided
    if not output_id:
        output_id = f"{dataframe_id}_grouped"

    # Group the DataFrame
    grouped_df = self.group_dataframe(df, by=by, agg_func=agg_func)

    if isinstance(grouped_df, dict) and "error" in grouped_df:
        return grouped_df

    # Store grouped DataFrame
    self.store_dataframe(output_id, grouped_df)

    # Get DataFrame info
    info = self.dataframe_info(grouped_df)

    return {
        "original_id": dataframe_id,
        "grouped_id": output_id,
        "grouped_by": by if isinstance(by, str) else list(by),
        "agg_func": agg_func if isinstance(agg_func, str) else dict(agg_func),
        "rows": grouped_df.shape[0],
        "head": info["head"],
        "status": "grouped"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Get statistical description of a DataFrame"
)
def xlsx_describe_dataframe(
    self,
    dataframe_id: str, 
    include: Union[str, List[str]] = None,
    exclude: Union[str, List[str]] = None,
    percentiles: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Get statistical description of a DataFrame.

    Calculates summary statistics of DataFrame columns.

    Args:
        dataframe_id: ID of the DataFrame to describe
        include: Types of columns to include (None, 'all', or list of dtypes)
        exclude: Types of columns to exclude (None or list of dtypes)
        percentiles: List of percentiles to include in output (default: [0.25, 0.5, 0.75])

    Returns:
        Dictionary with statistical description
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Describe the DataFrame
    result = self.describe_dataframe(df, include=include, exclude=exclude, percentiles=percentiles)

    if isinstance(result, dict) and "error" in result:
        return result

    return {
        "dataframe_id": dataframe_id,
        "description": result,
        "status": "described"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Get correlation matrix for a DataFrame"
)
def xlsx_get_correlation(
    self,
    dataframe_id: str, 
    method: str = "pearson"
) -> Dict[str, Any]:
    """
    Get correlation matrix for a DataFrame.

    Calculates the correlation between columns in a DataFrame.

    Args:
        dataframe_id: ID of the DataFrame
        method: Correlation method ('pearson', 'kendall', or 'spearman')

    Returns:
        Dictionary with correlation matrix
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Calculate correlation matrix
    result = self.get_correlation(df, method=method)
    
    if "error" in result:
        return result
        
    result["dataframe_id"] = dataframe_id
    return result

# DataFrame Export Tools

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Export a DataFrame to an Excel file"
)
def xlsx_dataframe_to_excel(
    self,
    dataframe_id: str, 
    filename: str, 
    sheet_name: str = "Sheet1",
    index: bool = True
) -> Dict[str, Any]:
    """
    Export a DataFrame to an Excel file.

    Saves a DataFrame to an Excel file for sharing or further use.

    Args:
        dataframe_id: ID of the DataFrame in memory
        filename: Path to save the Excel file
        sheet_name: Name of the sheet (default: "Sheet1")
        index: Whether to include the DataFrame index (default: True)

    Returns:
        Dictionary with export operation result
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Export to Excel
    result = self.dataframe_to_excel(df, filename, sheet_name=sheet_name, index=index)

    if isinstance(result, dict) and "error" in result:
        return result

    return {
        "dataframe_id": dataframe_id,
        "filename": filename,
        "sheet_name": sheet_name,
        "rows": result["rows"],
        "columns": result["columns"],
        "status": "exported"
    }

@register_tool(
    category="data_analysis",
    service_class=ExcelService,
    description="Export a DataFrame to a CSV file"
)
def xlsx_dataframe_to_csv(
    self,
    dataframe_id: str, 
    filename: str, 
    index: bool = True,
    encoding: str = "utf-8", 
    sep: str = ","
) -> Dict[str, Any]:
    """
    Export a DataFrame to a CSV file.

    Saves a DataFrame to a CSV file for sharing or further use.

    Args:
        dataframe_id: ID of the DataFrame in memory
        filename: Path to save the CSV file
        index: Whether to include the DataFrame index (default: True)
        encoding: File encoding (default: "utf-8")
        sep: Delimiter to use (default: ",")

    Returns:
        Dictionary with export operation result
    """
    # Get DataFrame from memory
    df = self.get_dataframe(dataframe_id)
    if df is None:
        return {"error": f"DataFrame with ID '{dataframe_id}' not found"}

    # Export to CSV
    result = self.dataframe_to_csv(df, filename, index=index, encoding=encoding, sep=sep)

    if isinstance(result, dict) and "error" in result:
        return result

    return {
        "dataframe_id": dataframe_id,
        "filename": filename,
        "rows": result["rows"],
        "columns": result["columns"],
        "status": "exported"
    }
