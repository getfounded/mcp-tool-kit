#!/usr/bin/env python3
"""
Outlook API tools for MCP toolkit.
"""
import json
from typing import Dict, List, Any, Optional

from app.tools.base.registry import register_tool
from app.tools.outlook.service import OutlookService


@register_tool(
    name="outlook_authenticate",
    category="outlook",
    service_class=OutlookService,
    description="Authenticate with Microsoft Outlook API"
)
async def outlook_authenticate(self, method: str = "client_credentials") -> str:
    """
    Authenticate with Microsoft Outlook API

    Parameters:
    - method: Authentication method to use ('client_credentials' or 'device_code')

    Returns:
    JSON string with authentication result
    """
    try:
        if method == "client_credentials":
            result = await self.auth_handler.authenticate_client_credentials()
        elif method == "device_code":
            result = await self.auth_handler.authenticate_device_code()
        else:
            return json.dumps({"error": f"Invalid authentication method: {method}"}, indent=2)

        # Simplify the response to avoid exposing tokens
        if "access_token" in result:
            return json.dumps({
                "status": "authenticated",
                "expires_at": self.auth_handler.token_expires_at,
                "token_type": "Bearer"
            }, indent=2)
        else:
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Authentication error: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_get_emails",
    category="outlook",
    service_class=OutlookService,
    description="Get emails from a specified Outlook folder"
)
async def outlook_get_emails(self, folder: str = "inbox", top: int = 10, skip: int = 0, include_body: bool = True) -> str:
    """
    Get emails from a specified Outlook folder

    Parameters:
    - folder: The folder to get emails from (inbox, drafts, sentitems, etc.)
    - top: Maximum number of emails to return
    - skip: Number of emails to skip (for pagination)
    - include_body: Whether to include email body in the results

    Returns:
    JSON string with list of emails
    """
    try:
        result = await self.get_emails(folder, top, skip, include_body)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving emails: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_send_email",
    category="outlook",
    service_class=OutlookService,
    description="Send an email using Outlook"
)
async def outlook_send_email(self, to_recipients: List[str], subject: str, body: str,
                             body_type: str = "HTML", cc_recipients: List[str] = None,
                             bcc_recipients: List[str] = None) -> str:
    """
    Send an email using Outlook

    Parameters:
    - to_recipients: List of email addresses to send to
    - subject: Email subject
    - body: Email body content
    - body_type: Content type (HTML or Text)
    - cc_recipients: List of email addresses to CC
    - bcc_recipients: List of email addresses to BCC

    Returns:
    JSON string with send result
    """
    try:
        result = await self.send_email(to_recipients, subject, body, body_type, cc_recipients, bcc_recipients)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error sending email: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_search_emails",
    category="outlook",
    service_class=OutlookService,
    description="Search for emails in a specified Outlook folder"
)
async def outlook_search_emails(self, query: str, folder: str = "inbox", top: int = 10,
                                skip: int = 0, include_body: bool = True) -> str:
    """
    Search for emails in a specified Outlook folder

    Parameters:
    - query: Search query string
    - folder: The folder to search in (inbox, drafts, sentitems, etc.)
    - top: Maximum number of emails to return
    - skip: Number of emails to skip (for pagination)
    - include_body: Whether to include email body in the results

    Returns:
    JSON string with search results
    """
    try:
        result = await self.search_emails(query, folder, top, skip, include_body)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error searching emails: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_get_calendar_events",
    category="outlook",
    service_class=OutlookService,
    description="Get calendar events from Outlook"
)
async def outlook_get_calendar_events(self, start_datetime: str = None, end_datetime: str = None,
                                      top: int = 10, skip: int = 0, timezone: str = None) -> str:
    """
    Get calendar events from Outlook

    Parameters:
    - start_datetime: Start date/time in ISO format (default: now)
    - end_datetime: End date/time in ISO format (default: 7 days from now)
    - top: Maximum number of events to return
    - skip: Number of events to skip (for pagination)
    - timezone: Timezone for the events (e.g., 'UTC', 'America/New_York')

    Returns:
    JSON string with list of calendar events
    """
    try:
        result = await self.get_calendar_events(start_datetime, end_datetime, top, skip, timezone)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving calendar events: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_create_calendar_event",
    category="outlook",
    service_class=OutlookService,
    description="Create a calendar event in Outlook"
)
async def outlook_create_calendar_event(self, subject: str, start_datetime: str, end_datetime: str,
                                        timezone: str = "UTC", body: str = None,
                                        body_type: str = "HTML", location: str = None,
                                        attendees: List[Dict] = None, is_online_meeting: bool = False) -> str:
    """
    Create a calendar event in Outlook

    Parameters:
    - subject: Event subject
    - start_datetime: Start date/time in ISO format
    - end_datetime: End date/time in ISO format
    - timezone: Timezone for the event (e.g., 'UTC', 'America/New_York')
    - body: Event body/description
    - body_type: Content type (HTML or Text)
    - location: Event location
    - attendees: List of attendees with their email and optional name and type
    - is_online_meeting: Whether to create an online Teams meeting

    Returns:
    JSON string with event creation result
    """
    try:
        result = await self.create_calendar_event(
            subject, start_datetime, end_datetime, timezone,
            body, body_type, location, attendees, is_online_meeting
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating calendar event: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_get_contacts",
    category="outlook",
    service_class=OutlookService,
    description="Get contacts from Outlook"
)
async def outlook_get_contacts(self, top: int = 10, skip: int = 0, search: str = None) -> str:
    """
    Get contacts from Outlook

    Parameters:
    - top: Maximum number of contacts to return
    - skip: Number of contacts to skip (for pagination)
    - search: Optional search string to filter contacts

    Returns:
    JSON string with list of contacts
    """
    try:
        result = await self.get_contacts(top, skip, search)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving contacts: {str(e)}"}, indent=2)


@register_tool(
    name="outlook_create_draft",
    category="outlook",
    service_class=OutlookService,
    description="Create a draft email in Outlook"
)
async def outlook_create_draft(self, to_recipients: List[str], subject: str, body: str,
                               body_type: str = "HTML", cc_recipients: List[str] = None,
                               bcc_recipients: List[str] = None) -> str:
    """
    Create a draft email in Outlook

    Parameters:
    - to_recipients: List of email addresses to send to
    - subject: Email subject
    - body: Email body content
    - body_type: Content type (HTML or Text)
    - cc_recipients: List of email addresses to CC
    - bcc_recipients: List of email addresses to BCC

    Returns:
    JSON string with draft creation result
    """
    try:
        result = await self.create_draft(to_recipients, subject, body, body_type, cc_recipients, bcc_recipients)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating draft: {str(e)}"}, indent=2)
