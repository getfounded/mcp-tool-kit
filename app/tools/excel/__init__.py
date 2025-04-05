"""
Excel tools for spreadsheet creation and data analysis.
"""
from app.tools.excel.tools import *


def get_xlsx_tools():
    """Return a dictionary of Excel tools for registration."""
    return {
        "xlsx_create_workbook": xlsx_create_workbook,
        "xlsx_add_worksheet": xlsx_add_worksheet,
        "xlsx_write_data": xlsx_write_data,
        "xlsx_write_matrix": xlsx_write_matrix,
        "xlsx_add_format": xlsx_add_format,
        "xlsx_add_chart": xlsx_add_chart,
        "xlsx_add_image": xlsx_add_image,
        "xlsx_add_formula": xlsx_add_formula,
        "xlsx_add_table": xlsx_add_table,
        "xlsx_close_workbook": xlsx_close_workbook,
        "xlsx_read_excel": xlsx_read_excel,
        "xlsx_read_csv": xlsx_read_csv,
        "xlsx_get_sheet_names": xlsx_get_sheet_names,
        "xlsx_dataframe_info": xlsx_dataframe_info,
        "xlsx_list_dataframes": xlsx_list_dataframes,
        "xlsx_clear_dataframe": xlsx_clear_dataframe,
        "xlsx_get_column_values": xlsx_get_column_values,
        "xlsx_filter_dataframe": xlsx_filter_dataframe,
        "xlsx_sort_dataframe": xlsx_sort_dataframe,
        "xlsx_group_dataframe": xlsx_group_dataframe,
        "xlsx_describe_dataframe": xlsx_describe_dataframe,
        "xlsx_get_correlation": xlsx_get_correlation,
        "xlsx_dataframe_to_excel": xlsx_dataframe_to_excel,
        "xlsx_dataframe_to_csv": xlsx_dataframe_to_csv
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_xlsx_service():
    """Initialize the Excel service."""
    # Implementation can be added as needed
    pass
