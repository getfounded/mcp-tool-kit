#!/usr/bin/env python3
"""
Filesystem tools implementation using the decorator pattern.
"""
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.filesystem.filesystem_service import FilesystemService

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Read the complete contents of a file from the file system"
)
async def read_file(self, path: str) -> str:
    """
    Read the complete contents of a file from the file system.
    
    Handles various text encodings and provides detailed error messages
    if the file cannot be read. Use this tool when you need to examine
    the contents of a single file. Only works within allowed directories.
    
    Args:
        path: Path to the file to read
        
    Returns:
        The file contents as a string
    """
    try:
        return await self.read_file(path)
    except Exception as e:
        return f"Error reading file: {str(e)}"

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Read the contents of multiple files simultaneously"
)
async def read_multiple_files(self, paths: List[str]) -> Dict[str, Any]:
    """
    Read the contents of multiple files simultaneously.
    
    This is more efficient than reading files one by one when you need to analyze
    or compare multiple files. Each file's content is returned with its
    path as a reference. Failed reads for individual files won't stop
    the entire operation. Only works within allowed directories.
    
    Args:
        paths: List of file paths to read
        
    Returns:
        Dictionary with file contents and status information
    """
    try:
        return await self.read_multiple_files(paths)
    except Exception as e:
        return {"error": f"Error reading multiple files: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Create a new file or completely overwrite an existing file with new content"
)
async def write_file(self, path: str, content: str) -> Dict[str, Any]:
    """
    Create a new file or completely overwrite an existing file with new content.
    
    Use with caution as it will overwrite existing files without warning.
    Handles text content with proper encoding. Only works within allowed directories.
    
    Args:
        path: Path to save the file
        content: Content to write to the file
        
    Returns:
        Dictionary with operation result
    """
    try:
        return await self.write_file(path, content)
    except Exception as e:
        return {"error": f"Error writing file: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Make line-based edits to a text file"
)
async def edit_file(
    self,
    path: str, 
    edits: List[Dict[str, str]], 
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Make line-based edits to a text file.
    
    Each edit replaces exact line sequences with new content. Returns a git-style diff
    showing the changes made. Only works within allowed directories.
    
    Args:
        path: Path to the file to edit
        edits: List of edit operations, each with 'oldText' and 'newText' properties
        dry_run: If True, returns diff without actually modifying the file
        
    Returns:
        Dictionary with operation result including diff
    """
    try:
        return await self.edit_file(path, edits, dry_run)
    except Exception as e:
        return {"error": f"Error editing file: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Create a new directory or ensure a directory exists"
)
async def create_directory(self, path: str) -> Dict[str, Any]:
    """
    Create a new directory or ensure a directory exists.
    
    Can create multiple nested directories in one operation. If the directory already exists,
    this operation will succeed silently. Perfect for setting up directory
    structures for projects or ensuring required paths exist. Only works within allowed directories.
    
    Args:
        path: Path to create
        
    Returns:
        Dictionary with operation result
    """
    try:
        return await self.create_directory(path)
    except Exception as e:
        return {"error": f"Error creating directory: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Get a detailed listing of all files and directories in a specified path"
)
async def list_directory(self, path: str) -> Dict[str, Any]:
    """
    Get a detailed listing of all files and directories in a specified path.
    
    Results clearly distinguish between files and directories with type information.
    This tool is essential for understanding directory structure and
    finding specific files within a directory. Only works within allowed directories.
    
    Args:
        path: Path to list
        
    Returns:
        Dictionary with directory contents
    """
    try:
        return await self.list_directory(path)
    except Exception as e:
        return {"error": f"Error listing directory: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Get a recursive tree view of files and directories"
)
async def directory_tree(self, path: str) -> Dict[str, Any]:
    """
    Get a recursive tree view of files and directories as a JSON structure.
    
    Each entry includes 'name', 'type' (file/directory), and 'children' for directories.
    Files have no children array, while directories always have a children array (which may be empty).
    The returned structure is perfect for visualizing directory hierarchy.
    Only works within allowed directories.
    
    Args:
        path: Root path for the tree
        
    Returns:
        Dictionary with tree structure
    """
    try:
        return await self.directory_tree(path)
    except Exception as e:
        return {"error": f"Error creating directory tree: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Move or rename files and directories"
)
async def move_file(self, source: str, destination: str) -> Dict[str, Any]:
    """
    Move or rename files and directories.
    
    Can move files between directories and rename them in a single operation.
    If the destination exists, the operation will fail. Works across different
    directories and can be used for simple renaming within the same directory.
    Both source and destination must be within allowed directories.
    
    Args:
        source: Source path
        destination: Destination path
        
    Returns:
        Dictionary with operation result
    """
    try:
        return await self.move_file(source, destination)
    except Exception as e:
        return {"error": f"Error moving file: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Recursively search for files and directories matching a pattern"
)
async def search_files(
    self,
    path: str, 
    pattern: str, 
    exclude_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Recursively search for files and directories matching a pattern.
    
    Searches through all subdirectories from the starting path. The search
    is case-insensitive and matches partial names. Returns full paths to all
    matching items. Great for finding files when you don't know their exact location.
    Only searches within allowed directories.
    
    Args:
        path: Root path for the search
        pattern: Search pattern
        exclude_patterns: Patterns to exclude
        
    Returns:
        Dictionary with search results
    """
    if exclude_patterns is None:
        exclude_patterns = []
    try:
        return await self.search_files(path, pattern, exclude_patterns)
    except Exception as e:
        return {"error": f"Error searching files: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Retrieve detailed metadata about a file or directory"
)
async def get_file_info(self, path: str) -> Dict[str, Any]:
    """
    Retrieve detailed metadata about a file or directory.
    
    Returns comprehensive information including size, creation time, last modified time,
    permissions, and type. This tool is perfect for understanding file characteristics
    without reading the actual content. Only works within allowed directories.
    
    Args:
        path: Path to get info for
        
    Returns:
        Dictionary with file information
    """
    try:
        return await self.get_file_info(path)
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}

@register_tool(
    category="filesystem",
    service_class=FilesystemService,
    description="Returns the list of directories that this server is allowed to access"
)
async def list_allowed_directories(self) -> Dict[str, Any]:
    """
    Returns the list of directories that this server is allowed to access.
    
    Use this to understand which directories are available before trying to access files.
    
    Returns:
        Dictionary with allowed directories
    """
    try:
        return await self.list_allowed_directories()
    except Exception as e:
        return {"error": f"Error listing allowed directories: {str(e)}"}
