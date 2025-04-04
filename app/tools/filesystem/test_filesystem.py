#!/usr/bin/env python3
"""
Tests for Filesystem tools.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import shutil

from app.tools.filesystem.filesystem_service import FilesystemService, FilesystemSecurity
from app.tools.filesystem.filesystem_tools import (
    read_file,
    write_file,
    create_directory,
    list_directory,
    get_file_info
)

class TestFilesystemTools:
    """Test case for filesystem tools."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        # Create a temporary directory for testing
        cls.temp_dir = tempfile.mkdtemp()
        cls.allowed_dirs = [cls.temp_dir]
        
        # Initialize service
        cls.service = FilesystemService()
        cls.service.security = FilesystemSecurity(cls.allowed_dirs)
        cls.service.initialized = True
        
        # Create some test files and directories
        os.makedirs(os.path.join(cls.temp_dir, "subdir"), exist_ok=True)
        with open(os.path.join(cls.temp_dir, "test.txt"), "w") as f:
            f.write("This is a test file.")
        with open(os.path.join(cls.temp_dir, "subdir", "nested.txt"), "w") as f:
            f.write("This is a nested file.")
    
    @classmethod
    def teardown_class(cls):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(cls.temp_dir)
    
    @pytest.mark.asyncio
    async def test_read_file(self):
        """Test read_file function."""
        # Test reading an existing file
        result = await read_file(self.service, os.path.join(self.temp_dir, "test.txt"))
        assert result == "This is a test file."
        
        # Test reading a non-existent file
        result = await read_file(self.service, os.path.join(self.temp_dir, "nonexistent.txt"))
        assert "Error reading file" in result
        
        # Test reading a file outside allowed directories
        result = await read_file(self.service, "/etc/passwd")
        assert "Error reading file" in result
        assert "Access denied" in result
    
    @pytest.mark.asyncio
    async def test_write_file(self):
        """Test write_file function."""
        # Test writing to a new file
        test_path = os.path.join(self.temp_dir, "new_file.txt")
        result = await write_file(self.service, test_path, "New file content")
        assert result["status"] == "success"
        assert result["path"] == test_path
        
        # Verify file was written correctly
        with open(test_path, "r") as f:
            content = f.read()
        assert content == "New file content"
        
        # Test writing to a file outside allowed directories
        result = await write_file(self.service, "/tmp/not_allowed.txt", "Not allowed")
        assert "error" in result
        assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_directory(self):
        """Test create_directory function."""
        # Test creating a new directory
        test_dir = os.path.join(self.temp_dir, "new_dir")
        result = await create_directory(self.service, test_dir)
        assert result["status"] == "success"
        assert result["path"] == test_dir
        assert os.path.isdir(test_dir)
        
        # Test creating a nested directory
        nested_dir = os.path.join(self.temp_dir, "nested1", "nested2")
        result = await create_directory(self.service, nested_dir)
        assert result["status"] == "success"
        assert result["path"] == nested_dir
        assert os.path.isdir(nested_dir)
        
        # Test creating a directory outside allowed directories
        result = await create_directory(self.service, "/tmp/not_allowed")
        assert "error" in result
        assert "Access denied" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_directory(self):
        """Test list_directory function."""
        # Test listing the root test directory
        result = await list_directory(self.service, self.temp_dir)
        assert result["status"] == "success"
        assert result["path"] == self.temp_dir
        
        # Verify entries
        assert result["total"] >= 3  # At least test.txt, subdir, and new_dir
        
        # Find specific entries
        test_txt = next((entry for entry in result["entries"] if entry["name"] == "test.txt"), None)
        assert test_txt is not None
        assert test_txt["type"] == "file"
        
        subdir = next((entry for entry in result["entries"] if entry["name"] == "subdir"), None)
        assert subdir is not None
        assert subdir["type"] == "directory"
        
        # Test listing a non-existent directory
        result = await list_directory(self.service, os.path.join(self.temp_dir, "nonexistent"))
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_file_info(self):
        """Test get_file_info function."""
        # Test getting info for a file
        test_file = os.path.join(self.temp_dir, "test.txt")
        result = await get_file_info(self.service, test_file)
        assert result["name"] == "test.txt"
        assert result["path"] == test_file
        assert result["isFile"] is True
        assert result["isDirectory"] is False
        assert result["size"] > 0
        
        # Test getting info for a directory
        test_dir = os.path.join(self.temp_dir, "subdir")
        result = await get_file_info(self.service, test_dir)
        assert result["name"] == "subdir"
        assert result["path"] == test_dir
        assert result["isFile"] is False
        assert result["isDirectory"] is True
        
        # Test getting info for a non-existent path
        result = await get_file_info(self.service, os.path.join(self.temp_dir, "nonexistent"))
        assert "error" in result

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
