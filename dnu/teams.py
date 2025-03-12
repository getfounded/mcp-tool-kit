#!/usr/bin/env python3
import os
import json
import logging
import base64
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from datetime import datetime, timedelta

# Microsoft Graph API client
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
    logging.info("Teams tools MCP reference set")


class TeamsTools(str, Enum):
    """Enum of Microsoft Teams tool names"""
    GET_TEAMS = "teams_get_teams"
    GET_CHANNELS = "teams_get_channels"
    GET_CHANNEL_MESSAGES = "teams_get_channel_messages"
    SEND_CHANNEL_MESSAGE = "teams_send_channel_message"
    CREATE_CHANNEL = "teams_create_channel"
    GET_CHATS = "teams_get_chats"
    SEND_CHAT_MESSAGE = "teams_send_chat_message"
    CREATE_MEETING = "teams_create_meeting"
    GET_MEETINGS = "teams_get_meetings"
    CREATE_TEAM = "teams_create_team"


class TeamsService:
    """Service to handle Microsoft Teams operations using Microsoft Graph API"""

    def __init__(self, client_id, client_secret, tenant_id, scopes=None):
        """Initialize the Teams service with Microsoft credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

        # Default scopes for Teams operations
        self.scopes = scopes or [
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

    async def get_teams(self, top=50):
        """Get list of teams the user has access to"""
        params = {
            "$top": top
        }

        endpoint = "me/joinedTeams"
        result = await self._make_request("get", endpoint, params=params)

        return result.get("value", [])

    async def get_channels(self, team_id, top=50):
        """Get list of channels in a team"""
        params = {
            "$top": top
        }

        endpoint = f"teams/{team_id}/channels"
        result = await self._make_request("get", endpoint, params=params)

        return result.get("value", [])

    async def get_channel_messages(self, team_id, channel_id, top=20):
        """Get messages from a channel"""
        params = {
            "$top": top,
            "$orderby": "createdDateTime desc"
        }

        endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
        result = await self._make_request("get", endpoint, params=params)

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

        return formatted_messages

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
        result = await self._make_request("post", endpoint, json_data=message_data)

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
        result = await self._make_request("post", endpoint, json_data=channel_data)

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
        result = await self._make_request("get", endpoint, params=params)

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

        return formatted_chats

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
        result = await self._make_request("post", endpoint, json_data=message_data)

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
        result = await self._make_request("post", endpoint, json_data=meeting_data)

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
        result = await self._make_request("get", endpoint, params=params)

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

        return formatted_meetings

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
        result = await self._make_request("post", endpoint, json_data=team_data)

        # Team creation is asynchronous, so we might not get an immediate result
        # We'll need to check the operation status or return what we have
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
                    await self._make_request("post", f"teams/{team_id}/members", json_data=member_data)
                except Exception as e:
                    # Log the error but continue with other members
                    logging.error(
                        f"Failed to add member {member['id']} to team: {str(e)}")

        return {
            "id": team_id,
            "display_name": display_name,
            "description": description,
            "status": "created" if team_id else "creation_in_progress"
        }

# Tool function definitions that will be registered with MCP


async def teams_get_teams(top: int = 50, ctx: Context = None) -> str:
    """Get list of Microsoft Teams the user has access to

    Parameters:
    - top: Maximum number of teams to return
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        teams = await teams_service.get_teams(top)
        return json.dumps(teams, indent=2)
    except Exception as e:
        return f"Error retrieving teams: {str(e)}"


async def teams_get_channels(team_id: str, top: int = 50, ctx: Context = None) -> str:
    """Get list of channels in a Microsoft Teams team

    Parameters:
    - team_id: ID of the team
    - top: Maximum number of channels to return
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        channels = await teams_service.get_channels(team_id, top)
        return json.dumps(channels, indent=2)
    except Exception as e:
        return f"Error retrieving channels: {str(e)}"


async def teams_get_channel_messages(team_id: str, channel_id: str, top: int = 20, ctx: Context = None) -> str:
    """Get messages from a Microsoft Teams channel

    Parameters:
    - team_id: ID of the team
    - channel_id: ID of the channel
    - top: Maximum number of messages to return
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        messages = await teams_service.get_channel_messages(team_id, channel_id, top)
        return json.dumps(messages, indent=2)
    except Exception as e:
        return f"Error retrieving channel messages: {str(e)}"


async def teams_send_channel_message(team_id: str, channel_id: str, content: str,
                                     content_type: str = "html", importance: str = "normal",
                                     ctx: Context = None) -> str:
    """Send a message to a Microsoft Teams channel

    Parameters:
    - team_id: ID of the team
    - channel_id: ID of the channel
    - content: Message content
    - content_type: Content type (html or text)
    - importance: Message importance (normal, high, urgent)
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        result = await teams_service.send_channel_message(team_id, channel_id, content, content_type, importance)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sending channel message: {str(e)}"


async def teams_create_channel(team_id: str, display_name: str, description: str = None,
                               membership_type: str = "standard", ctx: Context = None) -> str:
    """Create a new channel in a Microsoft Teams team

    Parameters:
    - team_id: ID of the team
    - display_name: Display name for the channel
    - description: Optional description for the channel
    - membership_type: Channel membership type (standard, private, shared)
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        result = await teams_service.create_channel(team_id, display_name, description, membership_type)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating channel: {str(e)}"


