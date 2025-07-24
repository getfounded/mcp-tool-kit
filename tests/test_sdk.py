"""
Test suite for MCP Tool Kit SDK
"""
import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from app.sdk import MCPToolKitSDK, ToolResult, FileOperations, GitOperations, WebOperations


class TestToolResult(unittest.TestCase):
    """Test ToolResult class."""
    
    def test_success_result(self):
        result = ToolResult(True, "test data")
        self.assertTrue(result.success)
        self.assertEqual(result.data, "test data")
        self.assertIsNone(result.error)
        
    def test_error_result(self):
        result = ToolResult(False, None, error="Test error")
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error, "Test error")
    
    def test_to_dict(self):
        result = ToolResult(True, "data", metadata={"cached": True})
        expected = {
            "success": True,
            "data": "data",
            "error": None,
            "metadata": {"cached": True}
        }
        self.assertEqual(result.to_dict(), expected)


class TestMCPToolKitSDK(unittest.TestCase):
    """Test main SDK class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sdk = MCPToolKitSDK()
        # Mock the client
        self.sdk.client = Mock()
    
    def test_initialization(self):
        """Test SDK initialization."""
        sdk = MCPToolKitSDK(
            server_url="http://test:8000",
            async_mode=True,
            retry_count=5,
            timeout=60,
            cache_ttl=600
        )
        self.assertEqual(sdk.retry_count, 5)
        self.assertEqual(sdk.timeout, 60)
        self.assertEqual(sdk.cache_ttl, 600)
        self.assertTrue(sdk.async_mode)
        self.assertIsNotNone(sdk._executor)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with MCPToolKitSDK() as sdk:
            self.assertIsInstance(sdk, MCPToolKitSDK)
    
    def test_call_tool_success(self):
        """Test successful tool call."""
        self.sdk.client.call_tool.return_value = json.dumps({"result": "success"})
        
        result = self.sdk.call_tool("test_tool", {"param": "value"})
        
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"result": "success"})
        self.assertIsNone(result.error)
        self.sdk.client.call_tool.assert_called_once_with("test_tool", {"param": "value"})
    
    def test_call_tool_error(self):
        """Test tool call with error."""
        self.sdk.client.call_tool.return_value = json.dumps({"error": "Tool failed"})
        
        result = self.sdk.call_tool("test_tool", {"param": "value"})
        
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error, "Tool failed")
    
    def test_call_tool_with_retry(self):
        """Test retry logic."""
        # First two calls fail, third succeeds
        self.sdk.client.call_tool.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            json.dumps({"result": "success"})
        ]
        
        result = self.sdk.call_tool("test_tool", {"param": "value"}, retry=3)
        
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"result": "success"})
        self.assertEqual(self.sdk.client.call_tool.call_count, 3)
    
    def test_caching(self):
        """Test caching functionality."""
        self.sdk.client.call_tool.return_value = json.dumps({"result": "cached"})
        
        # First call
        result1 = self.sdk.call_tool("test_tool", {"param": "value"})
        self.assertTrue(result1.success)
        
        # Second call should use cache
        result2 = self.sdk.call_tool("test_tool", {"param": "value"})
        self.assertTrue(result2.success)
        self.assertEqual(result2.metadata.get("cached"), True)
        
        # Client should only be called once
        self.sdk.client.call_tool.assert_called_once()
    
    def test_middleware(self):
        """Test middleware functionality."""
        def test_middleware(tool_name, params):
            params["added_by_middleware"] = True
            return params
        
        self.sdk.add_middleware(test_middleware)
        self.sdk.client.call_tool.return_value = json.dumps({"result": "success"})
        
        self.sdk.call_tool("test_tool", {"param": "value"})
        
        # Check that middleware modified params
        call_args = self.sdk.client.call_tool.call_args[0]
        self.assertEqual(call_args[0], "test_tool")
        self.assertTrue(call_args[1]["added_by_middleware"])
    
    def test_event_handlers(self):
        """Test event handler functionality."""
        events = []
        
        def before_handler(tool_name, params):
            events.append(("before", tool_name))
        
        def after_handler(tool_name, params, result):
            events.append(("after", tool_name))
        
        self.sdk.on("before_call", before_handler)
        self.sdk.on("after_call", after_handler)
        
        self.sdk.client.call_tool.return_value = json.dumps({"result": "success"})
        self.sdk.call_tool("test_tool", {})
        
        self.assertEqual(events, [("before", "test_tool"), ("after", "test_tool")])
    
    def test_batch_call(self):
        """Test batch operations."""
        self.sdk.client.call_tool.side_effect = [
            json.dumps({"result": "1"}),
            json.dumps({"result": "2"}),
            json.dumps({"error": "Failed"})
        ]
        
        operations = [
            {"tool": "tool1", "params": {"p": 1}},
            {"tool": "tool2", "params": {"p": 2}},
            {"tool": "tool3", "params": {"p": 3}}
        ]
        
        results = self.sdk.batch_call(operations)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(results[0].success)
        self.assertTrue(results[1].success)
        self.assertFalse(results[2].success)
    
    def test_list_tools(self):
        """Test tool listing."""
        self.sdk.client.call_tool.return_value = json.dumps([
            {"name": "tool1", "description": "Test tool 1"},
            {"name": "tool2", "description": "Test tool 2"}
        ])
        
        tools = self.sdk.list_tools()
        
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0]["name"], "tool1")
    
    def test_dynamic_methods(self):
        """Test dynamic method generation."""
        self.sdk.client.call_tool.return_value = json.dumps({"result": "dynamic"})
        
        # Call non-existent method
        result = self.sdk.some_tool(param="value")
        
        self.assertTrue(result.success)
        self.sdk.client.call_tool.assert_called_with("some_tool", {"param": "value"})


class TestFileOperations(unittest.TestCase):
    """Test FileOperations convenience class."""
    
    def setUp(self):
        self.sdk = Mock()
        self.file_ops = FileOperations(self.sdk, "test.txt")
    
    def test_read(self):
        """Test file read."""
        self.sdk.call_tool.return_value = ToolResult(True, "file content")
        
        content = self.file_ops.read()
        
        self.assertEqual(content, "file content")
        self.sdk.call_tool.assert_called_with("read_file", {"path": "test.txt"})
    
    def test_write(self):
        """Test file write."""
        self.sdk.call_tool.return_value = ToolResult(True, "Success")
        
        success = self.file_ops.write("new content")
        
        self.assertTrue(success)
        self.sdk.call_tool.assert_called_with("write_file", {
            "path": "test.txt",
            "content": "new content"
        })
    
    def test_append(self):
        """Test file append."""
        # Mock read and write
        self.sdk.call_tool.side_effect = [
            ToolResult(True, "existing content"),
            ToolResult(True, "Success")
        ]
        
        success = self.file_ops.append(" appended")
        
        self.assertTrue(success)
        # Check write was called with combined content
        write_call = self.sdk.call_tool.call_args_list[1]
        self.assertEqual(write_call[0][1]["content"], "existing content appended")


class TestGitOperations(unittest.TestCase):
    """Test GitOperations convenience class."""
    
    def setUp(self):
        self.sdk = Mock()
        self.git_ops = GitOperations(self.sdk, ".")
    
    def test_status(self):
        """Test git status."""
        self.sdk.call_tool.return_value = ToolResult(True, "On branch main")
        
        status = self.git_ops.status()
        
        self.assertEqual(status, "On branch main")
        self.sdk.call_tool.assert_called_with("git_status", {"repo_path": "."})
    
    def test_commit(self):
        """Test git commit."""
        self.sdk.call_tool.return_value = ToolResult(True, "Committed")
        
        success = self.git_ops.commit("Test commit", files=["file1.txt"])
        
        self.assertTrue(success)
        self.sdk.call_tool.assert_called_with("git_commit", {
            "repo_path": ".",
            "message": "Test commit",
            "files": ["file1.txt"]
        })


class TestWebOperations(unittest.TestCase):
    """Test WebOperations convenience class."""
    
    def setUp(self):
        self.sdk = Mock()
        self.web_ops = WebOperations(self.sdk)
    
    def test_get(self):
        """Test GET request."""
        self.sdk.call_tool.return_value = ToolResult(True, {"data": "response"})
        
        response = self.web_ops.get("https://api.example.com", headers={"Auth": "token"})
        
        self.assertEqual(response, {"data": "response"})
        self.sdk.call_tool.assert_called_with("fetch", {
            "url": "https://api.example.com",
            "method": "GET",
            "headers": {"Auth": "token"}
        })
    
    def test_post(self):
        """Test POST request."""
        self.sdk.call_tool.return_value = ToolResult(True, {"success": True})
        
        response = self.web_ops.post("https://api.example.com", {"key": "value"})
        
        self.assertEqual(response, {"success": True})
        self.sdk.call_tool.assert_called_with("fetch", {
            "url": "https://api.example.com",
            "method": "POST",
            "body": {"key": "value"}
        })


if __name__ == "__main__":
    unittest.main()