#!/usr/bin/env python3
import os
import json
import logging
import io
import base64
import tempfile
from typing import List, Dict, Any, Optional, Union

# PDF processing libraries
import pypdf
from pdf2image import convert_from_path
from PIL import Image as PILImage
import pytesseract

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import Tool, TextContent, ImageContent

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("PDF Document Management tools MCP reference set")


class PDFService:
    """Service to handle PDF document operations"""

    def __init__(self):
        # Create temp directory for processing
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_service_")

    async def get_pdf_info(self, file_path):
        """Get information about a PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)

                # Extract basic information
                info = {
                    "pages": len(pdf.pages),
                    "file_size": os.path.getsize(file_path),
                    "creator": pdf.metadata.creator if pdf.metadata else None,
                    "author": pdf.metadata.author if pdf.metadata else None,
                    "title": pdf.metadata.title if pdf.metadata else None,
                    "subject": pdf.metadata.subject if pdf.metadata else None,
                    "producer": pdf.metadata.producer if pdf.metadata else None,
                    "creation_date": pdf.metadata.creation_date_raw if pdf.metadata else None,
                    "modification_date": pdf.metadata.modification_date_raw if pdf.metadata else None,
                }

                # Get page dimensions for first page
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]
                    page_box = page.mediabox
                    info["page_width"] = page_box.width
                    info["page_height"] = page_box.height

                return info
        except Exception as e:
            raise ValueError(f"Error getting PDF info: {str(e)}")

    async def extract_text(self, file_path, pages=None, ocr=False):
        """Extract text from a PDF file"""
        try:
            results = {
                "pages": [],
                "total_text_length": 0
            }

            # Method 1: Use pypdf for text extraction
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)

                # If pages not specified, extract all pages
                if pages is None:
                    pages = list(range(len(pdf.pages)))
                else:
                    # Convert 1-indexed pages to 0-indexed
                    pages = [p-1 for p in pages if p >
                             0 and p <= len(pdf.pages)]

                # Extract text from each page
                for page_num in pages:
                    page = pdf.pages[page_num]
                    text = page.extract_text()

                    page_result = {
                        "page": page_num + 1,  # Return 1-indexed page numbers
                        "text": text,
                        "text_length": len(text)
                    }

                    # If OCR is requested and no text was extracted, try OCR
                    if ocr and (not text or len(text.strip()) == 0):
                        ocr_text = await self._ocr_page(file_path, page_num)
                        page_result["text"] = ocr_text
                        page_result["text_length"] = len(ocr_text)
                        page_result["source"] = "ocr"
                    else:
                        page_result["source"] = "pdf"

                    results["pages"].append(page_result)
                    results["total_text_length"] += page_result["text_length"]

            return results
        except Exception as e:
            raise ValueError(f"Error extracting text: {str(e)}")

    async def _ocr_page(self, file_path, page_num):
        """Extract text from a PDF page using OCR"""
        try:
            # Convert page to image
            images = convert_from_path(
                file_path, first_page=page_num+1, last_page=page_num+1)

            if not images:
                return ""

            # Run OCR on the image
            ocr_text = pytesseract.image_to_string(images[0])
            return ocr_text
        except Exception as e:
            logging.warning(f"OCR failed: {str(e)}")
            return ""

    async def extract_images(self, file_path, pages=None, min_size=100):
        """Extract images from a PDF file"""
        try:
            results = {
                "images": [],
                "total_images": 0
            }

            # Convert PDF pages to images
            if pages is None:
                # Get total pages
                with open(file_path, 'rb') as file:
                    pdf = pypdf.PdfReader(file)
                    pages = list(range(1, len(pdf.pages) + 1))

            # Convert specified pages
            page_images = convert_from_path(
                file_path,
                first_page=min(pages),
                last_page=max(pages)
            )

            # Process each page
            for i, image in enumerate(page_images):
                page_num = pages[i]

                # Save image to temp file
                img_path = os.path.join(self.temp_dir, f"page_{page_num}.png")
                image.save(img_path, "PNG")

                # Get image info
                width, height = image.size

                # Skip if image is too small
                if width < min_size or height < min_size:
                    continue

                # Encode image as base64
                with open(img_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()

                # Add to results
                results["images"].append({
                    "page": page_num,
                    "width": width,
                    "height": height,
                    "path": img_path,
                    "data": img_data
                })

            results["total_images"] = len(results["images"])
            return results
        except Exception as e:
            raise ValueError(f"Error extracting images: {str(e)}")

    async def split_pdf(self, file_path, output_dir, pages_per_file=1):
        """Split a PDF into multiple files"""
        try:
            results = {
                "files": [],
                "total_files": 0
            }

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Open the source PDF
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                total_pages = len(pdf.pages)

                # Calculate number of files needed
                num_files = (total_pages + pages_per_file -
                             1) // pages_per_file

                # Get base filename
                base_name = os.path.splitext(os.path.basename(file_path))[0]

                # Create each file
                for i in range(num_files):
                    start_page = i * pages_per_file
                    end_page = min(start_page + pages_per_file, total_pages)

                    # Create new PDF writer
                    pdf_writer = pypdf.PdfWriter()

                    # Add pages to the writer
                    for page_num in range(start_page, end_page):
                        pdf_writer.add_page(pdf.pages[page_num])

                    # Save to file
                    output_path = os.path.join(
                        output_dir, f"{base_name}_part_{i+1}.pdf")
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

                    # Add to results
                    results["files"].append({
                        "path": output_path,
                        "start_page": start_page + 1,  # 1-indexed
                        "end_page": end_page,
                        "pages": end_page - start_page
                    })

            results["total_files"] = len(results["files"])
            return results
        except Exception as e:
            raise ValueError(f"Error splitting PDF: {str(e)}")

    async def merge_pdfs(self, file_paths, output_path):
        """Merge multiple PDFs into a single file"""
        try:
            # Create PDF writer
            pdf_writer = pypdf.PdfWriter()

            # Track pages from each source
            source_info = []

            # Process each input file
            for file_path in file_paths:
                with open(file_path, 'rb') as file:
                    pdf = pypdf.PdfReader(file)

                    # Record source info
                    source_info.append({
                        "path": file_path,
                        "pages": len(pdf.pages)
                    })

                    # Add all pages to writer
                    for page in pdf.pages:
                        pdf_writer.add_page(page)

            # Write output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            return {
                "output_path": output_path,
                "total_pages": sum(source["pages"] for source in source_info),
                "source_files": source_info
            }
        except Exception as e:
            raise ValueError(f"Error merging PDFs: {str(e)}")

    async def add_watermark(self, file_path, output_path, text=None, image_path=None, opacity=0.3):
        """Add a text or image watermark to each page of a PDF"""
        try:
            if not text and not image_path:
                raise ValueError("Either text or image_path must be provided")

            # Create a watermark PDF
            watermark_path = os.path.join(self.temp_dir, "watermark.pdf")

            if text:
                # Create a text watermark
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter

                c = canvas.Canvas(watermark_path, pagesize=letter)
                width, height = letter

                # Set transparency
                c.setFillAlpha(opacity)

                # Add rotated text
                c.saveState()
                c.translate(width/2, height/2)
                c.rotate(45)
                c.setFont("Helvetica", 60)
                c.setFillColorRGB(0, 0, 0)  # Black
                c.drawCentredString(0, 0, text)
                c.restoreState()

                c.save()
            elif image_path:
                # Create an image watermark
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter

                # Open and resize image
                img = PILImage.open(image_path)
                width, height = letter
                img_width, img_height = img.size

                # Resize to fit on page with some margin
                scale = min((width * 0.8) / img_width,
                            (height * 0.8) / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                img = img.resize((new_width, new_height), PILImage.LANCZOS)

                # Save resized image
                img_resized_path = os.path.join(
                    self.temp_dir, "watermark_img.png")
                img.save(img_resized_path)

                # Create PDF with image
                c = canvas.Canvas(watermark_path, pagesize=letter)

                # Set transparency
                c.setFillAlpha(opacity)

                # Draw image in center
                c.drawImage(
                    img_resized_path,
                    (width - new_width) / 2,
                    (height - new_height) / 2,
                    width=new_width,
                    height=new_height
                )

                c.save()

            # Open the watermark PDF
            with open(watermark_path, 'rb') as watermark_file:
                watermark_pdf = pypdf.PdfReader(watermark_file)
                watermark_page = watermark_pdf.pages[0]

            # Open the source PDF
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                pdf_writer = pypdf.PdfWriter()

                # Apply watermark to each page
                for page in pdf.pages:
                    page.merge_page(watermark_page)
                    pdf_writer.add_page(page)

                # Write output file
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

            return {
                "output_path": output_path,
                "pages_processed": len(pdf.pages),
                "watermark_type": "text" if text else "image"
            }
        except Exception as e:
            raise ValueError(f"Error adding watermark: {str(e)}")

    async def encrypt_pdf(self, file_path, output_path, user_password, owner_password=None):
        """Encrypt a PDF file with password protection"""
        try:
            # If owner password not provided, use the same as user password
            if not owner_password:
                owner_password = user_password

            # Open the source PDF
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)
                pdf_writer = pypdf.PdfWriter()

                # Add all pages to writer
                for page in pdf.pages:
                    pdf_writer.add_page(page)

                # Encrypt the PDF
                pdf_writer.encrypt(user_password, owner_password)

                # Write output file
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

            return {
                "output_path": output_path,
                "pages": len(pdf.pages),
                "encrypted": True
            }
        except Exception as e:
            raise ValueError(f"Error encrypting PDF: {str(e)}")

    async def decrypt_pdf(self, file_path, output_path, password):
        """Decrypt an encrypted PDF file"""
        try:
            # Open the source PDF
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)

                # Check if PDF is encrypted
                if not pdf.is_encrypted:
                    return {
                        "output_path": file_path,
                        "pages": len(pdf.pages),
                        "encrypted": False,
                        "message": "PDF is not encrypted"
                    }

                # Try to decrypt
                success = pdf.decrypt(password)

                if not success:
                    raise ValueError("Invalid password")

                # Create new PDF without encryption
                pdf_writer = pypdf.PdfWriter()

                # Add all pages to writer
                for page in pdf.pages:
                    pdf_writer.add_page(page)

                # Write output file
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

            return {
                "output_path": output_path,
                "pages": len(pdf.pages),
                "decrypted": True
            }
        except Exception as e:
            raise ValueError(f"Error decrypting PDF: {str(e)}")

    async def get_form_fields(self, file_path):
        """Get all form fields in a PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)

                # Get form fields and their values
                try:
                    form_fields = pdf.get_form_text_fields() or {}
                except Exception:
                    # If there are no form fields or an error occurs
                    form_fields = {}

                return {
                    "form_fields": form_fields,
                    "count": len(form_fields)
                }
        except Exception as e:
            raise ValueError(f"Error getting form fields: {str(e)}")

    async def fill_form(self, file_path, output_path, form_data):
        """Fill out form fields in a PDF file"""
        try:
            # Open the source PDF
            with open(file_path, 'rb') as file:
                pdf = pypdf.PdfReader(file)

                # Get existing form fields to check if the provided fields exist
                try:
                    existing_fields = pdf.get_form_text_fields() or {}
                except Exception:
                    existing_fields = {}

                if not existing_fields:
                    raise ValueError(
                        "The PDF does not contain any form fields")

                # Validate form data
                for field_name in form_data.keys():
                    if field_name not in existing_fields:
                        raise ValueError(
                            f"Field '{field_name}' does not exist in the PDF form")

                # Create a PDF writer
                pdf_writer = pypdf.PdfWriter()

                # Add all pages to the writer
                for page in pdf.pages:
                    pdf_writer.add_page(page)

                # Use the appropriate method based on the pypdf version
                try:
                    # Try the newer method first (pypdf 3.0+)
                    pdf_writer.update_form_fields(form_data)
                except AttributeError:
                    # Fall back to updating pages individually
                    for i in range(len(pdf_writer.pages)):
                        pdf_writer.update_page_form_field_values(
                            pdf_writer.pages[i], form_data)

                # Write output file
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

                return {
                    "output_path": output_path,
                    "filled_fields": list(form_data.keys()),
                    "pages": len(pdf.pages)
                }
        except Exception as e:
            raise ValueError(f"Error filling form: {str(e)}")

