#!/usr/bin/env python3
"""
End-to-end tests for the MCP Toolkit server.
"""
import pytest
import requests
import subprocess
import time
import os
import signal
import json
import sys
from pathlib import Path

# Add server startup timeout (seconds)
SERVER_STARTUP_TIMEOUT = 10
# Server port for testing
SERVER_PORT = 8888

@pytest.fixture(scope="module")
def server_process():
    """Start the unified server for testing"""
    # Find the main.py file relative to this script
    base_path = Path(__file__).parent.parent.parent
    main_script = base_path / "main.py"
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, str(main_script), "server", "--port", str(SERVER_PORT), "--debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=dict(os.environ, MCP_SERVER_PORT=str(SERVER_PORT))
    )
    
    # Wait for server to start
    start_time = time.time()
    server_started = False
    
    while time.time() - start_time < SERVER_STARTUP_TIMEOUT:
        try:
            response = requests.get(f"http://localhost:{SERVER_PORT}/health")
            if response.status_code == 200:
                server_started = True
                break
        except requests.exceptions.ConnectionError:
            # Server not ready yet
            time.sleep(0.5)
    
    if not server_started:
        # If server didn't start, kill the process and raise an error
        os.kill(process.pid, signal.SIGTERM)
        process.wait()
        stdout, stderr = process.communicate()
        pytest.fail(f"Server failed to start within {SERVER_STARTUP_TIMEOUT} seconds.\n"
                   f"STDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}")
    
    # Server started successfully
    yield process
    
    # Clean up after tests
    os.kill(process.pid, signal.SIGTERM)
    process.wait()

def test_server_health(server_process):
    """Test server health endpoint"""
    response = requests.get(f"http://localhost:{SERVER_PORT}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok" or data["status"] == "healthy"

def test_tools_endpoint(server_process):
    """Test tools listing endpoint"""
    response = requests.get(f"http://localhost:{SERVER_PORT}/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0
    
    # Check if our new tools are present
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "pm_get_projects" in tool_names
    assert "qb_get_company_info" in tool_names

def test_categories_endpoint(server_process):
    """Test categories listing endpoint"""
    response = requests.get(f"http://localhost:{SERVER_PORT}/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    
    # Check if our new categories are present
    categories = data["categories"]
    assert "Project Management" in categories
    assert "QuickBooks" in categories

def test_tools_by_category_endpoint(server_process):
    """Test tools by category endpoint"""
    response = requests.get(f"http://localhost:{SERVER_PORT}/tools/category/Project%20Management")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    
    # Check if all PM tools are returned
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "pm_get_projects" in tool_names
    assert "pm_create_project" in tool_names
    assert "pm_get_tasks" in tool_names

def test_documentation_endpoint(server_process):
    """Test documentation endpoint"""
    response = requests.get(f"http://localhost:{SERVER_PORT}/docs")
    assert response.status_code == 200
    
    # Check if it's HTML content
    assert "text/html" in response.headers["Content-Type"]
    
    # Check if the HTML contains expected elements
    html_content = response.text.lower()
    assert "mcp toolkit" in html_content
    assert "api" in html_content
    
    # Check for our new tools in the documentation
    assert "project management" in html_content
    assert "quickbooks" in html_content

def test_tool_invoke_endpoint(server_process):
    """Test tool invoke endpoint with a simple tool"""
    # Since our tools might require authentication or have complex input,
    # we'll focus on testing the endpoint structure rather than actual execution
    
    # Prepare a test payload
    payload = {
        "tool": "pm_get_projects",
        "args": {
            "limit": 5
        }
    }
    
    # Make the request
    response = requests.post(
        f"http://localhost:{SERVER_PORT}/invoke",
        json=payload
    )
    
    # Even if the tool execution fails due to authentication,
    # we expect a structured response
    assert response.status_code in [200, 400, 401, 500]
    data = response.json()
    
    # Check that the response has expected structure
    assert "tool" in data
    assert data["tool"] == "pm_get_projects"
    assert "status" in data  # Could be 'success', 'error', etc.
