#!/usr/bin/env python3
"""
Utility functions for Document Management operations.
"""
import os
import mimetypes
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple

def get_file_hash(file_path: str, hash_algorithm: str = 'sha256', block_size: int = 65536) -> str:
    """
    Calculate a hash for a file.
    
    Args:
        file_path: Path to the file
        hash_algorithm: Hash algorithm to use (md5, sha1, sha256)
        block_size: Block size for reading file
        
    Returns:
        Hexadecimal string representation of the hash
    """
    if hash_algorithm == 'md5':
        hasher = hashlib.md5()
    elif hash_algorithm == 'sha1':
        hasher = hashlib.sha1()
    else:
        hasher = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(block_size)
    
    return hasher.hexdigest()

def detect_mime_type(file_path: str) -> Tuple[str, str]:
    """
    Detect MIME type and encoding for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (mime_type, encoding)
    """
    return mimetypes.guess_type(file_path)

def get_file_extension(file_path: str) -> str:
    """
    Get file extension without the dot.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension string without the dot
    """
    _, ext = os.path.splitext(file_path)
    return ext.lower().lstrip(".")

def create_temp_filename(original_path: str, suffix: str = None, directory: str = None) -> str:
    """
    Create a temporary filename based on the original.
    
    Args:
        original_path: Original file path
        suffix: Optional suffix to add to the filename
        directory: Optional directory for the temp file
        
    Returns:
        Path for a temporary file
    """
    base_name = os.path.basename(original_path)
    name, ext = os.path.splitext(base_name)
    
    if suffix:
        name = f"{name}_{suffix}"
    
    if directory:
        return os.path.join(directory, f"{name}{ext}")
    else:
        return f"{name}{ext}"

def get_document_category(mime_type: str) -> str:
    """
    Categorize document based on MIME type.
    
    Args:
        mime_type: MIME type string
        
    Returns:
        Category string
    """
    if not mime_type:
        return "unknown"
    
    mime_lower = mime_type.lower()
    
    if "pdf" in mime_lower:
        return "pdf"
    elif "word" in mime_lower or "docx" in mime_lower or "doc" in mime_lower:
        return "word"
    elif "excel" in mime_lower or "xlsx" in mime_lower or "xls" in mime_lower or "csv" in mime_lower:
        return "spreadsheet"
    elif "powerpoint" in mime_lower or "pptx" in mime_lower or "ppt" in mime_lower:
        return "presentation"
    elif "text" in mime_lower:
        if "html" in mime_lower or "xml" in mime_lower:
            return "markup"
        else:
            return "text"
    elif "image" in mime_lower:
        return "image"
    else:
        return "other"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for all platforms.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Trim spaces
    filename = filename.strip()
    
    # Ensure not empty
    if not filename:
        filename = "unnamed"
    
    return filename
