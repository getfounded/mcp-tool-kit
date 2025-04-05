#!/usr/bin/env python3
"""
Common test fixtures and utilities for MCP Toolkit tests.
"""
from app.toolkit import Toolkit
from app.tools.base.service import ToolServiceBase
from app.tools.base.registry import clear_registry
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def clear_tools_registry():
    """Clear the tools registry before and after each test"""
    clear_registry()
    yield
    clear_registry()


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    # Set common environment variables for tests
    env_vars = {
        # Server config
        "MCP_SERVER_HOST": "127.0.0.1",
        "MCP_SERVER_PORT": "8000",
        "MCP_LOG_LEVEL": "DEBUG",

        # Project Management
        "PM_API_KEY": "test_pm_api_key",
        "PM_INSTANCE_URL": "https://test.projectmanagement.com",
        "PM_PROVIDER": "asana",

        # QuickBooks
        "QB_CLIENT_ID": "test_qb_client_id",
        "QB_CLIENT_SECRET": "test_qb_client_secret",
        "QB_REDIRECT_URI": "https://localhost/callback",
        "QB_REFRESH_TOKEN": "test_qb_refresh_token",
        "QB_REALM_ID": "test_qb_realm_id"
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def mock_service_base():
    """Create a mock service base class for testing"""
    class MockServiceBase(ToolServiceBase):
        def __init__(self):
            super().__init__()
            self.initialized = False

        def initialize(self):
            self.initialized = True
            return True

    return MockServiceBase


@pytest.fixture
def toolkit():
    """Create a toolkit instance for testing"""
    tk = Toolkit()
    return tk


@pytest.fixture
def mock_requests():
    """Mock requests for API calls"""
    with patch('requests.get') as mock_get, \
            patch('requests.post') as mock_post, \
            patch('requests.put') as mock_put, \
            patch('requests.delete') as mock_delete:

        # Configure default responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"status": "success"}'
        mock_response.json.return_value = {"status": "success"}

        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response

        yield {
            'get': mock_get,
            'post': mock_post,
            'put': mock_put,
            'delete': mock_delete,
            'response': mock_response
        }
