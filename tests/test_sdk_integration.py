"""
Integration test for SDK with actual server
"""
import unittest
import tempfile
import os
from app.sdk import MCPToolKitSDK


class TestSDKIntegration(unittest.TestCase):
    """Integration tests with actual MCP server."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.sdk = MCPToolKitSDK()
        cls.test_dir = tempfile.mkdtemp()
        cls.test_file = os.path.join(cls.test_dir, "test_sdk.txt")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Clean up test files
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)
        if os.path.exists(cls.test_dir):
            os.rmdir(cls.test_dir)
    
    def test_file_operations(self):
        """Test file operations through SDK."""
        # Write file
        write_result = self.sdk.call_tool("write_file", {
            "path": self.test_file,
            "content": "Hello from SDK integration test!"
        })
        self.assertTrue(write_result.success, f"Write failed: {write_result.error}")
        
        # Read file
        read_result = self.sdk.call_tool("read_file", {
            "path": self.test_file
        })
        self.assertTrue(read_result.success, f"Read failed: {read_result.error}")
        self.assertIn("Hello from SDK integration test!", str(read_result.data))
        
        # List directory
        list_result = self.sdk.call_tool("list_directory", {
            "path": self.test_dir
        })
        self.assertTrue(list_result.success, f"List failed: {list_result.error}")
    
    def test_convenience_methods(self):
        """Test convenience classes."""
        # File operations
        file = self.sdk.file(self.test_file)
        
        # Write
        success = file.write("Testing convenience methods")
        self.assertTrue(success)
        
        # Read
        content = file.read()
        self.assertIn("Testing convenience methods", content)
        
        # Append
        success = file.append("\nAppended line")
        self.assertTrue(success)
        
        content = file.read()
        self.assertIn("Appended line", content)
    
    def test_batch_operations(self):
        """Test batch operations."""
        # Create multiple test files
        test_files = [
            os.path.join(self.test_dir, f"batch_test_{i}.txt")
            for i in range(3)
        ]
        
        # Batch write
        write_ops = [
            {
                "tool": "write_file",
                "params": {
                    "path": path,
                    "content": f"Batch content {i}"
                }
            }
            for i, path in enumerate(test_files)
        ]
        
        write_results = self.sdk.batch_call(write_ops)
        for result in write_results:
            self.assertTrue(result.success)
        
        # Batch read
        read_ops = [
            {"tool": "read_file", "params": {"path": path}}
            for path in test_files
        ]
        
        read_results = self.sdk.batch_call(read_ops)
        for i, result in enumerate(read_results):
            self.assertTrue(result.success)
            self.assertIn(f"Batch content {i}", str(result.data))
        
        # Clean up
        for path in test_files:
            if os.path.exists(path):
                os.remove(path)
    
    def test_error_handling(self):
        """Test error handling."""
        # Try to read non-existent file
        result = self.sdk.call_tool("read_file", {
            "path": "/nonexistent/file.txt"
        })
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_caching(self):
        """Test caching behavior."""
        # First call - not cached
        result1 = self.sdk.call_tool("list_directory", {"path": self.test_dir})
        self.assertTrue(result1.success)
        self.assertNotIn("cached", result1.metadata)
        
        # Second call - should be cached
        result2 = self.sdk.call_tool("list_directory", {"path": self.test_dir})
        self.assertTrue(result2.success)
        self.assertTrue(result2.metadata.get("cached", False))
        
        # Disable cache for specific call
        result3 = self.sdk.call_tool("list_directory", {"path": self.test_dir}, cache=False)
        self.assertTrue(result3.success)
        self.assertNotIn("cached", result3.metadata)


if __name__ == "__main__":
    print("Note: This test requires the MCP server to be running at http://localhost:8000")
    print("Start the server with: python -m app.mcp_unified_server")
    print()
    unittest.main()