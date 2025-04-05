#!/usr/bin/env python3
"""
Enhanced filesystem service for secure file operations.
"""
import os
import sys
import json
import shutil
import difflib
import fnmatch
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path

from app.tools.base.service import ToolServiceBase


class FilesystemSecurity:
    """Handles security validation for file paths"""

    def __init__(self, allowed_directories: List[str]):
        """
        Initialize with allowed directories.

        Args:
            allowed_directories: List of directories that can be accessed
        """
        # Normalize all allowed directories to absolute paths
        self.allowed_directories = [os.path.normpath(os.path.abspath(self._expand_home(d)))
                                    for d in allowed_directories]

    def _expand_home(self, path: str) -> str:
        """
        Expand ~ to user's home directory.

        Args:
            path: Path that may contain ~

        Returns:
            Path with ~ expanded
        """
        if path.startswith('~'):
            return os.path.expanduser(path)
        return path

    async def validate_path(self, requested_path: str) -> str:
        """
        Validate that a path is within allowed directories.

        Args:
            requested_path: Path to validate

        Returns:
            Absolute, normalized path if valid

        Raises:
            ValueError: If path is outside allowed directories
        """
        expanded_path = self._expand_home(requested_path)
        absolute_path = os.path.abspath(expanded_path)
        normalized_path = os.path.normpath(absolute_path)

        # Check if path is within allowed directories
        is_allowed = any(normalized_path.startswith(allowed_dir)
                         for allowed_dir in self.allowed_directories)

        if not is_allowed:
            raise ValueError(
                f"Access denied - path outside allowed directories: {normalized_path}")

        # Handle symlinks by checking their real path
        try:
            real_path = os.path.realpath(normalized_path)
            normalized_real = os.path.normpath(real_path)

            is_real_path_allowed = any(normalized_real.startswith(allowed_dir)
                                       for allowed_dir in self.allowed_directories)

            if not is_real_path_allowed:
                raise ValueError(
                    "Access denied - symlink target outside allowed directories")

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
                    raise ValueError(
                        "Access denied - parent directory outside allowed directories")

                return normalized_path
            except FileNotFoundError:
                raise ValueError(
                    f"Parent directory does not exist: {parent_dir}")


