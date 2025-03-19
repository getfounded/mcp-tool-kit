#!/usr/bin/env python3
import os
import json
import logging
import io
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Tuple
import pandas as pd

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("XlsxWriter tools MCP reference set")


class XlsxWriterTools(str, Enum):
    """Enum of XlsxWriter tool names"""
    # Existing tools
    CREATE_WORKBOOK = "xlsx_create_workbook"
    ADD_WORKSHEET = "xlsx_add_worksheet"
    WRITE_DATA = "xlsx_write_data"
    WRITE_MATRIX = "xlsx_write_matrix"
    ADD_FORMAT = "xlsx_add_format"
    ADD_CHART = "xlsx_add_chart"
    ADD_IMAGE = "xlsx_add_image"
    ADD_FORMULA = "xlsx_add_formula"
    ADD_TABLE = "xlsx_add_table"
    CLOSE_WORKBOOK = "xlsx_close_workbook"

    # New reading tools
    READ_EXCEL = "xlsx_read_excel"
    READ_CSV = "xlsx_read_csv"
    GET_SHEET_NAMES = "xlsx_get_sheet_names"

    # New manipulation tools
    FILTER_DATAFRAME = "xlsx_filter_dataframe"
    SORT_DATAFRAME = "xlsx_sort_dataframe"
    GROUP_DATAFRAME = "xlsx_group_dataframe"
    MODIFY_COLUMNS = "xlsx_modify_columns"
    DESCRIBE_DATAFRAME = "xlsx_describe_dataframe"

    # New export tools
    DATAFRAME_TO_EXCEL = "xlsx_dataframe_to_excel"
    DATAFRAME_TO_CSV = "xlsx_dataframe_to_csv"


# Storage for DataFrames in memory
_dataframes = {}


def _store_dataframe(dataframe_id, df):
    """Store DataFrame in memory for future operations"""
    _dataframes[dataframe_id] = df
    return dataframe_id


def _get_dataframe(dataframe_id):
    """Retrieve DataFrame from memory"""
    return _dataframes.get(dataframe_id)


def _list_dataframes():
    """List all available DataFrames in memory"""
    return list(_dataframes.keys())


def _clear_dataframe(dataframe_id):
    """Remove DataFrame from memory"""
    if dataframe_id in _dataframes:
        del _dataframes[dataframe_id]
        return True
    return False


