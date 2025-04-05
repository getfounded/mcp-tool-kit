# Filesystem Tool

## Overview
The Filesystem Tool provides a secure and robust way to interact with the file system. It includes functionality for reading, writing, and manipulating files and directories, with built-in security measures to limit access to allowed directories only.

## Features
- Read and write files with proper encoding handling
- Create and manipulate directories
- List directory contents
- Search for files and directories
- Get file metadata and directory structure
- Move and rename files
- Make line-based edits to text files
- Security restrictions to allowed directories

## Security
All filesystem operations are restricted to directories that the server is allowed to access. The tool includes a function to list these allowed directories, and all operations will fail if they attempt to access files outside of these directories.

## Usage Examples

### File Operations

```python
# Read a file
content = await read_file(path="/path/to/file.txt")
print(content)

# Write a file
result = await write_file(
    path="/path/to/new_file.txt",
    content="This is the content of the file."
)
print(result)

# Read multiple files at once
result = await read_multiple_files(
    paths=["/path/to/file1.txt", "/path/to/file2.txt"]
)
print(result)

# Edit specific lines in a file
edits = [
    {
        "oldText": "This is the old text",
        "newText": "This is the new text"
    }
]
result = await edit_file(
    path="/path/to/file.txt",
    edits=edits,
    dry_run=False  # Set to True to preview changes without making them
)
print(result)

# Get detailed file information
info = await get_file_info(path="/path/to/file.txt")
print(info)
```

### Directory Operations

```python
# Create a directory (works with nested directories too)
result = await create_directory(path="/path/to/new/directory")
print(result)

# List directory contents
contents = await list_directory(path="/path/to/directory")
print(contents)

# Get a recursive directory tree
tree = await directory_tree(path="/path/to/directory")
print(tree)

# Move or rename files/directories
result = await move_file(
    source="/path/to/source/file.txt",
    destination="/path/to/destination/file.txt"
)
print(result)

# Search for files matching a pattern
search_results = await search_files(
    path="/path/to/search/in",
    pattern="*.py",
    exclude_patterns=["__pycache__", "*.pyc"]
)
print(search_results)

# Check allowed directories
allowed = await list_allowed_directories()
print(allowed)
```

## API Reference

### read_file
Read the complete contents of a file from the file system.

**Parameters:**
- `path`: Path to the file to read

**Returns:**
- The file contents as a string, or an error message if the file cannot be read

### read_multiple_files
Read the contents of multiple files simultaneously.

**Parameters:**
- `paths`: List of file paths to read

**Returns:**
- Dictionary with file contents and status information

### write_file
Create a new file or completely overwrite an existing file with new content.

**Parameters:**
- `path`: Path to save the file
- `content`: Content to write to the file

**Returns:**
- Dictionary with operation result

### edit_file
Make line-based edits to a text file.

**Parameters:**
- `path`: Path to the file to edit
- `edits`: List of edit operations, each with 'oldText' and 'newText' properties
- `dry_run`: If True, returns diff without actually modifying the file

**Returns:**
- Dictionary with operation result including diff

### create_directory
Create a new directory or ensure a directory exists.

**Parameters:**
- `path`: Path to create

**Returns:**
- Dictionary with operation result

### list_directory
Get a detailed listing of all files and directories in a specified path.

**Parameters:**
- `path`: Path to list

**Returns:**
- Dictionary with directory contents

### directory_tree
Get a recursive tree view of files and directories as a JSON structure.

**Parameters:**
- `path`: Root path for the tree

**Returns:**
- Dictionary with tree structure

### move_file
Move or rename files and directories.

**Parameters:**
- `source`: Source path
- `destination`: Destination path

**Returns:**
- Dictionary with operation result

### search_files
Recursively search for files and directories matching a pattern.

**Parameters:**
- `path`: Root path for the search
- `pattern`: Search pattern
- `exclude_patterns`: Patterns to exclude

**Returns:**
- Dictionary with search results

### get_file_info
Retrieve detailed metadata about a file or directory.

**Parameters:**
- `path`: Path to get info for

**Returns:**
- Dictionary with file information

### list_allowed_directories
Returns the list of directories that this server is allowed to access.

**Returns:**
- Dictionary with allowed directories

## Error Handling
All filesystem operations include robust error handling. If an operation fails, the function will return an error message with details about what went wrong. Common errors include:
- File not found
- Permission denied
- Attempting to access a directory outside of allowed directories
- Invalid file paths
- File already exists (when moving files)

## Best Practices
1. Always check the allowed directories before attempting operations
2. Use path joining functions to construct paths rather than string concatenation
3. Handle errors gracefully by checking for error messages in the returned results
4. Use dry_run=True with edit_file to preview changes before applying them
5. Be careful with write_file as it will overwrite existing files without warning
