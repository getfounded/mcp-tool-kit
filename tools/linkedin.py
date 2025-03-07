import os
import json
import logging
import requests
import base64
import time
from enum import Enum
from typing import List, Dict, Optional, Any, Union

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    "Set the external MCP reference for tool registration"
    global external_mcp
    external_mcp = mcp
    logging.info("LinkedIn tools MCP reference set")


class LinkedInTools(str, Enum):
    "Enum of LinkedIn tool names"
    GET_PROFILE = "linkedin_get_profile"
    SEARCH_PEOPLE = "linkedin_search_people"
    SEARCH_COMPANIES = "linkedin_search_companies"
    POST_UPDATE = "linkedin_post_update"
    GET_CONNECTIONS = "linkedin_get_connections"
    SEND_MESSAGE = "linkedin_send_message"
    SHARE_POST = "linkedin_share_post"


class LinkedInService:
    """Service to handle LinkedIn API operations"""

    def __init__(self, client_id, client_secret, redirect_uri=None, token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://api.linkedin.com/v2"
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.token = token  # Store the token for API calls
        self.token_expires = None  # When the token expires

    async def ensure_token(self):
        """Ensure we have a valid access token"""
        # Check if token is still valid
        if self.token and self.token_expires and time.time() < self.token_expires:
            return self.token

        # If no token or expired, attempt to refresh or get a new one
        if not self.token:
            raise ValueError(
                "No access token available. Please authorize the application first.")

        # Refresh token logic
        refresh_token = self.token.get("refresh_token")
        if refresh_token:
            try:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                response = requests.post(self.token_url, data=data)
                token_data = response.json()

                if "access_token" in token_data:
                    self.token = token_data
                    self.token_expires = time.time() + token_data.get("expires_in", 3600)
                    return self.token
            except Exception as e:
                logging.error(f"Failed to refresh token: {str(e)}")

        raise ValueError(
            "Access token expired and could not be refreshed. Please reauthorize.")

    def get_auth_url(self, scopes=None):
        """Get the authorization URL for LinkedIn OAuth"""
        if scopes is None:
            scopes = ["r_liteprofile", "r_emailaddress", "w_member_social"]

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": base64.b64encode(os.urandom(16)).decode()
        }

        auth_url = self.auth_url + "?" + \
            "&".join(f"{k}={v}" for k, v in params.items())
        return auth_url

    async def exchange_code_for_token(self, code):
        """Exchange the OAuth code for an access token"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(self.token_url, data=data)
            token_data = response.json()

            if "access_token" in token_data:
                self.token = token_data
                self.token_expires = time.time() + token_data.get("expires_in", 3600)
                return token_data
            else:
                return {"error": "Failed to get access token", "details": token_data}
        except Exception as e:
            return {"error": str(e)}

    async def get_profile(self):
        """Get the current user's LinkedIn profile"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get basic profile (need r_liteprofile scope)
            profile_url = f"{self.base_url}/me"
            response = requests.get(profile_url, headers=headers)

            if response.status_code != 200:
                return {"error": f"Error getting profile: {response.text}"}

            profile_data = response.json()

            # Get email address if we have the scope (r_emailaddress)
            try:
                email_url = f"{self.base_url}/emailAddress?q=members&projection=(elements*(handle~))"
                email_response = requests.get(email_url, headers=headers)

                if email_response.status_code == 200:
                    email_data = email_response.json()
                    # Extract email from response
                    if email_data and "elements" in email_data and len(email_data["elements"]) > 0:
                        profile_data["email"] = email_data["elements"][0]["handle~"]["emailAddress"]
            except Exception as e:
                logging.warning(f"Could not retrieve email: {str(e)}")

            return profile_data
        except Exception as e:
            return {"error": str(e)}

    async def search_people(self, keywords, count=10, start=0):
        """Search for people on LinkedIn"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Use the search API
            search_url = f"{self.base_url}/search/blended?keywords={keywords}&start={start}&count={count}"
            response = requests.get(search_url, headers=headers)

            if response.status_code != 200:
                return {"error": f"Error searching people: {response.text}"}

            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def search_companies(self, keywords, count=10, start=0):
        """Search for companies on LinkedIn"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Use the search API
            search_url = f"{self.base_url}/search/blended?keywords={keywords}&start={start}&count={count}&filters=List(entityType->COMPANY)"
            response = requests.get(search_url, headers=headers)

            if response.status_code != 200:
                return {"error": f"Error searching companies: {response.text}"}

            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def post_update(self, text, visibility="PUBLIC"):
        """Post an update to LinkedIn"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get the user URN
            profile = await self.get_profile()
            if "error" in profile:
                return profile

            user_urn = f"urn:li:person:{profile['id']}"

            # Create the post payload
            payload = {
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }

            # Post the update
            post_url = f"{self.base_url}/ugcPosts"
            response = requests.post(post_url, json=payload, headers=headers)

            if response.status_code not in (200, 201):
                return {"error": f"Error posting update: {response.text}"}

            return {"status": "success", "response": response.json()}
        except Exception as e:
            return {"error": str(e)}

    async def get_connections(self, count=50, start=0):
        """Get the user's LinkedIn connections"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get connections (requires r_network scope)
            connections_url = f"{self.base_url}/connections?start={start}&count={count}"
            response = requests.get(connections_url, headers=headers)

            if response.status_code != 200:
                return {"error": f"Error getting connections: {response.text}"}

            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def send_message(self, recipient_urn, subject, body):
        """Send a message to a LinkedIn connection"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get the user URN
            profile = await self.get_profile()
            if "error" in profile:
                return profile

            sender_urn = f"urn:li:person:{profile['id']}"

            # Create the message payload
            payload = {
                "recipients": [recipient_urn],
                "subject": subject,
                "body": body,
                "sender": sender_urn
            }

            # Send the message
            message_url = f"{self.base_url}/messages"
            response = requests.post(
                message_url, json=payload, headers=headers)

            if response.status_code not in (200, 201):
                return {"error": f"Error sending message: {response.text}"}

            return {"status": "success", "response": response.json()}
        except Exception as e:
            return {"error": str(e)}

    async def share_post(self, post_urn, comment="", visibility="PUBLIC"):
        """Share a LinkedIn post"""
        try:
            await self.ensure_token()

            headers = {
                "Authorization": f"Bearer {self.token['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            # Get the user URN
            profile = await self.get_profile()
            if "error" in profile:
                return profile

            user_urn = f"urn:li:person:{profile['id']}"

            # Create the share payload
            payload = {
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": comment
                        },
                        "shareMediaCategory": "NONE",
                        "content": {
                            "contentEntities": [
                                {
                                    "entityLocation": post_urn
                                }
                            ],
                            "title": "Shared Post"
                        }
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }

            # Post the share
            share_url = f"{self.base_url}/ugcPosts"
            response = requests.post(share_url, json=payload, headers=headers)

            if response.status_code not in (200, 201):
                return {"error": f"Error sharing post: {response.text}"}

            return {"status": "success", "response": response.json()}
        except Exception as e:
            return {"error": str(e)}


# Tool function definitions that will be registered with MCP

async def linkedin_get_profile(ctx: Context = None) -> str:
    """Get the current user's LinkedIn profile information"""
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.get_profile()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving LinkedIn profile: {str(e)}"


