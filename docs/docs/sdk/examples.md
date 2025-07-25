---
sidebar_position: 4
---

# Examples

Practical examples demonstrating SDK usage patterns.

## Basic File Operations

### Reading and Writing Files

```python
from mcp_tool_kit import MCPToolKitSDK

with MCPToolKitSDK() as sdk:
    # Read a file
    result = sdk.call_tool("read_file", {"path": "input.txt"})
    if result.success:
        content = result.data
        
        # Process content
        processed = content.upper()
        
        # Write to new file
        result = sdk.call_tool("write_file", {
            "path": "output.txt",
            "content": processed
        })
```

### Using FileOperations Helper

```python
with MCPToolKitSDK() as sdk:
    file = sdk.file("data.json")
    
    # Read JSON data
    json_str = file.read()
    if json_str:
        import json
        data = json.loads(json_str)
        
        # Modify data
        data['updated'] = True
        
        # Write back
        file.write(json.dumps(data, indent=2))
```

## Batch Processing

### Processing Multiple Files

```python
def process_log_files(sdk, log_dir):
    """Process all log files in a directory."""
    
    # Get list of log files
    result = sdk.call_tool("list_directory", {"path": log_dir})
    if not result.success:
        return []
    
    log_files = [f for f in result.data if f.endswith('.log')]
    
    # Create batch operations
    operations = [
        {"tool": "read_file", "params": {"path": f"{log_dir}/{file}"}}
        for file in log_files
    ]
    
    # Execute batch
    results = sdk.batch_call(operations)
    
    # Process results
    summaries = []
    for file, result in zip(log_files, results):
        if result.success:
            lines = result.data.split('\n')
            errors = [l for l in lines if 'ERROR' in l]
            summaries.append({
                'file': file,
                'total_lines': len(lines),
                'errors': len(errors)
            })
    
    return summaries
```

### Parallel Processing with Async

```python
import asyncio

async def process_urls_async(urls):
    """Fetch multiple URLs concurrently."""
    
    async with MCPToolKitSDK(async_mode=True) as sdk:
        operations = [
            {"tool": "fetch", "params": {"url": url, "method": "GET"}}
            for url in urls
        ]
        
        results = await sdk.batch_call_async(operations)
        
        successful = []
        failed = []
        
        for url, result in zip(urls, results):
            if result.success:
                successful.append((url, len(str(result.data))))
            else:
                failed.append((url, result.error))
        
        return successful, failed

# Usage
urls = [
    "https://api.github.com/users/github",
    "https://api.github.com/users/torvalds",
    "https://api.github.com/users/gvanrossum"
]

successful, failed = asyncio.run(process_urls_async(urls))
```

## Error Handling and Retry

### Custom Retry Logic

```python
def reliable_file_operation(sdk, path, max_retries=5):
    """Read file with custom retry logic."""
    
    for attempt in range(max_retries):
        result = sdk.call_tool("read_file", {"path": path}, retry=1)
        
        if result.success:
            return result.data
        
        if "not found" in result.error.lower():
            # File doesn't exist, no point retrying
            raise FileNotFoundError(f"File {path} not found")
        
        if attempt < max_retries - 1:
            # Wait before retry with exponential backoff
            import time
            time.sleep(2 ** attempt)
            print(f"Retry {attempt + 1}/{max_retries} for {path}")
    
    raise Exception(f"Failed to read {path} after {max_retries} attempts")
```

### Error Recovery

```python
def safe_file_update(sdk, path, update_func):
    """Safely update a file with backup."""
    
    backup_path = f"{path}.backup"
    
    try:
        # Read original
        result = sdk.call_tool("read_file", {"path": path})
        if not result.success:
            raise Exception(f"Cannot read {path}: {result.error}")
        
        original_content = result.data
        
        # Create backup
        result = sdk.call_tool("write_file", {
            "path": backup_path,
            "content": original_content
        })
        if not result.success:
            raise Exception("Failed to create backup")
        
        # Apply update
        new_content = update_func(original_content)
        
        # Write updated content
        result = sdk.call_tool("write_file", {
            "path": path,
            "content": new_content
        })
        
        if result.success:
            # Remove backup on success
            sdk.call_tool("delete_file", {"path": backup_path})
        else:
            # Restore from backup on failure
            sdk.call_tool("write_file", {
                "path": path,
                "content": original_content
            })
            raise Exception("Update failed, restored from backup")
            
    except Exception as e:
        print(f"Error: {e}")
        raise
```

## Middleware and Events

### Authentication Middleware

```python
class AuthenticatedSDK:
    def __init__(self, api_key):
        self.sdk = MCPToolKitSDK()
        self.api_key = api_key
        
        # Add authentication to all requests
        self.sdk.add_middleware(self._auth_middleware)
        
        # Log all errors
        self.sdk.on('error', self._log_error)
    
    def _auth_middleware(self, tool_name, params):
        # Add API key to web requests
        if tool_name in ['fetch', 'web_request']:
            if 'headers' not in params:
                params['headers'] = {}
            params['headers']['Authorization'] = f"Bearer {self.api_key}"
        return params
    
    def _log_error(self, tool_name, params, error):
        import logging
        logging.error(f"Tool {tool_name} failed: {error}")
```

### Request Logging

