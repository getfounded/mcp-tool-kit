#!/usr/bin/env python3
"""
Unit tests for tool registry functionality.
"""
import pytest
from unittest.mock import MagicMock

from app.tools.base.registry import (
    register_tool, get_all_tools, get_tools_by_category,
    get_tool_categories, get_tools_by_service,
    get_or_create_service, get_service, clear_registry
)


class TestServiceClass:
    """Mock service class for testing"""

    def __init__(self):
        self.initialized = False

    def initialize(self):
        self.initialized = True
        return True


@pytest.fixture
def clear_tools_registry():
    """Clear the tools registry before and after each test"""
    clear_registry()
    yield
    clear_registry()


def test_register_tool(clear_tools_registry):
    """Test tool registration with decorator"""

    # Register a simple function without service
    @register_tool(name="test_func", category="Test")
    def test_function(arg1: str, arg2: int = 42):
        """Test function docstring"""
        return f"{arg1} {arg2}"

    # Get all registered tools
    tools = get_all_tools()

    # Check that the tool was registered
    assert "test_func" in tools
    assert tools["test_func"]["function"] == test_function
    assert tools["test_func"]["category"] == "Test"
    assert tools["test_func"]["service_class"] is None
    assert tools["test_func"]["doc"] == "Test function docstring"

    # Check parameter information
    params = tools["test_func"]["parameters"]
    assert "arg1" in params
    assert params["arg1"]["required"] == True
    assert params["arg1"]["type"] == "<class 'str'>"

    assert "arg2" in params
    assert params["arg2"]["required"] == False
    assert params["arg2"]["type"] == "<class 'int'>"
    assert params["arg2"]["default"] == 42


def test_register_tool_with_service(clear_tools_registry):
    """Test tool registration with service class"""
    # Register a function that requires a service
    @register_tool(name="service_func", category="Service Test", service_class=TestServiceClass)
    def service_function(self, param1: str):
        """Service function docstring"""
        return f"Service: {param1}"

    # Get all registered tools
    tools = get_all_tools()

    # Check that the tool was registered with service class
    assert "service_func" in tools
    assert tools["service_func"]["function"] == service_function
    assert tools["service_func"]["category"] == "Service Test"
    assert tools["service_func"]["service_class"] == TestServiceClass

    # Check parameter information (should not include 'self')
    params = tools["service_func"]["parameters"]
    assert "self" not in params
    assert "param1" in params


def test_get_tools_by_category(clear_tools_registry):
    """Test getting tools by category"""
    # Register tools in different categories
    @register_tool(name="cat1_tool1", category="Category1")
    def cat1_tool1(): pass

    @register_tool(name="cat1_tool2", category="Category1")
    def cat1_tool2(): pass

    @register_tool(name="cat2_tool", category="Category2")
    def cat2_tool(): pass

    # Get tools by category
    cat1_tools = get_tools_by_category("Category1")
    cat2_tools = get_tools_by_category("Category2")

    # Check results
    assert len(cat1_tools) == 2
    assert "cat1_tool1" in cat1_tools
    assert "cat1_tool2" in cat1_tools

    assert len(cat2_tools) == 1
    assert "cat2_tool" in cat2_tools

    # Non-existent category should return empty dict
    assert get_tools_by_category("NonExistent") == {}


def test_get_tool_categories(clear_tools_registry):
    """Test getting all tool categories"""
    # Register tools in different categories
    @register_tool(name="cat1_tool", category="Category1")
    def cat1_tool(): pass

    @register_tool(name="cat2_tool", category="Category2")
    def cat2_tool(): pass

    @register_tool(name="cat3_tool", category="Category3")
    def cat3_tool(): pass

    # Get all categories
    categories = get_tool_categories()

    # Check results
    assert len(categories) == 3
    assert "Category1" in categories
    assert "Category2" in categories
    assert "Category3" in categories

    # Categories should be sorted
    assert categories == sorted(categories)


def test_get_tools_by_service(clear_tools_registry):
    """Test getting tools by service class"""
    # Define another service class for testing
    class AnotherServiceClass:
        pass

    # Register tools with different service classes
    @register_tool(name="service1_tool1", service_class=TestServiceClass)
    def service1_tool1(): pass

    @register_tool(name="service1_tool2", service_class=TestServiceClass)
    def service1_tool2(): pass

    @register_tool(name="service2_tool", service_class=AnotherServiceClass)
    def service2_tool(): pass

    @register_tool(name="no_service_tool")
    def no_service_tool(): pass

    # Get tools by service class
    service1_tools = get_tools_by_service(TestServiceClass)
    service2_tools = get_tools_by_service(AnotherServiceClass)

    # Check results
    assert len(service1_tools) == 2
    assert "service1_tool1" in service1_tools
    assert "service1_tool2" in service1_tools

    assert len(service2_tools) == 1
    assert "service2_tool" in service2_tools

    # Non-existent service should return empty dict
    class NonExistentService:
        pass
    assert get_tools_by_service(NonExistentService) == {}


def test_get_or_create_service(clear_tools_registry):
    """Test service creation and retrieval"""
    # Get or create a service
    service1 = get_or_create_service(TestServiceClass)

    # Service should be initialized
    assert service1.initialized == True

    # Getting the same service again should return the same instance
    service2 = get_or_create_service(TestServiceClass)
    assert service2 is service1

    # Getting with get_service should also return the same instance
    service3 = get_service(TestServiceClass)
    assert service3 is service1


def test_service_injection(clear_tools_registry):
    """Test service injection in tool functions"""
    # Create a class with methods to be registered
    class TestService(TestServiceClass):
        def test_method(self, param):
            return f"Method: {param}"

    # Register a function that expects service as first argument
    @register_tool(name="service_func", service_class=TestService)
    def service_function(self, param):
        return self.test_method(param)

    # Call the wrapper function directly (without a service instance)
    # It should fetch/create the service and inject it
    func = get_all_tools()["service_func"]["function"]
    result = func("test")

    # Check that the service was injected and method called
    assert result == "Method: test"

    # Check the same with a method where 'self' is already bound
    test_service = TestService()
    bound_method = test_service.test_method

    # Register the bound method
    register_tool(name="bound_method", service_class=TestService)(bound_method)

    # Get the wrapper function
    wrapper = get_all_tools()["bound_method"]["function"]

    # Call wrapper directly, should work without duplicating 'self'
    result = wrapper("test2")
    assert result == "Method: test2"