class XlsxWriterService:
    """Service to handle Excel file creation, reading and manipulation"""

    def __init__(self):
        """Initialize the XlsxWriter service"""
        try:
            import xlsxwriter
            self.xlsxwriter = xlsxwriter
            self.initialized = True
        except ImportError:
            logging.error(
                "xlsxwriter library not installed. Please install with 'pip install XlsxWriter'")
            self.initialized = False
            self.xlsxwriter = None

        # Dictionary to store active workbooks and worksheets
        self.workbooks = {}

        # Check for pandas, openpyxl, and xlrd (for reading Excel)
        try:
            import pandas as pd
            self.pandas = pd
            self.pandas_available = True
        except ImportError:
            logging.error(
                "pandas library not installed. Please install with 'pip install pandas'")
            self.pandas_available = False
            self.pandas = None

        try:
            import openpyxl
            self.openpyxl_available = True
        except ImportError:
            logging.warning(
                "openpyxl library not installed. Some Excel reading features may be limited. Install with 'pip install openpyxl'")
            self.openpyxl_available = False

        try:
            import xlrd
            self.xlrd_available = True
        except ImportError:
            logging.warning(
                "xlrd library not installed. Reading older Excel formats may be limited. Install with 'pip install xlrd'")
            self.xlrd_available = False

    def _is_initialized(self):
        """Check if the service is properly initialized"""
        if not self.initialized:
            raise ValueError(
                "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed.")
        return True

    def _check_pandas_available(self):
        """Check if pandas is available for DataFrame operations"""
        if not self.pandas_available:
            raise ValueError(
                "pandas library not installed. Please install with 'pip install pandas'")
        return True

    async def create_workbook(self, filename):
        """Create a new Excel workbook"""
        try:
            self._is_initialized()

            # Create the workbook
            workbook = self.xlsxwriter.Workbook(filename)

            # Store in our dictionary
            self.workbooks[filename] = {
                "workbook": workbook,
                "worksheets": {},
                "formats": {},
                "charts": {}
            }

            return {"filename": filename, "status": "created"}
        except Exception as e:
            return {"error": f"Error creating workbook: {str(e)}"}

    async def add_worksheet(self, filename, name=None):
        """Add a worksheet to the workbook"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            workbook = self.workbooks[filename]["workbook"]

            # Add a worksheet
            worksheet = workbook.add_worksheet(name)

            # Store the worksheet
            worksheet_name = name if name else f"Sheet{len(self.workbooks[filename]['worksheets'])+1}"
            self.workbooks[filename]["worksheets"][worksheet_name] = worksheet

            return {"filename": filename, "worksheet": worksheet_name, "status": "added"}
        except Exception as e:
            return {"error": f"Error adding worksheet: {str(e)}"}

    async def write_data(self, filename, worksheet_name, row, col, data, format_name=None):
        """Write data to a cell"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            # Check if worksheet exists
            if worksheet_name not in self.workbooks[filename]["worksheets"]:
                return {"error": f"Worksheet {worksheet_name} not found in {filename}"}

            worksheet = self.workbooks[filename]["worksheets"][worksheet_name]

            # Get format if specified
            format_obj = None
            if format_name and format_name in self.workbooks[filename]["formats"]:
                format_obj = self.workbooks[filename]["formats"][format_name]

            # Write the data
            worksheet.write(row, col, data, format_obj)

            return {"filename": filename, "worksheet": worksheet_name, "row": row, "col": col, "data": data, "status": "written"}
        except Exception as e:
            return {"error": f"Error writing data: {str(e)}"}

    async def write_matrix(self, filename, worksheet_name, start_row, start_col, data, formats=None):
        """Write a matrix of data to a worksheet"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            # Check if worksheet exists
            if worksheet_name not in self.workbooks[filename]["worksheets"]:
                return {"error": f"Worksheet {worksheet_name} not found in {filename}"}

            worksheet = self.workbooks[filename]["worksheets"][worksheet_name]

            # Process formats if provided
            format_matrix = None
            if formats:
                format_matrix = []
                for row in formats:
                    format_row = []
                    for format_name in row:
                        if format_name and format_name in self.workbooks[filename]["formats"]:
                            format_row.append(
                                self.workbooks[filename]["formats"][format_name])
                        else:
                            format_row.append(None)
                    format_matrix.append(format_row)

            # Write the data matrix
            for i, row_data in enumerate(data):
                for j, cell_data in enumerate(row_data):
                    format_obj = None
                    if format_matrix and i < len(format_matrix) and j < len(format_matrix[i]):
                        format_obj = format_matrix[i][j]

                    worksheet.write(start_row + i, start_col +
                                    j, cell_data, format_obj)

            return {"filename": filename, "worksheet": worksheet_name, "rows": len(data), "cols": len(data[0]) if data else 0, "status": "written"}
        except Exception as e:
            return {"error": f"Error writing matrix: {str(e)}"}

    async def add_format(self, filename, format_name, format_props):
        """Create a cell format"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            workbook = self.workbooks[filename]["workbook"]

            # Create the format
            format_obj = workbook.add_format(format_props)

            # Store the format
            self.workbooks[filename]["formats"][format_name] = format_obj

            return {"filename": filename, "format": format_name, "properties": format_props, "status": "added"}
        except Exception as e:
            return {"error": f"Error adding format: {str(e)}"}

    async def add_chart(self, filename, worksheet_name, chart_type, data_range, position, options=None):
        """Add a chart to a worksheet"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            # Check if worksheet exists
            if worksheet_name not in self.workbooks[filename]["worksheets"]:
                return {"error": f"Worksheet {worksheet_name} not found in {filename}"}

            workbook = self.workbooks[filename]["workbook"]
            worksheet = self.workbooks[filename]["worksheets"][worksheet_name]

            # Create the chart
            chart = workbook.add_chart({'type': chart_type})

            # Add the data series
            for series in data_range:
                chart.add_series(series)

            # Set chart title and other options if provided
            if options:
                if 'title' in options:
                    chart.set_title({'name': options['title']})
                if 'x_axis' in options:
                    chart.set_x_axis(options['x_axis'])
                if 'y_axis' in options:
                    chart.set_y_axis(options['y_axis'])
                if 'style' in options:
                    chart.set_style(options['style'])

            # Insert the chart into the worksheet
            worksheet.insert_chart(position['row'], position['col'], chart)

            # Store the chart
            chart_name = f"Chart{len(self.workbooks[filename]['charts'])+1}"
            self.workbooks[filename]["charts"][chart_name] = chart

            return {"filename": filename, "worksheet": worksheet_name, "chart": chart_name, "status": "added"}
        except Exception as e:
            return {"error": f"Error adding chart: {str(e)}"}

    async def add_image(self, filename, worksheet_name, image_path, position, options=None):
        """Add an image to a worksheet"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            # Check if worksheet exists
            if worksheet_name not in self.workbooks[filename]["worksheets"]:
                return {"error": f"Worksheet {worksheet_name} not found in {filename}"}

            # Check if image file exists
            if not os.path.exists(image_path):
                return {"error": f"Image file {image_path} not found"}

            worksheet = self.workbooks[filename]["worksheets"][worksheet_name]

            # Insert the image
            worksheet.insert_image(
                position['row'], position['col'], image_path, options)

            return {"filename": filename, "worksheet": worksheet_name, "image": image_path, "status": "added"}
        except Exception as e:
            return {"error": f"Error adding image: {str(e)}"}

    async def add_formula(self, filename, worksheet_name, row, col, formula, format_name=None):
        """Add a formula to a cell"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            # Check if worksheet exists
            if worksheet_name not in self.workbooks[filename]["worksheets"]:
                return {"error": f"Worksheet {worksheet_name} not found in {filename}"}

            worksheet = self.workbooks[filename]["worksheets"][worksheet_name]

            # Get format if specified
            format_obj = None
            if format_name and format_name in self.workbooks[filename]["formats"]:
                format_obj = self.workbooks[filename]["formats"][format_name]

            # Write the formula
            worksheet.write_formula(row, col, formula, format_obj)

            return {"filename": filename, "worksheet": worksheet_name, "row": row, "col": col, "formula": formula, "status": "added"}
        except Exception as e:
            return {"error": f"Error adding formula: {str(e)}"}

    async def add_table(self, filename, worksheet_name, start_row, start_col, end_row, end_col, options=None):
        """Add a table to a worksheet"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            # Check if worksheet exists
            if worksheet_name not in self.workbooks[filename]["worksheets"]:
                return {"error": f"Worksheet {worksheet_name} not found in {filename}"}

            worksheet = self.workbooks[filename]["worksheets"][worksheet_name]

            # Add the table
            table_options = options or {}
            worksheet.add_table(start_row, start_col,
                                end_row, end_col, table_options)

            return {"filename": filename, "worksheet": worksheet_name, "table_range": f"{start_row}:{start_col}:{end_row}:{end_col}", "status": "added"}
        except Exception as e:
            return {"error": f"Error adding table: {str(e)}"}

    async def close_workbook(self, filename):
        """Close and save the workbook"""
        try:
            self._is_initialized()

            # Check if workbook exists
            if filename not in self.workbooks:
                return {"error": f"Workbook {filename} not found"}

            workbook = self.workbooks[filename]["workbook"]

            # Close the workbook (which saves it)
            workbook.close()

            # Remove from our dictionary
            del self.workbooks[filename]

            return {"filename": filename, "status": "closed"}
        except Exception as e:
            return {"error": f"Error closing workbook: {str(e)}"}

    #
    # New methods for reading Excel and CSV files
    #

    async def read_excel(self, filename, sheet_name=0, **kwargs):
        """Read Excel file into DataFrame"""
        try:
            self._check_pandas_available()

            # Check if file exists
            if not os.path.exists(filename):
                return {"error": f"File {filename} not found"}

            # Read Excel file
            df = self.pandas.read_excel(
                filename, sheet_name=sheet_name, **kwargs)

            # If it returned a dict of DataFrames (multiple sheets)
            if isinstance(df, dict):
                return {"sheets": list(df.keys()), "dataframes": df}

            return df
        except Exception as e:
            return {"error": f"Error reading Excel file: {str(e)}"}

    async def read_csv(self, filename, **kwargs):
        """Read CSV file into DataFrame"""
        try:
            self._check_pandas_available()

            # Check if file exists
            if not os.path.exists(filename):
                return {"error": f"File {filename} not found"}

            # Read CSV file
            df = self.pandas.read_csv(filename, **kwargs)
            return df
        except Exception as e:
            return {"error": f"Error reading CSV file: {str(e)}"}

    async def get_excel_sheet_names(self, filename):
        """Get sheet names from Excel file"""
        try:
            self._check_pandas_available()

            # Check if file exists
            if not os.path.exists(filename):
                return {"error": f"File {filename} not found"}

            # Get sheet names
            excel_file = self.pandas.ExcelFile(filename)
            sheet_names = excel_file.sheet_names

            return sheet_names
        except Exception as e:
            return {"error": f"Error getting sheet names: {str(e)}"}

    async def dataframe_info(self, df):
        """Get information about DataFrame"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Create a string buffer to capture DataFrame.info() output
            buffer = io.StringIO()
            df.info(buf=buffer)
            info_output = buffer.getvalue()

            # Basic info about the DataFrame
            result = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                # Convert to strings for JSON serialization
                "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
                "info": info_output,
                "memory_usage": df.memory_usage(deep=True).sum(),
                "has_nulls": df.isnull().any().any()
            }

            # Add sample data (first 5 rows)
            try:
                result["head"] = json.loads(
                    df.head().to_json(orient="records"))
            except:
                # Fallback if to_json fails for some reason
                result["head"] = str(df.head())

            return result
        except Exception as e:
            return {"error": f"Error getting DataFrame info: {str(e)}"}

    async def dataframe_to_excel(self, df, filename, sheet_name="Sheet1", index=True, **kwargs):
        """Export DataFrame to Excel file"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Export to Excel
            df.to_excel(filename, sheet_name=sheet_name, index=index, **kwargs)

            return {"filename": filename, "sheet_name": sheet_name, "rows": len(df), "columns": len(df.columns), "status": "exported"}
        except Exception as e:
            return {"error": f"Error exporting to Excel: {str(e)}"}

    async def dataframe_to_csv(self, df, filename, index=True, **kwargs):
        """Export DataFrame to CSV file"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Export to CSV
            df.to_csv(filename, index=index, **kwargs)

            return {"filename": filename, "rows": len(df), "columns": len(df.columns), "status": "exported"}
        except Exception as e:
            return {"error": f"Error exporting to CSV: {str(e)}"}

    #
    # Data manipulation methods
    #

    async def filter_dataframe(self, df, query=None, column=None, value=None, operator="=="):
        """Filter DataFrame by query or column condition"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Filter by query string
            if query:
                try:
                    filtered_df = df.query(query)
                    return filtered_df
                except Exception as e:
                    return {"error": f"Error in query: {str(e)}"}

            # Filter by column and value
            elif column and value is not None:
                if column not in df.columns:
                    return {"error": f"Column '{column}' not found"}

                if operator == "==":
                    filtered_df = df[df[column] == value]
                elif operator == "!=":
                    filtered_df = df[df[column] != value]
                elif operator == ">":
                    filtered_df = df[df[column] > value]
                elif operator == ">=":
                    filtered_df = df[df[column] >= value]
                elif operator == "<":
                    filtered_df = df[df[column] < value]
                elif operator == "<=":
                    filtered_df = df[df[column] <= value]
                elif operator == "in":
                    if not isinstance(value, list):
                        return {"error": "Value must be a list when using 'in' operator"}
                    filtered_df = df[df[column].isin(value)]
                elif operator == "contains":
                    filtered_df = df[df[column].astype(
                        str).str.contains(str(value))]
                else:
                    return {"error": f"Unknown operator: {operator}"}

                return filtered_df
            else:
                return {"error": "Either query or column+value must be provided"}

        except Exception as e:
            return {"error": f"Error filtering DataFrame: {str(e)}"}

    async def sort_dataframe(self, df, by, ascending=True):
        """Sort DataFrame by columns"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Ensure 'by' is a list
            if isinstance(by, str):
                by = [by]

            # Check if all columns exist
            for col in by:
                if col not in df.columns:
                    return {"error": f"Column '{col}' not found"}

            # Convert ascending to list if necessary
            if not isinstance(ascending, list):
                ascending = [ascending] * len(by)

            # Sort the DataFrame
            sorted_df = df.sort_values(by=by, ascending=ascending)

            return sorted_df
        except Exception as e:
            return {"error": f"Error sorting DataFrame: {str(e)}"}

    async def group_dataframe(self, df, by, agg_func=None):
        """Group DataFrame and apply aggregation"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Ensure 'by' is a list
            if isinstance(by, str):
                by = [by]

            # Check if all columns exist
            for col in by:
                if col not in df.columns:
                    return {"error": f"Column '{col}' not found"}

            # Group by columns
            grouped = df.groupby(by)

            # Apply aggregation function
            if agg_func:
                if isinstance(agg_func, dict):
                    # Complex aggregation with different functions per column
                    result_df = grouped.agg(agg_func)
                else:
                    # Simple aggregation with same function for all columns
                    result_df = grouped.agg(agg_func)
            else:
                # Default aggregation (count)
                result_df = grouped.count()

            return result_df.reset_index()
        except Exception as e:
            return {"error": f"Error grouping DataFrame: {str(e)}"}

    async def describe_dataframe(self, df, include=None, exclude=None, percentiles=None):
        """Get statistical description of DataFrame"""
        try:
            self._check_pandas_available()

            # Check if valid DataFrame
            if not isinstance(df, self.pandas.DataFrame):
                return {"error": "Invalid DataFrame"}

            # Get description
            desc_df = df.describe(
                include=include, exclude=exclude, percentiles=percentiles)

            # Convert to dict for JSON serialization
            result = {}
            for col in desc_df.columns:
                result[str(col)] = {str(idx): float(val) if not pd.isna(val) else None
                                    for idx, val in desc_df[col].items()}

            return result
        except Exception as e:
            return {"error": f"Error describing DataFrame: {str(e)}"}


