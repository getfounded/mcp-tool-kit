#!/usr/bin/env python3
"""
Microsoft Teams API tools for MCP toolkit.
"""
import json
from typing import Dict, List, Any, Optional

from app.tools.base.registry import register_tool
from app.tools.teams.service import TeamsService


@register_tool(
    name="teams_authenticate",
    category="teams",
    service_class=TeamsService,
    description="Authenticate with Microsoft Teams API"
)
async def teams_authenticate(self, method: str = "client_credentials") -> str:
    """
    Authenticate with Microsoft Teams API

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
    name="teams_get_teams",
    category="teams",
    service_class=TeamsService,
    description="Get list of Microsoft Teams the user has access to"
)
async def teams_get_teams(self, top: int = 50) -> str:
    """
    Get list of Microsoft Teams the user has access to

    Parameters:
    - top: Maximum number of teams to return

    Returns:
    JSON string with list of teams
    """
    try:
        result = await self.get_teams(top)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving teams: {str(e)}"}, indent=2)


@register_tool(
    name="teams_get_channels",
    category="teams",
    service_class=TeamsService,
    description="Get list of channels in a Microsoft Teams team"
)
async def teams_get_channels(self, team_id: str, top: int = 50) -> str:
    """
    Get list of channels in a Microsoft Teams team

    Parameters:
    - team_id: ID of the team
    - top: Maximum number of channels to return

    Returns:
    JSON string with list of channels
    """
    try:
        result = await self.get_channels(team_id, top)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving channels: {str(e)}"}, indent=2)


@register_tool(
    name="teams_get_channel_messages",
    category="teams",
    service_class=TeamsService,
    description="Get messages from a Microsoft Teams channel"
)
async def teams_get_channel_messages(self, team_id: str, channel_id: str, top: int = 20) -> str:
    """
    Get messages from a Microsoft Teams channel

    Parameters:
    - team_id: ID of the team
    - channel_id: ID of the channel
    - top: Maximum number of messages to return

    Returns:
    JSON string with list of messages
    """
    try:
        result = await self.get_channel_messages(team_id, channel_id, top)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving channel messages: {str(e)}"}, indent=2)


@register_tool(
    name="teams_send_channel_message",
    category="teams",
    service_class=TeamsService,
    description="Send a message to a Microsoft Teams channel"
)
async def teams_send_channel_message(self, team_id: str, channel_id: str, content: str,
                                     content_type: str = "html", importance: str = "normal") -> str:
    """
    Send a message to a Microsoft Teams channel

    Parameters:
    - team_id: ID of the team
    - channel_id: ID of the channel
    - content: Message content
    - content_type: Content type (html or text)
    - importance: Message importance (normal, high, urgent)

    Returns:
    JSON string with send result
    """
    try:
        result = await self.send_channel_message(team_id, channel_id, content, content_type, importance)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error sending channel message: {str(e)}"}, indent=2)


@register_tool(
    name="teams_create_channel",
    category="teams",
    service_class=TeamsService,
    description="Create a new channel in a Microsoft Teams team"
)
async def teams_create_channel(self, team_id: str, display_name: str, description: str = None,
                               membership_type: str = "standard") -> str:
    """
    Create a new channel in a Microsoft Teams team

    Parameters:
    - team_id: ID of the team
    - display_name: Display name for the channel
    - description: Optional description for the channel
    - membership_type: Channel membership type (standard, private, shared)

    Returns:
    JSON string with channel creation result
    """
    try:
        result = await self.create_channel(team_id, display_name, description, membership_type)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating channel: {str(e)}"}, indent=2)


@register_tool(
    name="teams_get_chats",
    category="teams",
    service_class=TeamsService,
    description="Get list of Microsoft Teams chats for the user"
)
async def teams_get_chats(self, top: int = 20) -> str:
    """
    Get list of Microsoft Teams chats for the user

    Parameters:
    - top: Maximum number of chats to return

    Returns:
    JSON string with list of chats
    """
    try:
        result = await self.get_chats(top)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving chats: {str(e)}"}, indent=2)


@register_tool(
    name="teams_send_chat_message",
    category="teams",
    service_class=TeamsService,
    description="Send a message to a Microsoft Teams chat"
)
async def teams_send_chat_message(self, chat_id: str, content: str,
                                  content_type: str = "html", importance: str = "normal") -> str:
    """
    Send a message to a Microsoft Teams chat

    Parameters:
    - chat_id: ID of the chat
    - content: Message content
    - content_type: Content type (html or text)
    - importance: Message importance (normal, high, urgent)

    Returns:
    JSON string with send result
    """
    try:
        result = await self.send_chat_message(chat_id, content, content_type, importance)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error sending chat message: {str(e)}"}, indent=2)


@register_tool(
    name="teams_create_meeting",
    category="teams",
    service_class=TeamsService,
    description="Create a Microsoft Teams meeting"
)
async def teams_create_meeting(self, subject: str, start_datetime: str, end_datetime: str,
                               timezone: str = "UTC", attendees: List[Dict] = None,
                               is_online_meeting: bool = True, content: str = None) -> str:
    """
    Create a Microsoft Teams meeting

    Parameters:
    - subject: Meeting subject
    - start_datetime: Start date/time in ISO format
    - end_datetime: End date/time in ISO format
    - timezone: Timezone for the meeting
    - attendees: List of attendees with email, name, and type
    - is_online_meeting: Whether this is an online Teams meeting
    - content: Optional meeting body content

    Returns:
    JSON string with meeting creation result
    """
    try:
        result = await self.create_meeting(subject, start_datetime, end_datetime,
                                           timezone, attendees, is_online_meeting, content)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating meeting: {str(e)}"}, indent=2)


@register_tool(
    name="teams_get_meetings",
    category="teams",
    service_class=TeamsService,
    description="Get Microsoft Teams meetings for the user"
)
async def teams_get_meetings(self, top: int = 10, skip: int = 0) -> str:
    """
    Get Microsoft Teams meetings for the user

    Parameters:
    - top: Maximum number of meetings to return
    - skip: Number of meetings to skip (for pagination)

    Returns:
    JSON string with list of meetings
    """
    try:
        result = await self.get_meetings(top, skip)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving meetings: {str(e)}"}, indent=2)


@register_tool(
    name="teams_create_team",
    category="teams",
    service_class=TeamsService,
    description="Create a new Microsoft Teams team"
)
async def teams_create_team(self, display_name: str, description: str = None,
                            mail_nickname: str = None, members: List[Dict] = None) -> str:
    """
    Create a new Microsoft Teams team

    Parameters:
    - display_name: Display name for the team
    - description: Optional description for the team
    - mail_nickname: Email nickname for the team (used for team email address)
    - members: List of members to add to the team with IDs and roles

    Returns:
    JSON string with team creation result
    """
    try:
        result = await self.create_team(display_name, description, mail_nickname, members)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating team: {str(e)}"}, indent=2)
