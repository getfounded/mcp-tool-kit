#!/usr/bin/env python3
"""
Test script for the MCP Toolkit infrastructure.
"""
import os
import sys
import logging
import json
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("InfrastructureTest")

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tool_discovery():
    """Test tool discovery and registration."""
    logger.info("Testing tool discovery...")
    
    # Import tool discovery
    from app.tools import discover_tools
    
    # Discover tools
    tools = discover_tools()
    
    # Log tools found
    logger.info(f"Discovered {len(tools)} tools")
    
    # Group tools by category
    categories = {}
    for tool_name, tool_info in tools.items():
        category = tool_info.get('category', 'Uncategorized')
        
        if category not in categories:
            categories[category] = []
            
        categories[category].append(tool_name)
    
    # Log tools by category
    for category, tool_names in categories.items():
        logger.info(f"Category '{category}': {len(tool_names)} tools")
        for tool_name in sorted(tool_names):
            logger.info(f"  - {tool_name}")
    
    return tools

def test_service_initialization():
    """Test service initialization."""
    logger.info("Testing service initialization...")
    
    # Import service base class
    from app.tools.base.service import ToolServiceBase
    from app.tools import initialize_services
    
    # Initialize services
    initialize_services(ToolServiceBase)
    
    # Test individual service initialization
    test_fred_service()
    test_yfinance_service()
    test_excel_service()
    test_brave_search_service()
    test_filesystem_service()
    test_time_service()
    
    logger.info("Service initialization test complete")

def test_fred_service():
    """Test FRED service initialization."""
    logger.info("Testing FRED service...")
    
    from app.tools.fred.fred_service import FREDService
    
    # Set environment variable
    os.environ["FRED_API_KEY"] = "test_api_key"
    
    # Create service
    service = FREDService()
    
    # Initialize service
    try:
        result = service.initialize()
        logger.info(f"FRED service initialization: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"FRED service initialization error: {e}")

def test_yfinance_service():
    """Test YFinance service initialization."""
    logger.info("Testing YFinance service...")
    
    from app.tools.yfinance.yfinance_service import YFinanceService
    
    # Set environment variables
    os.environ["YFINANCE_THROTTLE_CALLS"] = "5"
    os.environ["YFINANCE_THROTTLE_PERIOD"] = "60"
    
    # Create service
    service = YFinanceService()
    
    # Initialize service
    try:
        result = service.initialize()
        logger.info(f"YFinance service initialization: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"YFinance service initialization error: {e}")

def test_excel_service():
    """Test Excel service initialization."""
    logger.info("Testing Excel service...")
    
    from app.tools.excel.excel_service import ExcelService
    
    # Create service
    service = ExcelService()
    
    # Initialize service
    try:
        result = service.initialize()
        logger.info(f"Excel service initialization: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"Excel service initialization error: {e}")

def test_brave_search_service():
    """Test Brave Search service initialization."""
    logger.info("Testing Brave Search service...")
    
    from app.tools.brave_search.brave_search_service import BraveSearchService
    
    # Set environment variables
    os.environ["BRAVE_API_KEY"] = "test_api_key"
    
    # Create service
    service = BraveSearchService()
    
    # Initialize service
    try:
        result = service.initialize()
        logger.info(f"Brave Search service initialization: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"Brave Search service initialization error: {e}")

def test_filesystem_service():
    """Test Filesystem service initialization."""
    logger.info("Testing Filesystem service...")
    
    from app.tools.filesystem.filesystem_service import FilesystemService
    
    # Set environment variables
    os.environ["ALLOWED_DIRECTORIES"] = "/tmp,/data"
    
    # Create service
    service = FilesystemService()
    
    # Initialize service
    try:
        result = service.initialize()
        logger.info(f"Filesystem service initialization: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"Filesystem service initialization error: {e}")

def test_time_service():
    """Test Time service initialization."""
    logger.info("Testing Time service...")
    
    from app.tools.time.time_service import TimeService
    
    # Create service
    service = TimeService()
    
    # Initialize service
    try:
        result = service.initialize()
        logger.info(f"Time service initialization: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"Time service initialization error: {e}")

def test_toolkit_client():
    """Test the toolkit client."""
    logger.info("Testing toolkit client...")
    
    # Import toolkit
    from app.toolkit import MCPToolKit
    
    # Create toolkit instance
    toolkit = MCPToolKit(server_url="http://localhost:8000", log_level="DEBUG")
    
    # List available tools
    tools = toolkit.list_available_tools(include_parameters=True)
    logger.info(f"Toolkit client found {len(tools)} tools")
    
    # List categories
    categories = toolkit.list_categories()
    logger.info(f"Toolkit client found {len(categories)} categories: {categories}")
    
    # Test search functionality
    test_search_functions(toolkit)
    
    logger.info("Toolkit client test complete")

def test_search_functions(toolkit):
    """Test search functionality in toolkit."""
    logger.info("Testing search functionality...")
    
    # Test various search queries
    queries = ["time", "file", "market", "economic", "excel", "search"]
    
    for query in queries:
        search_results = toolkit.search_tools(query)
        logger.info(f"Search for '{query}' found {len(search_results)} tools")
        
        # Log first 3 results for each query
        for i, result in enumerate(search_results[:3]):
            logger.info(f"  - {result['name']} ({result.get('category', 'Uncategorized')})")

def main():
    """Main test function."""
    logger.info("Starting infrastructure tests...")
    
    try:
        # Test tool discovery
        tools = test_tool_discovery()
        
        # Test service initialization
        test_service_initialization()
        
        # Test toolkit client
        test_toolkit_client()
        
        logger.info("All infrastructure tests completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Infrastructure test failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
