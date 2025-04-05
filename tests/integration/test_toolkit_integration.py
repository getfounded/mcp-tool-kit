#!/usr/bin/env python3
"""
Integration tests for the MCP Toolkit.
"""
import pytest
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock

from app.toolkit import Toolkit
from app.tools.base.registry import get_all_tools, get_tool_categories
from app.tools.project_management.service import ProjectManagementService
from app.tools.quickbooks.service import QuickBooksService


@pytest.fixture
def toolkit_with_tools(mock_env_vars):
    """Create a toolkit with tools loaded"""
    from app.tools import discover_tools

    # Discover tools before creating toolkit
    discover_tools()

    # Create toolkit
    toolkit = Toolkit()
    return toolkit


def test_toolkit_initialization(toolkit_with_tools):
    """Test that the toolkit initializes with tools"""
    # Check that tools are registered
    all_tools = get_all_tools()
    assert len(all_tools) > 0

    # Check that our new tools are present
    tools = all_tools.keys()
    assert "pm_get_projects" in tools
    assert "qb_get_company_info" in tools

    # Check that tool categories exist
    categories = get_tool_categories()
    assert "Project Management" in categories
    assert "QuickBooks" in categories


def test_toolkit_category_access(toolkit_with_tools):
    """Test access to tools by category"""
    # Check that categories exist
    categories = toolkit_with_tools.get_categories()
    assert "Project Management" in categories
    assert "QuickBooks" in categories

    # Check tools in Project Management category
    pm_tools = toolkit_with_tools.get_tools_by_category("Project Management")
    assert len(pm_tools) >= 13  # We have at least 13 PM tools
    assert "pm_get_projects" in pm_tools
    assert "pm_create_task" in pm_tools

    # Check tools in QuickBooks category
    qb_tools = toolkit_with_tools.get_tools_by_category("QuickBooks")
    assert len(qb_tools) >= 20  # We have at least 20 QB tools
    assert "qb_get_company_info" in qb_tools
    assert "qb_get_customers" in qb_tools


def test_toolkit_dynamic_access(toolkit_with_tools):
    """Test dynamic access to tool functions"""
    # Check that tools are accessible via attributes
    assert hasattr(toolkit_with_tools, "pm_get_projects")
    assert hasattr(toolkit_with_tools, "qb_get_company_info")

    # Check that they are callable
    assert callable(getattr(toolkit_with_tools, "pm_get_projects"))
    assert callable(getattr(toolkit_with_tools, "qb_get_company_info"))


@pytest.mark.asyncio
async def test_pm_tools_integration(toolkit_with_tools, mock_requests):
    """Test integration of Project Management tools"""
    # Mock response for get_projects
    mock_response = mock_requests['response']
    mock_response.json.return_value = {
        "projects": [
            {
                "id": "proj_1",
                "name": "Test Project 1",
                "description": "Description for Test Project 1",
                "status": "active"
            },
            {
                "id": "proj_2",
                "name": "Test Project 2",
                "description": "Description for Test Project 2",
                "status": "completed"
            }
        ],
        "count": 2,
        "provider": "asana"
    }

    # Call the toolkit function
    # Note: We're calling through toolkit interface that would use registered tools
    result = await toolkit_with_tools.pm_get_projects(limit=2)

    # Verify results - the response should match our mock
    # tools should be converting to JSON strings, so parse back
    if isinstance(result, str):
        result = json.loads(result)

    assert "projects" in result
    assert len(result["projects"]) == 2
    assert result["projects"][0]["name"] == "Test Project 1"
    assert result["count"] == 2
    assert result["provider"] == "asana"


@pytest.mark.asyncio
async def test_qb_tools_integration(toolkit_with_tools, mock_requests):
    """Test integration of QuickBooks tools"""
    # Mock response for get_company_info
    mock_response = mock_requests['response']
    mock_response.json.return_value = {
        "CompanyInfo": {
            "CompanyName": "Test Company",
            "LegalName": "Test Company LLC",
            "CompanyAddr": {
                "Line1": "123 Test St",
                "City": "Testville"
            }
        }
    }

    # Mock the ensure_token method to prevent real API calls
    with patch('app.tools.quickbooks.service.QuickBooksService._ensure_token', new_callable=AsyncMock):
        # Call the toolkit function
        result = await toolkit_with_tools.qb_get_company_info()

        # Verify results - the response should match our mock
        # tools might return JSON strings, so parse back if needed
        if isinstance(result, str):
            result = json.loads(result)

        assert "CompanyInfo" in result
        assert result["CompanyInfo"]["CompanyName"] == "Test Company"
        assert result["CompanyInfo"]["LegalName"] == "Test Company LLC"


@pytest.mark.asyncio
async def test_cross_service_workflow(toolkit_with_tools, mock_requests):
    """Test a workflow that uses multiple services"""
    # Mock response for get_projects
    projects_response = {
        "projects": [
            {
                "id": "proj_1",
                "name": "Client Project A",
                "status": "active"
            }
        ],
        "count": 1,
        "provider": "asana"
    }

    # Mock response for get_customers
    customers_response = {
        "QueryResponse": {
            "Customer": [
                {
                    "Id": "cust_1",
                    "DisplayName": "Client A",
                    "PrimaryEmailAddr": {"Address": "clienta@example.com"}
                }
            ],
            "startPosition": 1,
            "maxResults": 1,
            "totalCount": 1
        }
    }

    # Configure mock to return different responses based on the URL
    def mock_get_side_effect(*args, **kwargs):
        url = args[0] if args else kwargs.get('url', '')
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        if "query" in url and "Customer" in url:
            mock_resp.json.return_value = customers_response
        else:
            mock_resp.json.return_value = projects_response

        return mock_resp

    mock_requests['get'].side_effect = mock_get_side_effect

    # Mock the ensure_token method to prevent real API calls
    with patch('app.tools.quickbooks.service.QuickBooksService._ensure_token', new_callable=AsyncMock):
        # Execute workflow: Get project and then find matching customer
        pm_result = await toolkit_with_tools.pm_get_projects(limit=1)
        if isinstance(pm_result, str):
            pm_result = json.loads(pm_result)

        # Get the project name
        project_name = pm_result["projects"][0]["name"]
        assert "Client" in project_name

        # Extract client name from project name
        client_name = project_name.split("Project")[0].strip()

        # Search for matching customer in QuickBooks
        qb_result = await toolkit_with_tools.qb_get_customers(query=f"DisplayName LIKE '%{client_name}%'")
        if isinstance(qb_result, str):
            qb_result = json.loads(qb_result)

        # Verify we found the matching customer
        assert "QueryResponse" in qb_result
        assert "Customer" in qb_result["QueryResponse"]
        assert len(qb_result["QueryResponse"]["Customer"]) == 1
        assert client_name in qb_result["QueryResponse"]["Customer"][0]["DisplayName"]
