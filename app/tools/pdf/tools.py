#!/usr/bin/env python3
"""
Tool functions for PDF operations.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.pdf.service import get_service


@register_tool(category="pdf")
async def pdf_info(file_path: str) -> str:
    """Get information about a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    """
    pdf_service = get_service()
    result = pdf_service.get_pdf_info(file_path)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_extract_text(
    file_path: str,
    pages: Optional[List[int]] = None,
    ocr: bool = False
) -> str:
    """Extract text from a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - pages: List of page numbers to extract (1-indexed)
    - ocr: Whether to use OCR for pages with no text
    """
    pdf_service = get_service()
    result = pdf_service.extract_text(file_path, pages, ocr)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_extract_images(
    file_path: str,
    pages: Optional[List[int]] = None,
    min_size: int = 100
) -> str:
    """Extract images from a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - pages: List of page numbers to extract (1-indexed)
    - min_size: Minimum image dimension in pixels
    """
    pdf_service = get_service()
    result = pdf_service.extract_images(file_path, pages, min_size)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_split(
    file_path: str,
    output_dir: str,
    pages_per_file: int = 1
) -> str:
    """Split a PDF into multiple files.

    Parameters:
    - file_path: Path to the PDF file
    - output_dir: Directory to save the split files
    - pages_per_file: Number of pages per output file
    """
    pdf_service = get_service()
    result = pdf_service.split_pdf(file_path, output_dir, pages_per_file)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_merge(
    file_paths: List[str],
    output_path: str
) -> str:
    """Merge multiple PDF files into one.

    Parameters:
    - file_paths: List of paths to the PDF files to merge
    - output_path: Path to save the merged file
    """
    pdf_service = get_service()
    result = pdf_service.merge_pdfs(file_paths, output_path)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_add_watermark(
    file_path: str,
    output_path: str,
    text: Optional[str] = None,
    image_path: Optional[str] = None,
    opacity: float = 0.3
) -> str:
    """Add a watermark to a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - output_path: Path to save the watermarked file
    - text: Text to use as watermark
    - image_path: Path to image to use as watermark
    - opacity: Opacity of the watermark (0-1)
    """
    pdf_service = get_service()
    result = pdf_service.add_watermark(
        file_path, output_path, text, image_path, opacity)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_encrypt(
    file_path: str,
    output_path: str,
    user_password: str,
    owner_password: Optional[str] = None
) -> str:
    """Encrypt a PDF document with password protection.

    Parameters:
    - file_path: Path to the PDF file
    - output_path: Path to save the encrypted file
    - user_password: Password required to open the PDF
    - owner_password: Password for full access (optional, defaults to user_password)
    """
    pdf_service = get_service()
    result = pdf_service.encrypt_pdf(
        file_path, output_path, user_password, owner_password)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_decrypt(
    file_path: str,
    output_path: str,
    password: str
) -> str:
    """Decrypt an encrypted PDF document.

    Parameters:
    - file_path: Path to the encrypted PDF file
    - output_path: Path to save the decrypted file
    - password: Password to decrypt the PDF
    """
    pdf_service = get_service()
    result = pdf_service.decrypt_pdf(file_path, output_path, password)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_get_form_fields(
    file_path: str
) -> str:
    """Get all form fields in a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    """
    pdf_service = get_service()
    result = pdf_service.get_form_fields(file_path)
    return json.dumps(result, indent=2)


@register_tool(category="pdf")
async def pdf_fill_form(
    file_path: str,
    output_path: str,
    form_data: Dict[str, str]
) -> str:
    """Fill out form fields in a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - output_path: Path to save the filled form
    - form_data: Dictionary with field names as keys and field values as values
    """
    pdf_service = get_service()
    result = pdf_service.fill_form(file_path, output_path, form_data)
    return json.dumps(result, indent=2)
