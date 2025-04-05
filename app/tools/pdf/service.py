#!/usr/bin/env python3
"""
Service implementation for PDF operations.
"""
import os
import logging
import tempfile
import io
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from app.tools.base.service import ToolServiceBase


class PDFService(ToolServiceBase):
    """Service to handle PDF operations"""

    def __init__(self):
        """Initialize the PDF service"""
        super().__init__()
        self.ocr_enabled = self._parse_bool(
            self.get_env_var("PDF_OCR_ENABLED", default="False"))
        self.temp_dir = self.get_env_var(
            "PDF_TEMP_DIR", default=tempfile.gettempdir())
        self.pytesseract_path = self.get_env_var("PYTESSERACT_PATH")

    def initialize(self) -> bool:
        """
        Initialize the PDF service.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Verify dependencies
            import PyPDF2

            # Configure OCR if enabled
            if self.ocr_enabled:
                try:
                    import pdf2image
                    import pytesseract
                    if self.pytesseract_path:
                        pytesseract.pytesseract.tesseract_cmd = self.pytesseract_path
                except ImportError as e:
                    self.logger.warning(
                        f"OCR dependencies not available: {str(e)}")
                    self.ocr_enabled = False

            # Ensure temp directory exists
            os.makedirs(self.temp_dir, exist_ok=True)

            self.initialized = True
            self.logger.info("PDF service initialized successfully")
            return True
        except ImportError as e:
            self.logger.error(f"Missing dependency: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize PDF service: {str(e)}")
            return False

    def _parse_bool(self, value: str) -> bool:
        """Parse string to boolean"""
        return value.lower() in ('true', 'yes', '1', 't', 'y')

    def _validate_pdf_path(self, file_path: str) -> bool:
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

    def _normalize_pages(self, pages: Optional[List[int]], total_pages: int) -> List[int]:
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
                raise ValueError(
                    f"Page number out of range: {p} (document has {total_pages} pages)")

            result.append(idx)

        return result

    def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dict with PDF metadata
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                info = reader.metadata

                # Convert PDF info object to dict
                metadata = {}
                if info:
                    for key in info:
                        value = info[key]
                        # Convert binary string to regular string if needed
                        if isinstance(value, bytes):
                            try:
                                value = value.decode('utf-8')
                            except UnicodeDecodeError:
                                value = str(value)
                        metadata[key] = value

                result = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "pages": len(reader.pages),
                    "metadata": metadata,
                    "is_encrypted": reader.is_encrypted,
                    "form_fields": bool(reader.get_fields()),
                    "page_sizes": [],
                }

                # Get page sizes (first 10 pages only to avoid performance issues with large docs)
                max_pages_for_size = min(10, len(reader.pages))
                for i in range(max_pages_for_size):
                    page = reader.pages[i]
                    box = page.mediabox
                    result["page_sizes"].append({
                        "page": i + 1,
                        "width": round(float(box.width), 2),
                        "height": round(float(box.height), 2),
                        "unit": "pt"
                    })

                return {
                    "status": "success",
                    "info": result
                }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error getting PDF info: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get PDF info: {str(e)}"
            }

    def extract_text(self, file_path: str, pages: Optional[List[int]] = None, use_ocr: bool = False) -> Dict[str, Any]:
        """
        Extract text from PDF pages.

        Args:
            file_path: Path to the PDF file
            pages: List of page numbers to extract (1-indexed) or None for all pages
            use_ocr: Whether to use OCR for pages with no text

        Returns:
            Dict with extracted text by page
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Initialize OCR if needed
            if use_ocr and self.ocr_enabled:
                import pdf2image
                import pytesseract
            elif use_ocr and not self.ocr_enabled:
                return {
                    "status": "error",
                    "message": "OCR is requested but not enabled or dependencies not installed"
                }

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)

                # Normalize pages
                page_indices = self._normalize_pages(pages, total_pages)

                result = {
                    "path": file_path,
                    "total_pages": total_pages,
                    "processed_pages": len(page_indices),
                    "text_by_page": {}
                }

                # Extract text from each page
                for idx in page_indices:
                    page = reader.pages[idx]
                    text = page.extract_text()

                    # Try OCR if no text found and OCR is enabled
                    if (not text or text.isspace()) and use_ocr and self.ocr_enabled:
                        try:
                            # Convert PDF page to image
                            images = pdf2image.convert_from_path(
                                file_path,
                                first_page=idx+1,
                                last_page=idx+1
                            )

                            if images:
                                # Use OCR to extract text from image
                                text = pytesseract.image_to_string(images[0])
                        except Exception as ocr_err:
                            self.logger.warning(
                                f"OCR failed for page {idx+1}: {str(ocr_err)}")

                    # Store the extracted text (1-indexed in result)
                    result["text_by_page"][str(idx + 1)] = text or ""

                return {
                    "status": "success",
                    "result": result
                }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error extracting text: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to extract text: {str(e)}"
            }

    def extract_images(self, file_path: str, pages: Optional[List[int]] = None, min_size: int = 100) -> Dict[str, Any]:
        """
        Extract images from PDF pages.

        Args:
            file_path: Path to the PDF file
            pages: List of page numbers to extract (1-indexed) or None for all pages
            min_size: Minimum image dimension in pixels

        Returns:
            Dict with extracted image info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Create output directory based on filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.join(self.temp_dir, f"{base_name}_images")
            os.makedirs(output_dir, exist_ok=True)

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)

                # Normalize pages
                page_indices = self._normalize_pages(pages, total_pages)

                result = {
                    "path": file_path,
                    "output_directory": output_dir,
                    "total_pages": total_pages,
                    "processed_pages": len(page_indices),
                    "extracted_images": []
                }

                # Counter for image filenames
                image_counter = 0

                # Process each page
                for idx in page_indices:
                    page = reader.pages[idx]
                    page_num = idx + 1  # 1-indexed for result

                    # Check for XObject images
                    if '/Resources' in page and '/XObject' in page['/Resources']:
                        xobjects = page['/Resources']['/XObject']

                        for key, xobject in xobjects.items():
                            if xobject['/Subtype'] == '/Image':
                                # Get image data and size
                                width = xobject['/Width']
                                height = xobject['/Height']

                                # Skip small images
                                if width < min_size or height < min_size:
                                    continue

                                # Determine image format and extraction method
                                image_format = None
                                image_data = None

                                if '/Filter' in xobject:
                                    filters = xobject['/Filter']
                                    if isinstance(filters, list):
                                        filters = filters[0]

                                    if filters == '/DCTDecode':
                                        image_format = 'jpg'
                                        image_data = xobject._data
                                    elif filters == '/FlateDecode':
                                        if '/ColorSpace' in xobject:
                                            colorspace = xobject['/ColorSpace']
                                            if isinstance(colorspace, list):
                                                colorspace = colorspace[0]

                                            if colorspace == '/DeviceRGB':
                                                image_format = 'png'
                                                # TODO: Convert data to PNG
                                            elif colorspace == '/DeviceGray':
                                                image_format = 'png'
                                                # TODO: Convert data to PNG

                                # Save image if format could be determined
                                if image_format and image_data:
                                    image_counter += 1
                                    image_filename = f"page{page_num}_image{image_counter}.{image_format}"
                                    image_path = os.path.join(
                                        output_dir, image_filename)

                                    with open(image_path, 'wb') as img_file:
                                        img_file.write(image_data)

                                    result["extracted_images"].append({
                                        "page": page_num,
                                        "filename": image_filename,
                                        "path": image_path,
                                        "width": width,
                                        "height": height,
                                        "format": image_format
                                    })

                return {
                    "status": "success",
                    "result": result
                }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error extracting images: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to extract images: {str(e)}"
            }

    def split_pdf(self, file_path: str, output_dir: str, pages_per_file: int = 1) -> Dict[str, Any]:
        """
        Split a PDF into multiple files.

        Args:
            file_path: Path to the PDF file
            output_dir: Directory to save the split files
            pages_per_file: Number of pages per output file

        Returns:
            Dict with split file info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Validate output directory
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            elif not os.path.isdir(output_dir):
                raise ValueError(
                    f"Output path is not a directory: {output_dir}")

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)

                # Calculate number of output files
                file_count = (total_pages + pages_per_file -
                              1) // pages_per_file

                result = {
                    "path": file_path,
                    "total_pages": total_pages,
                    "pages_per_file": pages_per_file,
                    "output_directory": output_dir,
                    "output_files": []
                }

                base_name = os.path.splitext(os.path.basename(file_path))[0]

                # Create each output file
                for i in range(file_count):
                    start_page = i * pages_per_file
                    end_page = min((i + 1) * pages_per_file, total_pages)

                    writer = PdfWriter()

                    # Add pages to writer
                    for p in range(start_page, end_page):
                        writer.add_page(reader.pages[p])

                    # Create output filename
                    output_filename = f"{base_name}_part{i+1}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    # Write the output file
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)

                    result["output_files"].append({
                        "filename": output_filename,
                        "path": output_path,
                        "start_page": start_page + 1,  # 1-indexed for result
                        "end_page": end_page,
                        "page_count": end_page - start_page
                    })

                return {
                    "status": "success",
                    "result": result
                }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error splitting PDF: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to split PDF: {str(e)}"
            }

    def merge_pdfs(self, file_paths: List[str], output_path: str) -> Dict[str, Any]:
        """
        Merge multiple PDFs into one.

        Args:
            file_paths: List of paths to the PDF files to merge
            output_path: Path to save the merged file

        Returns:
            Dict with merged file info
        """
        self._is_initialized()
        try:
            # Validate input files
            if not file_paths:
                raise ValueError("No input files provided")

            for path in file_paths:
                self._validate_pdf_path(path)

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Create PDF merger
            merger = PyPDF2.PdfMerger()

            # Add each file to the merger
            for path in file_paths:
                merger.append(path)

            # Write merged PDF
            merger.write(output_path)
            merger.close()

            result = {
                "input_files": file_paths,
                "output_path": output_path,
                "page_count": 0
            }

            # Get total page count from result
            with open(output_path, 'rb') as file:
                reader = PdfReader(file)
                result["page_count"] = len(reader.pages)

            return {
                "status": "success",
                "result": result
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error merging PDFs: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to merge PDFs: {str(e)}"
            }

    def add_watermark(self, file_path: str, output_path: str, text: Optional[str] = None,
                      image_path: Optional[str] = None, opacity: float = 0.3) -> Dict[str, Any]:
        """
        Add a watermark to a PDF.

        Args:
            file_path: Path to the PDF file
            output_path: Path to save the watermarked file
            text: Text to use as watermark
            image_path: Path to image to use as watermark
            opacity: Opacity of the watermark (0-1)

        Returns:
            Dict with watermarked file info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Validate input
            if not text and not image_path:
                raise ValueError("Either text or image_path must be provided")

            if image_path and not os.path.exists(image_path):
                raise ValueError(f"Image file not found: {image_path}")

            # Create watermark PDF
            watermark_buffer = io.BytesIO()
            c = canvas.Canvas(watermark_buffer)

            # Get the page size from the first page
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                if not reader.pages:
                    raise ValueError("PDF has no pages")

                page = reader.pages[0]
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)

            c.setPageSize((width, height))

            # Set transparency
            c.saveState()
            c.setFillAlpha(opacity)
            c.setStrokeAlpha(opacity)

            # Add text watermark
            if text:
                c.setFont("Helvetica", 60)
                c.translate(width/2, height/2)
                c.rotate(45)
                c.setFillColorRGB(0, 0, 0)
                c.drawCentredString(0, 0, text)

            # Add image watermark (TODO: implement image watermark support)
            # if image_path:
            #     img = ImageReader(image_path)
            #     c.drawImage(img, 0, 0, width=width, height=height)

            c.restoreState()
            c.save()

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Apply watermark to each page
            watermark_buffer.seek(0)
            watermark_pdf = PdfReader(watermark_buffer)
            watermark_page = watermark_pdf.pages[0]

            with open(file_path, 'rb') as input_file:
                reader = PdfReader(input_file)
                writer = PdfWriter()

                # Apply watermark to each page
                for page in reader.pages:
                    page.merge_page(watermark_page)
                    writer.add_page(page)

                # Copy metadata
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # Write output file
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return {
                "status": "success",
                "result": {
                    "input_path": file_path,
                    "output_path": output_path,
                    "watermark_type": "text" if text else "image",
                    "opacity": opacity
                }
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error adding watermark: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to add watermark: {str(e)}"
            }

    def encrypt_pdf(self, file_path: str, output_path: str, user_password: str,
                    owner_password: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt a PDF with password protection.

        Args:
            file_path: Path to the PDF file
            output_path: Path to save the encrypted file
            user_password: Password required to open the PDF
            owner_password: Password for full access (optional, defaults to user_password)

        Returns:
            Dict with encrypted file info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Validate passwords
            if not user_password:
                raise ValueError("User password is required")

            # Use user_password as owner_password if not provided
            if not owner_password:
                owner_password = user_password

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                # Add all pages to the writer
                for page in reader.pages:
                    writer.add_page(page)

                # Copy metadata
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # Encrypt the PDF
                writer.encrypt(user_password=user_password,
                               owner_password=owner_password)

                # Write encrypted PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return {
                "status": "success",
                "result": {
                    "input_path": file_path,
                    "output_path": output_path,
                    "is_encrypted": True
                }
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error encrypting PDF: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to encrypt PDF: {str(e)}"
            }

    def decrypt_pdf(self, file_path: str, output_path: str, password: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted PDF.

        Args:
            file_path: Path to the encrypted PDF file
            output_path: Path to save the decrypted file
            password: Password to decrypt the PDF

        Returns:
            Dict with decrypted file info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Validate password
            if not password:
                raise ValueError("Password is required")

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)

                # Check if the PDF is encrypted
                if not reader.is_encrypted:
                    return {
                        "status": "error",
                        "message": "PDF is not encrypted"
                    }

                # Try to decrypt
                try:
                    reader.decrypt(password)
                except Exception as decrypt_err:
                    return {
                        "status": "error",
                        "message": f"Failed to decrypt PDF: {str(decrypt_err)}"
                    }

                # Create a new PDF without encryption
                writer = PdfWriter()

                # Add all pages to the writer
                for page in reader.pages:
                    writer.add_page(page)

                # Copy metadata
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # Write decrypted PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return {
                "status": "success",
                "result": {
                    "input_path": file_path,
                    "output_path": output_path,
                    "is_encrypted": False
                }
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error decrypting PDF: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to decrypt PDF: {str(e)}"
            }

    def get_form_fields(self, file_path: str) -> Dict[str, Any]:
        """
        Get all form fields in a PDF.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dict with form field info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)

                # Get form fields
                fields = reader.get_fields()

                # If no fields found
                if not fields:
                    return {
                        "status": "success",
                        "result": {
                            "path": file_path,
                            "has_form": False,
                            "fields": {}
                        }
                    }

                # Process fields
                processed_fields = {}
                for key, field in fields.items():
                    field_type = field.get('/FT', 'Unknown')
                    field_value = reader.get_field(key)

                    # Determine field type
                    field_type_name = 'unknown'
                    if field_type == '/Tx':
                        field_type_name = 'text'
                    elif field_type == '/Btn':
                        if field.get('/Ff', 0) & 32768:  # RadioButton flag
                            field_type_name = 'radio'
                        else:
                            field_type_name = 'checkbox'
                    elif field_type == '/Ch':
                        if field.get('/Ff', 0) & 131072:  # Combo flag
                            field_type_name = 'combobox'
                        else:
                            field_type_name = 'listbox'

                    # Get options for choice fields
                    options = []
                    if field_type_name in ['combobox', 'listbox'] and '/Opt' in field:
                        opt = field['/Opt']
                        for item in opt:
                            if isinstance(item, list) and len(item) >= 2:
                                options.append(str(item[1]))
                            else:
                                options.append(str(item))

                    processed_fields[key] = {
                        'type': field_type_name,
                        'value': field_value,
                        'options': options
                    }

                return {
                    "status": "success",
                    "result": {
                        "path": file_path,
                        "has_form": True,
                        "fields": processed_fields
                    }
                }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error getting form fields: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get form fields: {str(e)}"
            }

    def fill_form(self, file_path: str, output_path: str, form_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Fill out form fields in a PDF.

        Args:
            file_path: Path to the PDF file
            output_path: Path to save the filled form
            form_data: Dictionary with field names as keys and field values as values

        Returns:
            Dict with filled form info
        """
        self._is_initialized()
        try:
            self._validate_pdf_path(file_path)

            # Validate form data
            if not form_data:
                raise ValueError("Form data is required")

            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                writer = PdfWriter()

                # Check if the PDF has a form
                if not reader.get_fields():
                    return {
                        "status": "error",
                        "message": "PDF has no form fields"
                    }

                # Add all pages to the writer
                for page in reader.pages:
                    writer.add_page(page)

                # Update form fields
                writer.update_page_form_field_values(
                    writer.pages[0], form_data
                )

                # Write the filled form
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            # Verify which fields were filled
            filled_fields = {}
            with open(output_path, 'rb') as file:
                reader = PdfReader(file)
                for field_name in form_data:
                    value = reader.get_field(field_name)
                    filled_fields[field_name] = str(
                        value) if value is not None else None

            return {
                "status": "success",
                "result": {
                    "input_path": file_path,
                    "output_path": output_path,
                    "filled_fields": filled_fields
                }
            }

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            self.logger.error(f"Error filling form: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to fill form: {str(e)}"
            }


# Singleton instance
_service_instance = None


def get_service() -> PDFService:
    """
    Get or initialize the PDF service singleton.

    Returns:
        PDFService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = PDFService()
        _service_instance.initialize()
    return _service_instance
