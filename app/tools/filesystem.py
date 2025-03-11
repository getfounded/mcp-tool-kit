#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import json
import shutil
import difflib
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import fnmatch
import logging
from datetime import datetime

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import Tool, TextContent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)

# External MCP reference for tool registration
external_mcp = None

def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Filesystem tools MCP reference set")

# Security utilities
class FilesystemSecurity:
    """Handles security validation for file paths"""
    
    def __init__(self, allowed_directories: List[str]):
        # Normalize all allowed directories to absolute paths
        self.allowed_directories = [os.path.normpath(os.path.abspath(self._expand_home(d))) 
                                   for d in allowed_directories]
        logging.info(f"Filesystem security initialized with allowed directories: {self.allowed_directories}")
    
    def _expand_home(self, path: str) -> str:
        """Expand ~ to user's home directory"""
        if path.startswith('~'):
            return os.path.expanduser(path)
        return path
    
    async def validate_path(self, requested_path: str) -> str:
        """
        Validate that a path is within allowed directories
        Returns the absolute, normalized path if valid, otherwise raises an exception
        """
        expanded_path = self._expand_home(requested_path)
        absolute_path = os.path.abspath(expanded_path)
        normalized_path = os.path.normpath(absolute_path)
        
        # Check if path is within allowed directories
        is_allowed = any(normalized_path.startswith(allowed_dir) 
                         for allowed_dir in self.allowed_directories)
        
        if not is_allowed:
            raise ValueError(f"Access denied - path outside allowed directories: {normalized_path} not in {self.allowed_directories}")
        
        # Handle symlinks by checking their real path
        try:
            real_path = os.path.realpath(normalized_path)
            normalized_real = os.path.normpath(real_path)
            
            is_real_path_allowed = any(normalized_real.startswith(allowed_dir) 
                                      for allowed_dir in self.allowed_directories)
            
            if not is_real_path_allowed:
                raise ValueError("Access denied - symlink target outside allowed directories")
            
            return real_path
        except FileNotFoundError:
            # For new files that don't exist yet, verify parent directory
            parent_dir = os.path.dirname(normalized_path)
            
            try:
                real_parent = os.path.realpath(parent_dir)
                normalized_parent = os.path.normpath(real_parent)
                
                is_parent_allowed = any(normalized_parent.startswith(allowed_dir) 
                                       for allowed_dir in self.allowed_directories)
                
                if not is_parent_allowed:
                    raise ValueError("Access denied - parent directory outside allowed directories")
                
                return normalized_path
            except FileNotFoundError:
                raise ValueError(f"Parent directory does not exist: {parent_dir}")