async def teams_get_chats(top: int = 20, ctx: Context = None) -> str:
    """Get list of Microsoft Teams chats for the user

    Parameters:
    - top: Maximum number of chats to return
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        chats = await teams_service.get_chats(top)
        return json.dumps(chats, indent=2)
    except Exception as e:
        return f"Error retrieving chats: {str(e)}"


async def teams_send_chat_message(chat_id: str, content: str,
                                  content_type: str = "html", importance: str = "normal",
                                  ctx: Context = None) -> str:
    """Send a message to a Microsoft Teams chat

    Parameters:
    - chat_id: ID of the chat
    - content: Message content
    - content_type: Content type (html or text)
    - importance: Message importance (normal, high, urgent)
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        result = await teams_service.send_chat_message(chat_id, content, content_type, importance)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sending chat message: {str(e)}"


async def teams_create_meeting(subject: str, start_datetime: str, end_datetime: str,
                               timezone: str = "UTC", attendees: List[Dict] = None,
                               is_online_meeting: bool = True, content: str = None,
                               ctx: Context = None) -> str:
    """Create a Microsoft Teams meeting

    Parameters:
    - subject: Meeting subject
    - start_datetime: Start date/time in ISO format
    - end_datetime: End date/time in ISO format
    - timezone: Timezone for the meeting
    - attendees: List of attendees with email, name, and type
    - is_online_meeting: Whether this is an online Teams meeting
    - content: Optional meeting body content
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        result = await teams_service.create_meeting(subject, start_datetime, end_datetime,
                                                    timezone, attendees, is_online_meeting, content)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating meeting: {str(e)}"


async def teams_get_meetings(top: int = 10, skip: int = 0, ctx: Context = None) -> str:
    """Get Microsoft Teams meetings for the user

    Parameters:
    - top: Maximum number of meetings to return
    - skip: Number of meetings to skip (for pagination)
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        meetings = await teams_service.get_meetings(top, skip)
        return json.dumps(meetings, indent=2)
    except Exception as e:
        return f"Error retrieving meetings: {str(e)}"


async def teams_create_team(display_name: str, description: str = None,
                            mail_nickname: str = None, members: List[Dict] = None,
                            ctx: Context = None) -> str:
    """Create a new Microsoft Teams team

    Parameters:
    - display_name: Display name for the team
    - description: Optional description for the team
    - mail_nickname: Email nickname for the team (used for team email address)
    - members: List of members to add to the team with IDs and roles
    """
    teams_service = _get_teams_service()
    if not teams_service:
        return "Microsoft Teams API is not configured. Please set the required environment variables."

    try:
        result = await teams_service.create_team(display_name, description, mail_nickname, members)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error creating team: {str(e)}"

# Tool registration and initialization
_teams_service = None


def initialize_teams_service(client_id=None, client_secret=None, tenant_id=None, scopes=None):
    """Initialize the Microsoft Teams service with Microsoft credentials"""
    global _teams_service

    # Use environment variables as fallback
    client_id = client_id or os.environ.get("MS_CLIENT_ID")
    client_secret = client_secret or os.environ.get("MS_CLIENT_SECRET")
    tenant_id = tenant_id or os.environ.get("MS_TENANT_ID")

    if not client_id or not client_secret or not tenant_id:
        logging.warning(
            "Microsoft Graph API credentials not configured. Please set MS_CLIENT_ID, MS_CLIENT_SECRET, and MS_TENANT_ID environment variables.")
        return None

    _teams_service = TeamsService(client_id, client_secret, tenant_id, scopes)
    return _teams_service


def _get_teams_service():
    """Get or initialize the Microsoft Teams service"""
    global _teams_service
    if _teams_service is None:
        _teams_service = initialize_teams_service()
    return _teams_service


def get_teams_tools():
    """Get a dictionary of all Microsoft Teams tools for registration with MCP"""
    return {
        TeamsTools.GET_TEAMS: teams_get_teams,
        TeamsTools.GET_CHANNELS: teams_get_channels,
        TeamsTools.GET_CHANNEL_MESSAGES: teams_get_channel_messages,
        TeamsTools.SEND_CHANNEL_MESSAGE: teams_send_channel_message,
        TeamsTools.CREATE_CHANNEL: teams_create_channel,
        TeamsTools.GET_CHATS: teams_get_chats,
        TeamsTools.SEND_CHAT_MESSAGE: teams_send_chat_message,
        TeamsTools.CREATE_MEETING: teams_create_meeting,
        TeamsTools.GET_MEETINGS: teams_get_meetings,
        TeamsTools.CREATE_TEAM: teams_create_team
    }

# This function will be called by the unified server to initialize the module


def initialize(mcp=None):
    """Initialize the Microsoft Teams module with MCP reference and credentials"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_teams_service()
    if service:
        logging.info("Microsoft Teams API service initialized successfully")
    else:
        logging.warning("Failed to initialize Microsoft Teams API service")

    return service is not None


# If this file is run directly, provide a test function
if __name__ == "__main__":
    import asyncio

    async def test_teams_api():
        """Test the Teams API functionality"""
        # Initialize the service
        service = initialize_teams_service()
        if not service:
            print(
                "Failed to initialize Microsoft Teams API service. Check your environment variables.")
            return

        # Get teams
        teams = await service.get_teams()
        print(f"Found {len(teams)} teams.")

        if teams:
            team_id = teams[0].get("id")
            print(f"Getting channels for team: {teams[0].get('displayName')}")

            # Get channels
            channels = await service.get_channels(team_id)
            print(f"Found {len(channels)} channels.")

            if channels:
                channel_id = channels[0].get("id")
                print(
                    f"Getting messages for channel: {channels[0].get('displayName')}")

                # Get messages
                messages = await service.get_channel_messages(team_id, channel_id)
                print(f"Found {len(messages)} messages.")

    # Run the test
    asyncio.run(test_teams_api())