# Tool function definitions that will be registered with MCP
async def xlsx_create_workbook(filename: str, ctx: Context = None) -> str:
    """Create a new Excel workbook

    Parameters:
    - filename: Path to save the Excel file

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.create_workbook(filename)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_add_worksheet(filename: str, name: str = None, ctx: Context = None) -> str:
    """Add a worksheet to the workbook

    Parameters:
    - filename: Path to the Excel file
    - name: (Optional) Name for the worksheet

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.add_worksheet(filename, name)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_write_data(filename: str, worksheet: str, row: int, col: int,
                          data: Any, format: str = None, ctx: Context = None) -> str:
    """Write data to a cell in a worksheet

    Parameters:
    - filename: Path to the Excel file
    - worksheet: Name of the worksheet
    - row: Row number (0-based)
    - col: Column number (0-based)
    - data: Data to write
    - format: (Optional) Name of a predefined format

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.write_data(filename, worksheet, row, col, data, format)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_write_matrix(filename: str, worksheet: str, start_row: int, start_col: int,
                            data: List[List[Any]], formats: List[List[str]] = None,
                            ctx: Context = None) -> str:
    """Write a matrix of data to a worksheet

    Parameters:
    - filename: Path to the Excel file
    - worksheet: Name of the worksheet
    - start_row: Starting row number (0-based)
    - start_col: Starting column number (0-based)
    - data: 2D list of data to write
    - formats: (Optional) 2D list of format names corresponding to data

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.write_matrix(filename, worksheet, start_row, start_col, data, formats)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_add_format(filename: str, format_name: str, properties: Dict[str, Any],
                          ctx: Context = None) -> str:
    """Create a cell format

    Parameters:
    - filename: Path to the Excel file
    - format_name: Name to identify the format
    - properties: Dictionary of format properties (e.g., {'bold': True, 'font_color': 'red'})

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.add_format(filename, format_name, properties)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_add_chart(filename: str, worksheet: str, chart_type: str, data_range: List[Dict[str, Any]],
                         position: Dict[str, int], options: Dict[str, Any] = None,
                         ctx: Context = None) -> str:
    """Add a chart to a worksheet

    Parameters:
    - filename: Path to the Excel file
    - worksheet: Name of the worksheet
    - chart_type: Type of chart (e.g., 'column', 'line', 'pie')
    - data_range: List of data series specifications
    - position: Dictionary with 'row' and 'col' keys specifying chart position
    - options: (Optional) Additional chart options

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.add_chart(filename, worksheet, chart_type, data_range, position, options)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_add_image(filename: str, worksheet: str, image_path: str,
                         position: Dict[str, int], options: Dict[str, Any] = None,
                         ctx: Context = None) -> str:
    """Add an image to a worksheet

    Parameters:
    - filename: Path to the Excel file
    - worksheet: Name of the worksheet
    - image_path: Path to the image file
    - position: Dictionary with 'row' and 'col' keys specifying image position
    - options: (Optional) Additional image options

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.add_image(filename, worksheet, image_path, position, options)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_add_formula(filename: str, worksheet: str, row: int, col: int,
                           formula: str, format: str = None, ctx: Context = None) -> str:
    """Add a formula to a cell

    Parameters:
    - filename: Path to the Excel file
    - worksheet: Name of the worksheet
    - row: Row number (0-based)
    - col: Column number (0-based)
    - formula: Excel formula (e.g., '=SUM(A1:A10)')
    - format: (Optional) Name of a predefined format

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.add_formula(filename, worksheet, row, col, formula, format)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_add_table(filename: str, worksheet: str, start_row: int, start_col: int,
                         end_row: int, end_col: int, options: Dict[str, Any] = None,
                         ctx: Context = None) -> str:
    """Add a table to a worksheet

    Parameters:
    - filename: Path to the Excel file
    - worksheet: Name of the worksheet
    - start_row: Starting row number (0-based)
    - start_col: Starting column number (0-based)
    - end_row: Ending row number (0-based)
    - end_col: Ending column number (0-based)
    - options: (Optional) Table options (e.g., {'header_row': True, 'columns': [{'header': 'Name'}]})

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.add_table(filename, worksheet, start_row, start_col, end_row, end_col, options)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def xlsx_close_workbook(filename: str, ctx: Context = None) -> str:
    """Close and save the workbook

    Parameters:
    - filename: Path to the Excel file

    Returns:
    - JSON string containing the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if xlsxwriter library is installed."

    try:
        result = await xlsx.close_workbook(filename)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


