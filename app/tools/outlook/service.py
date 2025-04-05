#!/usr/bin/env python3
"""
Outlook API Service for MCP toolkit.
"""
import os
import json
import logging
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase
from app.tools.utils.auth import create_auth_handler, MicrosoftAuth


class OutlookService(ToolServiceBase):
    """Service for Microsoft Outlook API operations using Microsoft Graph API"""

    def __init__(self):
        """Initialize the Outlook service"""
        super().__init__()
        self.auth_handler = None
        self.base_url = "https://graph.microsoft.com/v1.0"

    def initialize(self) -> bool:
        """
        Initialize the service with credentials from environment variables.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Get credentials from environment (using the same vars as SharePoint)
            self.client_id = self.get_env_var("MS_GRAPH_CLIENT_ID")
            self.client_secret = self.get_env_var("MS_GRAPH_CLIENT_SECRET")
            self.tenant_id = self.get_env_var("MS_GRAPH_TENANT_ID")

            if not (self.client_id and self.client_secret and self.tenant_id):
                self.logger.warning("Microsoft Graph API credentials not configured properly. "
                                    "Set MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET, and MS_GRAPH_TENANT_ID environment variables.")
                return False

            # Default scopes for Outlook operations
            self.scopes = [
                'https://graph.microsoft.com/Mail.Read',
                'https://graph.microsoft.com/Mail.ReadWrite',
                'https://graph.microsoft.com/Mail.Send',
                'https://graph.microsoft.com/Calendars.Read',
                'https://graph.microsoft.com/Calendars.ReadWrite',
                'https://graph.microsoft.com/Contacts.Read',
                'https://graph.microsoft.com/Contacts.ReadWrite'
            ]

            # Create rate limiter - Microsoft has various limits
            # Setting a conservative default of 600 calls per minute
            # 600 calls per minute
            self.create_rate_limiter("outlook_api", 600, 60)

            # Create auth handler
            self.auth_handler = create_auth_handler(
                service_name="outlook",
                auth_type="microsoft",
                client_id=self.client_id,
                client_secret=self.client_secret,
                tenant_id=self.tenant_id,
                scopes=self.scopes,
                client_id_env="MS_GRAPH_CLIENT_ID",
                client_secret_env="MS_GRAPH_CLIENT_SECRET",
                tenant_id_env="MS_GRAPH_TENANT_ID"
            )

            self.initialized = True
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Outlook service: {str(e)}")
            return False

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        self._is_initialized()

        if not self.auth_handler.is_authenticated():
            # Use client credentials flow since we're using an app context
            auth_result = await self.auth_handler.authenticate_client_credentials()
            if "error" in auth_result:
                raise ValueError(
                    f"Authentication error: {auth_result['error']}")

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                            data: Optional[Dict] = None, json_data: Optional[Dict] = None,
                            headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Microsoft Graph API"""
        # Ensure authentication
        await self._ensure_authenticated()

        # Apply rate limiting
        self.apply_rate_limit("outlook_api", wait=True)

        # Prepare URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Prepare headers
        request_headers = {
            "Content-Type": "application/json"
        }

        # Add auth headers
        request_headers.update(self.auth_handler.get_auth_headers())

        # Add custom headers if provided
        if headers:
            request_headers.update(headers)

        import requests
        # Make request
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers
            )

            # Check for errors
            response.raise_for_status()

            # Return JSON if available, otherwise text
            if response.status_code == 204:  # No content
                return {"status": "success"}
            elif response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            else:
                return {"content": response.text}

        except requests.HTTPError as e:
            error_msg = f"Microsoft Graph API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg = f"{error_msg} - {error_data['error'].get('message', 'Unknown error')}"
            except:
                error_msg = f"{error_msg} - {e.response.text}"

            self.logger.error(error_msg)
            return {"error": error_msg}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

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
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

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

        return {
            "value": emails,
            "total": len(emails),
            "@odata.count": result.get("@odata.count")
        }

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
        result = await self._make_request("POST", endpoint, json_data=email_data)

        if "error" in result:
            return result

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
        result = await self._make_request("POST", endpoint, json_data=draft_data)

        if "error" in result:
            return result

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
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

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

        return {
            "value": emails,
            "total": len(emails)
        }

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
        result = await self._make_request("GET", endpoint, params=params, headers=headers)

        if "error" in result:
            return result

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

        return {
            "value": events,
            "total": len(events)
        }

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
        result = await self._make_request("POST", endpoint, json_data=event_data)

        if "error" in result:
            return result

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
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

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

        return {
            "value": contacts,
            "total": len(contacts)
        }
