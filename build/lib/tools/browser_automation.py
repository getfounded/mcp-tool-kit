#!/usr/bin/env python3
import os
import json
import logging
import base64
import asyncio
import tempfile
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Tuple

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.types import Tool, TextContent, ImageContent

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Playwright tools MCP reference set")


class PlaywrightTools(str, Enum):
    """Enum of Playwright tool names"""
    LAUNCH_BROWSER = "playwright_launch_browser"
    CLOSE_BROWSER = "playwright_close_browser"
    NEW_PAGE = "playwright_new_page"
    CLOSE_PAGE = "playwright_close_page"
    NAVIGATE = "playwright_navigate"
    GET_CONTENT = "playwright_get_content"
    SCREENSHOT = "playwright_screenshot"
    CLICK = "playwright_click"
    FILL = "playwright_fill"
    TYPE = "playwright_type"
    SELECT_OPTION = "playwright_select_option"
    CHECK = "playwright_check"
    UNCHECK = "playwright_uncheck"
    EVALUATE = "playwright_evaluate"
    GET_TEXT = "playwright_get_text"
    GET_PROPERTY = "playwright_get_property"
    GET_ATTRIBUTE = "playwright_get_attribute"
    WAIT_FOR_SELECTOR = "playwright_wait_for_selector"
    WAIT_FOR_NAVIGATION = "playwright_wait_for_navigation"
    WAIT_FOR_LOAD_STATE = "playwright_wait_for_load_state"
    GO_BACK = "playwright_go_back"
    GO_FORWARD = "playwright_go_forward"
    RELOAD = "playwright_reload"
    SET_VIEWPORT_SIZE = "playwright_set_viewport_size"
    SET_EXTRA_HTTP_HEADERS = "playwright_set_extra_http_headers"
    ADD_INIT_SCRIPT = "playwright_add_init_script"
    EMULATE_MEDIA = "playwright_emulate_media"
    PDF = "playwright_pdf"
    LIST_BROWSERS = "playwright_list_browsers"
    LIST_PAGES = "playwright_list_pages"


