#!/usr/bin/env python3
"""
Tests for Brave Search tools.
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json

from app.tools.brave_search.service import BraveSearchService
from app.tools.brave_search.tools import brave_web_search, brave_local_search


@pytest.fixture
def mock_service():
    """Create a mock Brave Search service."""
    service = BraveSearchService()
    service.api_key = "test_api_key"
    service.initialized = True

    # Set up mock methods
    service.perform_web_search = AsyncMock()
    service.perform_local_search = AsyncMock()

    # Configure rate limiter
    service.create_rate_limiter("brave_search_api", calls=1, period=1.0)

    return service


@pytest.mark.asyncio
async def test_web_search(mock_service):
    """Test brave_web_search function."""
    # Configure mock response
    mock_service.perform_web_search.return_value = {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "description": "This is a test result",
                "url": "https://example.com/1",
                "index": 0
            },
            {
                "title": "Test Result 2",
                "description": "This is another test result",
                "url": "https://example.com/2",
                "index": 1
            }
        ],
        "count": 2,
        "has_more": False
    }

    # Call the function
    result = await brave_web_search(mock_service, "test query")

    # Verify mock was called with correct parameters
    mock_service.perform_web_search.assert_called_once_with(
        "test query", 10, 0)

    # Verify the result
    assert result["query"] == "test query"
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "Test Result 1"
    assert result["results"][1]["title"] == "Test Result 2"


@pytest.mark.asyncio
async def test_web_search_with_params(mock_service):
    """Test brave_web_search function with custom parameters."""
    # Configure mock response
    mock_service.perform_web_search.return_value = {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "description": "This is a test result",
                "url": "https://example.com/1",
                "index": 0
            }
        ],
        "count": 1,
        "has_more": True
    }

    # Call the function with custom parameters
    result = await brave_web_search(mock_service, "test query", count=5, offset=10)

    # Verify mock was called with correct parameters
    mock_service.perform_web_search.assert_called_once_with(
        "test query", 5, 10)

    # Verify the result
    assert result["query"] == "test query"
    assert len(result["results"]) == 1
    assert result["has_more"] is True


@pytest.mark.asyncio
async def test_local_search(mock_service):
    """Test brave_local_search function."""
    # Configure mock response
    mock_service.perform_local_search.return_value = {
        "query": "coffee shops",
        "results": [
            {
                "name": "Coffee Shop 1",
                "address": "123 Main St, City, State 12345",
                "phone": "123-456-7890",
                "rating": "4.5 (100 reviews)",
                "price_range": "$$",
                "hours": "Mon-Fri: 7AM-7PM, Sat-Sun: 8AM-6PM",
                "description": "Popular local coffee shop with free WiFi",
                "index": 0
            },
            {
                "name": "Coffee Shop 2",
                "address": "456 Oak Ave, City, State 12345",
                "phone": "098-765-4321",
                "rating": "4.2 (75 reviews)",
                "price_range": "$",
                "hours": "Mon-Sun: 6AM-8PM",
                "description": "Cozy coffee shop with homemade pastries",
                "index": 1
            }
        ],
        "count": 2
    }

    # Call the function
    result = await brave_local_search(mock_service, "coffee shops")

    # Verify mock was called with correct parameters
    mock_service.perform_local_search.assert_called_once_with(
        "coffee shops", 5)

    # Verify the result
    assert result["query"] == "coffee shops"
    assert len(result["results"]) == 2
    assert result["results"][0]["name"] == "Coffee Shop 1"
    assert result["results"][1]["name"] == "Coffee Shop 2"


@pytest.mark.asyncio
async def test_local_search_with_params(mock_service):
    """Test brave_local_search function with custom parameters."""
    # Configure mock response
    mock_service.perform_local_search.return_value = {
        "query": "restaurants",
        "results": [
            {
                "name": "Restaurant 1",
                "address": "789 Pine St, City, State 12345",
                "phone": "555-123-4567",
                "rating": "4.8 (200 reviews)",
                "price_range": "$$$",
                "hours": "Mon-Sun: 11AM-10PM",
                "description": "Fine dining restaurant with award-winning chef",
                "index": 0
            }
        ],
        "count": 1
    }

    # Call the function with custom parameters
    result = await brave_local_search(mock_service, "restaurants", count=3)

    # Verify mock was called with correct parameters
    mock_service.perform_local_search.assert_called_once_with("restaurants", 3)

    # Verify the result
    assert result["query"] == "restaurants"
    assert len(result["results"]) == 1
    assert result["results"][0]["name"] == "Restaurant 1"


@pytest.mark.asyncio
async def test_error_handling_web_search(mock_service):
    """Test error handling in brave_web_search."""
    # Configure mock to raise an exception
    mock_service.perform_web_search.side_effect = Exception("API error")

    # Call the function
    result = await brave_web_search(mock_service, "test query")

    # Verify the result contains an error message
    assert "API error" in str(result)


@pytest.mark.asyncio
async def test_error_handling_local_search(mock_service):
    """Test error handling in brave_local_search."""
    # Configure mock to raise an exception
    mock_service.perform_local_search.side_effect = Exception("API error")

    # Call the function
    result = await brave_local_search(mock_service, "coffee shops")

    # Verify the result contains an error message
    assert "API error" in str(result)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
