#!/usr/bin/env python3
import os
import json
import logging
from typing import List, Dict, Optional, Any, Union, Tuple
from enum import Enum
import asyncio

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("VAPI tools MCP reference set")


class VAPITools(str, Enum):
    """Enum of VAPI tool names"""
    MAKE_CALL = "vapi_make_call"
    LIST_CALLS = "vapi_list_calls"
    GET_CALL = "vapi_get_call"
    END_CALL = "vapi_end_call"
    GET_RECORDINGS = "vapi_get_recordings"
    ADD_HUMAN = "vapi_add_human"
    PAUSE_CALL = "vapi_pause_call"
    RESUME_CALL = "vapi_resume_call"
    SEND_EVENT = "vapi_send_event"


class VAPIService:
    """Service to handle VAPI operations"""
    
    def __init__(self, api_key=None):
        """Initialize the VAPI service with API key"""
        self.api_key = api_key or os.environ.get("VAPI_API_KEY")
        if not self.api_key:
            raise ValueError("VAPI API key is required")
        
        try:
            # Import the VAPI client SDK
            from vapi import Client
            self.client = Client(api_key=self.api_key)
            self.initialized = True
            logging.info("VAPI client initialized successfully")
        except ImportError:
            logging.error("VAPI library not installed. Please install with 'pip install vapi'")
            self.initialized = False
            self.client = None
    
    def _is_initialized(self):
        """Check if the service is properly initialized"""
        if not self.initialized or not self.client:
            raise ValueError("VAPI service not properly initialized. Check if vapi library is installed.")
        return True

    async def make_call(self, to: str, assistant_id: str, 
                        from_number: Optional[str] = None,
                        assistant_options: Optional[Dict[str, Any]] = None,
                        server_url: Optional[str] = None) -> Dict[str, Any]:
        """Make a call using VAPI"""
        try:
            self._is_initialized()
            
            # Prepare call parameters
            params = {
                "to": to,
                "assistant_id": assistant_id
            }
            
            # Add optional parameters if provided
            if from_number:
                params["from"] = from_number
            if assistant_options:
                params["options"] = assistant_options
            if server_url:
                params["server_url"] = server_url
                
            # Make the API call
            call = self.client.calls.create(**params)
            return call
        except Exception as e:
            error_msg = f"Error making call: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def list_calls(self, 
                         limit: Optional[int] = 10, 
                         before: Optional[str] = None,
                         after: Optional[str] = None,
                         status: Optional[str] = None) -> Dict[str, Any]:
        """List calls from VAPI"""
        try:
            self._is_initialized()
            
            # Prepare parameters
            params = {}
            if limit:
                params["limit"] = limit
            if before:
                params["before"] = before
            if after:
                params["after"] = after
            if status:
                params["status"] = status
                
            # Make the API call
            calls = self.client.calls.list(**params)
            return calls
        except Exception as e:
            error_msg = f"Error listing calls: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get details of a specific call"""
        try:
            self._is_initialized()
            
            # Make the API call
            call = self.client.calls.get(call_id)
            return call
        except Exception as e:
            error_msg = f"Error getting call details: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End a call"""
        try:
            self._is_initialized()
            
            # Make the API call
            result = self.client.calls.end(call_id)
            return result
        except Exception as e:
            error_msg = f"Error ending call: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def get_recordings(self, call_id: str) -> Dict[str, Any]:
        """Get recordings for a call"""
        try:
            self._is_initialized()
            
            # Make the API call
            recordings = self.client.calls.recordings(call_id)
            return recordings
        except Exception as e:
            error_msg = f"Error getting call recordings: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def add_human(self, call_id: str, 
                        phone_number: str = None,
                        transfer: bool = False) -> Dict[str, Any]:
        """Add a human to a call"""
        try:
            self._is_initialized()
            
            # Prepare parameters
            params = {}
            if phone_number:
                params["phone_number"] = phone_number
            if transfer is not None:
                params["transfer"] = transfer
                
            # Make the API call
            result = self.client.calls.add_human(call_id, **params)
            return result
        except Exception as e:
            error_msg = f"Error adding human to call: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def pause_call(self, call_id: str) -> Dict[str, Any]:
        """Pause a call"""
        try:
            self._is_initialized()
            
            # Make the API call
            result = self.client.calls.pause(call_id)
            return result
        except Exception as e:
            error_msg = f"Error pausing call: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def resume_call(self, call_id: str) -> Dict[str, Any]:
        """Resume a paused call"""
        try:
            self._is_initialized()
            
            # Make the API call
            result = self.client.calls.resume(call_id)
            return result
        except Exception as e:
            error_msg = f"Error resuming call: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def send_event(self, call_id: str, 
                          event_type: str, 
                          data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send an event to a call"""
        try:
            self._is_initialized()
            
            # Prepare parameters
            params = {
                "type": event_type
            }
            if data:
                params["data"] = data
                
            # Make the API call
            result = self.client.calls.send_event(call_id, params)
            return result
        except Exception as e:
            error_msg = f"Error sending event to call: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}


# Tool function definitions that will be registered with MCP

async def vapi_make_call(to: str, assistant_id: str, 
                        from_number: Optional[str] = None,
                        assistant_options: Optional[Dict[str, Any]] = None,
                        server_url: Optional[str] = None,
                        ctx: Context = None) -> str:
    """Make a phone call using VAPI.
    
    Initiates a call to the specified phone number using a VAPI assistant.
    
    Parameters:
    - to: Phone number to call (E.164 format recommended, e.g., +12125551234)
    - assistant_id: ID of the assistant to use for the call
    - from_number: Optional phone number to display as caller ID
    - assistant_options: Optional dictionary of assistant configuration options
    - server_url: Optional server URL for call events
    
    Returns:
    - JSON string with call details including call ID, status, and timestamps
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.make_call(to, assistant_id, from_number, assistant_options, server_url)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error making call: {str(e)}"}, indent=2)