class PlaywrightService:
    """Service to handle Playwright browser automation operations"""

    def __init__(self):
        """Initialize the Playwright service"""
        # Will be populated with active browser instances
        self.browsers = {}
        self.pages = {}
        self.contexts = {}
        self.next_browser_id = 1
        self.next_context_id = 1
        self.next_page_id = 1

        # Initialize Playwright when needed, not at instantiation
        self.playwright = None
        self.initialized = False

        # Create temp directory for downloads, screenshots, PDFs
        self.temp_dir = tempfile.mkdtemp(prefix="playwright_")

    async def _ensure_initialized(self):
        """Ensure Playwright is initialized"""
        if not self.initialized:
            try:
                from playwright.async_api import async_playwright
                self.playwright_module = async_playwright

                # Initialize playwright
                self.playwright = await self.playwright_module().__aenter__()
                self.initialized = True
                logging.info("Playwright initialized successfully")
            except ImportError:
                raise ImportError(
                    "Playwright not installed. Install with: pip install playwright")
            except Exception as e:
                raise Exception(f"Failed to initialize Playwright: {str(e)}")

    async def launch_browser(self, browser_type="chromium", headless=True, slow_mo=None,
                             proxy=None, downloads_path=None, args=None):
        """Launch a new browser instance"""
        await self._ensure_initialized()

        try:
            # Select the browser type
            if browser_type.lower() == "chromium":
                browser_launcher = self.playwright.chromium
            elif browser_type.lower() == "firefox":
                browser_launcher = self.playwright.firefox
            elif browser_type.lower() == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            # Prepare launch options
            launch_options = {
                "headless": headless
            }

            if slow_mo is not None:
                launch_options["slow_mo"] = slow_mo

            if proxy is not None:
                launch_options["proxy"] = proxy

            if downloads_path is not None:
                launch_options["downloads_path"] = downloads_path
            else:
                launch_options["downloads_path"] = os.path.join(
                    self.temp_dir, "downloads")

            if args is not None:
                launch_options["args"] = args

            # Launch the browser
            browser = await browser_launcher.launch(**launch_options)

            # Generate browser ID and store browser instance
            browser_id = f"browser_{self.next_browser_id}"
            self.next_browser_id += 1

            self.browsers[browser_id] = {
                "instance": browser,
                "type": browser_type,
                "contexts": [],
                "pages": []
            }

            # Create default browser context
            context = await browser.new_context()
            context_id = f"context_{self.next_context_id}"
            self.next_context_id += 1

            self.contexts[context_id] = {
                "instance": context,
                "browser_id": browser_id,
                "pages": []
            }

            self.browsers[browser_id]["contexts"].append(context_id)

            # Create default page
            page = await context.new_page()
            page_id = f"page_{self.next_page_id}"
            self.next_page_id += 1

            self.pages[page_id] = {
                "instance": page,
                "context_id": context_id,
                "browser_id": browser_id,
                "url": "about:blank",
                "title": ""
            }

            self.contexts[context_id]["pages"].append(page_id)
            self.browsers[browser_id]["pages"].append(page_id)

            return {
                "browser_id": browser_id,
                "context_id": context_id,
                "page_id": page_id,
                "browser_type": browser_type
            }
        except Exception as e:
            raise Exception(f"Failed to launch browser: {str(e)}")

    async def close_browser(self, browser_id):
        """Close a browser instance and clean up resources"""
        if browser_id not in self.browsers:
            raise ValueError(f"Browser ID not found: {browser_id}")

        browser_info = self.browsers[browser_id]
        browser = browser_info["instance"]

        try:
            # Close browser which automatically closes all pages and contexts
            await browser.close()

            # Clean up tracked pages and contexts
            for page_id in browser_info["pages"]:
                if page_id in self.pages:
                    del self.pages[page_id]

            for context_id in browser_info["contexts"]:
                if context_id in self.contexts:
                    del self.contexts[context_id]

            # Remove browser record
            del self.browsers[browser_id]

            return {
                "success": True,
                "browser_id": browser_id
            }
        except Exception as e:
            raise Exception(f"Failed to close browser: {str(e)}")

    async def new_page(self, browser_id=None, context_id=None):
        """Create a new page in an existing browser context"""
        # First ensure we have a valid browser and context
        if browser_id is None and context_id is None:
            # If no browser or context specified, use first available or create new
            if not self.browsers:
                # No browsers exist, launch a new one
                launch_result = await self.launch_browser()
                browser_id = launch_result["browser_id"]
                context_id = launch_result["context_id"]
            else:
                # Use the first available browser
                browser_id = next(iter(self.browsers))
                # And its first context
                context_id = self.browsers[browser_id]["contexts"][0]
        elif browser_id is not None and context_id is None:
            # Browser specified but not context
            if browser_id not in self.browsers:
                raise ValueError(f"Browser ID not found: {browser_id}")

            # Use the first context of the specified browser
            context_id = self.browsers[browser_id]["contexts"][0]
        elif context_id is not None:
            # Context specified, verify it exists
            if context_id not in self.contexts:
                raise ValueError(f"Context ID not found: {context_id}")

            # Get the browser for this context
            browser_id = self.contexts[context_id]["browser_id"]

        try:
            # Get the context instance
            context = self.contexts[context_id]["instance"]

            # Create a new page
            page = await context.new_page()
            page_id = f"page_{self.next_page_id}"
            self.next_page_id += 1

            # Track the new page
            self.pages[page_id] = {
                "instance": page,
                "context_id": context_id,
                "browser_id": browser_id,
                "url": "about:blank",
                "title": ""
            }

            # Update the context and browser page lists
            self.contexts[context_id]["pages"].append(page_id)
            self.browsers[browser_id]["pages"].append(page_id)

            return {
                "page_id": page_id,
                "context_id": context_id,
                "browser_id": browser_id
            }
        except Exception as e:
            raise Exception(f"Failed to create new page: {str(e)}")

    async def close_page(self, page_id):
        """Close a specific page"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page_info = self.pages[page_id]
        page = page_info["instance"]
        context_id = page_info["context_id"]
        browser_id = page_info["browser_id"]

        try:
            # Close the page
            await page.close()

            # Remove page from tracking
            del self.pages[page_id]

            # Remove page from context and browser lists
            if context_id in self.contexts:
                if page_id in self.contexts[context_id]["pages"]:
                    self.contexts[context_id]["pages"].remove(page_id)

            if browser_id in self.browsers:
                if page_id in self.browsers[browser_id]["pages"]:
                    self.browsers[browser_id]["pages"].remove(page_id)

            return {
                "success": True,
                "page_id": page_id
            }
        except Exception as e:
            raise Exception(f"Failed to close page: {str(e)}")

    async def navigate(self, page_id, url, wait_until="load", timeout=30000):
        """Navigate to a URL"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Navigate to URL
            response = await page.goto(url, wait_until=wait_until, timeout=timeout)

            # Update page info
            self.pages[page_id]["url"] = page.url
            self.pages[page_id]["title"] = await page.title()

            status = response.status if response else None

            return {
                "success": True,
                "page_id": page_id,
                "url": page.url,
                "title": await page.title(),
                "status": status
            }
        except Exception as e:
            raise Exception(f"Failed to navigate: {str(e)}")

    async def get_content(self, page_id):
        """Get the HTML content of a page"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            content = await page.content()

            return {
                "success": True,
                "page_id": page_id,
                "content": content
            }
        except Exception as e:
            raise Exception(f"Failed to get content: {str(e)}")

    async def screenshot(self, page_id, path=None, full_page=False, selector=None):
        """Take a screenshot of the page or a specific element"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Determine screenshot options
            screenshot_options = {
                "full_page": full_page,
                "type": "png"
            }

            # If path not specified, create a temp file
            if path is None:
                path = os.path.join(
                    self.temp_dir, f"screenshot_{page_id}_{int(asyncio.get_event_loop().time())}.png")

            screenshot_options["path"] = path

            # Take the screenshot
            if selector:
                # Screenshot of a specific element
                element = await page.query_selector(selector)
                if not element:
                    raise ValueError(
                        f"Element not found with selector: {selector}")
                screenshot_binary = await element.screenshot(**screenshot_options)
            else:
                # Screenshot of the page
                screenshot_binary = await page.screenshot(**screenshot_options)

            # Convert to base64 for returning
            screenshot_base64 = base64.b64encode(
                screenshot_binary).decode('utf-8')

            return {
                "success": True,
                "page_id": page_id,
                "path": path,
                "image_data": screenshot_base64
            }
        except Exception as e:
            raise Exception(f"Failed to take screenshot: {str(e)}")

    async def click(self, page_id, selector, button="left", click_count=1, delay=0,
                    position_x=None, position_y=None, timeout=30000):
        """Click on an element"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            click_options = {
                "button": button,
                "click_count": click_count,
                "delay": delay,
                "timeout": timeout
            }

            # If specific position requested
            if position_x is not None and position_y is not None:
                click_options["position"] = {"x": position_x, "y": position_y}

            # Click the element
            await page.click(selector, **click_options)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector
            }
        except Exception as e:
            raise Exception(f"Failed to click element: {str(e)}")

    async def fill(self, page_id, selector, value, timeout=30000):
        """Fill an input field with text"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Fill the form field
            await page.fill(selector, value, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "value": value
            }
        except Exception as e:
            raise Exception(f"Failed to fill input: {str(e)}")

    async def type(self, page_id, selector, text, delay=0, timeout=30000):
        """Type text into a field with an optional delay between keystrokes"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Type into the form field
            await page.type(selector, text, delay=delay, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "text": text
            }
        except Exception as e:
            raise Exception(f"Failed to type text: {str(e)}")

    async def select_option(self, page_id, selector, values, timeout=30000):
        """Select options in a select element"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Select options
            selected_values = await page.select_option(selector, values, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "selected_values": selected_values
            }
        except Exception as e:
            raise Exception(f"Failed to select option: {str(e)}")

    async def check(self, page_id, selector, timeout=30000):
        """Check a checkbox or radio button"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Check the element
            await page.check(selector, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector
            }
        except Exception as e:
            raise Exception(f"Failed to check element: {str(e)}")

    async def uncheck(self, page_id, selector, timeout=30000):
        """Uncheck a checkbox"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Uncheck the element
            await page.uncheck(selector, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector
            }
        except Exception as e:
            raise Exception(f"Failed to uncheck element: {str(e)}")

    async def evaluate(self, page_id, expression, arg=None):
        """Evaluate JavaScript in the page context"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Evaluate JavaScript
            if arg is not None:
                result = await page.evaluate(expression, arg)
            else:
                result = await page.evaluate(expression)

            return {
                "success": True,
                "page_id": page_id,
                "result": result
            }
        except Exception as e:
            raise Exception(f"Failed to evaluate JavaScript: {str(e)}")

    async def get_text(self, page_id, selector, timeout=30000):
        """Get text content of an element"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Wait for the selector to be visible
            await page.wait_for_selector(selector, state="visible", timeout=timeout)

            # Get text content
            text = await page.text_content(selector)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "text": text
            }
        except Exception as e:
            raise Exception(f"Failed to get text: {str(e)}")

    async def get_property(self, page_id, selector, property_name, timeout=30000):
        """Get a property of an element"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Wait for the selector
            element = await page.wait_for_selector(selector, timeout=timeout)
            if not element:
                raise ValueError(f"Element not found: {selector}")

            # Get the property
            property_value = await element.get_property(property_name)

            # Convert to JSON serializable value
            json_value = await property_value.json_value()

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "property": property_name,
                "value": json_value
            }
        except Exception as e:
            raise Exception(f"Failed to get property: {str(e)}")

    async def get_attribute(self, page_id, selector, attribute_name, timeout=30000):
        """Get an attribute of an element"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Get the attribute
            attribute_value = await page.get_attribute(selector, attribute_name, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "attribute": attribute_name,
                "value": attribute_value
            }
        except Exception as e:
            raise Exception(f"Failed to get attribute: {str(e)}")

    async def wait_for_selector(self, page_id, selector, state="visible", timeout=30000):
        """Wait for an element to be visible or hidden"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Wait for the selector
            await page.wait_for_selector(selector, state=state, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "selector": selector,
                "state": state
            }
        except Exception as e:
            raise Exception(f"Failed to wait for selector: {str(e)}")

    async def wait_for_navigation(self, page_id, url=None, wait_until="load", timeout=30000):
        """Wait for navigation to complete"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Create a navigation context based on URL pattern if provided
            if url:
                async with page.expect_navigation(url=url, wait_until=wait_until, timeout=timeout) as navigation_info:
                    # Return immediately, this will wait for navigation that is triggered elsewhere
                    response = await navigation_info.value
            else:
                async with page.expect_navigation(wait_until=wait_until, timeout=timeout) as navigation_info:
                    # Return immediately, this will wait for navigation that is triggered elsewhere
                    response = await navigation_info.value

            # Update page info
            self.pages[page_id]["url"] = page.url
            self.pages[page_id]["title"] = await page.title()

            status = response.status if response else None

            return {
                "success": True,
                "page_id": page_id,
                "url": page.url,
                "title": await page.title(),
                "status": status
            }
        except Exception as e:
            raise Exception(f"Failed to wait for navigation: {str(e)}")

    async def wait_for_load_state(self, page_id, state="load", timeout=30000):
        """Wait for page load state"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Wait for load state
            await page.wait_for_load_state(state=state, timeout=timeout)

            return {
                "success": True,
                "page_id": page_id,
                "state": state
            }
        except Exception as e:
            raise Exception(f"Failed to wait for load state: {str(e)}")

    async def go_back(self, page_id, wait_until="load", timeout=30000):
        """Navigate back in browser history"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Go back
            response = await page.go_back(wait_until=wait_until, timeout=timeout)

            # Update page info
            self.pages[page_id]["url"] = page.url
            self.pages[page_id]["title"] = await page.title()

            status = response.status if response else None

            return {
                "success": True,
                "page_id": page_id,
                "url": page.url,
                "title": await page.title(),
                "status": status
            }
        except Exception as e:
            raise Exception(f"Failed to go back: {str(e)}")

    async def go_forward(self, page_id, wait_until="load", timeout=30000):
        """Navigate forward in browser history"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Go forward
            response = await page.go_forward(wait_until=wait_until, timeout=timeout)

            # Update page info
            self.pages[page_id]["url"] = page.url
            self.pages[page_id]["title"] = await page.title()

            status = response.status if response else None

            return {
                "success": True,
                "page_id": page_id,
                "url": page.url,
                "title": await page.title(),
                "status": status
            }
        except Exception as e:
            raise Exception(f"Failed to go forward: {str(e)}")

    async def reload(self, page_id, wait_until="load", timeout=30000):
        """Reload the current page"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Reload the page
            response = await page.reload(wait_until=wait_until, timeout=timeout)

            status = response.status if response else None

            return {
                "success": True,
                "page_id": page_id,
                "url": page.url,
                "title": await page.title(),
                "status": status
            }
        except Exception as e:
            raise Exception(f"Failed to reload page: {str(e)}")

    async def set_viewport_size(self, page_id, width, height):
        """Set the viewport size"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Set viewport size
            await page.set_viewport_size({"width": width, "height": height})

            return {
                "success": True,
                "page_id": page_id,
                "width": width,
                "height": height
            }
        except Exception as e:
            raise Exception(f"Failed to set viewport size: {str(e)}")

    async def set_extra_http_headers(self, page_id, headers):
        """Set extra HTTP headers for all requests"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Set headers
            await page.set_extra_http_headers(headers)

            return {
                "success": True,
                "page_id": page_id,
                "headers": headers
            }
        except Exception as e:
            raise Exception(f"Failed to set HTTP headers: {str(e)}")

    async def add_init_script(self, page_id, script=None, script_path=None):
        """Add initialization script that will be run in each new page"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Add initialization script
            if script:
                await page.add_init_script(script=script)
            elif script_path:
                await page.add_init_script(path=script_path)
            else:
                raise ValueError(
                    "Either script or script_path must be provided")

            return {
                "success": True,
                "page_id": page_id
            }
        except Exception as e:
            raise Exception(f"Failed to add init script: {str(e)}")

    async def emulate_media(self, page_id, media=None, color_scheme=None):
        """Emulate media type and/or color scheme"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Set media and/or color scheme
            params = {}
            if media:
                params["media"] = media
            if color_scheme:
                params["color_scheme"] = color_scheme

            await page.emulate_media(**params)

            return {
                "success": True,
                "page_id": page_id,
                "media": media,
                "color_scheme": color_scheme
            }
        except Exception as e:
            raise Exception(f"Failed to emulate media: {str(e)}")

    async def pdf(self, page_id, path=None, landscape=False, format=None, width=None, height=None):
        """Generate a PDF from the page"""
        if page_id not in self.pages:
            raise ValueError(f"Page ID not found: {page_id}")

        page = self.pages[page_id]["instance"]

        try:
            # Check if this browser supports PDF (only Chromium does)
            browser_id = self.pages[page_id]["browser_id"]
            if self.browsers[browser_id]["type"].lower() != "chromium":
                raise ValueError(
                    "PDF generation is only supported in Chromium")

            # Build options
            pdf_options = {
                "landscape": landscape
            }

            if format:
                pdf_options["format"] = format

            if width and height:
                pdf_options["width"] = width
                pdf_options["height"] = height

            # If path not specified, create a temp file
            if path is None:
                path = os.path.join(
                    self.temp_dir, f"pdf_{page_id}_{int(asyncio.get_event_loop().time())}.pdf")

            pdf_options["path"] = path

            # Generate PDF
            pdf_data = await page.pdf(**pdf_options)

            # Convert to base64 for returning
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

            return {
                "success": True,
                "page_id": page_id,
                "path": path,
                "pdf_data": pdf_base64
            }
        except Exception as e:
            raise Exception(f"Failed to generate PDF: {str(e)}")

    async def list_browsers(self):
        """List all active browser instances"""
        try:
            browser_list = []

            for browser_id, browser_info in self.browsers.items():
                browser_data = {
                    "browser_id": browser_id,
                    "type": browser_info["type"],
                    "contexts": browser_info["contexts"],
                    "pages": browser_info["pages"]
                }
                browser_list.append(browser_data)

            return {
                "success": True,
                "browsers": browser_list,
                "count": len(browser_list)
            }
        except Exception as e:
            raise Exception(f"Failed to list browsers: {str(e)}")

    async def list_pages(self, browser_id=None, context_id=None):
        """List all active pages"""
        try:
            page_list = []

            for page_id, page_info in self.pages.items():
                # Filter by browser_id if provided
                if browser_id and page_info["browser_id"] != browser_id:
                    continue

                # Filter by context_id if provided
                if context_id and page_info["context_id"] != context_id:
                    continue

                page_data = {
                    "page_id": page_id,
                    "browser_id": page_info["browser_id"],
                    "context_id": page_info["context_id"],
                    "url": page_info["url"],
                    "title": page_info["title"]
                }
                page_list.append(page_data)

            return {
                "success": True,
                "pages": page_list,
                "count": len(page_list)
            }
        except Exception as e:
            raise Exception(f"Failed to list pages: {str(e)}")

    async def cleanup(self):
        """Close all browsers and clean up resources"""
        try:
            # Close all browsers
            browser_ids = list(self.browsers.keys())
            close_results = []

            for browser_id in browser_ids:
                try:
                    result = await self.close_browser(browser_id)
                    close_results.append(result)
                except Exception as e:
                    close_results.append({
                        "success": False,
                        "browser_id": browser_id,
                        "error": str(e)
                    })

            # Close Playwright
            if self.initialized and self.playwright:
                await self.playwright.__aexit__(None, None, None)
                self.initialized = False

            return {
                "success": True,
                "browsers_closed": close_results,
                "count": len(close_results)
            }
        except Exception as e:
            raise Exception(f"Failed to clean up: {str(e)}")

