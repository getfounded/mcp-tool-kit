#!/usr/bin/env python3
import os
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import msal
import httpx

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Outlook tools MCP reference set")


class OutlookTools(str, Enum):
    """Enum of Outlook tool names"""
    GET_EMAILS = "outlook_get_emails"
    SEND_EMAIL = "outlook_send_email"
    SEARCH_EMAILS = "outlook_search_emails"
    GET_CALENDAR_EVENTS = "outlook_get_calendar_events"
    CREATE_CALENDAR_EVENT = "outlook_create_calendar_event"
    GET_CONTACTS = "outlook_get_contacts"
    CREATE_DRAFT = "outlook_create_draft"


class OutlookService:
    """Service to handle Microsoft Outlook API operations using Microsoft Graph API"""

    def __init__(self, client_id, client_secret, tenant_id, scopes=None):
        """Initialize the Outlook service with Microsoft credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

        # Default scopes for Outlook operations
        self.scopes = scopes or [
            'https://graph.microsoft.com/Mail.Read',
            'https://graph.microsoft.com/Mail.ReadWrite',
            'https://graph.microsoft.com/Mail.Send',
            'https://graph.microsoft.com/Calendars.Read',
            'https://graph.microsoft.com/Calendars.ReadWrite',
            'https://graph.microsoft.com/Contacts.Read',
            'https://graph.microsoft.com/Contacts.ReadWrite'
        ]

        # Initialize token cache
        self.token = None
        self.token_expires = None

        # Initialize app
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )

    async def _ensure_token(self):
        """Ensure we have a valid access token"""
        # Check if token is still valid
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return

        # Acquire token using client credentials flow
        result = self.app.acquire_token_for_client(scopes=self.scopes)

        if "access_token" in result:
            self.token = result["access_token"]
            # Set expiration time (usually 1 hour, but subtract 5 minutes for safety)
            expires_in = result.get("expires_in", 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in - 300)
        else:
            error = result.get("error")
            error_description = result.get("error_description")
            raise Exception(
                f"Failed to acquire token: {error} - {error_description}")

    async def _make_request(self, method, endpoint, params=None, data=None, json_data=None):
        """Make an authenticated request to the Microsoft Graph API"""
        await self._ensure_token()

        base_url = "https://graph.microsoft.com/v1.0"
        url = f"{base_url}/{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            if method.lower() == "get":
                response = await client.get(url, headers=headers, params=params)
            elif method.lower() == "post":
                response = await client.post(url, headers=headers, params=params, data=data, json=json_data)
            elif method.lower() == "patch":
                response = await client.patch(url, headers=headers, params=params, data=data, json=json_data)
            elif method.lower() == "delete":
                response = await client.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code >= 400:
                raise Exception(
                    f"Microsoft Graph API error: {response.status_code} - {response.text}")

            if response.status_code != 204:  # No content
                return response.json()
            return None

    async def get_emails(self, folder="inbox", top=10, skip=0, include_body=True):
        """Get emails from a specified folder"""
        # Determine which properties to request
        select = "id,subject,receivedDateTime,from,toRecipients,ccRecipients,isRead"
        if include_body:
            select += ",body"

        params = {
            "$top": top,
            "$skip": skip,
            "$select": select,
            "$orderby": "receivedDateTime DESC"
        }

        endpoint = f"me/mailFolders/{folder}/messages"
        result = await self._make_request("get", endpoint, params=params)

        # Format the result for better readability
        emails = []
        for msg in result.get("value", []):
            email = {
                "id": msg.get("id"),
                "subject": msg.get("subject", "(No subject)"),
                "received": msg.get("receivedDateTime"),
                "is_read": msg.get("isRead", False),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "from_name": msg.get("from", {}).get("emailAddress", {}).get("name", ""),
                "to": [r.get("emailAddress", {}).get("address") for r in msg.get("toRecipients", [])],
                "cc": [r.get("emailAddress", {}).get("address") for r in msg.get("ccRecipients", [])]
            }

            if include_body and "body" in msg:
                email["body"] = msg.get("body", {}).get("content", "")
                email["body_type"] = msg.get(
                    "body", {}).get("contentType", "text")

            emails.append(email)

        return emails

    async def send_email(self, to_recipients, subject, body, body_type="HTML", cc_recipients=None, bcc_recipients=None, attachments=None):
        """Send an email using Microsoft Graph API"""
        to_list = [{"emailAddress": {"address": email}}
                   for email in to_recipients]

        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": body_type,
                    "content": body
                },
                "toRecipients": to_list
            }
        }

        # Add CC recipients if specified
        if cc_recipients:
            cc_list = [{"emailAddress": {"address": email}}
                       for email in cc_recipients]
            email_data["message"]["ccRecipients"] = cc_list

        # Add BCC recipients if specified
        if bcc_recipients:
            bcc_list = [{"emailAddress": {"address": email}}
                        for email in bcc_recipients]
            email_data["message"]["bccRecipients"] = bcc_list

        # Add attachments if specified
        if attachments:
            attach_list = []
            for attachment in attachments:
                # Handle file attachments with base64 encoding
                if "path" in attachment:
                    with open(attachment["path"], "rb") as file:
                        content = file.read()
                        content_b64 = base64.b64encode(content).decode("utf-8")

                    attach_list.append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": attachment.get("name", os.path.basename(attachment["path"])),
                        "contentType": attachment.get("content_type", "application/octet-stream"),
                        "contentBytes": content_b64
                    })
                # Handle inline attachments already in base64
                elif "content_b64" in attachment:
                    attach_list.append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": attachment.get("name", "attachment"),
                        "contentType": attachment.get("content_type", "application/octet-stream"),
                        "contentBytes": attachment["content_b64"]
                    })

            if attach_list:
                email_data["message"]["attachments"] = attach_list

        endpoint = "me/sendMail"
        result = await self._make_request("post", endpoint, json_data=email_data)

        return {
            "status": "sent",
            "to": to_recipients,
            "subject": subject
        }

    async def create_draft(self, to_recipients, subject, body, body_type="HTML", cc_recipients=None, bcc_recipients=None):
        """Create a draft email using Microsoft Graph API"""
        to_list = [{"emailAddress": {"address": email}}
                   for email in to_recipients]

        draft_data = {
            "subject": subject,
            "body": {
                "contentType": body_type,
                "content": body
            },
            "toRecipients": to_list
        }

        # Add CC recipients if specified
        if cc_recipients:
            cc_list = [{"emailAddress": {"address": email}}
                       for email in cc_recipients]
            draft_data["ccRecipients"] = cc_list

        # Add BCC recipients if specified
        if bcc_recipients:
            bcc_list = [{"emailAddress": {"address": email}}
                        for email in bcc_recipients]
            draft_data["bccRecipients"] = bcc_list

        endpoint = "me/messages"
        result = await self._make_request("post", endpoint, json_data=draft_data)

        return {
            "status": "draft_created",
            "id": result.get("id"),
            "to": to_recipients,
            "subject": subject
        }

    async def search_emails(self, query, folder="inbox", top=10, skip=0, include_body=True):
        """Search emails in a specified folder using a query string"""
        # Determine which properties to request
        select = "id,subject,receivedDateTime,from,toRecipients,ccRecipients,isRead"
        if include_body:
            select += ",body"

        params = {
            # Quoted to handle spaces and special chars
            "$search": f'"{query}"',
            "$top": top,
            "$skip": skip,
            "$select": select,
            "$orderby": "receivedDateTime DESC"
        }

        endpoint = f"me/mailFolders/{folder}/messages"
        result = await self._make_request("get", endpoint, params=params)

        # Format the result for better readability (same as get_emails)
        emails = []
        for msg in result.get("value", []):
            email = {
                "id": msg.get("id"),
                "subject": msg.get("subject", "(No subject)"),
                "received": msg.get("receivedDateTime"),
                "is_read": msg.get("isRead", False),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                "from_name": msg.get("from", {}).get("emailAddress", {}).get("name", ""),
                "to": [r.get("emailAddress", {}).get("address") for r in msg.get("toRecipients", [])],
                "cc": [r.get("emailAddress", {}).get("address") for r in msg.get("ccRecipients", [])]
            }

            if include_body and "body" in msg:
                email["body"] = msg.get("body", {}).get("content", "")
                email["body_type"] = msg.get(
                    "body", {}).get("contentType", "text")

            emails.append(email)

        return emails

    async def get_calendar_events(self, start_datetime=None, end_datetime=None, top=10, skip=0, timezone=None):
        """Get calendar events within a specified time range"""
        # Default to events from today to a week from now
        if not start_datetime:
            start_datetime = datetime.now().isoformat()
        if not end_datetime:
            end_datetime = (datetime.now() + timedelta(days=7)).isoformat()

        params = {
            "$top": top,
            "$skip": skip,
            "$orderby": "start/dateTime ASC",
            "$select": "id,subject,organizer,attendees,start,end,location,bodyPreview,isOnlineMeeting,onlineMeetingUrl"
        }

        # Use prefer header for timezone if specified
        headers = {}
        if timezone:
            headers["Prefer"] = f'outlook.timezone="{timezone}"'

        # Filter by time range
        filter_query = f"start/dateTime ge '{start_datetime}' and end/dateTime le '{end_datetime}'"
        params["$filter"] = filter_query

        endpoint = "me/calendar/events"
        result = await self._make_request("get", endpoint, params=params)

        # Format the result for better readability
        events = []
        for event in result.get("value", []):
            formatted_event = {
                "id": event.get("id"),
                "subject": event.get("subject", "(No subject)"),
                "start": event.get("start", {}).get("dateTime"),
                "start_timezone": event.get("start", {}).get("timeZone"),
                "end": event.get("end", {}).get("dateTime"),
                "end_timezone": event.get("end", {}).get("timeZone"),
                "organizer": event.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown"),
                "organizer_name": event.get("organizer", {}).get("emailAddress", {}).get("name", ""),
                "location": event.get("location", {}).get("displayName", ""),
                "is_online_meeting": event.get("isOnlineMeeting", False),
                "online_meeting_url": event.get("onlineMeetingUrl", ""),
                "preview": event.get("bodyPreview", "")
            }

            # Add attendees if present
            if "attendees" in event:
                formatted_event["attendees"] = [
                    {
                        "email": attendee.get("emailAddress", {}).get("address", ""),
                        "name": attendee.get("emailAddress", {}).get("name", ""),
                        "type": attendee.get("type", "")
                    }
                    for attendee in event.get("attendees", [])
                ]

            events.append(formatted_event)

        return events

    async def create_calendar_event(self, subject, start_datetime, end_datetime, timezone="UTC",
                                    body=None, body_type="HTML", location=None, attendees=None,
                                    is_online_meeting=False):
        """Create a calendar event using Microsoft Graph API"""
        event_data = {
            "subject": subject,
            "start": {
                "dateTime": start_datetime,
                "timeZone": timezone
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": timezone
            }
        }

        # Add body if specified
        if body:
            event_data["body"] = {
                "contentType": body_type,
                "content": body
            }

        # Add location if specified
        if location:
            event_data["location"] = {
                "displayName": location
            }

        # Add attendees if specified
        if attendees:
            event_data["attendees"] = [
                {
                    "emailAddress": {
                        "address": attendee["email"],
                        "name": attendee.get("name", "")
                    },
                    "type": attendee.get("type", "required")
                }
                for attendee in attendees
            ]

        # Set online meeting if requested
        if is_online_meeting:
            event_data["isOnlineMeeting"] = True
            event_data["onlineMeetingProvider"] = "teamsForBusiness"

        endpoint = "me/calendar/events"
        result = await self._make_request("post", endpoint, json_data=event_data)

        return {
            "status": "created",
            "id": result.get("id"),
            "subject": subject,
            "start": result.get("start", {}).get("dateTime"),
            "end": result.get("end", {}).get("dateTime"),
            "online_meeting_url": result.get("onlineMeetingUrl", "") if is_online_meeting else ""
        }

    async def get_contacts(self, top=10, skip=0, search=None):
        """Get contacts from the user's contact list"""
        params = {
            "$top": top,
            "$skip": skip,
            "$select": "id,displayName,emailAddresses,businessPhones,mobilePhone,jobTitle,companyName"
        }

        # Add search filter if specified
        if search:
            params["$filter"] = f"startswith(displayName,'{search}') or startswith(emailAddresses/any(email:email/address),'{search}')"

        endpoint = "me/contacts"
        result = await self._make_request("get", endpoint, params=params)

        # Format the result for better readability
        contacts = []
        for contact in result.get("value", []):
            formatted_contact = {
                "id": contact.get("id"),
                "display_name": contact.get("displayName", ""),
                "job_title": contact.get("jobTitle", ""),
                "company": contact.get("companyName", ""),
                "emails": [email.get("address") for email in contact.get("emailAddresses", [])],
                "business_phones": contact.get("businessPhones", []),
                "mobile_phone": contact.get("mobilePhone", "")
            }

            contacts.append(formatted_contact)

        return contacts

