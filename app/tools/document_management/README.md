# Document Management Tool

## Overview
The Document Management tool provides utilities for working with various document types, including parsing, conversion, text extraction, searching, and comparison. It's designed to handle different file formats and enable document analysis and transformation.

## Features
- Get document metadata and information
- Parse documents into structured content
- Convert documents between different formats
- Extract text from documents
- Search for content within documents
- Compare documents to identify differences
- Validate document properties

## Supported Document Types
The tool supports a variety of document formats including:
- PDF (.pdf)
- Microsoft Word (.doc, .docx)
- Microsoft Excel (.xls, .xlsx)
- Plain Text (.txt)
- Rich Text Format (.rtf)
- HTML (.html, .htm)
- Markdown (.md)

## Usage Examples

### Get Document Information
```python
# Get metadata about a document
info = await document_info(document_path="/path/to/my_document.pdf")
print(info)
```

### Parse a Document
```python
# Parse document into structured content
parsed = await document_parse(document_path="/path/to/my_document.docx")
print(parsed)
```

### Convert Documents
```python
# Convert from one format to another
result = await document_convert(
    input_path="/path/to/my_document.docx",
    output_path="/path/to/output.pdf",
    output_format="pdf"
)
print(result)
```

### Extract Text
```python
# Extract all text from a document
text = await document_extract_text(document_path="/path/to/my_document.pdf")
print(text)
```

### Search in Documents
```python
# Search for text in a document
search_results = await document_search(
    document_path="/path/to/my_document.pdf",
    query="specific text to find",
    case_sensitive=False
)
print(search_results)
```

### Compare Documents
```python
# Compare two documents
comparison = await document_compare(
    doc_path1="/path/to/document1.docx",
    doc_path2="/path/to/document2.docx"
)
print(comparison)
```

### Validate Documents
```python
# Validate a document's size and type
validation = await document_validate(document_path="/path/to/my_document.pdf")
print(validation)
```

## API Reference

### document_info
Get information about a document.

**Parameters:**
- `document_path`: Path to the document file

**Returns:**
- JSON string with document metadata (type, size, creation date, modification date, etc.)

### document_parse
Parse a document into structured content.

**Parameters:**
- `document_path`: Path to the document file

**Returns:**
- JSON string with structured content extracted from the document

### document_convert
Convert a document from one format to another.

**Parameters:**
- `input_path`: Path to the input document
- `output_path`: Path for the output document
- `output_format`: Target format (e.g., 'pdf', 'docx', 'html')

**Returns:**
- JSON string with conversion result and status

### document_extract_text
Extract text content from a document.

**Parameters:**
- `document_path`: Path to the document file

**Returns:**
- JSON string with extracted text content

### document_search
Search for text within a document.

**Parameters:**
- `document_path`: Path to the document file
- `query`: Text to search for
- `case_sensitive`: Whether the search is case-sensitive (default: False)

**Returns:**
- JSON string with search results, including locations and context

### document_compare
Compare two documents and find differences.

**Parameters:**
- `doc_path1`: Path to the first document
- `doc_path2`: Path to the second document

**Returns:**
- JSON string with comparison results, highlighting differences

### document_validate
Validate document size and type.

**Parameters:**
- `document_path`: Path to the document file

**Returns:**
- JSON string with validation results

## Error Handling
The tool will return JSON with error information if an operation fails. Common errors include:
- File not found
- Unsupported document format
- Permission issues
- Corrupted documents
- Conversion failures

Example error handling:
```python
result = await document_parse("/path/to/document.pdf")
result_json = json.loads(result)

if "error" in result_json:
    print(f"Error: {result_json['error']}")
else:
    print("Parsing successful!")
    # Process the parsed content
```

## Limitations
- Some conversions may lose formatting or complex elements
- Very large documents may cause performance issues
- Password-protected documents require special handling
- Some document features might not be supported in all formats
- Depending on the document complexity, text extraction and searching might not be 100% accurate
