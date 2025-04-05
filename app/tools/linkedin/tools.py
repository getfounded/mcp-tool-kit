#!/usr/bin/env python3
"""
LinkedIn API tools for MCP toolkit.
"""
import json
from typing import Dict, Any, Optional, List

from app.tools.base.registry import register_tool
from app.tools.linkedin.service import LinkedInService


@register_tool(
    name="linkedin_get_auth_url",
    category="linkedin",
    service_class=LinkedInService,
    description="Get the authorization URL for LinkedIn OAuth"
)
def linkedin_get_auth_url(self) -> str:
    """
    Get the authorization URL for LinkedIn OAuth

    This URL should be opened in a browser to authorize the application.
    After authorization, the user will be redirected to the configured
    redirect URI with a code parameter that can be used to authenticate.

    Returns:
    URL for LinkedIn OAuth authorization
    """
    try:
        auth_url = self.get_auth_url()
        return f"Please open the following URL in your browser to authorize the application:\n\n{auth_url}"
    except Exception as e:
        return f"Error generating authorization URL: {str(e)}"


@register_tool(
    name="linkedin_authenticate",
    category="linkedin",
    service_class=LinkedInService,
    description="Authenticate with LinkedIn using an authorization code"
)
async def linkedin_authenticate(self, code: str) -> str:
    """
    Authenticate with LinkedIn using an authorization code

    Parameters:
    - code: The authorization code obtained from the redirect URI after authorization

    Returns:
    JSON string with authentication result
    """
    try:
        result = await self.authenticate_with_code(code)

        # Simplify the response to avoid exposing tokens
        if "access_token" in result:
            return json.dumps({
                "status": "authenticated",
                "expires_in": result.get("expires_in", "Unknown"),
                "token_type": result.get("token_type", "Unknown")
            }, indent=2)
        else:
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Authentication error: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_get_profile",
    category="linkedin",
    service_class=LinkedInService,
    description="Get the current user's LinkedIn profile"
)
async def linkedin_get_profile(self) -> str:
    """
    Get the current user's LinkedIn profile information

    Returns:
    JSON string with profile information
    """
    try:
        result = await self.get_profile()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving LinkedIn profile: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_search_people",
    category="linkedin",
    service_class=LinkedInService,
    description="Search for people on LinkedIn"
)
async def linkedin_search_people(self, keywords: str, count: int = 10, start: int = 0) -> str:
    """
    Search for people on LinkedIn

    Parameters:
    - keywords: Search terms
    - count: Number of results to return (default: 10)
    - start: Offset for pagination

    Returns:
    JSON string with search results
    """
    try:
        result = await self.search_people(keywords, count, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error searching LinkedIn people: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_search_companies",
    category="linkedin",
    service_class=LinkedInService,
    description="Search for companies on LinkedIn"
)
async def linkedin_search_companies(self, keywords: str, count: int = 10, start: int = 0) -> str:
    """
    Search for companies on LinkedIn

    Parameters:
    - keywords: Search terms
    - count: Number of results to return (default: 10)
    - start: Offset for pagination

    Returns:
    JSON string with search results
    """
    try:
        result = await self.search_companies(keywords, count, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error searching LinkedIn companies: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_post_update",
    category="linkedin",
    service_class=LinkedInService,
    description="Post an update to LinkedIn"
)
async def linkedin_post_update(self, text: str, visibility: str = "PUBLIC") -> str:
    """
    Post an update to LinkedIn

    Parameters:
    - text: The content of the post
    - visibility: Post visibility, one of: PUBLIC, CONNECTIONS, or CONTAINER (default: PUBLIC)

    Returns:
    JSON string with post result
    """
    try:
        result = await self.post_update(text, visibility)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error posting LinkedIn update: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_get_connections",
    category="linkedin",
    service_class=LinkedInService,
    description="Get the user's LinkedIn connections"
)
async def linkedin_get_connections(self, count: int = 50, start: int = 0) -> str:
    """
    Get the user's LinkedIn connections

    Parameters:
    - count: Number of connections to retrieve (default: 50)
    - start: Offset for pagination

    Returns:
    JSON string with connections
    """
    try:
        result = await self.get_connections(count, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error retrieving LinkedIn connections: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_send_message",
    category="linkedin",
    service_class=LinkedInService,
    description="Send a message to a LinkedIn connection"
)
async def linkedin_send_message(self, recipient_urn: str, subject: str, body: str) -> str:
    """
    Send a message to a LinkedIn connection

    Parameters:
    - recipient_urn: URN of the recipient (format: urn:li:person:123456)
    - subject: Message subject
    - body: Message body

    Returns:
    JSON string with send result
    """
    try:
        result = await self.send_message(recipient_urn, subject, body)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error sending LinkedIn message: {str(e)}"}, indent=2)


@register_tool(
    name="linkedin_share_post",
    category="linkedin",
    service_class=LinkedInService,
    description="Share a LinkedIn post"
)
async def linkedin_share_post(self, post_urn: str, comment: str = "", visibility: str = "PUBLIC") -> str:
    """
    Share a LinkedIn post

    Parameters:
    - post_urn: URN of the post to share
    - comment: Optional comment to add to the share
    - visibility: Post visibility, one of: PUBLIC, CONNECTIONS, or CONTAINER (default: PUBLIC)

    Returns:
    JSON string with share result
    """
    try:
        result = await self.share_post(post_urn, comment, visibility)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error sharing LinkedIn post: {str(e)}"}, indent=2)