# Tool function definitions to be registered with MCP


async def outlook_get_emails(folder="inbox", top=10, skip=0, include_body=True, ctx: Context = None) -> str:
    """Get emails from a specified Outlook folder

    Parameters:
    - folder: The folder to get emails from (inbox, drafts, sentitems, etc.)
    - top: Maximum number of emails to return
    - skip: Number of emails to skip (for pagination)
    - include_body: Whether to include email body in the results
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        emails = await outlook.get_emails(folder, top, skip, include_body)
        return json.dumps(emails, indent=2)
    except Exception as e:
        return f"Error retrieving emails: {str(e)}"


async def outlook_send_email(to_recipients: List[str], subject: str, body: str,
                             body_type: str = "HTML", cc_recipients: List[str] = None,
                             bcc_recipients: List[str] = None, ctx: Context = None) -> str:
    """Send an email using Outlook

    Parameters:
    - to_recipients: List of email addresses to send to
    - subject: Email subject
    - body: Email body content
    - body_type: Content type (HTML or Text)
    - cc_recipients: List of email addresses to CC
    - bcc_recipients: List of email addresses to BCC
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        result = await outlook.send_email(to_recipients, subject, body, body_type, cc_recipients, bcc_recipients)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sending email: {str(e)}"


async def outlook_create_draft(to_recipients: List[str], subject: str, body: str,
                               body_type: str = "HTML", cc_recipients: List[str] = None,
                               bcc_recipients: List[str] = None, ctx: Context = None) -> str:
    """Create a draft email in Outlook

    Parameters:
    - to_recipients: List of email addresses to send to
    - subject: Email subject
    - body: Email body content
    - body_type: Content type (HTML or Text)
    - cc_recipients: List of email addresses to CC
    - bcc_recipients: List of email addresses to BCC
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        result = await outlook.create_draft(to_recipients, subject, body, body_type, cc_recipients, bcc_recipients)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating draft: {str(e)}"


async def outlook_search_emails(query: str, folder: str = "inbox", top: int = 10,
                                skip: int = 0, include_body: bool = True, ctx: Context = None) -> str:
    """Search for emails in a specified Outlook folder

    Parameters:
    - query: Search query string
    - folder: The folder to search in (inbox, drafts, sentitems, etc.)
    - top: Maximum number of emails to return
    - skip: Number of emails to skip (for pagination)
    - include_body: Whether to include email body in the results
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        emails = await outlook.search_emails(query, folder, top, skip, include_body)
        return json.dumps(emails, indent=2)
    except Exception as e:
        return f"Error searching emails: {str(e)}"


