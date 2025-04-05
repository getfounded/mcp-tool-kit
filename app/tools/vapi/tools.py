#!/usr/bin/env python3
"""
VAPI tools implementation using the decorator pattern.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.vapi.service import VAPIService

# Call Management Tools


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Make a phone call using VAPI"
)
async def vapi_make_call(
    self,
    to: str,
    assistant_id: str,
    from_number: Optional[str] = None,
    assistant_options: Optional[Dict[str, Any]] = None,
    server_url: Optional[str] = None
) -> str:
    """
    Make a phone call using VAPI.

    Initiates a call to the specified phone number using a VAPI assistant.

    Args:
        to: Phone number to call (E.164 format recommended, e.g., +12125551234)
        assistant_id: ID of the assistant to use for the call
        from_number: Optional phone number to display as caller ID
        assistant_options: Optional dictionary of assistant configuration options
        server_url: Optional server URL for call events

    Returns:
        JSON string with call details including call ID, status, and timestamps
    """
    result = await self.make_call(to, assistant_id, from_number, assistant_options, server_url)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="List phone calls made through VAPI"
)
async def vapi_list_calls(
    self,
    limit: int = 10,
    before: Optional[str] = None,
    after: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    List phone calls made through VAPI.

    Retrieves a list of calls with optional filtering.

    Args:
        limit: Maximum number of calls to return (default: 10)
        before: Return calls created before this cursor
        after: Return calls created after this cursor
        status: Filter calls by status (e.g., 'queued', 'ringing', 'in-progress', 'completed')

    Returns:
        JSON string with list of calls and pagination details
    """
    result = await self.list_calls(limit, before, after, status)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Get detailed information about a specific call"
)
async def vapi_get_call(self, call_id: str) -> str:
    """
    Get detailed information about a specific call.

    Retrieves complete information about a call by its ID.

    Args:
        call_id: ID of the call to retrieve

    Returns:
        JSON string with detailed call information including status, timestamps, and metadata
    """
    result = await self.get_call(call_id)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="End an ongoing call"
)
async def vapi_end_call(self, call_id: str) -> str:
    """
    End an ongoing call.

    Terminates an active call by its ID.

    Args:
        call_id: ID of the call to end

    Returns:
        JSON string with the result of the operation
    """
    result = await self.end_call(call_id)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Get recordings for a specific call"
)
async def vapi_get_recordings(self, call_id: str) -> str:
    """
    Get recordings for a specific call.

    Retrieves a list of recordings associated with a call.

    Args:
        call_id: ID of the call to get recordings for

    Returns:
        JSON string with recording metadata including URLs, durations, and timestamps
    """
    result = await self.get_recordings(call_id)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Add a human participant to a call"
)
async def vapi_add_human(
    self,
    call_id: str,
    phone_number: str = None,
    transfer: bool = False
) -> str:
    """
    Add a human participant to a call.

    Adds a human to an ongoing call, optionally transferring control.

    Args:
        call_id: ID of the call to add the human to
        phone_number: Phone number of the human to add
        transfer: Whether to transfer the call to the human (default: False)

    Returns:
        JSON string with the result of the operation
    """
    result = await self.add_human(call_id, phone_number, transfer)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Pause an ongoing call"
)
async def vapi_pause_call(self, call_id: str) -> str:
    """
    Pause an ongoing call.

    Temporarily pauses an active call.

    Args:
        call_id: ID of the call to pause

    Returns:
        JSON string with the result of the operation
    """
    result = await self.pause_call(call_id)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Resume a paused call"
)
async def vapi_resume_call(self, call_id: str) -> str:
    """
    Resume a paused call.

    Continues a previously paused call.

    Args:
        call_id: ID of the call to resume

    Returns:
        JSON string with the result of the operation
    """
    result = await self.resume_call(call_id)
    return json.dumps(result, indent=2)


@register_tool(
    category="voice_communication",
    service_class=VAPIService,
    description="Send a custom event to a call"
)
async def vapi_send_event(
    self,
    call_id: str,
    event_type: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Send a custom event to a call.

    Sends an event to a call to trigger custom behaviors.

    Args:
        call_id: ID of the call to send the event to
        event_type: Type of event to send
        data: Optional data payload for the event

    Returns:
        JSON string with the result of the operation
    """
    result = await self.send_event(call_id, event_type, data)
    return json.dumps(result, indent=2)
