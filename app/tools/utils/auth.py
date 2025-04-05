#!/usr/bin/env python3
"""
Authentication utilities for MCP toolkit services.

This module provides authentication handlers for various service types.
"""
import os
import json
import time
import logging
import threading
import requests
import base64
import webbrowser
from typing import Dict, List, Any, Optional, Union, Callable
from abc import ABC, abstractmethod

# For Microsoft-specific authentication (used by SharePoint, Teams, Outlook)
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    logging.warning("MSAL not available. Microsoft authentication will not work.")

# Global registry for auth handlers by service
_AUTH_HANDLERS = {}

class AuthBase(ABC):
    """Base class for authentication handlers"""
    
    def __init__(self, service_name: str):
        """Initialize the auth handler"""
        self.service_name = service_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{service_name}")
        
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        pass
        
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        pass
        
    @abstractmethod
    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """Perform authentication"""
        pass
    
    def save_token(self, token_data: Dict[str, Any], token_file: Optional[str] = None) -> bool:
        """Save token to a file for persistence"""
        if not token_file:
            token_file = f"{self.service_name.lower()}_token.json"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)
            
            with open(token_file, 'w') as f:
                json.dump(token_data, f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save token: {str(e)}")
            return False
    
    def load_token(self, token_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load token from a file"""
        if not token_file:
            token_file = f"{self.service_name.lower()}_token.json"
        
        try:
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load token: {str(e)}")
        
        return None

class ApiKeyAuth(AuthBase):
    """API Key authentication handler"""
    
    def __init__(self, service_name: str, api_key: Optional[str] = None, 
                 header_name: str = "X-API-Key", env_var: Optional[str] = None):
        """Initialize API Key auth handler"""
        super().__init__(service_name)
        self.header_name = header_name
        self.api_key = api_key or (env_var and os.environ.get(env_var))
        self.env_var = env_var
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers with API key"""
        if not self.is_authenticated():
            raise ValueError(f"API key for {self.service_name} not set")
        
        return {self.header_name: self.api_key}
    
    def is_authenticated(self) -> bool:
        """Check if API key is available"""
        return bool(self.api_key)
    
    def authenticate(self, api_key: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Set API key for authentication"""
        # Use provided key, or try environment variable again
        if api_key:
            self.api_key = api_key
        elif not self.api_key and self.env_var:
            self.api_key = os.environ.get(self.env_var)
        
        if not self.api_key:
            return {"error": f"API key for {self.service_name} not provided"}
        
        return {"status": "authenticated", "method": "api_key"}

class BasicAuth(AuthBase):
    """Basic authentication handler"""
    
    def __init__(self, service_name: str, username: Optional[str] = None, 
                 password: Optional[str] = None, 
                 username_env: Optional[str] = None, 
                 password_env: Optional[str] = None):
        """Initialize Basic auth handler"""
        super().__init__(service_name)
        self.username = username or (username_env and os.environ.get(username_env))
        self.password = password or (password_env and os.environ.get(password_env))
        self.username_env = username_env
        self.password_env = password_env
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers with basic auth"""
        if not self.is_authenticated():
            raise ValueError(f"Credentials for {self.service_name} not set")
        
        # Create basic auth header
        auth_str = f"{self.username}:{self.password}"
        auth_bytes = auth_str.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        return {"Authorization": f"Basic {auth_b64}"}
    
    def is_authenticated(self) -> bool:
        """Check if credentials are available"""
        return bool(self.username and self.password)
    
    def authenticate(self, username: Optional[str] = None, 
                    password: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Set credentials for authentication"""
        # Use provided credentials, or try environment variables again
        if username:
            self.username = username
        elif not self.username and self.username_env:
            self.username = os.environ.get(self.username_env)
            
        if password:
            self.password = password
        elif not self.password and self.password_env:
            self.password = os.environ.get(self.password_env)
        
        if not self.username or not self.password:
            return {"error": f"Credentials for {self.service_name} not provided"}
        
        return {"status": "authenticated", "method": "basic"}

class OAuth2Auth(AuthBase):
    """OAuth2 authentication handler"""
    
    def __init__(self, service_name: str, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None, redirect_uri: Optional[str] = None,
                 auth_url: Optional[str] = None, token_url: Optional[str] = None,
                 scopes: Optional[List[str]] = None,
                 client_id_env: Optional[str] = None,
                 client_secret_env: Optional[str] = None,
                 redirect_uri_env: Optional[str] = None):
        """Initialize OAuth2 handler"""
        super().__init__(service_name)
        
        # Try to get from provided values or environment
        self.client_id = client_id or (client_id_env and os.environ.get(client_id_env))
        self.client_secret = client_secret or (client_secret_env and os.environ.get(client_secret_env))
        self.redirect_uri = redirect_uri or (redirect_uri_env and os.environ.get(redirect_uri_env))
        
        # Store environment variable names for later use
        self.client_id_env = client_id_env
        self.client_secret_env = client_secret_env
        self.redirect_uri_env = redirect_uri_env
        
        # OAuth2 endpoints
        self.auth_url = auth_url
        self.token_url = token_url
        
        # Scopes and token data
        self.scopes = scopes or []
        self.token_data = None
        self.token_expires_at = 0
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers with OAuth2 token"""
        if not self.is_authenticated():
            raise ValueError(f"OAuth2 token for {self.service_name} not available or expired")
        
        return {"Authorization": f"Bearer {self.token_data['access_token']}"}
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with a valid token"""
        return (self.token_data and 'access_token' in self.token_data and 
                time.time() < self.token_expires_at - 300)  # 5 minute buffer
    
    def get_auth_url(self, state: Optional[str] = None) -> str:
        """Get the authorization URL for user login"""
        if not self.auth_url or not self.client_id or not self.redirect_uri:
            raise ValueError("Auth URL, client ID, and redirect URI are required")
        
        # Generate state if not provided
        if not state:
            state = base64.b64encode(os.urandom(16)).decode()
        
        # Build auth URL with parameters
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state
        }
        
        auth_url = f"{self.auth_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return auth_url
    
    async def exchange_code(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.token_url or not self.client_id or not self.redirect_uri:
            return {"error": "Token URL, client ID, and redirect URI are required"}
        
        try:
            # Prepare request data
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id
            }
            
            # Add client secret if available
            if self.client_secret:
                data["client_secret"] = self.client_secret
            
            # Make token request
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            # Parse response
            token_data = response.json()
            
            if "access_token" in token_data:
                self.token_data = token_data
                # Set token expiration time (default to 1 hour if not provided)
                self.token_expires_at = time.time() + token_data.get("expires_in", 3600)
                return token_data
            else:
                return {"error": "No access token in response", "details": token_data}
        
        except Exception as e:
            return {"error": f"Error exchanging code for token: {str(e)}"}
    
    async def refresh_token(self) -> Dict[str, Any]:
        """Refresh the access token"""
        if not self.token_url or not self.client_id:
            return {"error": "Token URL and client ID are required"}
        
        if not self.token_data or "refresh_token" not in self.token_data:
            return {"error": "No refresh token available"}
        
        try:
            # Prepare request data
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.token_data["refresh_token"],
                "client_id": self.client_id
            }
            
            # Add client secret if available
            if self.client_secret:
                data["client_secret"] = self.client_secret
            
            # Make refresh request
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            # Parse response
            new_token_data = response.json()
            
            if "access_token" in new_token_data:
                # Preserve refresh token if not returned
                if "refresh_token" not in new_token_data and "refresh_token" in self.token_data:
                    new_token_data["refresh_token"] = self.token_data["refresh_token"]
                
                self.token_data = new_token_data
                # Set token expiration time (default to 1 hour if not provided)
                self.token_expires_at = time.time() + new_token_data.get("expires_in", 3600)
                return new_token_data
            else:
                return {"error": "No access token in response", "details": new_token_data}
        
        except Exception as e:
            return {"error": f"Error refreshing token: {str(e)}"}
    
    def authenticate(self, token_data: Optional[Dict[str, Any]] = None, 
                   code: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Authenticate using token data or authorization code"""
        # If token data is directly provided
        if token_data and "access_token" in token_data:
            self.token_data = token_data
            self.token_expires_at = time.time() + token_data.get("expires_in", 3600)
            return {"status": "authenticated", "expires_at": self.token_expires_at}
        
        # If code is provided, exchange it for a token
        if code:
            # This is async, so caller needs to await the result
            return {"status": "pending", "action": "exchange_code"}
        
        # If no authentication data provided
        return {"error": "No token data or authorization code provided"}

class MicrosoftAuth(OAuth2Auth):
    """Microsoft-specific OAuth2 authentication handler"""
    
    def __init__(self, service_name: str, client_id: Optional[str] = None, 
                 tenant_id: Optional[str] = None, client_secret: Optional[str] = None,
                 scopes: Optional[List[str]] = None,
                 client_id_env: str = "MS_GRAPH_CLIENT_ID",
                 tenant_id_env: str = "MS_GRAPH_TENANT_ID",
                 client_secret_env: str = "MS_GRAPH_CLIENT_SECRET",
                 redirect_uri: Optional[str] = None,
                 redirect_uri_env: Optional[str] = "MS_GRAPH_REDIRECT_URI"):
        """Initialize Microsoft auth handler"""
        if not MSAL_AVAILABLE:
            raise ImportError("MSAL library is required for Microsoft authentication")
        
        # Get tenant ID from environment if not provided
        tenant_id = tenant_id or os.environ.get(tenant_id_env)
        
        # Define Microsoft-specific endpoints
        authority_url = f"https://login.microsoftonline.com/{tenant_id or 'common'}"
        auth_url = f"{authority_url}/oauth2/v2.0/authorize"
        token_url = f"{authority_url}/oauth2/v2.0/token"
        
        super().__init__(
            service_name=service_name,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            auth_url=auth_url,
            token_url=token_url,
            scopes=scopes,
            client_id_env=client_id_env,
            client_secret_env=client_secret_env,
            redirect_uri_env=redirect_uri_env
        )
        
        # Microsoft-specific attributes
        self.tenant_id = tenant_id
        self.tenant_id_env = tenant_id_env
        self.authority_url = authority_url
        self.app = None
        
        # Initialize MSAL app if credentials are available
        self._initialize_app()
    
    def _initialize_app(self):
        """Initialize the MSAL application"""
        if not self.client_id:
            return
        
        try:
            if self.client_secret:
                # Use confidential client application for service-to-service authentication
                self.app = msal.ConfidentialClientApplication(
                    client_id=self.client_id,
                    authority=self.authority_url,
                    client_credential=self.client_secret
                )
            else:
                # Use public client application for interactive authentication
                self.app = msal.PublicClientApplication(
                    client_id=self.client_id,
                    authority=self.authority_url
                )
            
            self.logger.info(f"Initialized MSAL app for {self.service_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize MSAL app: {str(e)}")
    
    async def authenticate_client_credentials(self) -> Dict[str, Any]:
        """Authenticate using client credentials flow (non-interactive)"""
        if not self.app or not self.client_secret:
            return {"error": "Confidential client app not initialized. Check credentials."}
        
        try:
            # Acquire token using client credentials
            result = self.app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                self.token_data = result
                self.token_expires_at = time.time() + result.get("expires_in", 3600)
                return {"status": "authenticated", "expires_at": self.token_expires_at}
            else:
                error_description = result.get("error_description", "Unknown error")
                return {"error": f"Authentication failed: {error_description}"}
        
        except Exception as e:
            return {"error": f"Client credentials authentication error: {str(e)}"}
    
    async def authenticate_device_code(self) -> Dict[str, Any]:
        """Authenticate using device code flow (interactive)"""
        if not self.app:
            return {"error": "MSAL app not initialized. Check credentials."}
        
        try:
            # Start device code flow
            flow = self.app.initiate_device_flow(scopes=self.scopes)
            if "user_code" not in flow:
                error_description = flow.get("error_description", "Unknown error")
                return {"error": f"Failed to initiate device code flow: {error_description}"}
            
            # Display information for user to authenticate
            message = f"To sign in, use a web browser to open {flow['verification_uri']} and enter the code {flow['user_code']} to authenticate."
            self.logger.info(message)
            print(message)
            
            # Try to open browser automatically
            try:
                webbrowser.open(flow["verification_uri"])
            except:
                pass
            
            # Poll for token
            result = self.app.acquire_token_by_device_flow(flow)
            
            if "access_token" in result:
                self.token_data = result
                self.token_expires_at = time.time() + result.get("expires_in", 3600)
                return {"status": "authenticated", "expires_at": self.token_expires_at}
            else:
                error_description = result.get("error_description", "Unknown error")
                return {"error": f"Authentication failed: {error_description}"}
        
        except Exception as e:
            return {"error": f"Device code authentication error: {str(e)}"}
    
    def authenticate(self, method: str = "device_code", **kwargs) -> Dict[str, Any]:
        """Authenticate using the specified method"""
        if method == "client_credentials":
            # This is async, so caller needs to await the result
            return {"status": "pending", "action": "authenticate_client_credentials"}
        elif method == "device_code":
            # This is async, so caller needs to await the result
            return {"status": "pending", "action": "authenticate_device_code"}
        else:
            return {"error": f"Unsupported authentication method: {method}"}

def register_auth_handler(service_name: str, handler: AuthBase) -> None:
    """Register an authentication handler for a service"""
    _AUTH_HANDLERS[service_name.lower()] = handler
    logging.info(f"Registered auth handler for {service_name}")

def get_auth_handler(service_name: str) -> Optional[AuthBase]:
    """Get the authentication handler for a service"""
    return _AUTH_HANDLERS.get(service_name.lower())

def create_auth_handler(service_name: str, auth_type: str, **kwargs) -> AuthBase:
    """Create and register an authentication handler"""
    handler = None
    
    if auth_type.lower() == "api_key":
        handler = ApiKeyAuth(service_name, **kwargs)
    elif auth_type.lower() == "basic":
        handler = BasicAuth(service_name, **kwargs)
    elif auth_type.lower() == "oauth2":
        handler = OAuth2Auth(service_name, **kwargs)
    elif auth_type.lower() == "microsoft":
        handler = MicrosoftAuth(service_name, **kwargs)
    else:
        raise ValueError(f"Unsupported auth type: {auth_type}")
    
    # Register the handler
    register_auth_handler(service_name, handler)
    
    return handler
