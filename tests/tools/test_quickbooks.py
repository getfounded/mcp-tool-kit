#!/usr/bin/env python3
"""
Unit tests for QuickBooks tools.
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock

from app.tools.quickbooks.service import QuickBooksService
from app.tools.base.registry import get_tools_by_service, get_tool_categories


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up environment variables for testing"""
    monkeypatch.setenv("QB_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("QB_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("QB_REDIRECT_URI", "https://test.example.com/callback")
    monkeypatch.setenv("QB_REFRESH_TOKEN", "test_refresh_token")
    monkeypatch.setenv("QB_REALM_ID", "test_realm_id")


@pytest.fixture
def qb_service(mock_env_vars):
    """Create a test QuickBooks service"""
    service = QuickBooksService()
    service.initialize()
    # Mock token to prevent real API calls
    service.access_token = "test_access_token"
    service.token_expires = None  # Force token refresh on first call
    return service


def test_service_initialization(qb_service):
    """Test service initialization"""
    assert qb_service.initialized
    assert qb_service.client_id == "test_client_id"
    assert qb_service.client_secret == "test_client_secret"
    assert qb_service.redirect_uri == "https://test.example.com/callback"
    assert qb_service.refresh_token == "test_refresh_token"
    assert qb_service.realm_id == "test_realm_id"
    assert qb_service.base_url == "https://quickbooks.api.intuit.com/v3/company"


def test_tools_registration():
    """Test that all QuickBooks tools are registered"""
    tools = get_tools_by_service(QuickBooksService)
    assert len(tools) >= 20  # At least 20 QB tools
    assert "qb_get_company_info" in tools
    assert "qb_get_customers" in tools
    assert "qb_create_invoice" in tools
    assert "qb_query" in tools

    # Check category registration
    categories = get_tool_categories()
    assert "QuickBooks" in categories


@pytest.mark.asyncio
@patch('app.tools.quickbooks.service.requests.get')
async def test_get_company_info(mock_get, qb_service):
    """Test get_company_info functionality with mocked response"""
    # Mock the response
    mock_response = MagicMock()
    mock_response.content = True
    mock_response.json.return_value = {
        "CompanyInfo": {
            "CompanyName": "Test Company",
            "LegalName": "Test Company LLC",
            "CompanyAddr": {
                "Line1": "123 Test St",
                "City": "Testville",
                "CountrySubDivisionCode": "CA",
                "PostalCode": "12345"
            },
            "Email": {
                "Address": "test@example.com"
            }
        }
    }
    mock_get.return_value = mock_response

    # Mock the ensure_token method to prevent real API calls
    qb_service._ensure_token = AsyncMock()

    # Call the service method
    result = await qb_service.get_company_info()

    # Verify results
    assert "CompanyInfo" in result
    assert result["CompanyInfo"]["CompanyName"] == "Test Company"
    assert result["CompanyInfo"]["Email"]["Address"] == "test@example.com"

    # Verify that the correct request was made
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    url = call_args[0][0]
    assert url == f"{qb_service.base_url}/{qb_service.realm_id}/companyinfo/{qb_service.realm_id}"


@pytest.mark.asyncio
@patch('app.tools.quickbooks.service.requests.get')
async def test_get_customers(mock_get, qb_service):
    """Test get_customers functionality with mocked response"""
    # Mock the response
    mock_response = MagicMock()
    mock_response.content = True
    mock_response.json.return_value = {
        "QueryResponse": {
            "Customer": [
                {
                    "Id": "1",
                    "DisplayName": "Test Customer 1",
                    "PrimaryEmailAddr": {"Address": "customer1@example.com"}
                },
                {
                    "Id": "2",
                    "DisplayName": "Test Customer 2",
                    "PrimaryEmailAddr": {"Address": "customer2@example.com"}
                }
            ],
            "startPosition": 1,
            "maxResults": 2,
            "totalCount": 2
        }
    }
    mock_get.return_value = mock_response

    # Mock the ensure_token method to prevent real API calls
    qb_service._ensure_token = AsyncMock()

    # Call the service method
    result = await qb_service.get_customers(max_results=2)

    # Verify results
    assert "QueryResponse" in result
    assert "Customer" in result["QueryResponse"]
    assert len(result["QueryResponse"]["Customer"]) == 2
    assert result["QueryResponse"]["Customer"][0]["DisplayName"] == "Test Customer 1"

    # Verify that the correct request was made
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    url = call_args[0][0]
    assert url == f"{qb_service.base_url}/{qb_service.realm_id}/query"
    assert "query" in call_args[1]["params"]
    assert call_args[1]["params"]["query"] == "select * from Customer"


@pytest.mark.asyncio
@patch('app.tools.quickbooks.service.requests.post')
async def test_create_customer(mock_post, qb_service):
    """Test create_customer functionality with mocked response"""
    # Mock the response
    mock_response = MagicMock()
    mock_response.content = True
    mock_response.json.return_value = {
        "Customer": {
            "Id": "3",
            "DisplayName": "New Test Customer",
            "PrimaryEmailAddr": {"Address": "newcustomer@example.com"}
        }
    }
    mock_post.return_value = mock_response

    # Mock the ensure_token method to prevent real API calls
    qb_service._ensure_token = AsyncMock()

    # Create test customer data
    customer_data = {
        "Customer": {
            "DisplayName": "New Test Customer",
            "PrimaryEmailAddr": {"Address": "newcustomer@example.com"}
        }
    }

    # Call the service method
    result = await qb_service.create_customer(customer_data)

    # Verify results
    assert "Customer" in result
    assert result["Customer"]["DisplayName"] == "New Test Customer"
    assert result["Customer"]["Id"] == "3"

    # Verify that the correct request was made
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    url = call_args[0][0]
    assert url == f"{qb_service.base_url}/{qb_service.realm_id}/customer"
    assert call_args[1]["data"] == json.dumps(customer_data)


@pytest.mark.asyncio
@patch('app.tools.quickbooks.service.requests.get')
async def test_custom_query(mock_get, qb_service):
    """Test query functionality with mocked response"""
    # Mock the response
    mock_response = MagicMock()
    mock_response.content = True
    mock_response.json.return_value = {
        "QueryResponse": {
            "Invoice": [
                {
                    "Id": "1",
                    "CustomerRef": {"value": "1"},
                    "TotalAmt": 150.00
                },
                {
                    "Id": "2",
                    "CustomerRef": {"value": "2"},
                    "TotalAmt": 250.00
                }
            ],
            "startPosition": 1,
            "maxResults": 2,
            "totalCount": 2
        }
    }
    mock_get.return_value = mock_response

    # Mock the ensure_token method to prevent real API calls
    qb_service._ensure_token = AsyncMock()

    # Call the service method
    query_string = "SELECT * FROM Invoice WHERE TotalAmt > '100.00'"
    result = await qb_service.query(query_string)

    # Verify results
    assert "QueryResponse" in result
    assert "Invoice" in result["QueryResponse"]
    assert len(result["QueryResponse"]["Invoice"]) == 2
    assert result["QueryResponse"]["Invoice"][0]["TotalAmt"] == 150.00

    # Verify that the correct request was made
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    url = call_args[0][0]
    assert "query" in url
    assert query_string in url


@pytest.mark.asyncio
@patch('app.tools.quickbooks.service.requests.get')
async def test_get_profit_loss_report(mock_get, qb_service):
    """Test get_profit_loss_report functionality with mocked response"""
    # Mock the response
    mock_response = MagicMock()
    mock_response.content = True
    mock_response.json.return_value = {
        "Header": {
            "ReportName": "Profit and Loss",
            "StartDate": "2023-01-01",
            "EndDate": "2023-12-31"
        },
        "Rows": [
            {
                "Header": {"ColData": [{"value": "Income"}]},
                "Rows": [
                    {"ColData": [{"value": "Sales"}, {"value": "10000.00"}]}
                ]
            },
            {
                "Header": {"ColData": [{"value": "Expenses"}]},
                "Rows": [
                    {"ColData": [{"value": "Rent"}, {"value": "2000.00"}]},
                    {"ColData": [{"value": "Utilities"}, {"value": "500.00"}]}
                ]
            },
            {
                "Summary": {"ColData": [{"value": "Net Income"}, {"value": "7500.00"}]}
            }
        ]
    }
    mock_get.return_value = mock_response

    # Mock the ensure_token method to prevent real API calls
    qb_service._ensure_token = AsyncMock()

    # Call the service method
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    accounting_method = "Accrual"
    result = await qb_service.get_profit_loss_report(start_date, end_date, accounting_method)

    # Verify results
    assert "Header" in result
    assert result["Header"]["ReportName"] == "Profit and Loss"
    assert "Rows" in result

    # Verify that the correct request was made
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    url = call_args[0][0]
    assert url == f"{qb_service.base_url}/{qb_service.realm_id}/reports/ProfitAndLoss"
    assert call_args[1]["params"]["start_date"] == start_date
    assert call_args[1]["params"]["end_date"] == end_date
    assert call_args[1]["params"]["accounting_method"] == accounting_method
