#!/usr/bin/env python3
import os
import json
import logging
from enum import Enum
from typing import List, Dict, Optional, Any, Union

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


class XlsxWriterService:
    """Service to handle Excel file creation and manipulation"""
    
    def __init__(self):
        """Initialize the XlsxWriter service"""
        try:
            import xlsxwriter
            self.xlsxwriter = xlsxwriter
            self.initialized = True
        except ImportError:
            logging.error("xlsxwriter library not installed. Please install with 'pip install XlsxWriter'")
            self.initialized = False
            self.xlsxwriter = None
            
        # Dictionary to store active workbooks and worksheets
        self.workbooks = {}
        
    def _is_initialized(self):
        """Check if the service is properly initialized"""
        if not self.initialized:
            raise ValueError("XlsxWriter service not properly initialized. Check if xlsxwriter library is installed.")
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
                            format_row.append(self.workbooks[filename]["formats"][format_name])
                        else:
                            format_row.append(None)
                    format_matrix.append(format_row)
            
            # Write the data matrix
            for i, row_data in enumerate(data):
                for j, cell_data in enumerate(row_data):
                    format_obj = None
                    if format_matrix and i < len(format_matrix) and j < len(format_matrix[i]):
                        format_obj = format_matrix[i][j]
                    
                    worksheet.write(start_row + i, start_col + j, cell_data, format_obj)
            
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
            worksheet.insert_image(position['row'], position['col'], image_path, options)
            
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
            worksheet.add_table(start_row, start_col, end_row, end_col, table_options)
            
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
        XlsxWriterTools.CREATE_WORKBOOK: xlsx_create_workbook,
        XlsxWriterTools.ADD_WORKSHEET: xlsx_add_worksheet,
        XlsxWriterTools.WRITE_DATA: xlsx_write_data,
        XlsxWriterTools.WRITE_MATRIX: xlsx_write_matrix,
        XlsxWriterTools.ADD_FORMAT: xlsx_add_format,
        XlsxWriterTools.ADD_CHART: xlsx_add_chart,
        XlsxWriterTools.ADD_IMAGE: xlsx_add_image,
        XlsxWriterTools.ADD_FORMULA: xlsx_add_formula,
        XlsxWriterTools.ADD_TABLE: xlsx_add_table,
        XlsxWriterTools.CLOSE_WORKBOOK: xlsx_close_workbook
    }

# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the XlsxWriter module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_xlsx_service()
    if service and service.initialized:
        logging.info("XlsxWriter service initialized successfully")
        return True
    else:
        logging.warning("Failed to initialize XlsxWriter service. Please ensure xlsxwriter is installed.")
        return False


if __name__ == "__main__":
    print("XlsxWriter service module - use with MCP Unified Server")