# File utility functions
class FilesystemTools:
    """Implements file operation tools that can be exposed via MCP"""
    
    def __init__(self, security: FilesystemSecurity):
        self.security = security
    
    async def read_file(self, path: str) -> str:
        """Read a file with path validation"""
        valid_path = await self.security.validate_path(path)
        
        try:
            with open(valid_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try different encodings
            try:
                with open(valid_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Failed to read file with alternative encoding: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")
    
    async def read_multiple_files(self, paths: List[str]) -> str:
        """Read multiple files and return their contents"""
        results = []
        
        for file_path in paths:
            try:
                content = await self.read_file(file_path)
                results.append(f"{file_path}:\n{content}\n")
            except Exception as e:
                results.append(f"{file_path}: Error - {str(e)}")
        
        return "\n---\n".join(results)
    
    async def write_file(self, path: str, content: str) -> str:
        """Write content to a file with path validation"""
        valid_path = await self.security.validate_path(path)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(valid_path), exist_ok=True)
            
            with open(valid_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote to {path}"
        except Exception as e:
            raise ValueError(f"Failed to write file: {str(e)}")
    
    def _normalize_line_endings(self, text: str) -> str:
        """Normalize line endings to \n"""
        return text.replace('\r\n', '\n')
    
    def _create_unified_diff(self, original: str, modified: str, filepath: str = 'file') -> str:
        """Create a unified diff between two texts"""
        original_norm = self._normalize_line_endings(original)
        modified_norm = self._normalize_line_endings(modified)
        
        original_lines = original_norm.splitlines(keepends=True)
        modified_lines = modified_norm.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines, 
            modified_lines,
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
            lineterm=''
        )
        
        return ''.join(diff)
    
    async def edit_file(self, path: str, edits: List[Dict[str, str]], dry_run: bool = False) -> str:
        """Apply edits to a file and return a diff of changes"""
        valid_path = await self.security.validate_path(path)
        
        try:
            content = await self.read_file(valid_path)
            content_norm = self._normalize_line_endings(content)
            
            # Apply edits sequentially
            modified_content = content_norm
            for edit in edits:
                old_text = self._normalize_line_endings(edit.get('oldText', ''))
                new_text = self._normalize_line_endings(edit.get('newText', ''))
                
                # If exact match exists, use it
                if old_text in modified_content:
                    modified_content = modified_content.replace(old_text, new_text)
                    continue
                
                # Try line-by-line matching with flexibility for whitespace
                old_lines = old_text.split('\n')
                content_lines = modified_content.split('\n')
                match_found = False
                
                for i in range(len(content_lines) - len(old_lines) + 1):
                    potential_match = content_lines[i:i+len(old_lines)]
                    
                    # Compare lines with normalized whitespace
                    is_match = all(ol.strip() == pl.strip() for ol, pl in zip(old_lines, potential_match))
                    
                    if is_match:
                        # Preserve original indentation of first line
                        original_indent = ''
                        match = content_lines[i].lstrip()
                        if match and len(content_lines[i]) > len(match):
                            original_indent = content_lines[i][:-len(match)]
                        
                        # Create new lines with preserved indentation
                        new_lines = []
                        for j, line in enumerate(new_text.split('\n')):
                            if j == 0:
                                new_lines.append(original_indent + line.lstrip())
                            else:
                                new_lines.append(line)
                        
                        # Replace lines in content
                        content_lines[i:i+len(old_lines)] = new_lines
                        modified_content = '\n'.join(content_lines)
                        match_found = True
                        break
                
                if not match_found:
                    raise ValueError(f"Could not find exact match for edit: {old_text}")
            
            # Create unified diff
            diff = self._create_unified_diff(content, modified_content, path)
            
            # Format diff with appropriate number of backticks
            num_backticks = 3
            while '`' * num_backticks in diff:
                num_backticks += 1
                
            formatted_diff = f"{'`' * num_backticks}diff\n{diff}{'`' * num_backticks}\n\n"
            
            if not dry_run:
                await self.write_file(path, modified_content)
                
            return formatted_diff
        except Exception as e:
            raise ValueError(f"Failed to edit file: {str(e)}")
    
    async def create_directory(self, path: str) -> str:
        """Create a directory with path validation"""
        valid_path = await self.security.validate_path(path)
        
        try:
            os.makedirs(valid_path, exist_ok=True)
            return f"Successfully created directory {path}"
        except Exception as e:
            raise ValueError(f"Failed to create directory: {str(e)}")
    
    async def list_directory(self, path: str) -> str:
        """List contents of a directory with path validation"""
        valid_path = await self.security.validate_path(path)
        
        try:
            entries = os.listdir(valid_path)
            formatted = []
            
            for entry in entries:
                entry_path = os.path.join(valid_path, entry)
                entry_type = "[DIR]" if os.path.isdir(entry_path) else "[FILE]"
                formatted.append(f"{entry_type} {entry}")
            
            return "\n".join(formatted)
        except Exception as e:
            raise ValueError(f"Failed to list directory: {str(e)}")
    
    async def directory_tree(self, path: str) -> str:
        """Generate a directory tree structure as JSON"""
        valid_path = await self.security.validate_path(path)
        
        try:
            def build_tree(current_path):
                entries = os.listdir(current_path)
                result = []
                
                for entry in entries:
                    entry_path = os.path.join(current_path, entry)
                    entry_data = {
                        "name": entry,
                        "type": "directory" if os.path.isdir(entry_path) else "file"
                    }
                    
                    if os.path.isdir(entry_path):
                        entry_data["children"] = build_tree(entry_path)
                    
                    result.append(entry_data)
                
                return result
            
            tree_data = build_tree(valid_path)
            return json.dumps(tree_data, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to create directory tree: {str(e)}")
    
    async def move_file(self, source: str, destination: str) -> str:
        """Move a file or directory with path validation"""
        valid_source = await self.security.validate_path(source)
        valid_dest = await self.security.validate_path(destination)
        
        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(valid_dest), exist_ok=True)
            
            shutil.move(valid_source, valid_dest)
            return f"Successfully moved {source} to {destination}"
        except Exception as e:
            raise ValueError(f"Failed to move file: {str(e)}")
    
    async def search_files(self, path: str, pattern: str, exclude_patterns: List[str] = None) -> str:
        """Recursively search for files matching a pattern"""
        if exclude_patterns is None:
            exclude_patterns = []
            
        valid_root = await self.security.validate_path(path)
        results = []
        
        try:
            for root, dirs, files in os.walk(valid_root):
                # Check if the directory should be excluded
                rel_dir = os.path.relpath(root, valid_root)
                if rel_dir == '.':
                    rel_dir = ''
                    
                should_skip = False
                for exclude in exclude_patterns:
                    if fnmatch.fnmatch(rel_dir, exclude):
                        should_skip = True
                        break
                
                if should_skip:
                    continue
                
                # Process directories
                for i, dir_name in enumerate(dirs):
                    if any(fnmatch.fnmatch(dir_name, pat) for pat in exclude_patterns):
                        dirs.pop(i)  # Don't traverse this directory
                        continue
                        
                    if pattern.lower() in dir_name.lower():
                        results.append(os.path.join(root, dir_name))
                
                # Process files
                for file_name in files:
                    if any(fnmatch.fnmatch(file_name, pat) for pat in exclude_patterns):
                        continue
                        
                    if pattern.lower() in file_name.lower():
                        results.append(os.path.join(root, file_name))
            
            return "\n".join(results) if results else "No matches found"
        except Exception as e:
            raise ValueError(f"Failed to search files: {str(e)}")
    
    async def get_file_info(self, path: str) -> str:
        """Get detailed metadata about a file or directory"""
        valid_path = await self.security.validate_path(path)
        
        try:
            stats = os.stat(valid_path)
            
            info = {
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
                "isDirectory": os.path.isdir(valid_path),
                "isFile": os.path.isfile(valid_path),
                "permissions": oct(stats.st_mode)[-3:],  # Last 3 digits of octal representation
                "absolutePath": os.path.abspath(valid_path),
                "filename": os.path.basename(valid_path)
            }
            
            return "\n".join(f"{key}: {value}" for key, value in info.items())
        except Exception as e:
            raise ValueError(f"Failed to get file info: {str(e)}")
    
    async def list_allowed_directories(self) -> str:
        """List all allowed directories"""
        return "Allowed directories:\n" + "\n".join(self.security.allowed_directories)


# Tool registration functions with proper MCP integration
class FileSystemTools:
    """Class containing tools for file system operations"""
    
    def __init__(self, allowed_dirs=None):
        # Default to user's home directory if no dirs specified
        if allowed_dirs is None:
            allowed_dirs = [os.path.expanduser("~")]
            
        self.security = FilesystemSecurity(allowed_dirs)
        self.tools = FilesystemTools(self.security)
        logging.info(f"Filesystem tools initialized with allowed directories: {allowed_dirs}")


# Tool function definitions that will be registered with MCP
async def read_file(path: str, ctx: Context = None) -> str:
    """Read the complete contents of a file from the file system.
    
    Handles various text encodings and provides detailed error messages
    if the file cannot be read. Use this tool when you need to examine
    the contents of a single file. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.read_file(path)
    except Exception as e:
        return f"Error reading file: {str(e)}"


async def read_multiple_files(paths: List[str], ctx: Context = None) -> str:
    """Read the contents of multiple files simultaneously.
    
    This is more efficient than reading files one by one when you need to analyze
    or compare multiple files. Each file's content is returned with its
    path as a reference. Failed reads for individual files won't stop
    the entire operation. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.read_multiple_files(paths)
    except Exception as e:
        return f"Error reading multiple files: {str(e)}"


async def write_file(path: str, content: str, ctx: Context = None) -> str:
    """Create a new file or completely overwrite an existing file with new content.
    
    Use with caution as it will overwrite existing files without warning.
    Handles text content with proper encoding. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.write_file(path, content)
    except Exception as e:
        return f"Error writing file: {str(e)}"


async def edit_file(path: str, edits: List[Dict[str, str]], dry_run: bool = False, ctx: Context = None) -> str:
    """Make line-based edits to a text file.
    
    Each edit replaces exact line sequences with new content. Returns a git-style diff
    showing the changes made. Only works within allowed directories.
    
    Parameters:
    - path: Path to the file to edit
    - edits: List of edit operations, each with 'oldText' and 'newText' properties
    - dry_run: If True, returns diff without actually modifying the file
    """
    try:
        return await _get_fs_tools().tools.edit_file(path, edits, dry_run)
    except Exception as e:
        return f"Error editing file: {str(e)}"


async def create_directory(path: str, ctx: Context = None) -> str:
    """Create a new directory or ensure a directory exists.
    
    Can create multiple nested directories in one operation. If the directory already exists,
    this operation will succeed silently. Perfect for setting up directory
    structures for projects or ensuring required paths exist. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.create_directory(path)
    except Exception as e:
        return f"Error creating directory: {str(e)}"


async def list_directory(path: str, ctx: Context = None) -> str:
    """Get a detailed listing of all files and directories in a specified path.
    
    Results clearly distinguish between files and directories with [FILE] and [DIR]
    prefixes. This tool is essential for understanding directory structure and
    finding specific files within a directory. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.list_directory(path)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


async def directory_tree(path: str, ctx: Context = None) -> str:
    """Get a recursive tree view of files and directories as a JSON structure.
    
    Each entry includes 'name', 'type' (file/directory), and 'children' for directories.
    Files have no children array, while directories always have a children array (which may be empty).
    The output is formatted with 2-space indentation for readability. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.directory_tree(path)
    except Exception as e:
        return f"Error creating directory tree: {str(e)}"


async def move_file(source: str, destination: str, ctx: Context = None) -> str:
    """Move or rename files and directories.
    
    Can move files between directories and rename them in a single operation.
    If the destination exists, the operation will fail. Works across different
    directories and can be used for simple renaming within the same directory.
    Both source and destination must be within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.move_file(source, destination)
    except Exception as e:
        return f"Error moving file: {str(e)}"


async def search_files(path: str, pattern: str, exclude_patterns: List[str] = None, ctx: Context = None) -> str:
    """Recursively search for files and directories matching a pattern.
    
    Searches through all subdirectories from the starting path. The search
    is case-insensitive and matches partial names. Returns full paths to all
    matching items. Great for finding files when you don't know their exact location.
    Only searches within allowed directories.
    """
    if exclude_patterns is None:
        exclude_patterns = []
    try:
        return await _get_fs_tools().tools.search_files(path, pattern, exclude_patterns)
    except Exception as e:
        return f"Error searching files: {str(e)}"


async def get_file_info(path: str, ctx: Context = None) -> str:
    """Retrieve detailed metadata about a file or directory.
    
    Returns comprehensive information including size, creation time, last modified time,
    permissions, and type. This tool is perfect for understanding file characteristics
    without reading the actual content. Only works within allowed directories.
    """
    try:
        return await _get_fs_tools().tools.get_file_info(path)
    except Exception as e:
        return f"Error getting file info: {str(e)}"


async def list_allowed_directories(ctx: Context = None) -> str:
    """Returns the list of directories that this server is allowed to access.
    
    Use this to understand which directories are available before trying to access files.
    """
    try:
        return await _get_fs_tools().tools.list_allowed_directories()
    except Exception as e:
        return f"Error listing allowed directories: {str(e)}"


# Tool registration and initialization
_fs_tools_instance = None

def initialize_fs_tools(allowed_dirs=None):
    """Initialize the filesystem tools with specified allowed directories"""
    global _fs_tools_instance
    _fs_tools_instance = FileSystemTools(allowed_dirs)
    return _fs_tools_instance

def _get_fs_tools():
    """Get or initialize the filesystem tools"""
    global _fs_tools_instance
    if _fs_tools_instance is None:
        _fs_tools_instance = initialize_fs_tools()
    return _fs_tools_instance

def get_filesystem_tools(allowed_dirs=None):
    """Get a dictionary of all filesystem tools for registration with MCP"""
    # Initialize with allowed dirs if specified
    if allowed_dirs:
        initialize_fs_tools(allowed_dirs)
    
    return {
        "read_file": read_file,
        "read_multiple_files": read_multiple_files,
        "write_file": write_file,
        "edit_file": edit_file,
        "create_directory": create_directory,
        "list_directory": list_directory,
        "directory_tree": directory_tree,
        "move_file": move_file,
        "search_files": search_files,
        "get_file_info": get_file_info,
        "list_allowed_directories": list_allowed_directories
    }

# If this file is run directly, print the list of tools
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python filesystem.py <allowed-directory> [additional-directories...]")
        sys.exit(1)
    
    allowed_dirs = [os.path.abspath(d) for d in sys.argv[1:]]
    initialize_fs_tools(allowed_dirs)
    
    print(f"Filesystem tools initialized with allowed directories: {allowed_dirs}")
    print("Available tools:")
    for tool_name in get_filesystem_tools().keys():
        print(f"- {tool_name}")