# Tool function definitions that will be registered with MCP


async def playwright_launch_browser(
    browser_type: str = "chromium",
    headless: bool = True,
    slow_mo: Optional[int] = None,
    proxy: Optional[Dict[str, str]] = None,
    downloads_path: Optional[str] = None,
    args: Optional[List[str]] = None,
    ctx: Context = None
) -> str:
    """Launch a new browser instance.

    Parameters:
    - browser_type: Type of browser to launch ('chromium', 'firefox', or 'webkit')
    - headless: Whether to run browser in headless mode
    - slow_mo: Slow down operations by the specified amount of milliseconds
    - proxy: Proxy configuration, e.g. {'server': 'http://myproxy.com:3128'}
    - downloads_path: Directory to download files to
    - args: Additional arguments to pass to the browser instance

    Returns:
    - JSON string with browser information including IDs for the browser, context, and page
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.launch_browser(
            browser_type=browser_type,
            headless=headless,
            slow_mo=slow_mo,
            proxy=proxy,
            downloads_path=downloads_path,
            args=args
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_close_browser(
    browser_id: str,
    ctx: Context = None
) -> str:
    """Close a browser instance and all its pages.

    Parameters:
    - browser_id: ID of the browser to close

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.close_browser(browser_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_new_page(
    browser_id: Optional[str] = None,
    context_id: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Create a new page in an existing browser context.

    Parameters:
    - browser_id: ID of the browser (optional if context_id is provided)
    - context_id: ID of the browser context (optional if browser_id is provided)

    Returns:
    - JSON string with page information
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.new_page(browser_id, context_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_close_page(
    page_id: str,
    ctx: Context = None
) -> str:
    """Close a specific page.

    Parameters:
    - page_id: ID of the page to close

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.close_page(page_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_navigate(
    page_id: str,
    url: str,
    wait_until: str = "load",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Navigate to a URL.

    Parameters:
    - page_id: ID of the page
    - url: URL to navigate to
    - wait_until: When to consider navigation complete ('load', 'domcontentloaded', 'networkidle', 'commit')
    - timeout: Maximum navigation time in milliseconds

    Returns:
    - JSON string with navigation result
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.navigate(page_id, url, wait_until, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_get_content(
    page_id: str,
    ctx: Context = None
) -> str:
    """Get the HTML content of a page.

    Parameters:
    - page_id: ID of the page

    Returns:
    - JSON string with HTML content
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.get_content(page_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_screenshot(
    page_id: str,
    path: Optional[str] = None,
    full_page: bool = False,
    selector: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Take a screenshot of the page or an element.

    Parameters:
    - page_id: ID of the page
    - path: Path to save the screenshot to (optional)
    - full_page: Whether to take a screenshot of the full page or just the viewport
    - selector: CSS selector of element to screenshot (optional)

    Returns:
    - JSON string with screenshot information
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.screenshot(page_id, path, full_page, selector)

        # If we have MCP context and a successful result with image data
        if ctx and "success" in result and "image_data" in result:
            img = Image(data=result["image_data"], format="png")
            img_resource_id = f"playwright_screenshot_{id(result)}"
            ctx.set_resource(img_resource_id, img)
            result["image_resource"] = img_resource_id
            # Remove base64 data to keep response smaller
            del result["image_data"]

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_click(
    page_id: str,
    selector: str,
    button: str = "left",
    click_count: int = 1,
    delay: int = 0,
    position_x: Optional[int] = None,
    position_y: Optional[int] = None,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Click on an element.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the element to click
    - button: Mouse button to use ('left', 'right', 'middle')
    - click_count: Number of clicks
    - delay: Delay between mouse down and mouse up in milliseconds
    - position_x: X coordinate relative to the element to click at
    - position_y: Y coordinate relative to the element to click at
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.click(
            page_id, selector, button, click_count,
            delay, position_x, position_y, timeout
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_fill(
    page_id: str,
    selector: str,
    value: str,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Fill an input field with text.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the input field
    - value: Text to fill the field with
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.fill(page_id, selector, value, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_type(
    page_id: str,
    selector: str,
    text: str,
    delay: int = 0,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Type text into a field with optional delay between keystrokes.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the input field
    - text: Text to type
    - delay: Delay between keystrokes in milliseconds
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.type(page_id, selector, text, delay, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_select_option(
    page_id: str,
    selector: str,
    values: Union[str, List[str], Dict[str, str]],
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Select options in a select element.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the select element
    - values: Option values to select (string, list of strings, or dict with value/label/index)
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.select_option(page_id, selector, values, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_check(
    page_id: str,
    selector: str,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Check a checkbox or radio button.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the element
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.check(page_id, selector, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_uncheck(
    page_id: str,
    selector: str,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Uncheck a checkbox.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the checkbox
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.uncheck(page_id, selector, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_evaluate(
    page_id: str,
    expression: str,
    arg: Any = None,
    ctx: Context = None
) -> str:
    """Evaluate JavaScript in the page context.

    Parameters:
    - page_id: ID of the page
    - expression: JavaScript to evaluate
    - arg: Argument to pass to the expression

    Returns:
    - JSON string with result of the evaluation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.evaluate(page_id, expression, arg)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_get_text(
    page_id: str,
    selector: str,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Get text content of an element.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the element
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with the element's text content
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.get_text(page_id, selector, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_get_property(
    page_id: str,
    selector: str,
    property_name: str,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Get a property of an element.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the element
    - property_name: Name of the property to get
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with the property value
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.get_property(page_id, selector, property_name, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_get_attribute(
    page_id: str,
    selector: str,
    attribute_name: str,
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Get an attribute of an element.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the element
    - attribute_name: Name of the attribute to get
    - timeout: Maximum time to wait for the element in milliseconds

    Returns:
    - JSON string with the attribute value
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.get_attribute(page_id, selector, attribute_name, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_wait_for_selector(
    page_id: str,
    selector: str,
    state: str = "visible",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Wait for an element to be visible, hidden, attached, or detached.

    Parameters:
    - page_id: ID of the page
    - selector: CSS selector of the element
    - state: State to wait for ('visible', 'hidden', 'attached', 'detached')
    - timeout: Maximum time to wait in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.wait_for_selector(page_id, selector, state, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_wait_for_navigation(
    page_id: str,
    url: Optional[str] = None,
    wait_until: str = "load",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Wait for navigation to complete.

    Parameters:
    - page_id: ID of the page
    - url: Optional URL or regexp pattern to wait for
    - wait_until: When to consider navigation complete ('load', 'domcontentloaded', 'networkidle', 'commit')
    - timeout: Maximum navigation time in milliseconds

    Returns:
    - JSON string with navigation result
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.wait_for_navigation(page_id, url, wait_until, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_wait_for_load_state(
    page_id: str,
    state: str = "load",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Wait for the page to reach a specific load state.

    Parameters:
    - page_id: ID of the page
    - state: Load state to wait for ('load', 'domcontentloaded', 'networkidle')
    - timeout: Maximum time to wait in milliseconds

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.wait_for_load_state(page_id, state, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_go_back(
    page_id: str,
    wait_until: str = "load",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Navigate to the previous page in history.

    Parameters:
    - page_id: ID of the page
    - wait_until: When to consider navigation complete ('load', 'domcontentloaded', 'networkidle', 'commit')
    - timeout: Maximum navigation time in milliseconds

    Returns:
    - JSON string with navigation result
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.go_back(page_id, wait_until, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_go_forward(
    page_id: str,
    wait_until: str = "load",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Navigate to the next page in history.

    Parameters:
    - page_id: ID of the page
    - wait_until: When to consider navigation complete ('load', 'domcontentloaded', 'networkidle', 'commit')
    - timeout: Maximum navigation time in milliseconds

    Returns:
    - JSON string with navigation result
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.go_forward(page_id, wait_until, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_reload(
    page_id: str,
    wait_until: str = "load",
    timeout: int = 30000,
    ctx: Context = None
) -> str:
    """Reload the current page.

    Parameters:
    - page_id: ID of the page
    - wait_until: When to consider navigation complete ('load', 'domcontentloaded', 'networkidle', 'commit')
    - timeout: Maximum navigation time in milliseconds

    Returns:
    - JSON string with navigation result
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.reload(page_id, wait_until, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_set_viewport_size(
    page_id: str,
    width: int,
    height: int,
    ctx: Context = None
) -> str:
    """Set the viewport size.

    Parameters:
    - page_id: ID of the page
    - width: Viewport width in pixels
    - height: Viewport height in pixels

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.set_viewport_size(page_id, width, height)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_set_extra_http_headers(
    page_id: str,
    headers: Dict[str, str],
    ctx: Context = None
) -> str:
    """Set extra HTTP headers for all requests.

    Parameters:
    - page_id: ID of the page
    - headers: Dictionary of HTTP headers

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.set_extra_http_headers(page_id, headers)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_add_init_script(
    page_id: str,
    script: Optional[str] = None,
    script_path: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Add initialization script that will be run in the page.

    Parameters:
    - page_id: ID of the page
    - script: JavaScript to run in the page
    - script_path: Path to a JavaScript file

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.add_init_script(page_id, script, script_path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_emulate_media(
    page_id: str,
    media: Optional[str] = None,
    color_scheme: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Emulate media type and/or color scheme.

    Parameters:
    - page_id: ID of the page
    - media: Media type to emulate ('screen', 'print', 'null')
    - color_scheme: Color scheme to emulate ('light', 'dark', 'no-preference', 'null')

    Returns:
    - JSON string with result of the operation
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.emulate_media(page_id, media, color_scheme)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_pdf(
    page_id: str,
    path: Optional[str] = None,
    landscape: bool = False,
    format: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Generate a PDF from the page (Chromium only).

    Parameters:
    - page_id: ID of the page
    - path: Path to save the PDF to (optional)
    - landscape: Whether to use landscape orientation
    - format: Paper format ('Letter', 'Legal', 'Tabloid', 'A0', 'A1', 'A2', 'A3', 'A4', etc.)
    - width: Paper width, accepts values labeled with units ('100px', '1in', etc.)
    - height: Paper height, accepts values labeled with units ('100px', '1in', etc.)

    Returns:
    - JSON string with PDF information
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.pdf(page_id, path, landscape, format, width, height)

        # If we have MCP context and a successful result with PDF data
        if ctx and "success" in result and "pdf_data" in result:
            # Could potentially set resource here if MCP supports PDF format
            pass

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_list_browsers(
    ctx: Context = None
) -> str:
    """List all active browser instances.

    Returns:
    - JSON string with list of browser information
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.list_browsers()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def playwright_list_pages(
    browser_id: Optional[str] = None,
    context_id: Optional[str] = None,
    ctx: Context = None
) -> str:
    """List all active pages.

    Parameters:
    - browser_id: ID of the browser to filter pages by (optional)
    - context_id: ID of the browser context to filter pages by (optional)

    Returns:
    - JSON string with list of page information
    """
    try:
        playwright = _get_playwright_service()
        result = await playwright.list_pages(browser_id, context_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# Tool registration and initialization
_playwright_service = None


def initialize_playwright_service():
    """Initialize the Playwright service"""
    global _playwright_service
    _playwright_service = PlaywrightService()
    return _playwright_service


def _get_playwright_service():
    """Get or initialize the Playwright service"""
    global _playwright_service
    if _playwright_service is None:
        _playwright_service = initialize_playwright_service()
    return _playwright_service


def get_playwright_tools():
    """Get a dictionary of all Playwright tools for registration with MCP"""
    return {
        PlaywrightTools.LAUNCH_BROWSER: playwright_launch_browser,
        PlaywrightTools.CLOSE_BROWSER: playwright_close_browser,
        PlaywrightTools.NEW_PAGE: playwright_new_page,
        PlaywrightTools.CLOSE_PAGE: playwright_close_page,
        PlaywrightTools.NAVIGATE: playwright_navigate,
        PlaywrightTools.GET_CONTENT: playwright_get_content,
        PlaywrightTools.SCREENSHOT: playwright_screenshot,
        PlaywrightTools.CLICK: playwright_click,
        PlaywrightTools.FILL: playwright_fill,
        PlaywrightTools.TYPE: playwright_type,
        PlaywrightTools.SELECT_OPTION: playwright_select_option,
        PlaywrightTools.CHECK: playwright_check,
        PlaywrightTools.UNCHECK: playwright_uncheck,
        PlaywrightTools.EVALUATE: playwright_evaluate,
        PlaywrightTools.GET_TEXT: playwright_get_text,
        PlaywrightTools.GET_PROPERTY: playwright_get_property,
        PlaywrightTools.GET_ATTRIBUTE: playwright_get_attribute,
        PlaywrightTools.WAIT_FOR_SELECTOR: playwright_wait_for_selector,
        PlaywrightTools.WAIT_FOR_NAVIGATION: playwright_wait_for_navigation,
        PlaywrightTools.WAIT_FOR_LOAD_STATE: playwright_wait_for_load_state,
        PlaywrightTools.GO_BACK: playwright_go_back,
        PlaywrightTools.GO_FORWARD: playwright_go_forward,
        PlaywrightTools.RELOAD: playwright_reload,
        PlaywrightTools.SET_VIEWPORT_SIZE: playwright_set_viewport_size,
        PlaywrightTools.SET_EXTRA_HTTP_HEADERS: playwright_set_extra_http_headers,
        PlaywrightTools.ADD_INIT_SCRIPT: playwright_add_init_script,
        PlaywrightTools.EMULATE_MEDIA: playwright_emulate_media,
        PlaywrightTools.PDF: playwright_pdf,
        PlaywrightTools.LIST_BROWSERS: playwright_list_browsers,
        PlaywrightTools.LIST_PAGES: playwright_list_pages
    }

# This function will be called by the unified server to initialize the module


def initialize(mcp=None):
    """Initialize the Playwright module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_playwright_service()

    # Import playwright to check if it's installed
    try:
        import playwright

        # Get version using importlib.metadata instead of __version__
        try:
            import importlib.metadata
            playwright_version = importlib.metadata.version('playwright')
            logging.info(
                f"Playwright is installed, version: {playwright_version}")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            logging.info(
                "Playwright is installed, but version could not be determined")

        # Check if browsers are installed
        import subprocess
        import sys
        try:
            # Try to run playwright install command if needed
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "--help"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info("Playwright CLI tools are available")
        except subprocess.CalledProcessError:
            logging.warning(
                "Playwright CLI tools may not be properly installed")
        except FileNotFoundError:
            logging.warning("Playwright CLI tools not found")

        return True
    except ImportError:
        logging.error(
            "Playwright not installed. Please install with: pip install playwright")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Playwright service module - use with MCP Unified Server")