async def outlook_get_calendar_events(start_datetime: str = None, end_datetime: str = None,
                                      top: int = 10, skip: int = 0, timezone: str = None,
                                      ctx: Context = None) -> str:
    """Get calendar events from Outlook

    Parameters:
    - start_datetime: Start date/time in ISO format (default: now)
    - end_datetime: End date/time in ISO format (default: 7 days from now)
    - top: Maximum number of events to return
    - skip: Number of events to skip (for pagination)
    - timezone: Timezone for the events (e.g., 'UTC', 'America/New_York')
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        events = await outlook.get_calendar_events(start_datetime, end_datetime, top, skip, timezone)
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error retrieving calendar events: {str(e)}"


async def outlook_create_calendar_event(subject: str, start_datetime: str, end_datetime: str,
                                        timezone: str = "UTC", body: str = None,
                                        body_type: str = "HTML", location: str = None,
                                        attendees: List[Dict] = None, is_online_meeting: bool = False,
                                        ctx: Context = None) -> str:
    """Create a calendar event in Outlook

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
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        event = await outlook.create_calendar_event(
            subject, start_datetime, end_datetime, timezone,
            body, body_type, location, attendees, is_online_meeting
        )
        return json.dumps(event, indent=2)
    except Exception as e:
        return f"Error creating calendar event: {str(e)}"