# Tool function definitions that will be registered with MCP


async def pdf_info(file_path: str, ctx: Context = None) -> str:
    """Get information about a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    """
    try:
        pdf_service = _get_pdf_service()
        info = await pdf_service.get_pdf_info(file_path)
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_extract_text(file_path: str, pages: List[int] = None,
                           ocr: bool = False, ctx: Context = None) -> str:
    """Extract text from a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - pages: List of page numbers to extract (1-indexed)
    - ocr: Whether to use OCR for pages with no text
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.extract_text(file_path, pages, ocr)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_extract_images(file_path: str, pages: List[int] = None,
                             min_size: int = 100, ctx: Context = None) -> str:
    """Extract images from a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - pages: List of page numbers to extract (1-indexed)
    - min_size: Minimum image dimension in pixels
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.extract_images(file_path, pages, min_size)

        # If images were extracted and we have MCP context, create resources
        if "images" in results and results["images"] and ctx:
            for i, img_info in enumerate(results["images"]):
                if "data" in img_info:
                    img = Image(data=img_info["data"], format="png")
                    img_resource_id = f"pdf_img_{os.path.basename(file_path)}_{img_info['page']}"
                    ctx.set_resource(img_resource_id, img)
                    # Replace base64 data with resource ID
                    results["images"][i]["resource_id"] = img_resource_id
                    # Remove base64 data to keep response smaller
                    del results["images"][i]["data"]

        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_split(file_path: str, output_dir: str,
                    pages_per_file: int = 1, ctx: Context = None) -> str:
    """Split a PDF into multiple files.

    Parameters:
    - file_path: Path to the PDF file
    - output_dir: Directory to save the split files
    - pages_per_file: Number of pages per output file
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.split_pdf(file_path, output_dir, pages_per_file)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_merge(file_paths: List[str], output_path: str, ctx: Context = None) -> str:
    """Merge multiple PDF files into one.

    Parameters:
    - file_paths: List of paths to the PDF files to merge
    - output_path: Path to save the merged file
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.merge_pdfs(file_paths, output_path)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_add_watermark(file_path: str, output_path: str, text: str = None,
                            image_path: str = None, opacity: float = 0.3, ctx: Context = None) -> str:
    """Add a watermark to a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - output_path: Path to save the watermarked file
    - text: Text to use as watermark
    - image_path: Path to image to use as watermark
    - opacity: Opacity of the watermark (0-1)
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.add_watermark(file_path, output_path, text, image_path, opacity)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_encrypt(file_path: str, output_path: str, user_password: str,
                      owner_password: str = None, ctx: Context = None) -> str:
    """Encrypt a PDF document with password protection.

    Parameters:
    - file_path: Path to the PDF file
    - output_path: Path to save the encrypted file
    - user_password: Password required to open the PDF
    - owner_password: Password for full access (optional, defaults to user_password)
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.encrypt_pdf(file_path, output_path, user_password, owner_password)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_decrypt(file_path: str, output_path: str, password: str, ctx: Context = None) -> str:
    """Decrypt an encrypted PDF document.

    Parameters:
    - file_path: Path to the encrypted PDF file
    - output_path: Path to save the decrypted file
    - password: Password to decrypt the PDF
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.decrypt_pdf(file_path, output_path, password)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_get_form_fields(file_path: str, ctx: Context = None) -> str:
    """Get all form fields in a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.get_form_fields(file_path)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pdf_fill_form(file_path: str, output_path: str, form_data: Dict[str, str], ctx: Context = None) -> str:
    """Fill out form fields in a PDF document.

    Parameters:
    - file_path: Path to the PDF file
    - output_path: Path to save the filled form
    - form_data: Dictionary with field names as keys and field values as values
    """
    try:
        pdf_service = _get_pdf_service()
        results = await pdf_service.fill_form(file_path, output_path, form_data)
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# Tool registration and initialization
_pdf_service = None


def initialize_pdf_service():
    """Initialize the PDF service"""
    global _pdf_service
    _pdf_service = PDFService()
    return _pdf_service


def _get_pdf_service():
    """Get or initialize the PDF service"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = initialize_pdf_service()
    return _pdf_service


def get_pdf_tools():
    """Get a dictionary of all PDF tools for registration with MCP"""
    return {
        "pdf_info": pdf_info,
        "pdf_extract_text": pdf_extract_text,
        "pdf_extract_images": pdf_extract_images,
        "pdf_split": pdf_split,
        "pdf_merge": pdf_merge,
        "pdf_add_watermark": pdf_add_watermark,
        "pdf_encrypt": pdf_encrypt,
        "pdf_decrypt": pdf_decrypt,
        "pdf_get_form_fields": pdf_get_form_fields,
        "pdf_fill_form": pdf_fill_form
    }
