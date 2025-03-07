#!/usr/bin/env python3
import os
import json
import logging
import base64
import io
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
    logging.info("PyAutoGUI tools MCP reference set")

class PyAutoGUITools(str, Enum):
    """Enum of PyAutoGUI tool names"""
    MOVE_MOUSE = "pyautogui_move_mouse"
    CLICK = "pyautogui_click"
    RIGHT_CLICK = "pyautogui_right_click"
    DOUBLE_CLICK = "pyautogui_double_click"
    DRAG_MOUSE = "pyautogui_drag_mouse"
    SCROLL = "pyautogui_scroll"
    TYPE_TEXT = "pyautogui_type_text"
    PRESS_KEY = "pyautogui_press_key"
    HOTKEY = "pyautogui_hotkey"
    SCREENSHOT = "pyautogui_screenshot"
    LOCATE_ON_SCREEN = "pyautogui_locate_on_screen"
    GET_SCREEN_SIZE = "pyautogui_get_screen_size"
    GET_MOUSE_POSITION = "pyautogui_get_mouse_position"
    ALERT = "pyautogui_alert"
    CONFIRM = "pyautogui_confirm"
    PROMPT = "pyautogui_prompt"
    GET_ACTIVE_WINDOW = "pyautogui_get_active_window"

class PyAutoGUIService:
    """Service to handle PyAutoGUI operations"""
    
    def __init__(self):
        """Initialize the PyAutoGUI service"""
        try:
            import pyautogui
            self.pyautogui = pyautogui
            # Set a reasonable pause between PyAutoGUI commands
            self.pyautogui.PAUSE = 0.5
            # Set failsafe to True (moving mouse to corner will abort)
            self.pyautogui.FAILSAFE = True
            self.initialized = True
        except ImportError:
            logging.error("PyAutoGUI library not installed. Please install with 'pip install pyautogui'")
            self.initialized = False
            self.pyautogui = None
    
    def _is_initialized(self):
        """Check if the service is properly initialized"""
        if not self.initialized:
            raise ValueError("PyAutoGUI service not properly initialized. Check if pyautogui library is installed.")
        return True
    
    async def move_mouse(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """Move the mouse to the specified position"""
        try:
            self._is_initialized()
            self.pyautogui.moveTo(x, y, duration=duration)
            return {
                "success": True,
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def click(self, x: Optional[int] = None, y: Optional[int] = None, 
                    button: str = "left", clicks: int = 1, interval: float = 0.0) -> Dict[str, Any]:
        """Click at the specified position or current mouse position"""
        try:
            self._is_initialized()
            result = self.pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            # If x or y is None, get current mouse position
            if x is None or y is None:
                pos = self.pyautogui.position()
                x, y = pos.x, pos.y
            
            return {
                "success": True,
                "position": {"x": x, "y": y},
                "button": button,
                "clicks": clicks
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Right-click at the specified position or current mouse position"""
        try:
            self._is_initialized()
            self.pyautogui.rightClick(x, y)
            # If x or y is None, get current mouse position
            if x is None or y is None:
                pos = self.pyautogui.position()
                x, y = pos.x, pos.y
                
            return {
                "success": True,
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Double-click at the specified position or current mouse position"""
        try:
            self._is_initialized()
            self.pyautogui.doubleClick(x, y)
            # If x or y is None, get current mouse position
            if x is None or y is None:
                pos = self.pyautogui.position()
                x, y = pos.x, pos.y
                
            return {
                "success": True,
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def drag_mouse(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                         duration: float = 0.5, button: str = "left") -> Dict[str, Any]:
        """Drag mouse from start position to end position"""
        try:
            self._is_initialized()
            # First move to start position
            self.pyautogui.moveTo(start_x, start_y, duration=duration/2)
            # Then drag to end position
            self.pyautogui.dragTo(end_x, end_y, duration=duration/2, button=button)
            
            return {
                "success": True,
                "start_position": {"x": start_x, "y": start_y},
                "end_position": {"x": end_x, "y": end_y}
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> Dict[str, Any]:
        """Scroll the mouse wheel by the specified amount"""
        try:
            self._is_initialized()
            self.pyautogui.scroll(clicks, x, y)
            # If x or y is None, get current mouse position
            if x is None or y is None:
                pos = self.pyautogui.position()
                x, y = pos.x, pos.y
                
            return {
                "success": True,
                "position": {"x": x, "y": y},
                "scroll_amount": clicks
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def type_text(self, text: str, interval: float = 0.0) -> Dict[str, Any]:
        """Type the specified text"""
        try:
            self._is_initialized()
            self.pyautogui.write(text, interval=interval)
            
            return {
                "success": True,
                "text": text,
                "interval": interval
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def press_key(self, key: str) -> Dict[str, Any]:
        """Press and release the specified key"""
        try:
            self._is_initialized()
            self.pyautogui.press(key)
            
            return {
                "success": True,
                "key": key
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def hotkey(self, *keys) -> Dict[str, Any]:
        """Press the specified hotkey combination"""
        try:
            self._is_initialized()
            self.pyautogui.hotkey(*keys)
            
            return {
                "success": True,
                "keys": keys
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict[str, Any]:
        """Take a screenshot of the entire screen or a region"""
        try:
            self._is_initialized()
            if region:
                screenshot = self.pyautogui.screenshot(region=region)
            else:
                screenshot = self.pyautogui.screenshot()
            
            # Convert to base64 string for JSON
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "success": True,
                "region": region,
                "image_data": img_str,
                "width": screenshot.width,
                "height": screenshot.height
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def locate_on_screen(self, image_path: str, confidence: float = 0.9) -> Dict[str, Any]:
        """Locate the position of an image on the screen"""
        try:
            self._is_initialized()
            try:
                # Try to locate with OpenCV (need confidence parameter)
                location = self.pyautogui.locateOnScreen(image_path, confidence=confidence)
            except:
                # Fall back to exact match if OpenCV not available
                location = self.pyautogui.locateOnScreen(image_path)
                
            if location:
                return {
                    "success": True,
                    "found": True,
                    "position": {
                        "left": location.left,
                        "top": location.top,
                        "width": location.width,
                        "height": location.height
                    }
                }
            else:
                return {
                    "success": True,
                    "found": False
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_screen_size(self) -> Dict[str, Any]:
        """Get the screen size"""
        try:
            self._is_initialized()
            width, height = self.pyautogui.size()
            
            return {
                "success": True,
                "width": width,
                "height": height
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_mouse_position(self) -> Dict[str, Any]:
        """Get the current mouse position"""
        try:
            self._is_initialized()
            x, y = self.pyautogui.position()
            
            return {
                "success": True,
                "position": {"x": x, "y": y}
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def alert(self, text: str, title: str = "PyAutoGUI Alert") -> Dict[str, Any]:
        """Display an alert box"""
        try:
            self._is_initialized()
            self.pyautogui.alert(text=text, title=title)
            
            return {
                "success": True,
                "text": text,
                "title": title
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def confirm(self, text: str, title: str = "PyAutoGUI Confirm") -> Dict[str, Any]:
        """Display a confirm box and return the result"""
        try:
            self._is_initialized()
            result = self.pyautogui.confirm(text=text, title=title)
            
            return {
                "success": True,
                "result": result,
                "text": text,
                "title": title
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def prompt(self, text: str, title: str = "PyAutoGUI Prompt", default: str = "") -> Dict[str, Any]:
        """Display a prompt box and return the result"""
        try:
            self._is_initialized()
            result = self.pyautogui.prompt(text=text, title=title, default=default)
            
            return {
                "success": True,
                "result": result,
                "text": text,
                "title": title
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_active_window(self) -> Dict[str, Any]:
        """Get information about the active window"""
        try:
            self._is_initialized()
            # This is OS-specific and might not work on all platforms
            try:
                # For Windows using pygetwindow (usually installed with pyautogui)
                import pygetwindow as gw
                window = gw.getActiveWindow()
                if window:
                    return {
                        "success": True,
                        "title": window.title,
                        "position": {
                            "left": window.left,
                            "top": window.top,
                            "width": window.width,
                            "height": window.height
                        }
                    }
                else:
                    return {
                        "success": True,
                        "window_found": False
                    }
            except:
                # Fallback
                return {
                    "success": True,
                    "error": "GetActiveWindow not supported on this platform"
                }
        except Exception as e:
            return {"error": str(e)}

# Tool function definitions that will be registered with MCP

async def pyautogui_move_mouse(x: int, y: int, duration: float = 0.5, ctx: Context = None) -> str:
    """Move the mouse to the specified screen coordinates.

    Parameters:
    - x: X-coordinate to move to
    - y: Y-coordinate to move to
    - duration: How long the movement should take in seconds (default: 0.5)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.move_mouse(x, y, duration)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_click(x: Optional[int] = None, y: Optional[int] = None, 
                         button: str = "left", clicks: int = 1, 
                         interval: float = 0.0, ctx: Context = None) -> str:
    """Click at the specified position or the current mouse position.

    Parameters:
    - x: X-coordinate to click at (default: current position)
    - y: Y-coordinate to click at (default: current position)
    - button: Mouse button to use (left, middle, right)
    - clicks: Number of clicks to perform
    - interval: Time between clicks in seconds
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.click(x, y, button, clicks, interval)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_right_click(x: Optional[int] = None, y: Optional[int] = None, ctx: Context = None) -> str:
    """Right-click at the specified position or the current mouse position.

    Parameters:
    - x: X-coordinate to click at (default: current position)
    - y: Y-coordinate to click at (default: current position)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.right_click(x, y)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_double_click(x: Optional[int] = None, y: Optional[int] = None, ctx: Context = None) -> str:
    """Double-click at the specified position or the current mouse position.

    Parameters:
    - x: X-coordinate to click at (default: current position)
    - y: Y-coordinate to click at (default: current position)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.double_click(x, y)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int, 
                             duration: float = 0.5, button: str = "left", ctx: Context = None) -> str:
    """Drag the mouse from one position to another.

    Parameters:
    - start_x: Starting X-coordinate
    - start_y: Starting Y-coordinate
    - end_x: Ending X-coordinate
    - end_y: Ending Y-coordinate
    - duration: How long the drag should take in seconds (default: 0.5)
    - button: Mouse button to use (left, middle, right)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.drag_mouse(start_x, start_y, end_x, end_y, duration, button)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_scroll(clicks: int, x: Optional[int] = None, y: Optional[int] = None, ctx: Context = None) -> str:
    """Scroll the mouse wheel.

    Parameters:
    - clicks: Number of "clicks" to scroll, positive is up, negative is down
    - x: X-coordinate for the scroll (default: current position)
    - y: Y-coordinate for the scroll (default: current position)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.scroll(clicks, x, y)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_type_text(text: str, interval: float = 0.0, ctx: Context = None) -> str:
    """Type the specified text at the current cursor position.

    Parameters:
    - text: The text to type
    - interval: Time between key presses in seconds (default: 0.0)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.type_text(text, interval)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_press_key(key: str, ctx: Context = None) -> str:
    """Press and release a keyboard key.

    Parameters:
    - key: The key to press (e.g., 'enter', 'tab', 'a', '1', etc.)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.press_key(key)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_hotkey(*keys, ctx: Context = None) -> str:
    """Press a combination of keys.

    Parameters:
    - *keys: The keys to press in sequence (e.g., 'ctrl', 'c' for copy)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.hotkey(*keys)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_screenshot(region: List[int] = None, ctx: Context = None) -> str:
    """Take a screenshot of the entire screen or a region.

    Parameters:
    - region: Optional [left, top, width, height] for a partial screenshot
    
    Returns:
    - JSON string with result of the operation and base64-encoded image data
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        # Convert region list to tuple if provided
        region_tuple = tuple(region) if region else None
        result = await pyautogui_service.screenshot(region_tuple)
        
        # If we have MCP context and a successful result with image data, set a resource
        if ctx and "success" in result and "image_data" in result:
            img = Image(data=result["image_data"], format="png")
            img_resource_id = f"pyautogui_screenshot_{id(result)}"
            ctx.set_resource(img_resource_id, img)
            result["image_resource"] = img_resource_id
            # Remove base64 data to keep response smaller
            del result["image_data"]
            
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_locate_on_screen(image_path: str, confidence: float = 0.9, ctx: Context = None) -> str:
    """Locate the position of an image on the screen.

    Parameters:
    - image_path: Path to the image file to find on screen
    - confidence: Match confidence threshold (0.0-1.0, requires OpenCV)
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.locate_on_screen(image_path, confidence)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_get_screen_size(ctx: Context = None) -> str:
    """Get the screen size in pixels.
    
    Returns:
    - JSON string with width and height of the screen
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.get_screen_size()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_get_mouse_position(ctx: Context = None) -> str:
    """Get the current position of the mouse cursor.
    
    Returns:
    - JSON string with x and y coordinates of the mouse
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.get_mouse_position()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_alert(text: str, title: str = "PyAutoGUI Alert", ctx: Context = None) -> str:
    """Display an alert box with the specified message.

    Parameters:
    - text: The message to display
    - title: The title of the alert box
    
    Returns:
    - JSON string with result of the operation
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.alert(text, title)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_confirm(text: str, title: str = "PyAutoGUI Confirm", ctx: Context = None) -> str:
    """Display a confirmation dialog and return the user's response.

    Parameters:
    - text: The message to display
    - title: The title of the confirmation dialog
    
    Returns:
    - JSON string with result of the operation including the user's response
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.confirm(text, title)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_prompt(text: str, title: str = "PyAutoGUI Prompt", default: str = "", ctx: Context = None) -> str:
    """Display a prompt dialog and return the user's input.

    Parameters:
    - text: The message to display
    - title: The title of the prompt dialog
    - default: Default text to show in the input field
    
    Returns:
    - JSON string with result of the operation including the user's input
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.prompt(text, title, default)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def pyautogui_get_active_window(ctx: Context = None) -> str:
    """Get information about the currently active window.
    
    Returns:
    - JSON string with window title and position details
    """
    pyautogui_service = _get_pyautogui_service()
    if not pyautogui_service:
        return json.dumps({"error": "PyAutoGUI service not properly initialized"}, indent=2)
    
    try:
        result = await pyautogui_service.get_active_window()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# Tool registration and initialization
_pyautogui_service = None

def initialize_pyautogui_service():
    """Initialize the PyAutoGUI service"""
    global _pyautogui_service
    _pyautogui_service = PyAutoGUIService()
    return _pyautogui_service

def _get_pyautogui_service():
    """Get or initialize the PyAutoGUI service"""
    global _pyautogui_service
    if _pyautogui_service is None:
        _pyautogui_service = initialize_pyautogui_service()
    return _pyautogui_service

def get_pyautogui_tools():
    """Get a dictionary of all PyAutoGUI tools for registration with MCP"""
    return {
        PyAutoGUITools.MOVE_MOUSE: pyautogui_move_mouse,
        PyAutoGUITools.CLICK: pyautogui_click,
        PyAutoGUITools.RIGHT_CLICK: pyautogui_right_click,
        PyAutoGUITools.DOUBLE_CLICK: pyautogui_double_click,
        PyAutoGUITools.DRAG_MOUSE: pyautogui_drag_mouse,
        PyAutoGUITools.SCROLL: pyautogui_scroll,
        PyAutoGUITools.TYPE_TEXT: pyautogui_type_text,
        PyAutoGUITools.PRESS_KEY: pyautogui_press_key,
        PyAutoGUITools.HOTKEY: pyautogui_hotkey,
        PyAutoGUITools.SCREENSHOT: pyautogui_screenshot,
        PyAutoGUITools.LOCATE_ON_SCREEN: pyautogui_locate_on_screen,
        PyAutoGUITools.GET_SCREEN_SIZE: pyautogui_get_screen_size,
        PyAutoGUITools.GET_MOUSE_POSITION: pyautogui_get_mouse_position,
        PyAutoGUITools.ALERT: pyautogui_alert,
        PyAutoGUITools.CONFIRM: pyautogui_confirm,
        PyAutoGUITools.PROMPT: pyautogui_prompt,
        PyAutoGUITools.GET_ACTIVE_WINDOW: pyautogui_get_active_window
    }

# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the PyAutoGUI module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)
    
    # Initialize the service
    service = initialize_pyautogui_service()
    
    # Check if the initialization was successful
    if service and service.initialized:
        logging.info("PyAutoGUI service initialized successfully")
        return True
    else:
        logging.warning("Failed to initialize PyAutoGUI service. Please ensure pyautogui is installed.")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("PyAutoGUI service module - use with MCP Unified Server")