async def outlook_get_contacts(top: int = 10, skip: int = 0, search: str = None, ctx: Context = None) -> str:
    """Get contacts from Outlook

    Parameters:
    - top: Maximum number of contacts to return
    - skip: Number of contacts to skip (for pagination)
    - search: Optional search string to filter contacts
    """
    outlook = _get_outlook_service()
    if not outlook:
        return "Outlook API is not configured. Please set the required environment variables."

    try:
        contacts = await outlook.get_contacts(top, skip, search)
        return json.dumps(contacts, indent=2)
    except Exception as e:
        return f"Error retrieving contacts: {str(e)}"

# Tool registration and initialization
_outlook_service = None


def initialize_outlook_service(client_id=None, client_secret=None, tenant_id=None, scopes=None):
    """Initialize the Outlook service with Microsoft credentials"""
    global _outlook_service

    # Use environment variables as fallback
    client_id = client_id or os.environ.get("MS_CLIENT_ID")
    client_secret = client_secret or os.environ.get("MS_CLIENT_SECRET")
    tenant_id = tenant_id or os.environ.get("MS_TENANT_ID")

    if not client_id or not client_secret or not tenant_id:
        logging.warning(
            "Microsoft Graph API credentials not configured. Please set MS_CLIENT_ID, MS_CLIENT_SECRET, and MS_TENANT_ID environment variables.")
        return None

    _outlook_service = OutlookService(
        client_id, client_secret, tenant_id, scopes)
    return _outlook_service


def _get_outlook_service():
    """Get or initialize the Outlook service"""
    global _outlook_service
    if _outlook_service is None:
        _outlook_service = initialize_outlook_service()
    return _outlook_service


def get_outlook_tools():
    """Get a dictionary of all Outlook tools for registration with MCP"""
    return {
        OutlookTools.GET_EMAILS: outlook_get_emails,
        OutlookTools.SEND_EMAIL: outlook_send_email,
        OutlookTools.SEARCH_EMAILS: outlook_search_emails,
        OutlookTools.GET_CALENDAR_EVENTS: outlook_get_calendar_events,
        OutlookTools.CREATE_CALENDAR_EVENT: outlook_create_calendar_event,
        OutlookTools.GET_CONTACTS: outlook_get_contacts,
        OutlookTools.CREATE_DRAFT: outlook_create_draft
    }

# This function will be called by the unified server to initialize the module


def initialize(mcp=None):
    """Initialize the Outlook module with MCP reference and credentials"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_outlook_service()
    if service:
        logging.info("Outlook API service initialized successfully")
    else:
        logging.warning("Failed to initialize Outlook API service")

    return service is not None
