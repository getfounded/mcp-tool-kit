import logging
from typing import List, Dict, Optional, Any, Union

# Assuming MCPClient is defined elsewhere
from app.toolkit_client import MCPClient


class MCPToolKit:
    """Client wrapper for the MCP Tool Kit providing easy access to all tools."""

    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initialize the MCP Tool Kit client.

        Args:
            server_url: URL of the MCP Tool Kit server. Defaults to http://localhost:8000.
        """
        self.client = MCPClient(server_url)
        self.logger = logging.getLogger("MCPToolKit")

        # Set up logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    #
    # File System Operations
    #

    def read_file(self, path: str) -> str:
        """
        Read the contents of a file.

        Args:
            path: Path to the file to read.

        Returns:
            The contents of the file as a string.
        """
        return self.client.call_tool("read_file", {"path": path})

    def read_multiple_files(self, paths: List[str]) -> str:
        """
        Read multiple files at once.

        Args:
            paths: List of file paths to read.

        Returns:
            The contents of all files, separated by file boundaries.
        """
        return self.client.call_tool("read_multiple_files", {"paths": paths})

    def write_file(self, path: str, content: str) -> str:
        """
        Write content to a file. Creates the file if it doesn't exist.

        Args:
            path: Path where the file should be written.
            content: Content to write to the file.

        Returns:
            Confirmation message.
        """
        return self.client.call_tool("write_file", {"path": path, "content": content})

    def edit_file(self, path: str, edits: List[Dict[str, str]], dry_run: bool = False) -> str:
        """
        Make line-based edits to a text file.

        Args:
            path: Path to the file to edit.
            edits: List of edit operations, each with 'oldText' and 'newText' properties.
            dry_run: If True, returns diff without actually modifying the file.

        Returns:
            A diff showing the changes made or that would be made.
        """
        return self.client.call_tool("edit_file", {
            "path": path,
            "edits": edits,
            "dry_run": dry_run
        })

    def create_directory(self, path: str) -> str:
        """
        Create a new directory or ensure a directory exists.

        Args:
            path: Path where the directory should be created.

        Returns:
            Confirmation message.
        """
        return self.client.call_tool("create_directory", {"path": path})

    def list_directory(self, path: str) -> str:
        """
        List contents of a directory.

        Args:
            path: Path to the directory to list.

        Returns:
            Formatted string of directory contents.
        """
        return self.client.call_tool("list_directory", {"path": path})

    def directory_tree(self, path: str) -> str:
        """
        Get a recursive tree view of a directory as JSON.

        Args:
            path: Path to the directory.

        Returns:
            JSON string representing the directory structure.
        """
        return self.client.call_tool("directory_tree", {"path": path})

    def move_file(self, source: str, destination: str) -> str:
        """
        Move or rename a file or directory.

        Args:
            source: Path to the file or directory to move.
            destination: Path where the file or directory should be moved.

        Returns:
            Confirmation message.
        """
        return self.client.call_tool("move_file", {
            "source": source,
            "destination": destination
        })

    def search_files(self, path: str, pattern: str, exclude_patterns: Optional[List[str]] = None) -> str:
        """
        Search for files matching a pattern.

        Args:
            path: Root path to start the search.
            pattern: Pattern to search for.
            exclude_patterns: List of patterns to exclude from search.

        Returns:
            List of matching files.
        """
        return self.client.call_tool("search_files", {
            "path": path,
            "pattern": pattern,
            "exclude_patterns": exclude_patterns or []
        })

    def get_file_info(self, path: str) -> str:
        """
        Get detailed information about a file or directory.

        Args:
            path: Path to the file or directory.

        Returns:
            Formatted string with file metadata.
        """
        return self.client.call_tool("get_file_info", {"path": path})

    def list_allowed_directories(self) -> str:
        """
        List all directories that the server is allowed to access.

        Returns:
            List of allowed directories.
        """
        return self.client.call_tool("list_allowed_directories", {})

    #
    # Brave Search Operations
    #

    def web_search(self, query: str, count: int = 10, offset: int = 0) -> str:
        """
        Perform a web search using Brave Search.

        Args:
            query: Search query.
            count: Number of results to return (max 20).
            offset: Offset for pagination.

        Returns:
            Formatted search results.
        """
        return self.client.call_tool("brave_web_search", {
            "query": query,
            "count": min(count, 20),
            "offset": offset
        })

    def local_search(self, query: str, count: int = 5) -> str:
        """
        Search for local businesses and places using Brave's Local Search API.

        Args:
            query: Search query.
            count: Number of results to return.

        Returns:
            Formatted search results for local businesses.
        """
        return self.client.call_tool("brave_local_search", {
            "query": query,
            "count": count
        })

    #
    # Browser Automation Operations
    #

    def browser_launch(self, browser_type: str = "chromium", headless: bool = True,
                       slow_mo: Optional[int] = None, proxy: Optional[Dict[str, str]] = None,
                       downloads_path: Optional[str] = None, args: Optional[List[str]] = None) -> str:
        """
        Launch a new browser instance.

        Args:
            browser_type: Type of browser to launch ('chromium', 'firefox', or 'webkit').
            headless: Whether to run browser in headless mode.
            slow_mo: Slow down operations by the specified amount of milliseconds.
            proxy: Proxy configuration, e.g. {'server': 'http://myproxy.com:3128'}.
            downloads_path: Directory to download files to.
            args: Additional arguments to pass to the browser instance.

        Returns:
            JSON string with browser information.
        """
        return self.client.call_tool("playwright_launch_browser", {
            "browser_type": browser_type,
            "headless": headless,
            "slow_mo": slow_mo,
            "proxy": proxy,
            "downloads_path": downloads_path,
            "args": args
        })

    def browser_close(self, browser_id: str) -> str:
        """
        Close a browser instance and all its pages.

        Args:
            browser_id: ID of the browser to close.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_close_browser", {"browser_id": browser_id})

    def browser_new_page(self, browser_id: Optional[str] = None, context_id: Optional[str] = None) -> str:
        """
        Create a new page in an existing browser context.

        Args:
            browser_id: ID of the browser (optional if context_id is provided).
            context_id: ID of the browser context (optional if browser_id is provided).

        Returns:
            JSON string with page information.
        """
        params = {}
        if browser_id:
            params["browser_id"] = browser_id
        if context_id:
            params["context_id"] = context_id

        return self.client.call_tool("playwright_new_page", params)

    def browser_close_page(self, page_id: str) -> str:
        """
        Close a specific page.

        Args:
            page_id: ID of the page to close.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_close_page", {"page_id": page_id})

    def browser_navigate(self, page_id: str, url: str, wait_until: str = "load",
                         timeout: int = 30000) -> str:
        """
        Navigate to a URL.

        Args:
            page_id: ID of the page.
            url: URL to navigate to.
            wait_until: When to consider navigation complete.
            timeout: Maximum navigation time in milliseconds.

        Returns:
            JSON string with navigation result.
        """
        return self.client.call_tool("playwright_navigate", {
            "page_id": page_id,
            "url": url,
            "wait_until": wait_until,
            "timeout": timeout
        })

    def browser_get_content(self, page_id: str) -> str:
        """
        Get the HTML content of a page.

        Args:
            page_id: ID of the page.

        Returns:
            JSON string with HTML content.
        """
        return self.client.call_tool("playwright_get_content", {"page_id": page_id})

    def browser_screenshot(self, page_id: str, path: Optional[str] = None,
                           full_page: bool = False, selector: Optional[str] = None) -> str:
        """
        Take a screenshot of the page or an element.

        Args:
            page_id: ID of the page.
            path: Path to save the screenshot to (optional).
            full_page: Whether to take a screenshot of the full page.
            selector: CSS selector of element to screenshot (optional).

        Returns:
            JSON string with screenshot information.
        """
        return self.client.call_tool("playwright_screenshot", {
            "page_id": page_id,
            "path": path,
            "full_page": full_page,
            "selector": selector
        })

    def browser_click(self, page_id: str, selector: str, button: str = "left",
                      click_count: int = 1, delay: int = 0, position_x: Optional[int] = None,
                      position_y: Optional[int] = None, timeout: int = 30000) -> str:
        """
        Click on an element.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the element to click.
            button: Mouse button to use ('left', 'right', 'middle').
            click_count: Number of clicks.
            delay: Delay between mouse down and mouse up in milliseconds.
            position_x: X coordinate relative to the element to click at.
            position_y: Y coordinate relative to the element to click at.
            timeout: Maximum time to wait for the element in milliseconds.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_click", {
            "page_id": page_id,
            "selector": selector,
            "button": button,
            "click_count": click_count,
            "delay": delay,
            "position_x": position_x,
            "position_y": position_y,
            "timeout": timeout
        })

    def browser_fill(self, page_id: str, selector: str, value: str, timeout: int = 30000) -> str:
        """
        Fill an input field with text.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the input field.
            value: Text to fill the field with.
            timeout: Maximum time to wait for the element in milliseconds.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_fill", {
            "page_id": page_id,
            "selector": selector,
            "value": value,
            "timeout": timeout
        })

    def browser_type(self, page_id: str, selector: str, text: str,
                     delay: int = 0, timeout: int = 30000) -> str:
        """
        Type text into a field with optional delay between keystrokes.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the input field.
            text: Text to type.
            delay: Delay between keystrokes in milliseconds.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_type", {
            "page_id": page_id,
            "selector": selector,
            "text": text,
            "delay": delay,
            "timeout": timeout
        })

    def browser_select_option(self, page_id: str, selector: str, values: Union[str, List[str], Dict[str, str]],
                              timeout: int = 30000) -> str:
        """
        Select options in a select element.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the select element.
            values: Option values to select.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_select_option", {
            "page_id": page_id,
            "selector": selector,
            "values": values,
            "timeout": timeout
        })

    def browser_check(self, page_id: str, selector: str, timeout: int = 30000) -> str:
        """
        Check a checkbox or radio button.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the element.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_check", {
            "page_id": page_id,
            "selector": selector,
            "timeout": timeout
        })

    def browser_uncheck(self, page_id: str, selector: str, timeout: int = 30000) -> str:
        """
        Uncheck a checkbox.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the checkbox.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_uncheck", {
            "page_id": page_id,
            "selector": selector,
            "timeout": timeout
        })

    def browser_evaluate(self, page_id: str, expression: str, arg: Any = None) -> str:
        """
        Evaluate JavaScript in the page context.

        Args:
            page_id: ID of the page.
            expression: JavaScript to evaluate.
            arg: Argument to pass to the expression.

        Returns:
            JSON string with result of the evaluation.
        """
        return self.client.call_tool("playwright_evaluate", {
            "page_id": page_id,
            "expression": expression,
            "arg": arg
        })

    def browser_get_text(self, page_id: str, selector: str, timeout: int = 30000) -> str:
        """
        Get text content of an element.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the element.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with the element's text content.
        """
        return self.client.call_tool("playwright_get_text", {
            "page_id": page_id,
            "selector": selector,
            "timeout": timeout
        })

    def browser_get_property(self, page_id: str, selector: str, property_name: str,
                             timeout: int = 30000) -> str:
        """
        Get a property of an element.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the element.
            property_name: Name of the property to get.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with the property value.
        """
        return self.client.call_tool("playwright_get_property", {
            "page_id": page_id,
            "selector": selector,
            "property_name": property_name,
            "timeout": timeout
        })

    def browser_get_attribute(self, page_id: str, selector: str, attribute_name: str,
                              timeout: int = 30000) -> str:
        """
        Get an attribute of an element.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the element.
            attribute_name: Name of the attribute to get.
            timeout: Maximum time to wait for the element.

        Returns:
            JSON string with the attribute value.
        """
        return self.client.call_tool("playwright_get_attribute", {
            "page_id": page_id,
            "selector": selector,
            "attribute_name": attribute_name,
            "timeout": timeout
        })

    def browser_wait_for_selector(self, page_id: str, selector: str,
                                  state: str = "visible", timeout: int = 30000) -> str:
        """
        Wait for an element to be visible, hidden, attached, or detached.

        Args:
            page_id: ID of the page.
            selector: CSS selector of the element.
            state: State to wait for.
            timeout: Maximum time to wait.

        Returns:
            JSON string with result of the operation.
        """
        return self.client.call_tool("playwright_wait_for_selector", {
            "page_id": page_id,
            "selector": selector,
            "state": state,
            "timeout": timeout
        })

    def browser_wait_for_navigation(self, page_id: str, url: Optional[str] = None,
                                    wait_until: str = "load", timeout: int = 30000) -> str:
        """
        Wait for navigation to complete.

        Args:
            page_id: ID of the page.
            url: Optional URL or regexp pattern to wait for.
            wait_until: When to consider navigation complete.
            timeout: Maximum navigation time in milliseconds.

        Returns:
            JSON string with navigation result.
        """
        return self.client.call_tool("playwright_wait_for_navigation", {
            "page_id": page_id,
            "url": url,
            "wait_until": wait_until,
            "timeout": timeout
        })

    def browser_list_browsers(self) -> str:
        """
        List all active browser instances.

        Returns:
            JSON string with list of browser information.
        """
        return self.client.call_tool("playwright_list_browsers", {})

    def browser_list_pages(self, browser_id: Optional[str] = None,
                           context_id: Optional[str] = None) -> str:
        """
        List all active pages.

        Args:
            browser_id: ID of the browser to filter pages by (optional).
            context_id: ID of the browser context to filter pages by (optional).

        Returns:
            JSON string with list of page information.
        """
        params = {}
        if browser_id:
            params["browser_id"] = browser_id
        if context_id:
            params["context_id"] = context_id

        return self.client.call_tool("playwright_list_pages", params)

    #
    # Excel Operations
    #

    def excel_create_workbook(self, filename: str) -> str:
        """
        Create a new Excel workbook.

        Args:
            filename: Path to save the Excel file.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_create_workbook", {"filename": filename})

    def excel_add_worksheet(self, filename: str, name: Optional[str] = None) -> str:
        """
        Add a worksheet to the workbook.

        Args:
            filename: Path to the Excel file.
            name: (Optional) Name for the worksheet.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_add_worksheet", {
            "filename": filename,
            "name": name
        })

    def excel_write_data(self, filename: str, worksheet: str, row: int, col: int,
                         data: Any, format: Optional[str] = None) -> str:
        """
        Write data to a cell in a worksheet.

        Args:
            filename: Path to the Excel file.
            worksheet: Name of the worksheet.
            row: Row number (0-based).
            col: Column number (0-based).
            data: Data to write.
            format: (Optional) Name of a predefined format.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_write_data", {
            "filename": filename,
            "worksheet": worksheet,
            "row": row,
            "col": col,
            "data": data,
            "format": format
        })

    def excel_write_matrix(self, filename: str, worksheet: str, start_row: int, start_col: int,
                           data: List[List[Any]], formats: Optional[List[List[str]]] = None) -> str:
        """
        Write a matrix of data to a worksheet.

        Args:
            filename: Path to the Excel file.
            worksheet: Name of the worksheet.
            start_row: Starting row number (0-based).
            start_col: Starting column number (0-based).
            data: 2D list of data to write.
            formats: (Optional) 2D list of format names corresponding to data.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_write_matrix", {
            "filename": filename,
            "worksheet": worksheet,
            "start_row": start_row,
            "start_col": start_col,
            "data": data,
            "formats": formats
        })

    def excel_add_format(self, filename: str, format_name: str, properties: Dict[str, Any]) -> str:
        """
        Create a cell format.

        Args:
            filename: Path to the Excel file.
            format_name: Name to identify the format.
            properties: Dictionary of format properties.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_add_format", {
            "filename": filename,
            "format_name": format_name,
            "properties": properties
        })

    def excel_add_chart(self, filename: str, worksheet: str, chart_type: str,
                        data_range: List[Dict[str, Any]], position: Dict[str, int],
                        options: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a chart to a worksheet.

        Args:
            filename: Path to the Excel file.
            worksheet: Name of the worksheet.
            chart_type: Type of chart.
            data_range: List of data series specifications.
            position: Dictionary with position information.
            options: (Optional) Additional chart options.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_add_chart", {
            "filename": filename,
            "worksheet": worksheet,
            "chart_type": chart_type,
            "data_range": data_range,
            "position": position,
            "options": options
        })

    def excel_add_table(self, filename: str, worksheet: str, start_row: int, start_col: int,
                        end_row: int, end_col: int, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a table to a worksheet.

        Args:
            filename: Path to the Excel file.
            worksheet: Name of the worksheet.
            start_row: Starting row number (0-based).
            start_col: Starting column number (0-based).
            end_row: Ending row number (0-based).
            end_col: Ending column number (0-based).
            options: (Optional) Table options.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_add_table", {
            "filename": filename,
            "worksheet": worksheet,
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col,
            "options": options
        })

    def excel_close_workbook(self, filename: str) -> str:
        """
        Close and save the workbook.

        Args:
            filename: Path to the Excel file.

        Returns:
            JSON string containing the result.
        """
        return self.client.call_tool("xlsx_close_workbook", {"filename": filename})

    #
    # FRED (Federal Reserve Economic Data) Operations
    #

    def fred_get_series(self, series_id: str, observation_start: Optional[str] = None,
                        observation_end: Optional[str] = None, frequency: Optional[str] = None,
                        units: Optional[str] = None) -> str:
        """
        Get data for a FRED series.

        Args:
            series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL').
            observation_start: Start date in YYYY-MM-DD format (optional).
            observation_end: End date in YYYY-MM-DD format (optional).
            frequency: Data frequency ('d', 'w', 'm', 'q', 'sa', 'a') (optional).
            units: Units transformation (optional).

        Returns:
            JSON string with the series data.
        """
        params = {"series_id": series_id}
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if frequency:
            params["frequency"] = frequency
        if units:
            params["units"] = units

        return self.client.call_tool("fred_get_series", params)

    def fred_search(self, search_text: str, limit: int = 10, order_by: str = 'search_rank',
                    sort_order: str = 'desc') -> str:
        """
        Search for FRED series.

        Args:
            search_text: The words to match against economic data series.
            limit: Maximum number of results to return.
            order_by: Order results by values of the specified attribute.
            sort_order: Sort results in ascending or descending order.

        Returns:
            String with formatted search results.
        """
        return self.client.call_tool("fred_search", {
            "search_text": search_text,
            "limit": limit,
            "order_by": order_by,
            "sort_order": sort_order
        })

    def fred_get_series_info(self, series_id: str) -> str:
        """
        Get metadata about a FRED series.

        Args:
            series_id: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL').

        Returns:
            JSON string with series metadata.
        """
        return self.client.call_tool("fred_get_series_info", {"series_id": series_id})

    def fred_get_category(self, category_id: int = 0) -> str:
        """
        Get information about a FRED category.

        Args:
            category_id: The FRED category ID (default: 0, which is the root category).

        Returns:
            JSON string with category information.
        """
        return self.client.call_tool("fred_get_category", {"category_id": category_id})

    # Add these new methods to MCPToolKit class, after the existing Excel methods

    #
    # Excel Reading Operations
    #

    def excel_read_excel(self, filename: str, sheet_name: Union[str, int] = 0,
                         output_id: Optional[str] = None, header: Union[int, List[int], None] = 0,
                         names: Optional[List[str]] = None,
                         skiprows: Union[int, List[int], None] = None) -> str:
        """
        Read an Excel file into a pandas DataFrame.

        Args:
            filename: Path to the Excel file.
            sheet_name: Sheet name or index (default: 0).
            output_id: ID to store the DataFrame in memory (default: filename).
            header: Row(s) to use as column names (default: 0).
            names: List of custom column names (default: None).
            skiprows: Row indices to skip or number of rows to skip (default: None).

        Returns:
            JSON string with DataFrame information.
        """
        params = {
            "filename": filename,
            "sheet_name": sheet_name,
            "header": header
        }

        if output_id:
            params["output_id"] = output_id
        if names:
            params["names"] = names
        if skiprows is not None:
            params["skiprows"] = skiprows

        return self.client.call_tool("xlsx_read_excel", params)

    def excel_read_csv(self, filename: str, output_id: Optional[str] = None,
                       delimiter: str = ",", header: Union[int, List[int], None] = 0,
                       names: Optional[List[str]] = None,
                       skiprows: Union[int, List[int], None] = None,
                       encoding: Optional[str] = None) -> str:
        """
        Read a CSV file into a pandas DataFrame.

        Args:
            filename: Path to the CSV file.
            output_id: ID to store the DataFrame in memory (default: filename).
            delimiter: Delimiter to use (default: ",").
            header: Row(s) to use as column names (default: 0).
            names: List of custom column names (default: None).
            skiprows: Row indices to skip or number of rows to skip (default: None).
            encoding: File encoding (default: None, pandas will try to detect).

        Returns:
            JSON string with DataFrame information.
        """
        params = {
            "filename": filename,
            "delimiter": delimiter,
            "header": header
        }

        if output_id:
            params["output_id"] = output_id
        if names:
            params["names"] = names
        if skiprows is not None:
            params["skiprows"] = skiprows
        if encoding:
            params["encoding"] = encoding

        return self.client.call_tool("xlsx_read_csv", params)

    def excel_get_sheet_names(self, filename: str) -> str:
        """
        Get sheet names from an Excel file.

        Args:
            filename: Path to the Excel file.

        Returns:
            JSON string with sheet names.
        """
        return self.client.call_tool("xlsx_get_sheet_names", {"filename": filename})

    #
    # DataFrame Management Operations
    #

    def excel_dataframe_info(self, dataframe_id: str) -> str:
        """
        Get information about a DataFrame.

        Args:
            dataframe_id: ID of the DataFrame in memory.

        Returns:
            JSON string with DataFrame information.
        """
        return self.client.call_tool("xlsx_dataframe_info", {"dataframe_id": dataframe_id})

    def excel_list_dataframes(self) -> str:
        """
        List all DataFrames currently in memory.

        Returns:
            JSON string with list of DataFrame IDs.
        """
        return self.client.call_tool("xlsx_list_dataframes", {})

    def excel_clear_dataframe(self, dataframe_id: str) -> str:
        """
        Remove a DataFrame from memory.

        Args:
            dataframe_id: ID of the DataFrame to clear.

        Returns:
            JSON string with the result.
        """
        return self.client.call_tool("xlsx_clear_dataframe", {"dataframe_id": dataframe_id})

    def excel_get_column_values(self, dataframe_id: str, column: str,
                                unique: bool = False, count: bool = False) -> str:
        """
        Get values from a specific column in a DataFrame.

        Args:
            dataframe_id: ID of the DataFrame.
            column: Name of the column to get values from.
            unique: Whether to return only unique values (default: False).
            count: Whether to count occurrences of each value (default: False).

        Returns:
            JSON string with the column values.
        """
        return self.client.call_tool("xlsx_get_column_values", {
            "dataframe_id": dataframe_id,
            "column": column,
            "unique": unique,
            "count": count
        })

    #
    # DataFrame Manipulation Operations
    #

    def excel_filter_dataframe(self, dataframe_id: str, query: Optional[str] = None,
                               column: Optional[str] = None, value: Any = None,
                               operator: str = "==", output_id: Optional[str] = None) -> str:
        """
        Filter a DataFrame by query or column condition.

        Args:
            dataframe_id: ID of the DataFrame to filter.
            query: Query string for filtering (e.g., "column > 5 and column2 == 'value'").
            column: Column name to filter by (alternative to query).
            value: Value to compare with (used with column and operator).
            operator: Comparison operator (used with column and value): ==, !=, >, >=, <, <=, in, contains.
            output_id: ID to store the filtered DataFrame (default: dataframe_id + "_filtered").

        Returns:
            JSON string with the result.
        """
        params = {"dataframe_id": dataframe_id}

        if query:
            params["query"] = query
        if column:
            params["column"] = column
        if value is not None:
            params["value"] = value

        params["operator"] = operator

        if output_id:
            params["output_id"] = output_id

        return self.client.call_tool("xlsx_filter_dataframe", params)

    def excel_sort_dataframe(self, dataframe_id: str, by: Union[str, List[str]],
                             ascending: Union[bool, List[bool]] = True,
                             output_id: Optional[str] = None) -> str:
        """
        Sort a DataFrame by columns.

        Args:
            dataframe_id: ID of the DataFrame to sort.
            by: Column name(s) to sort by (string or list of strings).
            ascending: Whether to sort in ascending order (boolean or list of booleans).
            output_id: ID to store the sorted DataFrame (default: dataframe_id + "_sorted").

        Returns:
            JSON string with the result.
        """
        params = {
            "dataframe_id": dataframe_id,
            "by": by,
            "ascending": ascending
        }

        if output_id:
            params["output_id"] = output_id

        return self.client.call_tool("xlsx_sort_dataframe", params)

    def excel_group_dataframe(self, dataframe_id: str, by: Union[str, List[str]],
                              agg_func: Union[str, Dict[str, str]] = "mean",
                              output_id: Optional[str] = None) -> str:
        """
        Group a DataFrame and apply aggregation.

        Args:
            dataframe_id: ID of the DataFrame to group.
            by: Column name(s) to group by (string or list of strings).
            agg_func: Aggregation function(s) to apply (string or dict of column->function).
            output_id: ID to store the grouped DataFrame (default: dataframe_id + "_grouped").

        Returns:
            JSON string with the result.
        """
        params = {
            "dataframe_id": dataframe_id,
            "by": by,
            "agg_func": agg_func
        }

        if output_id:
            params["output_id"] = output_id

        return self.client.call_tool("xlsx_group_dataframe", params)

    def excel_describe_dataframe(self, dataframe_id: str,
                                 include: Union[str, List[str], None] = None,
                                 exclude: Union[str, List[str], None] = None,
                                 percentiles: Optional[List[float]] = None) -> str:
        """
        Get statistical description of a DataFrame.

        Args:
            dataframe_id: ID of the DataFrame to describe.
            include: Types of columns to include (None, 'all', or list of dtypes).
            exclude: Types of columns to exclude (None or list of dtypes).
            percentiles: List of percentiles to include in output (default: [0.25, 0.5, 0.75]).

        Returns:
            JSON string with the statistical description.
        """
        params = {"dataframe_id": dataframe_id}

        if include is not None:
            params["include"] = include
        if exclude is not None:
            params["exclude"] = exclude
        if percentiles:
            params["percentiles"] = percentiles

        return self.client.call_tool("xlsx_describe_dataframe", params)

    def excel_get_correlation(self, dataframe_id: str, method: str = "pearson") -> str:
        """
        Get correlation matrix for a DataFrame.

        Args:
            dataframe_id: ID of the DataFrame.
            method: Correlation method ('pearson', 'kendall', or 'spearman').

        Returns:
            JSON string with the correlation matrix.
        """
        return self.client.call_tool("xlsx_get_correlation", {
            "dataframe_id": dataframe_id,
            "method": method
        })

    #
    # DataFrame Export Operations
    #

    def excel_dataframe_to_excel(self, dataframe_id: str, filename: str,
                                 sheet_name: str = "Sheet1", index: bool = True) -> str:
        """
        Export a DataFrame to an Excel file.

        Args:
            dataframe_id: ID of the DataFrame in memory.
            filename: Path to save the Excel file.
            sheet_name: Name of the sheet (default: "Sheet1").
            index: Whether to include the DataFrame index (default: True).

        Returns:
            JSON string with the result.
        """
        return self.client.call_tool("xlsx_dataframe_to_excel", {
            "dataframe_id": dataframe_id,
            "filename": filename,
            "sheet_name": sheet_name,
            "index": index
        })

    def excel_dataframe_to_csv(self, dataframe_id: str, filename: str,
                               index: bool = True, encoding: str = "utf-8",
                               sep: str = ",") -> str:
        """
        Export a DataFrame to a CSV file.

        Args:
            dataframe_id: ID of the DataFrame in memory.
            filename: Path to save the CSV file.
            index: Whether to include the DataFrame index (default: True).
            encoding: File encoding (default: "utf-8").
            sep: Delimiter to use (default: ",").

        Returns:
            JSON string with the result.
        """
        return self.client.call_tool("xlsx_dataframe_to_csv", {
            "dataframe_id": dataframe_id,
            "filename": filename,
            "index": index,
            "encoding": encoding,
            "sep": sep
        })

    #
    # VAPI Phone Call Operations
    #

    def vapi_make_call(self, to: str, assistant_id: str,
                       from_number: str = None,
                       assistant_options: dict = None,
                       server_url: str = None) -> str:
        """
        Make a phone call using VAPI.

        Args:
            to: Phone number to call (E.164 format recommended, e.g., +12125551234)
            assistant_id: ID of the assistant to use for the call
            from_number: Optional phone number to display as caller ID
            assistant_options: Optional dictionary of assistant configuration options
            server_url: Optional server URL for call events

        Returns:
            JSON string with call details including call ID, status, and timestamps
        """
        params = {
            "to": to,
            "assistant_id": assistant_id
        }

        if from_number:
            params["from_number"] = from_number
        if assistant_options:
            params["assistant_options"] = assistant_options
        if server_url:
            params["server_url"] = server_url

        return self.client.call_tool("vapi_make_call", params)

    def vapi_list_calls(self, limit: int = 10,
                        before: str = None,
                        after: str = None,
                        status: str = None) -> str:
        """
        List phone calls made through VAPI.

        Args:
            limit: Maximum number of calls to return (default: 10)
            before: Return calls created before this cursor
            after: Return calls created after this cursor
            status: Filter calls by status (e.g., 'queued', 'ringing', 'in-progress', 'completed')

        Returns:
            JSON string with list of calls and pagination details
        """
        params = {"limit": limit}

        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if status:
            params["status"] = status

        return self.client.call_tool("vapi_list_calls", params)

    def vapi_get_call(self, call_id: str) -> str:
        """
        Get detailed information about a specific call.

        Args:
            call_id: ID of the call to retrieve

        Returns:
            JSON string with detailed call information including status, timestamps, and metadata
        """
        return self.client.call_tool("vapi_get_call", {"call_id": call_id})

    def vapi_end_call(self, call_id: str) -> str:
        """
        End an ongoing call.

        Args:
            call_id: ID of the call to end

        Returns:
            JSON string with the result of the operation
        """
        return self.client.call_tool("vapi_end_call", {"call_id": call_id})

    def vapi_get_recordings(self, call_id: str) -> str:
        """
        Get recordings for a specific call.

        Args:
            call_id: ID of the call to get recordings for

        Returns:
            JSON string with recording metadata including URLs, durations, and timestamps
        """
        return self.client.call_tool("vapi_get_recordings", {"call_id": call_id})

    def vapi_add_human(self, call_id: str,
                       phone_number: str = None,
                       transfer: bool = False) -> str:
        """
        Add a human participant to a call.

        Args:
            call_id: ID of the call to add the human to
            phone_number: Phone number of the human to add
            transfer: Whether to transfer the call to the human (default: False)

        Returns:
            JSON string with the result of the operation
        """
        params = {"call_id": call_id}

        if phone_number:
            params["phone_number"] = phone_number
        if transfer is not None:
            params["transfer"] = transfer

        return self.client.call_tool("vapi_add_human", params)

    def vapi_pause_call(self, call_id: str) -> str:
        """
        Pause an ongoing call.

        Args:
            call_id: ID of the call to pause

        Returns:
            JSON string with the result of the operation
        """
        return self.client.call_tool("vapi_pause_call", {"call_id": call_id})

    def vapi_resume_call(self, call_id: str) -> str:
        """
        Resume a paused call.

        Args:
            call_id: ID of the call to resume

        Returns:
            JSON string with the result of the operation
        """
        return self.client.call_tool("vapi_resume_call", {"call_id": call_id})

    def vapi_send_event(self, call_id: str,
                        event_type: str,
                        data: dict = None) -> str:
        """
        Send a custom event to a call.

        Args:
            call_id: ID of the call to send the event to
            event_type: Type of event to send
            data: Optional data payload for the event

        Returns:
            JSON string with the result of the operation
        """
        params = {
            "call_id": call_id,
            "event_type": event_type
        }

        if data:
            params["data"] = data

        return self.client.call_tool("vapi_send_event", params)

    #
    # PDF Document Management Operations
    #

    def pdf_info(self, file_path: str) -> str:
        """
        Get information about a PDF document.

        Args:
            file_path: Path to the PDF file.

        Returns:
            JSON string with PDF information including number of pages, file size, and metadata.
        """
        return self.client.call_tool("pdf_info", {"file_path": file_path})

    def pdf_extract_text(self, file_path: str, pages: Optional[List[int]] = None,
                         ocr: bool = False) -> str:
        """
        Extract text from a PDF document.

        Args:
            file_path: Path to the PDF file.
            pages: List of page numbers to extract (1-indexed). If None, extracts all pages.
            ocr: Whether to use OCR for pages with no text.

        Returns:
            JSON string with extracted text organized by page.
        """
        return self.client.call_tool("pdf_extract_text", {
            "file_path": file_path,
            "pages": pages,
            "ocr": ocr
        })

    def pdf_extract_images(self, file_path: str, pages: Optional[List[int]] = None,
                           min_size: int = 100) -> str:
        """
        Extract images from a PDF document.

        Args:
            file_path: Path to the PDF file.
            pages: List of page numbers to extract images from (1-indexed). If None, extracts from all pages.
            min_size: Minimum image dimension in pixels.

        Returns:
            JSON string with extracted images metadata and resource IDs.
        """
        return self.client.call_tool("pdf_extract_images", {
            "file_path": file_path,
            "pages": pages,
            "min_size": min_size
        })

    def pdf_split(self, file_path: str, output_dir: str, pages_per_file: int = 1) -> str:
        """
        Split a PDF into multiple files.

        Args:
            file_path: Path to the PDF file to split.
            output_dir: Directory to save the split files.
            pages_per_file: Number of pages per output file.

        Returns:
            JSON string with information about the created files.
        """
        return self.client.call_tool("pdf_split", {
            "file_path": file_path,
            "output_dir": output_dir,
            "pages_per_file": pages_per_file
        })

    def pdf_merge(self, file_paths: List[str], output_path: str) -> str:
        """
        Merge multiple PDF files into one.

        Args:
            file_paths: List of paths to the PDF files to merge.
            output_path: Path to save the merged file.

        Returns:
            JSON string with information about the merged file.
        """
        return self.client.call_tool("pdf_merge", {
            "file_paths": file_paths,
            "output_path": output_path
        })

    def pdf_add_watermark(self, file_path: str, output_path: str, text: Optional[str] = None,
                          image_path: Optional[str] = None, opacity: float = 0.3) -> str:
        """
        Add a watermark to a PDF document.

        Args:
            file_path: Path to the PDF file.
            output_path: Path to save the watermarked file.
            text: Text to use as watermark. Either text or image_path must be provided.
            image_path: Path to image to use as watermark. Either text or image_path must be provided.
            opacity: Opacity of the watermark (0-1).

        Returns:
            JSON string with information about the watermarking operation.
        """
        return self.client.call_tool("pdf_add_watermark", {
            "file_path": file_path,
            "output_path": output_path,
            "text": text,
            "image_path": image_path,
            "opacity": opacity
        })

    def pdf_encrypt(self, file_path: str, output_path: str, user_password: str,
                    owner_password: Optional[str] = None) -> str:
        """
        Encrypt a PDF document with password protection.

        Args:
            file_path: Path to the PDF file.
            output_path: Path to save the encrypted file.
            user_password: Password required to open the PDF.
            owner_password: Password for full access (optional, defaults to user_password).

        Returns:
            JSON string with information about the encryption operation.
        """
        return self.client.call_tool("pdf_encrypt", {
            "file_path": file_path,
            "output_path": output_path,
            "user_password": user_password,
            "owner_password": owner_password
        })

    def pdf_decrypt(self, file_path: str, output_path: str, password: str) -> str:
        """
        Decrypt an encrypted PDF document.

        Args:
            file_path: Path to the encrypted PDF file.
            output_path: Path to save the decrypted file.
            password: Password to decrypt the PDF.

        Returns:
            JSON string with information about the decryption operation.
        """
        return self.client.call_tool("pdf_decrypt", {
            "file_path": file_path,
            "output_path": output_path,
            "password": password
        })

    def pdf_get_form_fields(self, file_path: str) -> str:
        """
        Get all form fields in a PDF document.

        Args:
            file_path: Path to the PDF file.

        Returns:
            JSON string with form field names and their current values.
        """
        return self.client.call_tool("pdf_get_form_fields", {"file_path": file_path})

    def pdf_fill_form(self, file_path: str, output_path: str, form_data: Dict[str, str]) -> str:
        """
        Fill out form fields in a PDF document.

        Args:
            file_path: Path to the PDF file.
            output_path: Path to save the filled form.
            form_data: Dictionary with field names as keys and field values as values.

        Returns:
            JSON string with information about the form filling operation.
        """
        return self.client.call_tool("pdf_fill_form", {
            "file_path": file_path,
            "output_path": output_path,
            "form_data": form_data
        })

    #
    # News API Operations
    #

    def news_top_headlines(self, country: Optional[str] = None, category: Optional[str] = None,
                           sources: Optional[str] = None, q: Optional[str] = None,
                           page_size: int = 5, page: int = 1) -> str:
        """
        Get top headlines from NewsAPI.

        Args:
            country: The 2-letter ISO 3166-1 code of the country.
            category: The category to get headlines for.
            sources: Comma-separated string of source IDs.
            q: Keywords or phrases to search for.
            page_size: Number of results per page.
            page: Page number to fetch.

        Returns:
            Formatted string with news headlines.
        """
        params = {}
        if country:
            params["country"] = country
        if category:
            params["category"] = category
        if sources:
            params["sources"] = sources
        if q:
            params["q"] = q

        params["page_size"] = page_size
        params["page"] = page

        return self.client.call_tool("news_top_headlines", params)

    def news_search(self, q: str, sources: Optional[str] = None, domains: Optional[str] = None,
                    from_param: Optional[str] = None, to: Optional[str] = None,
                    language: str = "en", sort_by: str = "publishedAt",
                    page_size: int = 5, page: int = 1) -> str:
        """
        Search for news articles using NewsAPI.

        Args:
            q: Keywords or phrases to search for.
            sources: Comma-separated string of source IDs.
            domains: Comma-separated string of domains to restrict search to.
            from_param: A date in ISO 8601 format to get articles from.
            to: A date in ISO 8601 format to get articles until.
            language: The 2-letter ISO-639-1 code of the language.
            sort_by: The order to sort articles.
            page_size: Number of results per page.
            page: Page number to fetch.

        Returns:
            Formatted string with news articles.
        """
        params = {"q": q}

        if sources:
            params["sources"] = sources
        if domains:
            params["domains"] = domains
        if from_param:
            params["from_param"] = from_param
        if to:
            params["to"] = to

        params["language"] = language
        params["sort_by"] = sort_by
        params["page_size"] = page_size
        params["page"] = page

        return self.client.call_tool("news_search", params)

    def news_sources(self, category: Optional[str] = None, language: Optional[str] = None,
                     country: Optional[str] = None) -> str:
        """
        Get available news sources from NewsAPI.

        Args:
            category: Find sources that display news of this category.
            language: Find sources that display news in a specific language.
            country: Find sources that display news in a specific country.

        Returns:
            Formatted string with news sources.
        """
        params = {}

        if category:
            params["category"] = category
        if language:
            params["language"] = language
        if country:
            params["country"] = country

        return self.client.call_tool("news_sources", params)

    #
    # PowerPoint Operations
    #

    def ppt_create_presentation(self, session_id: str, template_path: Optional[str] = None) -> str:
        """
        Create a new PowerPoint presentation.

        Args:
            session_id: Unique identifier for the presentation session.
            template_path: Optional path to a template file.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_create_presentation", {
            "session_id": session_id,
            "template_path": template_path
        })

    def ppt_open_presentation(self, session_id: str, file_path: str) -> str:
        """
        Open an existing PowerPoint presentation.

        Args:
            session_id: Unique identifier for the presentation session.
            file_path: Path to the presentation file.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_open_presentation", {
            "session_id": session_id,
            "file_path": file_path
        })

    def ppt_save_presentation(self, session_id: str, file_path: Optional[str] = None) -> str:
        """
        Save the active PowerPoint presentation.

        Args:
            session_id: Identifier of the presentation session.
            file_path: Optional path to save the file.

        Returns:
            Status message.
        """
        params = {"session_id": session_id}
        if file_path:
            params["file_path"] = file_path

        return self.client.call_tool("ppt_save_presentation", params)

    def ppt_add_slide(self, session_id: str, layout_index: int = 1,
                      title: Optional[str] = None, content: Optional[str] = None) -> str:
        """
        Add a new slide to the presentation.

        Args:
            session_id: Identifier of the presentation session.
            layout_index: Index of the slide layout to use.
            title: Optional title for the slide.
            content: Optional content for the slide.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_add_slide", {
            "session_id": session_id,
            "layout_index": layout_index,
            "title": title,
            "content": content
        })

    def ppt_add_text(self, session_id: str, slide_index: int, text: str,
                     left: float = 1.0, top: float = 1.0, width: float = 8.0, height: float = 1.0,
                     font_size: int = 18, font_name: str = 'Calibri', bold: bool = False,
                     italic: bool = False, color: str = '000000') -> str:
        """
        Add text box to a slide.

        Args:
            session_id: Identifier of the presentation session.
            slide_index: Index of the slide to add text to.
            text: Text content to add.
            left, top, width, height: Position and size of the text box.
            font_size: Size of the font.
            font_name: Name of the font.
            bold: Whether the text should be bold.
            italic: Whether the text should be italic.
            color: Hex color code for the text.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_add_text", {
            "session_id": session_id,
            "slide_index": slide_index,
            "text": text,
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "font_size": font_size,
            "font_name": font_name,
            "bold": bold,
            "italic": italic,
            "color": color
        })

    def ppt_add_image(self, session_id: str, slide_index: int, image_path: str,
                      left: float = 1.0, top: float = 1.0,
                      width: Optional[float] = None, height: Optional[float] = None) -> str:
        """
        Add an image to a slide.

        Args:
            session_id: Identifier of the presentation session.
            slide_index: Index of the slide to add the image to.
            image_path: Path to the image file.
            left, top: Position of the image.
            width, height: Optional size of the image.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_add_image", {
            "session_id": session_id,
            "slide_index": slide_index,
            "image_path": image_path,
            "left": left,
            "top": top,
            "width": width,
            "height": height
        })

    def ppt_add_chart(self, session_id: str, slide_index: int, chart_type: str,
                      categories: List[str], series_names: List[str], series_values: List[List[float]],
                      left: float = 1.0, top: float = 1.0, width: float = 8.0, height: float = 5.0,
                      chart_title: Optional[str] = None) -> str:
        """
        Add a chart to a slide.

        Args:
            session_id: Identifier of the presentation session.
            slide_index: Index of the slide to add the chart to.
            chart_type: Type of chart to add.
            categories: List of category labels.
            series_names: List of series names.
            series_values: List of lists containing series values.
            left, top, width, height: Position and size of the chart.
            chart_title: Optional title for the chart.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_add_chart", {
            "session_id": session_id,
            "slide_index": slide_index,
            "chart_type": chart_type,
            "categories": categories,
            "series_names": series_names,
            "series_values": series_values,
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "chart_title": chart_title
        })

    def ppt_add_table(self, session_id: str, slide_index: int, rows: int, cols: int,
                      data: List[List[str]], left: float = 1.0, top: float = 1.0,
                      width: float = 8.0, height: float = 5.0) -> str:
        """
        Add a table to a slide.

        Args:
            session_id: Identifier of the presentation session.
            slide_index: Index of the slide to add the table to.
            rows: Number of rows in the table.
            cols: Number of columns in the table.
            data: 2D list containing table data.
            left, top, width, height: Position and size of the table.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_add_table", {
            "session_id": session_id,
            "slide_index": slide_index,
            "rows": rows,
            "cols": cols,
            "data": data,
            "left": left,
            "top": top,
            "width": width,
            "height": height
        })

    def ppt_analyze_presentation(self, session_id: str) -> str:
        """
        Analyze the content and structure of a presentation.

        Args:
            session_id: Identifier of the presentation session.

        Returns:
            JSON string with analysis results.
        """
        return self.client.call_tool("ppt_analyze_presentation", {"session_id": session_id})

    def ppt_enhance_presentation(self, session_id: str) -> str:
        """
        Provide suggestions to enhance the presentation.

        Args:
            session_id: Identifier of the presentation session.

        Returns:
            JSON string with enhancement suggestions.
        """
        return self.client.call_tool("ppt_enhance_presentation", {"session_id": session_id})

    def ppt_generate_presentation(self, session_id: str, title: str, content: str) -> str:
        """
        Generate a presentation from text content.

        Args:
            session_id: Identifier for the presentation session.
            title: Title for the presentation.
            content: Text content to generate slides from.

        Returns:
            Status message.
        """
        return self.client.call_tool("ppt_generate_presentation", {
            "session_id": session_id,
            "title": title,
            "content": content
        })

    #
    # Sequential Thinking Operation
    #

    def sequential_thinking(self, thought: str, thought_number: int, total_thoughts: int,
                            next_thought_needed: bool, is_revision: Optional[bool] = None,
                            revises_thought: Optional[int] = None, branch_from_thought: Optional[int] = None,
                            branch_id: Optional[str] = None, needs_more_thoughts: Optional[bool] = None) -> str:
        """
        Process a step in sequential thinking.

        Args:
            thought: The content of the current thought.
            thought_number: Number of this thought in the sequence.
            total_thoughts: Total number of thoughts expected.
            next_thought_needed: Whether more thoughts are needed.
            is_revision: Whether this thought is a revision of a previous one.
            revises_thought: Number of the thought being revised.
            branch_from_thought: Number of the thought where this branch starts.
            branch_id: Identifier for the thought branch.
            needs_more_thoughts: Whether additional thoughts are needed beyond what was initially planned.

        Returns:
            JSON string with thinking process state.
        """
        return self.client.call_tool("sequentialthinking", {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "isRevision": is_revision,
            "revisesThought": revises_thought,
            "branchFromThought": branch_from_thought,
            "branchId": branch_id,
            "needsMoreThoughts": needs_more_thoughts
        })

    #
    # Shopify Operations
    #

    def shopify_get_products(self, limit: int = 50, page_info: Optional[str] = None,
                             collection_id: Optional[str] = None, product_type: Optional[str] = None,
                             vendor: Optional[str] = None) -> str:
        """
        Get a list of products from Shopify store.

        Args:
            limit: Maximum number of products to return.
            page_info: Pagination parameter from previous response.
            collection_id: Filter by collection ID.
            product_type: Filter by product type.
            vendor: Filter by vendor name.

        Returns:
            JSON string with products data.
        """
        params = {"limit": limit}

        if page_info:
            params["page_info"] = page_info
        if collection_id:
            params["collection_id"] = collection_id
        if product_type:
            params["product_type"] = product_type
        if vendor:
            params["vendor"] = vendor

        return self.client.call_tool("shopify_get_products", params)

    def shopify_get_product(self, product_id: str) -> str:
        """
        Get a specific product by ID.

        Args:
            product_id: The ID of the product to retrieve.

        Returns:
            JSON string with product data.
        """
        return self.client.call_tool("shopify_get_product", {"product_id": product_id})

    def shopify_create_product(self, title: str, product_type: Optional[str] = None,
                               vendor: Optional[str] = None, body_html: Optional[str] = None,
                               variants: Optional[List[Dict]] = None,
                               images: Optional[List[Dict]] = None,
                               tags: Optional[str] = None) -> str:
        """
        Create a new product in the Shopify store.

        Args:
            title: Product title.
            product_type: Type of product.
            vendor: Vendor name.
            body_html: Product description in HTML.
            variants: List of variant objects.
            images: List of image objects.
            tags: Comma-separated list of tags.

        Returns:
            JSON string with created product data.
        """
        params = {"title": title}

        if product_type:
            params["product_type"] = product_type
        if vendor:
            params["vendor"] = vendor
        if body_html:
            params["body_html"] = body_html
        if variants:
            params["variants"] = variants
        if images:
            params["images"] = images
        if tags:
            params["tags"] = tags

        return self.client.call_tool("shopify_create_product", params)

    #
    # Streamlit Operations
    #

    def streamlit_create_app(self, app_id: str, code: str, overwrite: bool = False) -> str:
        """
        Create a new Streamlit app with the provided code.

        Args:
            app_id: Unique identifier for the app.
            code: Python code for the Streamlit app.
            overwrite: Whether to overwrite an existing app with the same ID.

        Returns:
            JSON string with creation result.
        """
        return self.client.call_tool("streamlit_create_app", {
            "app_id": app_id,
            "code": code,
            "overwrite": overwrite
        })

    def streamlit_run_app(self, app_id: str, port: Optional[int] = None, browser: bool = False) -> str:
        """
        Run a Streamlit app as a background process.

        Args:
            app_id: Identifier of the app to run.
            port: Optional port number.
            browser: Whether to open the app in a browser window.

        Returns:
            JSON string with run result.
        """
        params = {"app_id": app_id}

        if port:
            params["port"] = port

        params["browser"] = browser

        return self.client.call_tool("streamlit_run_app", params)

    def streamlit_stop_app(self, app_id: str) -> str:
        """
        Stop a running Streamlit app.

        Args:
            app_id: Identifier of the app to stop.

        Returns:
            JSON string with stop result.
        """
        return self.client.call_tool("streamlit_stop_app", {"app_id": app_id})

    def streamlit_list_apps(self) -> str:
        """
        List all available Streamlit apps.

        Returns:
            JSON string with list of apps.
        """
        return self.client.call_tool("streamlit_list_apps", {})

    def streamlit_get_app_url(self, app_id: str) -> str:
        """
        Get the URL for a running Streamlit app.

        Args:
            app_id: Identifier of the app.

        Returns:
            JSON string with app URL information.
        """
        return self.client.call_tool("streamlit_get_app_url", {"app_id": app_id})

    def streamlit_modify_app(self, app_id: str, code_updates: Optional[List[tuple]] = None,
                             append_code: Optional[str] = None) -> str:
        """
        Modify an existing Streamlit app.

        Args:
            app_id: Identifier of the app to modify.
            code_updates: List of tuples (old_text, new_text) for text replacements.
            append_code: Code to append to the end of the app.

        Returns:
            JSON string with modification result.
        """
        params = {"app_id": app_id}

        if code_updates:
            params["code_updates"] = code_updates
        if append_code:
            params["append_code"] = append_code

        return self.client.call_tool("streamlit_modify_app", params)

    def streamlit_check_deps(self) -> str:
        """
        Check if Streamlit and required dependencies are installed.

        Returns:
            JSON string with dependency check results.
        """
        return self.client.call_tool("streamlit_check_deps", {})

    #
    # Time Operations
    #

    def get_current_time(self, timezone: str) -> str:
        """
        Get current time in specified timezone.

        Args:
            timezone: The timezone name.

        Returns:
            JSON string with current time information.
        """
        return self.client.call_tool("get_current_time", {"timezone": timezone})

    def convert_time(self, source_timezone: str, time: str, target_timezone: str) -> str:
        """
        Convert time between timezones.

        Args:
            source_timezone: Source timezone name.
            time: Time string in HH:MM format.
            target_timezone: Target timezone name.

        Returns:
            JSON string with time conversion information.
        """
        return self.client.call_tool("convert_time", {
            "source_timezone": source_timezone,
            "time": time,
            "target_timezone": target_timezone
        })

    #
    # World Bank Operations
    #

    def worldbank_get_indicator(self, country_id: str, indicator_id: str) -> str:
        """
        Get indicator data for a specific country from the World Bank API.

        Args:
            country_id: ISO country code or country ID.
            indicator_id: World Bank indicator ID.

        Returns:
            CSV string with indicator data.
        """
        return self.client.call_tool("worldbank_get_indicator", {
            "country_id": country_id,
            "indicator_id": indicator_id
        })

    #
    # YFinance Operations
    #

    def yfinance_get_ticker_info(self, ticker_symbol: str) -> str:
        """
        Get basic information about a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).

        Returns:
            JSON string with ticker information.
        """
        return self.client.call_tool("yfinance_get_ticker_info", {"ticker_symbol": ticker_symbol})

    def yfinance_get_historical_data(self, ticker_symbol: str, period: str = "1mo",
                                     interval: str = "1d", start: Optional[str] = None,
                                     end: Optional[str] = None) -> str:
        """
        Get historical market data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).
            period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
            start: Start date string (YYYY-MM-DD) - if provided with end, overrides period.
            end: End date string (YYYY-MM-DD) - if provided with start, overrides period.

        Returns:
            JSON string with historical price data.
        """
        params = {
            "ticker_symbol": ticker_symbol,
            "period": period,
            "interval": interval
        }

        if start:
            params["start"] = start
        if end:
            params["end"] = end

        return self.client.call_tool("yfinance_get_historical_data", params)

    def yfinance_get_financials(self, ticker_symbol: str, quarterly: bool = False) -> str:
        """
        Get income statement data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).
            quarterly: If True, get quarterly data instead of annual.

        Returns:
            JSON string with financial data.
        """
        return self.client.call_tool("yfinance_get_financials", {
            "ticker_symbol": ticker_symbol,
            "quarterly": quarterly
        })

    def yfinance_get_balance_sheet(self, ticker_symbol: str, quarterly: bool = False) -> str:
        """
        Get balance sheet data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).
            quarterly: If True, get quarterly data instead of annual.

        Returns:
            JSON string with balance sheet data.
        """
        return self.client.call_tool("yfinance_get_balance_sheet", {
            "ticker_symbol": ticker_symbol,
            "quarterly": quarterly
        })

    def yfinance_get_cashflow(self, ticker_symbol: str, quarterly: bool = False) -> str:
        """
        Get cash flow data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).
            quarterly: If True, get quarterly data instead of annual.

        Returns:
            JSON string with cash flow data.
        """
        return self.client.call_tool("yfinance_get_cashflow", {
            "ticker_symbol": ticker_symbol,
            "quarterly": quarterly
        })

    def yfinance_get_earnings(self, ticker_symbol: str, quarterly: bool = False) -> str:
        """
        Get earnings data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).
            quarterly: If True, get quarterly data instead of annual.

        Returns:
            JSON string with earnings data.
        """
        return self.client.call_tool("yfinance_get_earnings", {
            "ticker_symbol": ticker_symbol,
            "quarterly": quarterly
        })

    def yfinance_get_options(self, ticker_symbol: str, date: Optional[str] = None) -> str:
        """
        Get options chain data for a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).
            date: Options expiration date (format: YYYY-MM-DD). If none, uses first available date.

        Returns:
            JSON string with options chain data.
        """
        params = {"ticker_symbol": ticker_symbol}
        if date:
            params["date"] = date

        return self.client.call_tool("yfinance_get_options", params)

    def yfinance_get_news(self, ticker_symbol: str) -> str:
        """
        Get recent news about a ticker symbol.

        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple).

        Returns:
            JSON string with news articles.
        """
        return self.client.call_tool("yfinance_get_news", {"ticker_symbol": ticker_symbol})

    def yfinance_download_data(self, tickers: Union[str, List[str]], period: str = "1mo",
                               interval: str = "1d", start: Optional[str] = None,
                               end: Optional[str] = None, group_by: str = "ticker",
                               threads: bool = True) -> str:
        """
        Download historical market data for multiple tickers.

        Args:
            tickers: Single ticker string or list of ticker symbols.
            period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo).
            start: Start date string (YYYY-MM-DD) - if provided with end, overrides period.
            end: End date string (YYYY-MM-DD) - if provided with start, overrides period.
            group_by: How to group the data ('ticker' or 'column').
            threads: Whether to use multi-threading for faster downloads.

        Returns:
            JSON string with downloaded data.
        """
        params = {
            "tickers": tickers,
            "period": period,
            "interval": interval,
            "group_by": group_by,
            "threads": threads
        }

        if start:
            params["start"] = start
        if end:
            params["end"] = end

        return self.client.call_tool("yfinance_download_data", params)