async def linkedin_search_people(keywords: str, count: int = 10, start: int = 0, ctx: Context = None) -> str:
    """Search for people on LinkedIn

    Parameters:
    - keywords: Search terms
    - count: Number of results to return (default: 10)
    - start: Offset for pagination
    """
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.search_people(keywords, count, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error searching LinkedIn people: {str(e)}"


async def linkedin_search_companies(keywords: str, count: int = 10, start: int = 0, ctx: Context = None) -> str:
    """Search for companies on LinkedIn

    Parameters:
    - keywords: Search terms
    - count: Number of results to return (default: 10)
    - start: Offset for pagination
    """
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.search_companies(keywords, count, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error searching LinkedIn companies: {str(e)}"


async def linkedin_post_update(text: str, visibility: str = "PUBLIC", ctx: Context = None) -> str:
    """Post an update to LinkedIn

    Parameters:
    - text: The content of the post
    - visibility: Post visibility, one of: PUBLIC, CONNECTIONS, or CONTAINER (default: PUBLIC)
    """
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.post_update(text, visibility)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error posting LinkedIn update: {str(e)}"


async def linkedin_get_connections(count: int = 50, start: int = 0, ctx: Context = None) -> str:
    """Get the user's LinkedIn connections

    Parameters:
    - count: Number of connections to retrieve (default: 50)
    - start: Offset for pagination
    """
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.get_connections(count, start)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving LinkedIn connections: {str(e)}"


async def linkedin_send_message(recipient_urn: str, subject: str, body: str, ctx: Context = None) -> str:
    """Send a message to a LinkedIn connection

    Parameters:
    - recipient_urn: URN of the recipient (format: urn:li:person:123456)
    - subject: Message subject
    - body: Message body
    """
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.send_message(recipient_urn, subject, body)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sending LinkedIn message: {str(e)}"


async def linkedin_share_post(post_urn: str, comment: str = "", visibility: str = "PUBLIC", ctx: Context = None) -> str:
    """Share a LinkedIn post

    Parameters:
    - post_urn: URN of the post to share
    - comment: Optional comment to add to the share
    - visibility: Post visibility, one of: PUBLIC, CONNECTIONS, or CONTAINER (default: PUBLIC)
    """
    linkedin = _get_linkedin_service()
    if not linkedin:
        return "LinkedIn API is not configured. Please set the required environment variables."

    try:
        result = await linkedin.share_post(post_urn, comment, visibility)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error sharing LinkedIn post: {str(e)}"


# Tool registration and initialization
_linkedin_service = None


def initialize_linkedin_service(client_id=None, client_secret=None, redirect_uri=None, token=None):
    """Initialize the LinkedIn service"""
    global _linkedin_service

    # Use environment variables as fallback
    client_id = client_id or os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = client_secret or os.environ.get("LINKEDIN_CLIENT_SECRET")
    redirect_uri = redirect_uri or os.environ.get("LINKEDIN_REDIRECT_URI")

    # Check for token in environment variable
    token_str = os.environ.get("LINKEDIN_TOKEN")
    if token_str and not token:
        try:
            token = json.loads(token_str)
        except Exception as e:
            logging.warning(f"Could not parse LINKEDIN_TOKEN: {str(e)}")

    if not client_id or not client_secret:
        logging.warning(
            "LinkedIn API credentials not configured. Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        return None

    _linkedin_service = LinkedInService(
        client_id, client_secret, redirect_uri, token)
    return _linkedin_service


def _get_linkedin_service():
    """Get or initialize the LinkedIn service"""
    global _linkedin_service
    if _linkedin_service is None:
        _linkedin_service = initialize_linkedin_service()
    return _linkedin_service


def get_linkedin_tools():
    """Get a dictionary of all LinkedIn tools for registration with MCP"""
    return {
        LinkedInTools.GET_PROFILE: linkedin_get_profile,
        LinkedInTools.SEARCH_PEOPLE: linkedin_search_people,
        LinkedInTools.SEARCH_COMPANIES: linkedin_search_companies,
        LinkedInTools.POST_UPDATE: linkedin_post_update,
        LinkedInTools.GET_CONNECTIONS: linkedin_get_connections,
        LinkedInTools.SEND_MESSAGE: linkedin_send_message,
        LinkedInTools.SHARE_POST: linkedin_share_post
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the LinkedIn module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_linkedin_service()
    if service:
        logging.info("LinkedIn API service initialized successfully")
    else:
        logging.warning("Failed to initialize LinkedIn API service")

    return service is not None


if __name__ == "__main__":
    print("LinkedIn service module - use with MCP Unified Server")
