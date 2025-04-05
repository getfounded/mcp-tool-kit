#!/usr/bin/env python3
"""
Utility functions for PDF operations.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, Union

def validate_pdf_path(file_path: str) -> bool:
    """
    Validate that a file exists and is a PDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        bool: True if valid, raises ValueError otherwise
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}")
    
    # Check file extension
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"File is not a PDF: {file_path}")
    
    return True

def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure
        
    Returns:
        The directory path
    """
    if not directory:
        return tempfile.gettempdir()
    
    os.makedirs(directory, exist_ok=True)
    return directory

def normalize_pages(pages: Optional[List[int]], total_pages: int) -> List[int]:
    """
    Normalize page numbers to 0-indexed list within valid range.
    
    Args:
        pages: List of page numbers (1-indexed) or None for all pages
        total_pages: Total number of pages in the PDF
        
    Returns:
        List of 0-indexed page numbers
    """
    if pages is None:
        return list(range(total_pages))
    
    # Convert 1-indexed to 0-indexed and validate
    result = []
    for p in pages:
        if not isinstance(p, int):
            try:
                p = int(p)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid page number: {p}")
        
        # Convert 1-indexed to 0-indexed
        idx = p - 1 if p > 0 else p
        
        # Validate page number
        if idx < 0 or idx >= total_pages:
            raise ValueError(f"Page number out of range: {p} (document has {total_pages} pages)")
        
        result.append(idx)
    
    return result

def format_pdf_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception into a standard error response.
    
    Args:
        error: The exception to format
        
    Returns:
        Formatted error response
    """
    if isinstance(error, ValueError):
        return {
            "status": "error",
            "message": str(error)
        }
    
    return {
        "status": "error",
        "message": f"PDF operation failed: {str(error)}"
    }

def parse_bool(value: str) -> bool:
    """
    Parse string to boolean.
    
    Args:
        value: String value to parse
        
    Returns:
        Boolean value
    """
    return value.lower() in ('true', 'yes', '1', 't', 'y')