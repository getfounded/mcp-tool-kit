#!/usr/bin/env python3
"""
Tool functions for Document Management operations.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.document_management.service import get_service, DocumentManagementService


@register_tool(
    name="document_info",
    category="document_management",
    description="Get information about a document"
)
async def document_info(document_path: str) -> str:
    """Get information about a document.

    Parameters:
    - document_path: Path to the document file
    """
    service = get_service()
    result = service.get_document_info(document_path)
    return json.dumps(result, indent=2)


@register_tool(
    name="document_parse",
    category="document_management",
    description="Parse a document into structured content"
)
async def document_parse(document_path: str) -> str:
    """Parse a document into structured content.

    Parameters:
    - document_path: Path to the document file
    """
    service = get_service()
    result = service.parse_document(document_path)
    return json.dumps(result, indent=2)


@register_tool(
    name="document_convert",
    category="document_management",
    description="Convert a document from one format to another"
)
async def document_convert(
    input_path: str,
    output_path: str,
    output_format: str
) -> str:
    """Convert a document from one format to another.

    Parameters:
    - input_path: Path to the input document
    - output_path: Path for the output document
    - output_format: Target format (e.g., 'pdf', 'docx', 'html')
    """
    service = get_service()
    result = service.convert_document(input_path, output_path, output_format)
    return json.dumps(result, indent=2)


@register_tool(
    name="document_extract_text",
    category="document_management",
    description="Extract text content from a document"
)
async def document_extract_text(document_path: str) -> str:
    """Extract text content from a document.

    Parameters:
    - document_path: Path to the document file
    """
    service = get_service()
    result = service.extract_text(document_path)
    return json.dumps(result, indent=2)


@register_tool(
    name="document_search",
    category="document_management",
    description="Search for text within a document"
)
async def document_search(
    document_path: str,
    query: str,
    case_sensitive: bool = False
) -> str:
    """Search for text within a document.

    Parameters:
    - document_path: Path to the document file
    - query: Text to search for
    - case_sensitive: Whether the search is case-sensitive (default: False)
    """
    service = get_service()
    result = service.search_document(document_path, query, case_sensitive)
    return json.dumps(result, indent=2)


@register_tool(
    name="document_compare",
    category="document_management",
    description="Compare two documents and find differences"
)
async def document_compare(doc_path1: str, doc_path2: str) -> str:
    """Compare two documents and find differences.

    Parameters:
    - doc_path1: Path to the first document
    - doc_path2: Path to the second document
    """
    service = get_service()
    result = service.compare_documents(doc_path1, doc_path2)
    return json.dumps(result, indent=2)


@register_tool(
    name="document_validate",
    category="document_management",
    description="Validate document size and type"
)
async def document_validate(document_path: str) -> str:
    """Validate document size and type.

    Parameters:
    - document_path: Path to the document file
    """
    service = get_service()
    result = service.validate_document(document_path)
    return json.dumps(result, indent=2)
