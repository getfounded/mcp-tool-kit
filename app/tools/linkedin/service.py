#!/usr/bin/env python3
"""
LinkedIn API Service for MCP toolkit.
"""
import os
import json
import logging
import requests
import base64
import time
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase
from app.tools.utils.auth import create_auth_handler, OAuth2Auth


class LinkedInService(ToolServiceBase):
    """Service for LinkedIn API operations"""

    def __init__(self):
        """Initialize the LinkedIn service"""
        super().__init__()
        self.auth_handler = None
        self.base_url = "https://api.linkedin.com/v2"

    def initialize(self) -> bool:
        """
        Initialize the service with credentials from environment variables.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Get credentials from environment
            self.client_id = self.get_env_var("LINKEDIN_CLIENT_ID")
            self.client_secret = self.get_env_var("LINKEDIN_CLIENT_SECRET")
            self.redirect_uri = self.get_env_var("LINKEDIN_REDIRECT_URI")

            if not (self.client_id and self.client_secret):
                self.logger.warning("LinkedIn API credentials not configured properly. "
                                    "Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
                return False

            # Load token if available
            token_str = self.get_env_var("LINKEDIN_TOKEN")
            token_data = None
            if token_str:
                try:
                    token_data = json.loads(token_str)
                except Exception as e:
                    self.logger.warning(
                        f"Could not parse LINKEDIN_TOKEN: {str(e)}")

            # Set default scopes
            self.scopes = [
                "r_liteprofile",
                "r_emailaddress",
                "w_member_social"
            ]

            # Create rate limiter - LinkedIn has a limit of 100 calls per day per user/app
            self.create_rate_limiter("linkedin_api", 100, 86400)  # 24 hours

            # Create auth handler
            self.auth_handler = create_auth_handler(
                service_name="linkedin",
                auth_type="oauth2",
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                auth_url="https://www.linkedin.com/oauth/v2/authorization",
                token_url="https://www.linkedin.com/oauth/v2/accessToken",
                scopes=self.scopes,
                client_id_env="LINKEDIN_CLIENT_ID",
                client_secret_env="LINKEDIN_CLIENT_SECRET",
                redirect_uri_env="LINKEDIN_REDIRECT_URI"
            )

            # Set token if available
            if token_data and "access_token" in token_data:
                self.auth_handler.authenticate(token_data=token_data)
                self.logger.info(
                    "LinkedIn service initialized with existing token")

            self.initialized = True
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to initialize LinkedIn service: {str(e)}")
            return False

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        self._is_initialized()

        if not self.auth_handler.is_authenticated():
            # Try to refresh token
            if hasattr(self.auth_handler, "token_data") and self.auth_handler.token_data and "refresh_token" in self.auth_handler.token_data:
                refresh_result = await self.auth_handler.refresh_token()
                if "error" in refresh_result:
                    raise ValueError(
                        f"Authentication error: {refresh_result['error']}")
            else:
                raise ValueError(
                    "Not authenticated. Please authenticate with get_auth_url and authenticate_with_code first.")

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                            data: Optional[Dict] = None, json_data: Optional[Dict] = None,
                            headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to LinkedIn API"""
        # Ensure authentication
        await self._ensure_authenticated()

        # Apply rate limiting
        self.apply_rate_limit("linkedin_api", wait=True)

        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        # Add auth headers
        request_headers.update(self.auth_handler.get_auth_headers())

        # Add custom headers if provided
        if headers:
            request_headers.update(headers)

        # Prepare URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

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
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            else:
                return {"content": response.text}

        except requests.HTTPError as e:
            error_msg = f"LinkedIn API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_msg = f"{error_msg} - {error_data['message']}"
            except:
                error_msg = f"{error_msg} - {e.response.text}"

            self.logger.error(error_msg)
            return {"error": error_msg}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    def get_auth_url(self) -> str:
        """Get the authorization URL for LinkedIn OAuth"""
        self._is_initialized()
        return self.auth_handler.get_auth_url()

    async def authenticate_with_code(self, code: str) -> Dict[str, Any]:
        """Exchange the OAuth code for an access token"""
        self._is_initialized()
        return await self.auth_handler.exchange_code(code)

    async def get_profile(self) -> Dict[str, Any]:
        """Get the current user's LinkedIn profile"""
        # Get basic profile (need r_liteprofile scope)
        profile_data = await self._make_request("GET", "/me")
        if "error" in profile_data:
            return profile_data

        # Get email address if we have the scope (r_emailaddress)
        try:
            email_data = await self._make_request("GET", "/emailAddress?q=members&projection=(elements*(handle~))")

            if "error" not in email_data and "elements" in email_data and len(email_data["elements"]) > 0:
                profile_data["email"] = email_data["elements"][0]["handle~"]["emailAddress"]
        except Exception as e:
            self.logger.warning(f"Could not retrieve email: {str(e)}")

        return profile_data

    async def search_people(self, keywords: str, count: int = 10, start: int = 0) -> Dict[str, Any]:
        """Search for people on LinkedIn"""
        # Use the search API
        params = {
            "keywords": keywords,
            "start": start,
            "count": count
        }
        return await self._make_request("GET", "/search/blended", params=params)

    async def search_companies(self, keywords: str, count: int = 10, start: int = 0) -> Dict[str, Any]:
        """Search for companies on LinkedIn"""
        # Use the search API
        params = {
            "keywords": keywords,
            "start": start,
            "count": count,
            "filters": "List(entityType->COMPANY)"
        }
        return await self._make_request("GET", "/search/blended", params=params)

    async def post_update(self, text: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """Post an update to LinkedIn"""
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
        return await self._make_request("POST", "/ugcPosts", json_data=payload)

    async def get_connections(self, count: int = 50, start: int = 0) -> Dict[str, Any]:
        """Get the user's LinkedIn connections"""
        # Get connections (requires r_network scope)
        params = {
            "start": start,
            "count": count
        }
        return await self._make_request("GET", "/connections", params=params)

    async def send_message(self, recipient_urn: str, subject: str, body: str) -> Dict[str, Any]:
        """Send a message to a LinkedIn connection"""
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
        return await self._make_request("POST", "/messages", json_data=payload)

    async def share_post(self, post_urn: str, comment: str = "", visibility: str = "PUBLIC") -> Dict[str, Any]:
        """Share a LinkedIn post"""
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
        return await self._make_request("POST", "/ugcPosts", json_data=payload)
