#!/usr/bin/env python3
"""
Microsoft Teams API Service for MCP toolkit.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase
from app.tools.utils.auth import create_auth_handler, MicrosoftAuth


class TeamsService(ToolServiceBase):
    """Service for Microsoft Teams API operations using Microsoft Graph API"""

    def __init__(self):
        """Initialize the Teams service"""
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

            # Default scopes for Teams operations
            self.scopes = [
                'https://graph.microsoft.com/Team.ReadBasic.All',
                'https://graph.microsoft.com/Team.Create',
                'https://graph.microsoft.com/Channel.ReadBasic.All',
                'https://graph.microsoft.com/Channel.Create',
                'https://graph.microsoft.com/ChannelMessage.Read.All',
                'https://graph.microsoft.com/ChannelMessage.Send',
                'https://graph.microsoft.com/Chat.ReadWrite',
                'https://graph.microsoft.com/ChatMessage.Read',
                'https://graph.microsoft.com/ChatMessage.Send',
                'https://graph.microsoft.com/OnlineMeetings.ReadWrite'
            ]

            # Create rate limiter - Microsoft has various limits
            # Setting a conservative default of 600 calls per minute
            # 600 calls per minute
            self.create_rate_limiter("teams_api", 600, 60)

            # Create auth handler
            self.auth_handler = create_auth_handler(
                service_name="teams",
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
            self.logger.error(f"Failed to initialize Teams service: {str(e)}")
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
        self.apply_rate_limit("teams_api", wait=True)

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

    async def get_teams(self, top=50):
        """Get list of teams the user has access to"""
        params = {
            "$top": top
        }

        endpoint = "me/joinedTeams"
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

        # Format the result
        teams = result.get("value", [])
        return {
            "value": teams,
            "total": len(teams)
        }

    async def get_channels(self, team_id, top=50):
        """Get list of channels in a team"""
        params = {
            "$top": top
        }

        endpoint = f"teams/{team_id}/channels"
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

        # Format the result
        channels = result.get("value", [])
        return {
            "value": channels,
            "total": len(channels)
        }

    async def get_channel_messages(self, team_id, channel_id, top=20):
        """Get messages from a channel"""
        params = {
            "$top": top,
            "$orderby": "createdDateTime desc"
        }

        endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

        messages = result.get("value", [])

        # Format messages for better readability
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                "id": msg.get("id"),
                "content": msg.get("body", {}).get("content", ""),
                "content_type": msg.get("body", {}).get("contentType", "text"),
                "created_time": msg.get("createdDateTime"),
                "sender": msg.get("from", {}).get("user", {}).get("displayName", "Unknown"),
                "sender_user_id": msg.get("from", {}).get("user", {}).get("id", ""),
                "importance": msg.get("importance", "normal"),
                "attachments": [
                    {
                        "id": attachment.get("id"),
                        "name": attachment.get("name"),
                        "content_type": attachment.get("contentType"),
                        "content_url": attachment.get("contentUrl")
                    }
                    for attachment in msg.get("attachments", [])
                ]
            }

            # Add reactions if present
            if "reactions" in msg:
                formatted_msg["reactions"] = [
                    {
                        "reaction_type": reaction.get("reactionType"),
                        "count": reaction.get("count"),
                        "user_ids": reaction.get("user_ids", [])
                    }
                    for reaction in msg.get("reactions", [])
                ]

            formatted_messages.append(formatted_msg)

        return {
            "value": formatted_messages,
            "total": len(formatted_messages)
        }

    async def send_channel_message(self, team_id, channel_id, content, content_type="html", importance="normal"):
        """Send a message to a channel"""
        message_data = {
            "body": {
                "content": content,
                "contentType": content_type
            },
            "importance": importance
        }

        endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
        result = await self._make_request("POST", endpoint, json_data=message_data)

        if "error" in result:
            return result

        return {
            "id": result.get("id"),
            "status": "sent",
            "team_id": team_id,
            "channel_id": channel_id
        }

    async def create_channel(self, team_id, display_name, description=None, membership_type="standard"):
        """Create a new channel in a team"""
        channel_data = {
            "displayName": display_name,
            "membershipType": membership_type
        }

        if description:
            channel_data["description"] = description

        endpoint = f"teams/{team_id}/channels"
        result = await self._make_request("POST", endpoint, json_data=channel_data)

        if "error" in result:
            return result

        return {
            "id": result.get("id"),
            "display_name": result.get("displayName"),
            "description": result.get("description", ""),
            "team_id": team_id,
            "status": "created"
        }

    async def get_chats(self, top=20):
        """Get list of user's chats"""
        params = {
            "$top": top,
            "$expand": "members",
            "$orderby": "lastUpdatedDateTime desc"
        }

        endpoint = "me/chats"
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

        chats = result.get("value", [])

        # Format chats for better readability
        formatted_chats = []
        for chat in chats:
            members = chat.get("members", [])
            formatted_members = []

            for member in members:
                user = member.get("user", {})
                formatted_members.append({
                    "display_name": user.get("displayName", ""),
                    "id": user.get("id", ""),
                    "email": user.get("email", "") or user.get("userPrincipalName", "")
                })

            formatted_chat = {
                "id": chat.get("id"),
                "topic": chat.get("topic", ""),
                "chat_type": chat.get("chatType", ""),
                "last_updated": chat.get("lastUpdatedDateTime", ""),
                "members": formatted_members
            }

            formatted_chats.append(formatted_chat)

        return {
            "value": formatted_chats,
            "total": len(formatted_chats)
        }

    async def send_chat_message(self, chat_id, content, content_type="html", importance="normal"):
        """Send a message to a chat"""
        message_data = {
            "body": {
                "content": content,
                "contentType": content_type
            },
            "importance": importance
        }

        endpoint = f"chats/{chat_id}/messages"
        result = await self._make_request("POST", endpoint, json_data=message_data)

        if "error" in result:
            return result

        return {
            "id": result.get("id"),
            "status": "sent",
            "chat_id": chat_id
        }

    async def create_meeting(self, subject, start_datetime, end_datetime, timezone="UTC",
                             attendees=None, is_online_meeting=True, content=None):
        """Create a Teams meeting"""
        meeting_data = {
            "subject": subject,
            "isOnlineMeeting": is_online_meeting,
            "onlineMeetingProvider": "teamsForBusiness",
            "start": {
                "dateTime": start_datetime,
                "timeZone": timezone
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": timezone
            }
        }

        if content:
            meeting_data["body"] = {
                "contentType": "html",
                "content": content
            }

        if attendees:
            meeting_data["attendees"] = [
                {
                    "emailAddress": {
                        "address": attendee["email"],
                        "name": attendee.get("name", "")
                    },
                    "type": attendee.get("type", "required")
                }
                for attendee in attendees
            ]

        endpoint = "me/onlineMeetings"
        result = await self._make_request("POST", endpoint, json_data=meeting_data)

        if "error" in result:
            return result

        return {
            "id": result.get("id"),
            "join_url": result.get("joinUrl"),
            "subject": result.get("subject"),
            "start": result.get("startDateTime"),
            "end": result.get("endDateTime"),
            "meeting_id": result.get("onlineMeeting", {}).get("joinWebUrl")
        }

    async def get_meetings(self, top=10, skip=0):
        """Get user's Teams meetings"""
        # Use calendar events to get meetings
        params = {
            "$top": top,
            "$skip": skip,
            "$filter": "isOnlineMeeting eq true and onlineMeetingProvider eq 'teamsForBusiness'",
            "$orderby": "start/dateTime asc",
            "$select": "id,subject,organizer,attendees,start,end,isOnlineMeeting,onlineMeeting"
        }

        endpoint = "me/events"
        result = await self._make_request("GET", endpoint, params=params)

        if "error" in result:
            return result

        events = result.get("value", [])

        # Format meetings for better readability
        formatted_meetings = []
        for event in events:
            formatted_meeting = {
                "id": event.get("id"),
                "subject": event.get("subject", ""),
                "start": event.get("start", {}).get("dateTime"),
                "start_timezone": event.get("start", {}).get("timeZone"),
                "end": event.get("end", {}).get("dateTime"),
                "end_timezone": event.get("end", {}).get("timeZone"),
                "organizer": event.get("organizer", {}).get("emailAddress", {}).get("address", ""),
                "organizer_name": event.get("organizer", {}).get("emailAddress", {}).get("name", ""),
                "join_url": event.get("onlineMeeting", {}).get("joinUrl", "")
            }

            # Add attendees if present
            if "attendees" in event:
                formatted_meeting["attendees"] = [
                    {
                        "email": attendee.get("emailAddress", {}).get("address", ""),
                        "name": attendee.get("emailAddress", {}).get("name", ""),
                        "type": attendee.get("type", "")
                    }
                    for attendee in event.get("attendees", [])
                ]

            formatted_meetings.append(formatted_meeting)

        return {
            "value": formatted_meetings,
            "total": len(formatted_meetings)
        }

    async def create_team(self, display_name, description=None, mail_nickname=None, members=None):
        """Create a new Microsoft Teams team"""
        team_data = {
            "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
            "displayName": display_name,
            "visibility": "private"  # Default to private for security
        }

        if description:
            team_data["description"] = description

        if mail_nickname:
            team_data["mailNickname"] = mail_nickname

        endpoint = "teams"
        result = await self._make_request("POST", endpoint, json_data=team_data)

        if "error" in result:
            return result

        # Team creation is asynchronous, so we might not get an immediate result
        team_id = result.get("id", "")

        # If we have members to add and a team ID, add them
        if team_id and members:
            for member in members:
                member_data = {
                    "@odata.type": "#microsoft.graph.aadUserConversationMember",
                    "roles": member.get("roles", ["member"]),
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{member['id']}')"
                }

                try:
                    member_result = await self._make_request("POST", f"teams/{team_id}/members", json_data=member_data)
                    if "error" in member_result:
                        self.logger.error(
                            f"Failed to add member {member['id']} to team: {member_result['error']}")
                except Exception as e:
                    # Log the error but continue with other members
                    self.logger.error(
                        f"Failed to add member {member['id']} to team: {str(e)}")

        return {
            "id": team_id,
            "display_name": display_name,
            "description": description,
            "status": "created" if team_id else "creation_in_progress"
        }