#
# New tool functions for reading Excel and CSV files
#

async def xlsx_read_excel(filename: str, sheet_name: Union[str, int] = 0,
                          output_id: str = None, header: Union[int, List[int], None] = 0,
                          names: List[str] = None, skiprows: Union[int, List[int], None] = None,
                          ctx: Context = None) -> str:
    """Read an Excel file into a pandas DataFrame

    Parameters:
    - filename: Path to the Excel file
    - sheet_name: Sheet name or index (default: 0)
    - output_id: ID to store the DataFrame in memory (default: filename)
    - header: Row(s) to use as column names (default: 0)
    - names: List of custom column names (default: None)
    - skiprows: Row indices to skip or number of rows to skip (default: None)

    Returns:
    - JSON string with DataFrame information
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Set default output_id to filename without extension
        if not output_id:
            output_id = os.path.splitext(os.path.basename(filename))[0]

        # Read the Excel file
        result = await xlsx.read_excel(filename, sheet_name=sheet_name, header=header,
                                       names=names, skiprows=skiprows)

        # Handle both single sheet and multiple sheets
        if isinstance(result, dict) and "error" in result:
            return json.dumps(result, indent=2)

        elif isinstance(result, dict) and "sheets" in result:
            # Multiple sheets returned
            sheet_info = {}
            for sheet_name, df in result["dataframes"].items():
                sheet_id = f"{output_id}_{sheet_name}"
                _store_dataframe(sheet_id, df)
                info = await xlsx.dataframe_info(df)
                sheet_info[sheet_name] = {
                    "dataframe_id": sheet_id,
                    "shape": info["shape"],
                    "columns": info["columns"]
                }

            return json.dumps({
                "filename": filename,
                "sheets": result["sheets"],
                "sheet_info": sheet_info,
                "status": "read",
                "message": f"Multiple sheets read. Access individual DataFrames using their IDs."
            }, indent=2)

        else:
            # Single sheet returned
            _store_dataframe(output_id, result)
            info = await xlsx.dataframe_info(result)

            response = {
                "filename": filename,
                "dataframe_id": output_id,
                "shape": info["shape"],
                "columns": info["columns"],
                "dtypes": info["dtypes"],
                "has_nulls": info["has_nulls"],
                "head": info["head"],
                "status": "read"
            }

            return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error reading Excel file: {str(e)}"}, indent=2)


async def xlsx_read_csv(filename: str, output_id: str = None, delimiter: str = ",",
                        header: Union[int, List[int], None] = 0, names: List[str] = None,
                        skiprows: Union[int, List[int], None] = None, encoding: str = None,
                        ctx: Context = None) -> str:
    """Read a CSV file into a pandas DataFrame

    Parameters:
    - filename: Path to the CSV file
    - output_id: ID to store the DataFrame in memory (default: filename)
    - delimiter: Delimiter to use (default: ",")
    - header: Row(s) to use as column names (default: 0)
    - names: List of custom column names (default: None)
    - skiprows: Row indices to skip or number of rows to skip (default: None)
    - encoding: File encoding (default: None, pandas will try to detect)

    Returns:
    - JSON string with DataFrame information
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Set default output_id to filename without extension
        if not output_id:
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

        result = await xlsx.read_csv(filename, **kwargs)

        if isinstance(result, dict) and "error" in result:
            return json.dumps(result, indent=2)

        # Store DataFrame in memory
        _store_dataframe(output_id, result)

        # Get DataFrame info
        info = await xlsx.dataframe_info(result)

        response = {
            "filename": filename,
            "dataframe_id": output_id,
            "shape": info["shape"],
            "columns": info["columns"],
            "dtypes": info["dtypes"],
            "has_nulls": info["has_nulls"],
            "head": info["head"],
            "status": "read"
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error reading CSV file: {str(e)}"}, indent=2)


async def xlsx_get_sheet_names(filename: str, ctx: Context = None) -> str:
    """Get sheet names from an Excel file

    Parameters:
    - filename: Path to the Excel file

    Returns:
    - JSON string with sheet names
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        result = await xlsx.get_excel_sheet_names(filename)

        if isinstance(result, dict) and "error" in result:
            return json.dumps(result, indent=2)

        return json.dumps({
            "filename": filename,
            "sheet_names": result,
            "count": len(result),
            "status": "success"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting sheet names: {str(e)}"}, indent=2)


async def xlsx_dataframe_info(dataframe_id: str, ctx: Context = None) -> str:
    """Get information about a DataFrame

    Parameters:
    - dataframe_id: ID of the DataFrame in memory

    Returns:
    - JSON string with DataFrame information
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Get DataFrame info
        info = await xlsx.dataframe_info(df)

        if isinstance(info, dict) and "error" in info:
            return json.dumps(info, indent=2)

        response = {
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

        return json.dumps(response, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting DataFrame info: {str(e)}"}, indent=2)


async def xlsx_list_dataframes(ctx: Context = None) -> str:
    """List all DataFrames currently in memory

    Returns:
    - JSON string with list of DataFrame IDs
    """
    try:
        dataframe_ids = _list_dataframes()

        # Get basic info for each DataFrame
        dataframes_info = {}
        xlsx = _get_xlsx_service()

        for df_id in dataframe_ids:
            df = _get_dataframe(df_id)
            if df is not None:
                dataframes_info[df_id] = {
                    "shape": df.shape,
                    "columns": list(df.columns)
                }

        return json.dumps({
            "dataframe_ids": dataframe_ids,
            "count": len(dataframe_ids),
            "dataframes_info": dataframes_info,
            "status": "success"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error listing DataFrames: {str(e)}"}, indent=2)


async def xlsx_clear_dataframe(dataframe_id: str, ctx: Context = None) -> str:
    """Remove a DataFrame from memory

    Parameters:
    - dataframe_id: ID of the DataFrame to clear

    Returns:
    - JSON string with the result
    """
    try:
        result = _clear_dataframe(dataframe_id)

        if result:
            return json.dumps({
                "dataframe_id": dataframe_id,
                "status": "cleared",
                "message": f"DataFrame with ID '{dataframe_id}' has been removed from memory"
            }, indent=2)
        else:
            return json.dumps({
                "error": f"DataFrame with ID '{dataframe_id}' not found",
                "status": "not_found"
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error clearing DataFrame: {str(e)}"}, indent=2)


async def xlsx_dataframe_to_excel(dataframe_id: str, filename: str, sheet_name: str = "Sheet1",
                                  index: bool = True, ctx: Context = None) -> str:
    """Export a DataFrame to an Excel file

    Parameters:
    - dataframe_id: ID of the DataFrame in memory
    - filename: Path to save the Excel file
    - sheet_name: Name of the sheet (default: "Sheet1")
    - index: Whether to include the DataFrame index (default: True)

    Returns:
    - JSON string with the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Export to Excel
        result = await xlsx.dataframe_to_excel(df, filename, sheet_name=sheet_name, index=index)

        if isinstance(result, dict) and "error" in result:
            return json.dumps(result, indent=2)

        return json.dumps({
            "dataframe_id": dataframe_id,
            "filename": filename,
            "sheet_name": sheet_name,
            "rows": result["rows"],
            "columns": result["columns"],
            "status": "exported"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error exporting DataFrame to Excel: {str(e)}"}, indent=2)


async def xlsx_dataframe_to_csv(dataframe_id: str, filename: str, index: bool = True,
                                encoding: str = "utf-8", sep: str = ",", ctx: Context = None) -> str:
    """Export a DataFrame to a CSV file

    Parameters:
    - dataframe_id: ID of the DataFrame in memory
    - filename: Path to save the CSV file
    - index: Whether to include the DataFrame index (default: True)
    - encoding: File encoding (default: "utf-8")
    - sep: Delimiter to use (default: ",")

    Returns:
    - JSON string with the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Export to CSV
        result = await xlsx.dataframe_to_csv(df, filename, index=index, encoding=encoding, sep=sep)

        if isinstance(result, dict) and "error" in result:
            return json.dumps(result, indent=2)

        return json.dumps({
            "dataframe_id": dataframe_id,
            "filename": filename,
            "rows": result["rows"],
            "columns": result["columns"],
            "status": "exported"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error exporting DataFrame to CSV: {str(e)}"}, indent=2)


#
# Data Manipulation Tools
#

async def xlsx_filter_dataframe(dataframe_id: str, query: str = None, column: str = None,
                                value: Any = None, operator: str = "==",
                                output_id: str = None, ctx: Context = None) -> str:
    """Filter a DataFrame by query or column condition

    Parameters:
    - dataframe_id: ID of the DataFrame to filter
    - query: Query string for filtering (e.g., "column > 5 and column2 == 'value'")
    - column: Column name to filter by (alternative to query)
    - value: Value to compare with (used with column and operator)
    - operator: Comparison operator (used with column and value): ==, !=, >, >=, <, <=, in, contains
    - output_id: ID to store the filtered DataFrame (default: dataframe_id + "_filtered")

    Returns:
    - JSON string with the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Set default output ID if not provided
        if not output_id:
            output_id = f"{dataframe_id}_filtered"

        # Filter the DataFrame
        if query:
            # Filter by query string
            filtered_df = await xlsx.filter_dataframe(df, query=query)
        elif column and value is not None:
            # Filter by column and value
            filtered_df = await xlsx.filter_dataframe(df, column=column, value=value, operator=operator)
        else:
            return json.dumps({"error": "Either query or column+value must be provided"}, indent=2)

        if isinstance(filtered_df, dict) and "error" in filtered_df:
            return json.dumps(filtered_df, indent=2)

        # Store filtered DataFrame
        _store_dataframe(output_id, filtered_df)

        # Get DataFrame info
        info = await xlsx.dataframe_info(filtered_df)

        return json.dumps({
            "original_id": dataframe_id,
            "filtered_id": output_id,
            "original_rows": df.shape[0],
            "filtered_rows": filtered_df.shape[0],
            "columns": info["columns"],
            "head": info["head"],
            "status": "filtered"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error filtering DataFrame: {str(e)}"}, indent=2)


async def xlsx_sort_dataframe(dataframe_id: str, by: Union[str, List[str]],
                              ascending: Union[bool, List[bool]] = True,
                              output_id: str = None, ctx: Context = None) -> str:
    """Sort a DataFrame by columns

    Parameters:
    - dataframe_id: ID of the DataFrame to sort
    - by: Column name(s) to sort by (string or list of strings)
    - ascending: Whether to sort in ascending order (boolean or list of booleans)
    - output_id: ID to store the sorted DataFrame (default: dataframe_id + "_sorted")

    Returns:
    - JSON string with the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Set default output ID if not provided
        if not output_id:
            output_id = f"{dataframe_id}_sorted"

        # Sort the DataFrame
        sorted_df = await xlsx.sort_dataframe(df, by=by, ascending=ascending)

        if isinstance(sorted_df, dict) and "error" in sorted_df:
            return json.dumps(sorted_df, indent=2)

        # Store sorted DataFrame
        _store_dataframe(output_id, sorted_df)

        # Get DataFrame info
        info = await xlsx.dataframe_info(sorted_df)

        return json.dumps({
            "original_id": dataframe_id,
            "sorted_id": output_id,
            "sorted_by": by if isinstance(by, str) else list(by),
            "ascending": ascending if isinstance(ascending, bool) else list(ascending),
            "rows": sorted_df.shape[0],
            "head": info["head"],
            "status": "sorted"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error sorting DataFrame: {str(e)}"}, indent=2)


async def xlsx_group_dataframe(dataframe_id: str, by: Union[str, List[str]],
                               agg_func: Union[str, Dict[str, str]] = "mean",
                               output_id: str = None, ctx: Context = None) -> str:
    """Group a DataFrame and apply aggregation

    Parameters:
    - dataframe_id: ID of the DataFrame to group
    - by: Column name(s) to group by (string or list of strings)
    - agg_func: Aggregation function(s) to apply (string or dict of column->function)
    - output_id: ID to store the grouped DataFrame (default: dataframe_id + "_grouped")

    Returns:
    - JSON string with the result
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Set default output ID if not provided
        if not output_id:
            output_id = f"{dataframe_id}_grouped"

        # Group the DataFrame
        grouped_df = await xlsx.group_dataframe(df, by=by, agg_func=agg_func)

        if isinstance(grouped_df, dict) and "error" in grouped_df:
            return json.dumps(grouped_df, indent=2)

        # Store grouped DataFrame
        _store_dataframe(output_id, grouped_df)

        # Get DataFrame info
        info = await xlsx.dataframe_info(grouped_df)

        return json.dumps({
            "original_id": dataframe_id,
            "grouped_id": output_id,
            "grouped_by": by if isinstance(by, str) else list(by),
            "agg_func": agg_func if isinstance(agg_func, str) else dict(agg_func),
            "rows": grouped_df.shape[0],
            "head": info["head"],
            "status": "grouped"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error grouping DataFrame: {str(e)}"}, indent=2)


async def xlsx_describe_dataframe(dataframe_id: str, include: Union[str, List[str]] = None,
                                  exclude: Union[str, List[str]] = None,
                                  percentiles: List[float] = None, ctx: Context = None) -> str:
    """Get statistical description of a DataFrame

    Parameters:
    - dataframe_id: ID of the DataFrame to describe
    - include: Types of columns to include (None, 'all', or list of dtypes)
    - exclude: Types of columns to exclude (None or list of dtypes)
    - percentiles: List of percentiles to include in output (default: [0.25, 0.5, 0.75])

    Returns:
    - JSON string with the statistical description
    """
    xlsx = _get_xlsx_service()
    if not xlsx:
        return "XlsxWriter service not properly initialized. Check if pandas and xlsxwriter libraries are installed."

    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Describe the DataFrame
        result = await xlsx.describe_dataframe(df, include=include, exclude=exclude, percentiles=percentiles)

        if isinstance(result, dict) and "error" in result:
            return json.dumps(result, indent=2)

        return json.dumps({
            "dataframe_id": dataframe_id,
            "description": result,
            "status": "described"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error describing DataFrame: {str(e)}"}, indent=2)


async def xlsx_get_column_values(dataframe_id: str, column: str, unique: bool = False,
                                 count: bool = False, ctx: Context = None) -> str:
    """Get values from a specific column in a DataFrame

    Parameters:
    - dataframe_id: ID of the DataFrame
    - column: Name of the column to get values from
    - unique: Whether to return only unique values (default: False)
    - count: Whether to count occurrences of each value (default: False)

    Returns:
    - JSON string with the column values
    """
    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Check if column exists
        if column not in df.columns:
            return json.dumps({"error": f"Column '{column}' not found in DataFrame '{dataframe_id}'"}, indent=2)

        if count:
            # Count occurrences of each value
            value_counts = df[column].value_counts().to_dict()

            return json.dumps({
                "dataframe_id": dataframe_id,
                "column": column,
                "value_counts": value_counts,
                "total_values": len(df[column]),
                "unique_values": len(value_counts),
                "status": "success"
            }, indent=2)

        elif unique:
            # Get unique values
            unique_values = df[column].unique().tolist()

            # Convert non-serializable values to strings if necessary
            unique_values = [str(v) if not isinstance(
                v, (int, float, bool, str, type(None))) else v for v in unique_values]

            return json.dumps({
                "dataframe_id": dataframe_id,
                "column": column,
                "unique_values": unique_values,
                "count": len(unique_values),
                "status": "success"
            }, indent=2)

        else:
            # Get all values
            values = df[column].tolist()

            # Convert non-serializable values to strings if necessary
            values = [str(v) if not isinstance(
                v, (int, float, bool, str, type(None))) else v for v in values]

            return json.dumps({
                "dataframe_id": dataframe_id,
                "column": column,
                "values": values,
                "count": len(values),
                "status": "success"
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error getting column values: {str(e)}"}, indent=2)


async def xlsx_get_correlation(dataframe_id: str, method: str = "pearson", ctx: Context = None) -> str:
    """Get correlation matrix for a DataFrame

    Parameters:
    - dataframe_id: ID of the DataFrame
    - method: Correlation method ('pearson', 'kendall', or 'spearman')

    Returns:
    - JSON string with the correlation matrix
    """
    try:
        # Get DataFrame from memory
        df = _get_dataframe(dataframe_id)
        if df is None:
            return json.dumps({"error": f"DataFrame with ID '{dataframe_id}' not found"}, indent=2)

        # Calculate correlation matrix
        corr = df.corr(method=method).round(4).to_dict()

        return json.dumps({
            "dataframe_id": dataframe_id,
            "correlation_matrix": corr,
            "method": method,
            "status": "success"
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error calculating correlation: {str(e)}"}, indent=2)


# Tool registration and initialization
_xlsx_service = None


def initialize_xlsx_service():
    """Initialize the XlsxWriter service"""
    global _xlsx_service
    _xlsx_service = XlsxWriterService()
    return _xlsx_service


def _get_xlsx_service():
    """Get or initialize the XlsxWriter service"""
    global _xlsx_service
    if _xlsx_service is None:
        _xlsx_service = initialize_xlsx_service()
    return _xlsx_service


def get_xlsx_tools():
    """Get a dictionary of all XlsxWriter tools for registration with MCP"""
    return {
        # Existing tools
        XlsxWriterTools.CREATE_WORKBOOK: xlsx_create_workbook,
        XlsxWriterTools.ADD_WORKSHEET: xlsx_add_worksheet,
        XlsxWriterTools.WRITE_DATA: xlsx_write_data,
        XlsxWriterTools.WRITE_MATRIX: xlsx_write_matrix,
        XlsxWriterTools.ADD_FORMAT: xlsx_add_format,
        XlsxWriterTools.ADD_CHART: xlsx_add_chart,
        XlsxWriterTools.ADD_IMAGE: xlsx_add_image,
        XlsxWriterTools.ADD_FORMULA: xlsx_add_formula,
        XlsxWriterTools.ADD_TABLE: xlsx_add_table,
        XlsxWriterTools.CLOSE_WORKBOOK: xlsx_close_workbook,

        # New reading tools
        XlsxWriterTools.READ_EXCEL: xlsx_read_excel,
        XlsxWriterTools.READ_CSV: xlsx_read_csv,
        XlsxWriterTools.GET_SHEET_NAMES: xlsx_get_sheet_names,

        # DataFrame management
        "xlsx_dataframe_info": xlsx_dataframe_info,
        "xlsx_list_dataframes": xlsx_list_dataframes,
        "xlsx_clear_dataframe": xlsx_clear_dataframe,
        "xlsx_get_column_values": xlsx_get_column_values,

        # Data manipulation
        XlsxWriterTools.FILTER_DATAFRAME: xlsx_filter_dataframe,
        XlsxWriterTools.SORT_DATAFRAME: xlsx_sort_dataframe,
        XlsxWriterTools.GROUP_DATAFRAME: xlsx_group_dataframe,
        XlsxWriterTools.DESCRIBE_DATAFRAME: xlsx_describe_dataframe,
        "xlsx_get_correlation": xlsx_get_correlation,

        # Export tools
        XlsxWriterTools.DATAFRAME_TO_EXCEL: xlsx_dataframe_to_excel,
        XlsxWriterTools.DATAFRAME_TO_CSV: xlsx_dataframe_to_csv
    }

# This function will be called by the unified server to initialize the module


def initialize(mcp=None):
    """Initialize the XlsxWriter module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_xlsx_service()

    # Check for required dependencies
    missing_deps = []
    try:
        import xlsxwriter
    except ImportError:
        missing_deps.append("xlsxwriter")

    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")

    try:
        import openpyxl
    except ImportError:
        # Optional but recommended
        logging.warning(
            "openpyxl not installed. Some Excel reading features may be limited.")

    try:
        import xlrd
    except ImportError:
        # Optional but recommended for older Excel formats
        logging.warning(
            "xlrd not installed. Reading older Excel formats may be limited.")

    if missing_deps:
        logging.warning(
            f"Missing required dependencies: {', '.join(missing_deps)}. Please install them.")
        return False

    if service and service.initialized and service.pandas_available:
        logging.info(
            "XlsxWriter service initialized successfully with pandas support")
        return True
    else:
        logging.warning(
            "Failed to initialize XlsxWriter service. Please ensure xlsxwriter and pandas are installed.")
        return False


if __name__ == "__main__":
    print("XlsxWriter service module - use with MCP Unified Server")