class FilesystemService(ToolServiceBase):
    """Service for secure filesystem operations"""

    def __init__(self):
        """Initialize the filesystem service"""
        super().__init__()
        self.security = None

    def initialize(self) -> bool:
        """
        Initialize the service with allowed directories from environment.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Get allowed directories from environment
            allowed_dirs_str = self.get_env_var(
                "ALLOWED_DIRECTORIES", default="")

            if allowed_dirs_str:
                # Split by comma and strip whitespace
                allowed_dirs = [d.strip() for d in allowed_dirs_str.split(',')]
            else:
                # Default to current directory if not specified
                allowed_dirs = [os.getcwd()]

            # Initialize security
            self.security = FilesystemSecurity(allowed_dirs)

            self.logger.info(
                f"Filesystem service initialized with allowed directories: {allowed_dirs}")
            self.initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize filesystem service: {e}")
            return False

    async def read_file(self, path: str) -> str:
        """
        Read a file with path validation.

        Args:
            path: Path to the file to read

        Returns:
            File content as a string

        Raises:
            ValueError: If the file cannot be read
        """
        self._is_initialized()

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
                raise ValueError(
                    f"Failed to read file with alternative encoding: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")

    async def read_multiple_files(self, paths: List[str]) -> Dict[str, Any]:
        """
        Read multiple files and return their contents.

        Args:
            paths: List of file paths to read

        Returns:
            Dictionary with file paths as keys and contents as values
        """
        self._is_initialized()

        results = {}

        for file_path in paths:
            try:
                content = await self.read_file(file_path)
                results[file_path] = {
                    "content": content,
                    "status": "success"
                }
            except Exception as e:
                results[file_path] = {
                    "error": str(e),
                    "status": "error"
                }

        return {
            "files": results,
            "total": len(paths),
            "successful": sum(1 for r in results.values() if r["status"] == "success")
        }

    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file with path validation.

        Args:
            path: Path to write the file to
            content: Content to write

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If the file cannot be written
        """
        self._is_initialized()

        valid_path = await self.security.validate_path(path)

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(valid_path), exist_ok=True)

            with open(valid_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "path": path,
                "bytes_written": len(content.encode('utf-8')),
                "status": "success"
            }
        except Exception as e:
            raise ValueError(f"Failed to write file: {str(e)}")

    def _normalize_line_endings(self, text: str) -> str:
        """
        Normalize line endings to \n.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized line endings
        """
        return text.replace('\r\n', '\n')

    def _create_unified_diff(self, original: str, modified: str, filepath: str = 'file') -> str:
        """
        Create a unified diff between two texts.

        Args:
            original: Original text
            modified: Modified text
            filepath: Filename for the diff

        Returns:
            Unified diff as a string
        """
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

    async def edit_file(self, path: str, edits: List[Dict[str, str]], dry_run: bool = False) -> Dict[str, Any]:
        """
        Apply edits to a file and return a diff of changes.

        Args:
            path: Path to the file to edit
            edits: List of edit operations, each with 'oldText' and 'newText'
            dry_run: If True, returns diff without modifying the file

        Returns:
            Dictionary with operation result including diff

        Raises:
            ValueError: If the file cannot be edited
        """
        self._is_initialized()

        valid_path = await self.security.validate_path(path)

        try:
            content = await self.read_file(valid_path)
            content_norm = self._normalize_line_endings(content)

            # Apply edits sequentially
            modified_content = content_norm
            edits_applied = 0

            for edit in edits:
                old_text = self._normalize_line_endings(
                    edit.get('oldText', ''))
                new_text = self._normalize_line_endings(
                    edit.get('newText', ''))

                # If exact match exists, use it
                if old_text in modified_content:
                    modified_content = modified_content.replace(
                        old_text, new_text)
                    edits_applied += 1
                    continue

                # Try line-by-line matching with flexibility for whitespace
                old_lines = old_text.split('\n')
                content_lines = modified_content.split('\n')
                match_found = False

                for i in range(len(content_lines) - len(old_lines) + 1):
                    potential_match = content_lines[i:i+len(old_lines)]

                    # Compare lines with normalized whitespace
                    is_match = all(ol.strip() == pl.strip()
                                   for ol, pl in zip(old_lines, potential_match))

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
                                new_lines.append(
                                    original_indent + line.lstrip())
                            else:
                                new_lines.append(line)

                        # Replace lines in content
                        content_lines[i:i+len(old_lines)] = new_lines
                        modified_content = '\n'.join(content_lines)
                        match_found = True
                        edits_applied += 1
                        break

                if not match_found:
                    raise ValueError(
                        f"Could not find exact match for edit: {old_text}")

            # Create unified diff
            diff = self._create_unified_diff(content, modified_content, path)

            if not dry_run:
                await self.write_file(path, modified_content)

            return {
                "path": path,
                "diff": diff,
                "edits_applied": edits_applied,
                "dry_run": dry_run,
                "status": "success"
            }
        except Exception as e:
            raise ValueError(f"Failed to edit file: {str(e)}")

    async def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory with path validation.

        Args:
            path: Path to create

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If the directory cannot be created
        """
        self._is_initialized()

        valid_path = await self.security.validate_path(path)

        try:
            os.makedirs(valid_path, exist_ok=True)
            return {
                "path": path,
                "status": "success"
            }
        except Exception as e:
            raise ValueError(f"Failed to create directory: {str(e)}")

    async def list_directory(self, path: str) -> Dict[str, Any]:
        """
        List contents of a directory with path validation.

        Args:
            path: Path to list

        Returns:
            Dictionary with directory contents

        Raises:
            ValueError: If the directory cannot be listed
        """
        self._is_initialized()

        valid_path = await self.security.validate_path(path)

        try:
            entries = os.listdir(valid_path)
            formatted = []

            for entry in entries:
                entry_path = os.path.join(valid_path, entry)
                entry_type = "directory" if os.path.isdir(
                    entry_path) else "file"
                formatted.append({
                    "name": entry,
                    "type": entry_type,
                    "path": os.path.join(path, entry)
                })

            return {
                "path": path,
                "entries": formatted,
                "directories": sum(1 for entry in formatted if entry["type"] == "directory"),
                "files": sum(1 for entry in formatted if entry["type"] == "file"),
                "total": len(formatted)
            }
        except Exception as e:
            raise ValueError(f"Failed to list directory: {str(e)}")

    async def directory_tree(self, path: str) -> Dict[str, Any]:
        """
        Generate a directory tree structure.

        Args:
            path: Root path for the tree

        Returns:
            Dictionary with tree structure

        Raises:
            ValueError: If the tree cannot be created
        """
        self._is_initialized()

        valid_path = await self.security.validate_path(path)

        try:
            def build_tree(current_path):
                entries = os.listdir(current_path)
                result = []

                for entry in sorted(entries):
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
            return {
                "path": path,
                "tree": tree_data
            }
        except Exception as e:
            raise ValueError(f"Failed to create directory tree: {str(e)}")

    async def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Move a file or directory with path validation.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If the file cannot be moved
        """
        self._is_initialized()

        valid_source = await self.security.validate_path(source)
        valid_dest = await self.security.validate_path(destination)

        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(valid_dest), exist_ok=True)

            shutil.move(valid_source, valid_dest)
            return {
                "source": source,
                "destination": destination,
                "status": "success"
            }
        except Exception as e:
            raise ValueError(f"Failed to move file: {str(e)}")

    async def search_files(self, path: str, pattern: str, exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Recursively search for files matching a pattern.

        Args:
            path: Root path for the search
            pattern: Search pattern
            exclude_patterns: Patterns to exclude

        Returns:
            Dictionary with search results

        Raises:
            ValueError: If the search fails
        """
        self._is_initialized()

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

                # Process directories (in-place modification to skip excluded dirs)
                for i in reversed(range(len(dirs))):
                    if any(fnmatch.fnmatch(dirs[i], pat) for pat in exclude_patterns):
                        dirs.pop(i)  # Don't traverse this directory

                # Process directories for matches
                for dir_name in dirs:
                    if pattern.lower() in dir_name.lower():
                        dir_path = os.path.join(root, dir_name)
                        rel_path = os.path.relpath(dir_path, valid_root)
                        results.append({
                            "name": dir_name,
                            "type": "directory",
                            "path": os.path.join(path, rel_path)
                        })

                # Process files
                for file_name in files:
                    if any(fnmatch.fnmatch(file_name, pat) for pat in exclude_patterns):
                        continue

                    if pattern.lower() in file_name.lower():
                        file_path = os.path.join(root, file_name)
                        rel_path = os.path.relpath(file_path, valid_root)
                        results.append({
                            "name": file_name,
                            "type": "file",
                            "path": os.path.join(path, rel_path)
                        })

            return {
                "path": path,
                "pattern": pattern,
                "results": results,
                "count": len(results),
                "directories": sum(1 for r in results if r["type"] == "directory"),
                "files": sum(1 for r in results if r["type"] == "file")
            }
        except Exception as e:
            raise ValueError(f"Failed to search files: {str(e)}")

    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        Get detailed metadata about a file or directory.

        Args:
            path: Path to get info for

        Returns:
            Dictionary with file information

        Raises:
            ValueError: If the info cannot be retrieved
        """
        self._is_initialized()

        valid_path = await self.security.validate_path(path)

        try:
            stats = os.stat(valid_path)

            info = {
                "name": os.path.basename(valid_path),
                "path": path,
                "absolutePath": os.path.abspath(valid_path),
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
                "isDirectory": os.path.isdir(valid_path),
                "isFile": os.path.isfile(valid_path),
                "permissions": oct(stats.st_mode)[-3:],
                "extension": os.path.splitext(valid_path)[1] if os.path.isfile(valid_path) else ""
            }

            return info
        except Exception as e:
            raise ValueError(f"Failed to get file info: {str(e)}")

    async def list_allowed_directories(self) -> Dict[str, Any]:
        """
        List all allowed directories.

        Returns:
            Dictionary with allowed directories
        """
        self._is_initialized()

        return {
            "directories": self.security.allowed_directories,
            "count": len(self.security.allowed_directories)
        }
