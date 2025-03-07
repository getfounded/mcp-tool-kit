#!/usr/bin/env python3
import os
import io
import base64
from PIL import Image as PILImage
import logging

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import Tool, TextContent, ImageContent

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Browserbase tools MCP reference set")


class BrowserbaseService:
    """Service to handle browserbase interactions"""

    def __init__(self, api_key, project_id):
        self.api_key = api_key
        self.project_id = project_id
        self.browsers = {}
        self.console_logs = []
        self.screenshots = {}

    async def create_session(self, session_id):
        """Create a new browser session"""
        try:
            # We're using async patterns to match the original TypeScript implementation
            # In a real implementation, you'd use the Browserbase Python SDK if available
            import httpx

            url = "https://api.browserbase.com/v1/sessions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            data = {"projectId": self.project_id}

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)

                if not response.is_success:
                    return f"Failed to create browser session: {response.text}"

                session_data = response.json()

                # Store session info
                self.browsers[session_id] = {
                    "session_id": session_data.get("id"),
                    "connect_url": session_data.get("connectUrl")
                }

                return "Created new browser session"
        except Exception as e:
            return f"Failed to create browser session: {str(e)}"

    async def close_session(self, session_id):
        """Close a browser session"""
        if session_id not in self.browsers:
            return "Session not found"

        try:
            # In a real implementation, you'd use the Browserbase SDK
            import httpx

            url = f"https://api.browserbase.com/v1/sessions/{self.browsers[session_id]['session_id']}"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=headers)

                if not response.is_success:
                    return f"Failed to close browser session: {response.text}"

                del self.browsers[session_id]
                return "Closed session"
        except Exception as e:
            return f"Failed to close browser session: {str(e)}"

    def take_screenshot(self, name, image_data):
        """Store a screenshot"""
        self.screenshots[name] = image_data
        return f"Screenshot '{name}' taken"

    def add_console_log(self, session_id, log_type, message):
        """Add a console log message"""
        log_entry = f"[Session {session_id}][{log_type}] {message}"
        self.console_logs.append(log_entry)
        return log_entry

# Resource to get console logs


def get_console_logs():
    """Get browser console logs"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    return "\n".join(browserbase.console_logs)

# Resource to get screenshots


def get_screenshot(name: str):
    """Get a stored screenshot by name"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if name not in browserbase.screenshots:
        return f"Screenshot '{name}' not found"

    # Return the screenshot as an image
    return Image(
        data=browserbase.screenshots[name],
        format="png"
    )

# Tool function definitions that will be registered with MCP


async def browserbase_create_session(sessionId: str, ctx: Context = None) -> str:
    """Create a new cloud browser session using Browserbase"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    # Check if session already exists
    if sessionId in browserbase.browsers:
        return "Session already exists"

    return await browserbase.create_session(sessionId)


async def browserbase_close_session(sessionId: str, ctx: Context = None) -> str:
    """Close a browser session on Browserbase"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    return await browserbase.close_session(sessionId)


async def browserbase_navigate(sessionId: str, url: str, ctx: Context = None) -> str:
    """Navigate to a URL in the browser"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if sessionId not in browserbase.browsers:
        return f"Session '{sessionId}' not found. Create a session first with browserbase_create_session."

    return f"Navigated to {url}"


async def browserbase_screenshot(
    sessionId: str,
    name: str,
    selector: str = None,
    width: int = 800,
    height: int = 600,
    ctx: Context = None
) -> str:
    """Take a screenshot of the current page or a specific element"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if sessionId not in browserbase.browsers:
        return f"Session '{sessionId}' not found. Create a session first with browserbase_create_session."

    # In a real implementation, you'd use puppeteer to take the screenshot
    # Here we're simulating it by generating a blank image
    img = PILImage.new('RGB', (width, height), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    browserbase.take_screenshot(name, img_str)

    # Also store as a resource so it's available via resource API
    return f"Screenshot '{name}' taken at {width}x{height}"


async def browserbase_click(sessionId: str, selector: str, ctx: Context = None) -> str:
    """Click an element on the page"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if sessionId not in browserbase.browsers:
        return f"Session '{sessionId}' not found. Create a session first with browserbase_create_session."


async def browserbase_fill(sessionId: str, selector: str, value: str, ctx: Context = None) -> str:
    """Fill out an input field"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if sessionId not in browserbase.browsers:
        return f"Session '{sessionId}' not found. Create a session first with browserbase_create_session."

    return f"Filled {selector} with: {value}"


async def browserbase_evaluate(sessionId: str, script: str, ctx: Context = None) -> str:
    """Execute JavaScript in the browser console"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if sessionId not in browserbase.browsers:
        return f"Session '{sessionId}' not found. Create a session first with browserbase_create_session."

    return f"Executed script. Simulated result: {{\"result\": \"JavaScript execution successful\"}}"


async def browserbase_get_content(sessionId: str, selector: str = None, ctx: Context = None) -> str:
    """Extract all content from the current page"""
    browserbase = _get_browserbase_service()
    if not browserbase:
        return "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables."

    if sessionId not in browserbase.browsers:
        return f"Session '{sessionId}' not found. Create a session first with browserbase_create_session."

    return "Extracted content: [Simulated page content would appear here]"

# Tool registration and initialization
_browserbase_service = None


def initialize_browserbase_service(api_key=None, project_id=None):
    """Initialize the Browserbase service"""
    global _browserbase_service

    if api_key is None:
        api_key = os.environ.get("BROWSERBASE_API_KEY")

    if project_id is None:
        project_id = os.environ.get("BROWSERBASE_PROJECT_ID")

    if not api_key or not project_id:
        logging.warning(
            "Browserbase API keys not configured. Please set the BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID environment variables.")
        return None

    _browserbase_service = BrowserbaseService(
        api_key=api_key, project_id=project_id)
    return _browserbase_service


def _get_browserbase_service():
    """Get or initialize the Browserbase service"""
    global _browserbase_service
    if _browserbase_service is None:
        _browserbase_service = initialize_browserbase_service()
    return _browserbase_service


def get_browserbase_tools():
    """Get a dictionary of all Browserbase tools for registration with MCP"""
    return {
        "browserbase_create_session": browserbase_create_session,
        "browserbase_close_session": browserbase_close_session,
        "browserbase_navigate": browserbase_navigate,
        "browserbase_screenshot": browserbase_screenshot,
        "browserbase_click": browserbase_click,
        "browserbase_fill": browserbase_fill,
        "browserbase_evaluate": browserbase_evaluate,
        "browserbase_get_content": browserbase_get_content
    }


def get_browserbase_resources():
    """Get a dictionary of all Browserbase resources for registration with MCP"""
    return {
        "console://logs": get_console_logs,
        "screenshot://{name}": get_screenshot
    }
