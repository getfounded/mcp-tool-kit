# VAPI API Tool for MCP

A comprehensive tool for integrating with the VAPI API, enabling Claude to make phone calls, read call logs, manage call recordings, and interact with ongoing calls.

## Overview

VAPI is a powerful API for making and managing AI-powered voice calls. This integration allows Claude to:

- Initiate outbound calls with AI assistants
- List and retrieve details about calls
- End, pause, and resume active calls
- Access call recordings
- Add human participants to calls
- Send custom events to calls

## Installation

1. Add the `vapi.py` file to your `tools` directory in the MCP Unified Server
2. Add `vapi` to your `requirements.txt` file
3. Update the `mcp_unified_server.py` file to import and register the VAPI module
4. Add VAPI API credentials to your `.env` file

## Configuration

The VAPI API tool requires the following environment variable:

```env
# VAPI API Credentials
VAPI_API_KEY=your_vapi_api_key_here
```

## Adding to mcp_unified_server.py

Add the following code to your `mcp_unified_server.py` file:

```python
# Initialize VAPI tools
try:
    from app.tools.vapi import get_vapi_tools, set_external_mcp, initialize_vapi_service

    # Pass our MCP instance to the VAPI module
    set_external_mcp(mcp)

    # Initialize VAPI tools
    if initialize_vapi_service():
        # Register VAPI tools
        vapi_tools = get_vapi_tools()
        for tool_name, tool_func in vapi_tools.items():
            # Register each VAPI tool with the main MCP instance
            tool_name_str = tool_name if isinstance(tool_name, str) else tool_name.value
            mcp.tool(name=tool_name_str)(tool_func)

        # Add VAPI dependencies to MCP dependencies
        mcp.dependencies.extend(["vapi"])

        logging.info("VAPI tools registered successfully.")
    else:
        logging.warning("Failed to initialize VAPI tools.")
except ImportError as e:
    logging.warning(f"Could not load VAPI tools: {e}")
```

## Available Tools

### vapi_make_call

Initiates a call to a phone number using a VAPI assistant.

```python
vapi_make_call(
    to: str,                                    # Phone number to call (E.164 format, e.g., +12125551234)
    assistant_id: str,                          # ID of the assistant to use for the call
    from_number: Optional[str] = None,          # Phone number to display as caller ID
    assistant_options: Optional[Dict] = None,   # Assistant configuration options
    server_url: Optional[str] = None            # Server URL for call events
)
```

### vapi_list_calls

Lists calls with optional filtering.

```python
vapi_list_calls(
    limit: int = 10,                           # Maximum number of calls to return
    before: Optional[str] = None,              # Return calls created before this cursor
    after: Optional[str] = None,               # Return calls created after this cursor
    status: Optional[str] = None               # Filter by call status
)
```

### vapi_get_call

Gets detailed information about a specific call.

```python
vapi_get_call(
    call_id: str                               # ID of the call to retrieve
)
```

### vapi_end_call

Terminates an active call.

```python
vapi_end_call(
    call_id: str                               # ID of the call to end
)
```

### vapi_get_recordings

Retrieves recordings associated with a call.

```python
vapi_get_recordings(
    call_id: str                               # ID of the call to get recordings for
)
```

### vapi_add_human

Adds a human participant to an ongoing call.

```python
vapi_add_human(
    call_id: str,                              # ID of the call to add the human to
    phone_number: str = None,                  # Phone number of the human to add
    transfer: bool = False                     # Whether to transfer the call to the human
)
```

### vapi_pause_call

Temporarily pauses an active call.

```python
vapi_pause_call(
    call_id: str                               # ID of the call to pause
)
```

### vapi_resume_call

Continues a previously paused call.

```python
vapi_resume_call(
    call_id: str                               # ID of the call to resume
)
```

### vapi_send_event

Sends a custom event to a call.

```python
vapi_send_event(
    call_id: str,                              # ID of the call to send the event to
    event_type: str,                           # Type of event to send
    data: Optional[Dict] = None                # Optional data payload for the event
)
```

## Usage Examples

### Initiating a Call

```python
# Make a call to a phone number using a VAPI assistant
response = await mcp.call_tool("vapi_make_call", {
    "to": "+12125551234",
    "assistant_id": "asst_123456789",
    "from_number": "+18005551000"  # Optional caller ID
})

# Parse the response to get the call ID
call_info = json.loads(response)
call_id = call_info.get("id")
```

### Checking Call Status

```python
# Get details about a specific call
response = await mcp.call_tool("vapi_get_call", {
    "call_id": "call_123456789"
})

# Parse the response to check call status
call_info = json.loads(response)
call_status = call_info.get("status")
```

### Ending a Call

```python
# End an active call
response = await mcp.call_tool("vapi_end_call", {
    "call_id": "call_123456789"
})
```

### Getting Call Recordings

```python
# Get recordings for a completed call
response = await mcp.call_tool("vapi_get_recordings", {
    "call_id": "call_123456789"
})

# Parse the response to get recording URLs
recordings = json.loads(response)
for recording in recordings.get("data", []):
    recording_url = recording.get("url")
    recording_duration = recording.get("duration")
```

### Inviting a Human to Join a Call

```python
# Add a human participant to an ongoing call
response = await mcp.call_tool("vapi_add_human", {
    "call_id": "call_123456789",
    "phone_number": "+13105551234"
})
```

## Working with Claude

### Example Prompts for Claude

Here are some example prompts to help Claude use the VAPI tools effectively:

1. **Making an Outbound Call**:
   ```
   Please make a call to +1 (212) 555-1234 using the VAPI assistant "asst_123456789". Let me know when the call has been initiated.
   ```

2. **Checking Call Logs**:
   ```
   Please list the most recent 5 calls made through the VAPI system and tell me their status.
   ```

3. **Managing an Ongoing Call**:
   ```
   The current call (call_123456789) needs to be paused while I gather some information. Please pause it and let me know when I can resume it.
   ```

4. **Getting Call Recordings**:
   ```
   Can you get the recordings from my last call with John (call_123456789) and provide the URLs?
   ```

## Error Handling

The VAPI tools include robust error handling:

- If the VAPI API key is not configured, the tools will return appropriate error messages
- Invalid parameters are caught and reported in a user-friendly format
- API errors from VAPI are captured and returned with context

## Dependencies

This tool requires the following Python packages:
- `vapi`: The official VAPI Python SDK

## Technical Notes

- All phone numbers should use E.164 format (+12125551234) for best compatibility
- Assistant IDs must be valid VAPI assistant IDs
- Call IDs are returned from the `vapi_make_call` tool and must be used for subsequent operations
- Some operations (e.g., ending calls) can only be performed on active calls
- Recordings are only available for completed calls