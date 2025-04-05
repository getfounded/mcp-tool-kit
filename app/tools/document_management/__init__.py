"""
Document management tools for PDF operations and document processing.
"""
from app.tools.document_management.tools import *
from app.tools.document_management import *


def get_pdf_tools():
    """Return a dictionary of PDF tools for registration."""
    return {
        "document_info": document_info,
        "document_parse": document_parse,
        "document_convert": document_convert,
        "document_extract_text": document_extract_text,
        "document_search": document_search,
        "document_compare": document_compare,
        "document_validate": document_validate
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize_pdf_service():
    """Initialize the PDF service."""
    # Implementation can be added as needed
    pass