async def vapi_list_calls(limit: int = 10, 
                         before: Optional[str] = None,
                         after: Optional[str] = None,
                         status: Optional[str] = None,
                         ctx: Context = None) -> str:
    """List phone calls made through VAPI.
    
    Retrieves a list of calls with optional filtering.
    
    Parameters:
    - limit: Maximum number of calls to return (default: 10)
    - before: Return calls created before this cursor
    - after: Return calls created after this cursor
    - status: Filter calls by status (e.g., 'queued', 'ringing', 'in-progress', 'completed')
    
    Returns:
    - JSON string with list of calls and pagination details
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.list_calls(limit, before, after, status)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing calls: {str(e)}"}, indent=2)


async def vapi_get_call(call_id: str, ctx: Context = None) -> str:
    """Get detailed information about a specific call.
    
    Retrieves complete information about a call by its ID.
    
    Parameters:
    - call_id: ID of the call to retrieve
    
    Returns:
    - JSON string with detailed call information including status, timestamps, and metadata
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.get_call(call_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error getting call: {str(e)}"}, indent=2)


async def vapi_end_call(call_id: str, ctx: Context = None) -> str:
    """End an ongoing call.
    
    Terminates an active call by its ID.
    
    Parameters:
    - call_id: ID of the call to end
    
    Returns:
    - JSON string with the result of the operation
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.end_call(call_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error ending call: {str(e)}"}, indent=2)


async def vapi_get_recordings(call_id: str, ctx: Context = None) -> str:
    """Get recordings for a specific call.
    
    Retrieves a list of recordings associated with a call.
    
    Parameters:
    - call_id: ID of the call to get recordings for
    
    Returns:
    - JSON string with recording metadata including URLs, durations, and timestamps
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.get_recordings(call_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error getting recordings: {str(e)}"}, indent=2)


async def vapi_add_human(call_id: str, 
                        phone_number: str = None,
                        transfer: bool = False,
                        ctx: Context = None) -> str:
    """Add a human participant to a call.
    
    Adds a human to an ongoing call, optionally transferring control.
    
    Parameters:
    - call_id: ID of the call to add the human to
    - phone_number: Phone number of the human to add
    - transfer: Whether to transfer the call to the human (default: False)
    
    Returns:
    - JSON string with the result of the operation
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.add_human(call_id, phone_number, transfer)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error adding human to call: {str(e)}"}, indent=2)


async def vapi_pause_call(call_id: str, ctx: Context = None) -> str:
    """Pause an ongoing call.
    
    Temporarily pauses an active call.
    
    Parameters:
    - call_id: ID of the call to pause
    
    Returns:
    - JSON string with the result of the operation
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.pause_call(call_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error pausing call: {str(e)}"}, indent=2)


async def vapi_resume_call(call_id: str, ctx: Context = None) -> str:
    """Resume a paused call.
    
    Continues a previously paused call.
    
    Parameters:
    - call_id: ID of the call to resume
    
    Returns:
    - JSON string with the result of the operation
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.resume_call(call_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error resuming call: {str(e)}"}, indent=2)


async def vapi_send_event(call_id: str, 
                         event_type: str, 
                         data: Optional[Dict[str, Any]] = None,
                         ctx: Context = None) -> str:
    """Send a custom event to a call.
    
    Sends an event to a call to trigger custom behaviors.
    
    Parameters:
    - call_id: ID of the call to send the event to
    - event_type: Type of event to send
    - data: Optional data payload for the event
    
    Returns:
    - JSON string with the result of the operation
    """
    vapi = _get_vapi_service()
    if not vapi:
        return json.dumps({"error": "VAPI service not properly initialized."})

    try:
        result = await vapi.send_event(call_id, event_type, data)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error sending event to call: {str(e)}"}, indent=2)


# Tool registration and initialization
_vapi_service = None


def initialize_vapi_service(api_key=None):
    """Initialize the VAPI service with API key"""
    global _vapi_service

    if api_key is None:
        api_key = os.environ.get("VAPI_API_KEY")

    if not api_key:
        logging.warning("VAPI API key not configured. Please set the VAPI_API_KEY environment variable.")
        return None

    try:
        _vapi_service = VAPIService(api_key=api_key)
        return _vapi_service
    except Exception as e:
        logging.error(f"Failed to initialize VAPI service: {str(e)}")
        return None


def _get_vapi_service():
    """Get or initialize the VAPI service"""
    global _vapi_service
    if _vapi_service is None:
        _vapi_service = initialize_vapi_service()
    return _vapi_service


def get_vapi_tools():
    """Get a dictionary of all VAPI tools for registration with MCP"""
    return {
        VAPITools.MAKE_CALL: vapi_make_call,
        VAPITools.LIST_CALLS: vapi_list_calls,
        VAPITools.GET_CALL: vapi_get_call,
        VAPITools.END_CALL: vapi_end_call,
        VAPITools.GET_RECORDINGS: vapi_get_recordings,
        VAPITools.ADD_HUMAN: vapi_add_human,
        VAPITools.PAUSE_CALL: vapi_pause_call,
        VAPITools.RESUME_CALL: vapi_resume_call,
        VAPITools.SEND_EVENT: vapi_send_event
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the VAPI module with MCP reference and API key"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_vapi_service()
    if service and service.initialized:
        logging.info("VAPI service initialized successfully")
        return True
    else:
        logging.warning("Failed to initialize VAPI service. Please ensure vapi is installed and API key is configured.")
        return False


if __name__ == "__main__":
    print("VAPI service module - use with MCP Unified Server")