```python
def setup_request_logging(sdk):
    """Add comprehensive logging to SDK."""
    
    import time
    import logging
    
    logger = logging.getLogger("mcp_sdk")
    
    # Track request timing
    request_times = {}
    
    def before_request(tool_name, params):
        request_id = f"{tool_name}_{time.time()}"
        request_times[request_id] = time.time()
        logger.info(f"Starting {tool_name} with params: {params}")
        return request_id
    
    def after_request(tool_name, params, result):
        # Find matching request
        for req_id, start_time in request_times.items():
            if req_id.startswith(tool_name):
                duration = time.time() - start_time
                logger.info(f"{tool_name} completed in {duration:.2f}s")
                del request_times[req_id]
                break
    
    sdk.on('before_call', before_request)
    sdk.on('after_call', after_request)
    sdk.on('error', lambda t, p, e: logger.error(f"{t} error: {e}"))
```

## Git Integration

### Automated Git Workflow

```python
def auto_commit_changes(sdk, repo_path, message_prefix="Auto-update"):
    """Automatically commit all changes in a repository."""
    
    git = sdk.git(repo_path)
    
    # Check status
    status = git.status()
    if "nothing to commit" in status:
        print("No changes to commit")
        return False
    
    # Get list of changed files
    result = sdk.call_tool("git_diff", {"repo_path": repo_path})
    if result.success:
        # Parse changed files from diff
        changed_files = parse_changed_files(result.data)
        
        # Generate commit message
        message = f"{message_prefix}: Updated {len(changed_files)} files"
        
        # Commit changes
        if git.commit(message, files=changed_files):
            print(f"Committed: {message}")
            return True
    
    return False
```

## Data Processing Pipeline

### CSV Processing Example

```python
def process_csv_files(sdk, input_dir, output_dir):
    """Process all CSV files in a directory."""
    
    import csv
    import io
    
    # Ensure output directory exists
    sdk.call_tool("create_directory", {"path": output_dir})
    
    # Get all CSV files
    result = sdk.call_tool("list_directory", {"path": input_dir})
    if not result.success:
        return
    
    csv_files = [f for f in result.data if f.endswith('.csv')]
    
    for csv_file in csv_files:
        # Read CSV
        file_path = f"{input_dir}/{csv_file}"
        result = sdk.call_tool("read_file", {"path": file_path})
        
        if result.success:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(result.data))
            rows = list(reader)
            
            # Process data (example: convert to uppercase)
            for row in rows:
                for key in row:
                    if isinstance(row[key], str):
                        row[key] = row[key].upper()
            
            # Write processed CSV
            output = io.StringIO()
            if rows:
                writer = csv.DictWriter(output, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            
            # Save to output directory
            output_path = f"{output_dir}/{csv_file}"
            sdk.call_tool("write_file", {
                "path": output_path,
                "content": output.getvalue()
            })
            
            print(f"Processed {csv_file} -> {output_path}")
```

## Custom Integration

### Building a File Sync Service

```python
class FileSyncService:
    """Sync files between local and remote locations."""
    
    def __init__(self, local_dir, remote_url):
        self.sdk = MCPToolKitSDK()
        self.local_dir = local_dir
        self.remote_url = remote_url
        
        # Track sync status
        self.synced_files = {}
    
    def sync_file(self, filename):
        """Sync a single file."""
        local_path = f"{self.local_dir}/{filename}"
        
        # Read local file
        file = self.sdk.file(local_path)
        content = file.read()
        
        if not content:
            return False
        
        # Calculate checksum
        import hashlib
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        # Check if file needs sync
        if self.synced_files.get(filename) == checksum:
            return True  # Already synced
        
        # Upload to remote
        web = self.sdk.web()
        response = web.post(
            f"{self.remote_url}/upload",
            {
                "filename": filename,
                "content": content,
                "checksum": checksum
            }
        )
        
        if response:
            self.synced_files[filename] = checksum
            return True
        
        return False
    
    def sync_directory(self):
        """Sync all files in directory."""
        result = self.sdk.call_tool("list_directory", {"path": self.local_dir})
        
        if result.success:
            files = [f for f in result.data if not f.startswith('.')]
            
            success_count = 0
            for file in files:
                if self.sync_file(file):
                    success_count += 1
                    print(f"Synced: {file}")
                else:
                    print(f"Failed: {file}")
            
            print(f"Synced {success_count}/{len(files)} files")
```

## Testing with the SDK

### Unit Test Helper

```python
import unittest
from unittest.mock import Mock

class TestWithSDK(unittest.TestCase):
    """Base test class with SDK mocking."""
    
    def setUp(self):
        self.sdk = MCPToolKitSDK()
        self.sdk.client = Mock()
    
    def mock_tool_response(self, tool_name, response_data):
        """Mock a successful tool response."""
        self.sdk.client.call_tool.return_value = json.dumps(response_data)
    
    def mock_tool_error(self, tool_name, error_message):
        """Mock a tool error."""
        self.sdk.client.call_tool.return_value = json.dumps({
            "error": error_message
        })

class TestFileOperations(TestWithSDK):
    def test_read_file(self):
        # Mock response
        self.mock_tool_response("read_file", "file contents")
        
        # Test
        file = self.sdk.file("test.txt")
        content = file.read()
        
        # Assert
        self.assertEqual(content, "file contents")
        self.sdk.client.call_tool.assert_called_with(
            "read_file",
            {"path": "test.txt"}
        )
```