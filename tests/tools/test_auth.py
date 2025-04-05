#!/usr/bin/env python3
"""
Unit tests for authentication utilities.
"""
import pytest
import os
import json
import base64
import time
from unittest.mock import patch, MagicMock

from app.tools.utils.auth import (
    AuthBase, ApiKeyAuth, BasicAuth, OAuth2Auth, MicrosoftAuth,
    register_auth_handler, get_auth_handler, create_auth_handler
)


class TestApiKeyAuth:

    def test_initialization(self):
        """Test API key auth initialization"""
        # Initialize with direct API key
        auth = ApiKeyAuth("test_service", api_key="test_key",
                          header_name="X-API-Key")
        assert auth.service_name == "test_service"
        assert auth.api_key == "test_key"
        assert auth.header_name == "X-API-Key"

        # Initialize with environment variable
        with patch.dict(os.environ, {"TEST_API_KEY": "env_key"}):
            auth = ApiKeyAuth("test_service", env_var="TEST_API_KEY")
            assert auth.api_key == "env_key"

    def test_is_authenticated(self):
        """Test is_authenticated functionality"""
        # Should be authenticated if API key is set
        auth = ApiKeyAuth("test_service", api_key="test_key")
        assert auth.is_authenticated() == True

        # Should not be authenticated if API key is not set
        auth = ApiKeyAuth("test_service")
        assert auth.is_authenticated() == False

    def test_get_auth_headers(self):
        """Test get_auth_headers functionality"""
        auth = ApiKeyAuth("test_service", api_key="test_key",
                          header_name="X-API-Key")
        headers = auth.get_auth_headers()
        assert headers == {"X-API-Key": "test_key"}

        # Should raise error if not authenticated
        auth = ApiKeyAuth("test_service")
        with pytest.raises(ValueError, match="API key for test_service not set"):
            auth.get_auth_headers()

    def test_authenticate(self):
        """Test authenticate functionality"""
        auth = ApiKeyAuth("test_service")

        # Authenticate with direct API key
        result = auth.authenticate(api_key="new_key")
        assert result["status"] == "authenticated"
        assert auth.api_key == "new_key"

        # Authenticate with environment variable
        with patch.dict(os.environ, {"TEST_API_KEY": "env_key"}):
            auth = ApiKeyAuth("test_service", env_var="TEST_API_KEY")
            result = auth.authenticate()
            assert result["status"] == "authenticated"
            assert auth.api_key == "env_key"

        # Authenticate with missing key
        auth = ApiKeyAuth("test_service")
        result = auth.authenticate()
        assert "error" in result


class TestBasicAuth:

    def test_initialization(self):
        """Test basic auth initialization"""
        # Initialize with direct credentials
        auth = BasicAuth("test_service", username="user", password="pass")
        assert auth.service_name == "test_service"
        assert auth.username == "user"
        assert auth.password == "pass"

        # Initialize with environment variables
        with patch.dict(os.environ, {"TEST_USERNAME": "env_user", "TEST_PASSWORD": "env_pass"}):
            auth = BasicAuth(
                "test_service",
                username_env="TEST_USERNAME",
                password_env="TEST_PASSWORD"
            )
            assert auth.username == "env_user"
            assert auth.password == "env_pass"

    def test_is_authenticated(self):
        """Test is_authenticated functionality"""
        # Should be authenticated if username and password are set
        auth = BasicAuth("test_service", username="user", password="pass")
        assert auth.is_authenticated() == True

        # Should not be authenticated if either is missing
        auth = BasicAuth("test_service", username="user")
        assert auth.is_authenticated() == False

        auth = BasicAuth("test_service", password="pass")
        assert auth.is_authenticated() == False

    def test_get_auth_headers(self):
        """Test get_auth_headers functionality"""
        auth = BasicAuth("test_service", username="user", password="pass")
        headers = auth.get_auth_headers()

        # Header should be "Basic " + base64(user:pass)
        expected_token = "Basic " + \
            base64.b64encode("user:pass".encode()).decode()
        assert headers["Authorization"] == expected_token

        # Should raise error if not authenticated
        auth = BasicAuth("test_service")
        with pytest.raises(ValueError, match="Credentials for test_service not set"):
            auth.get_auth_headers()

    def test_authenticate(self):
        """Test authenticate functionality"""
        auth = BasicAuth("test_service")

        # Authenticate with direct credentials
        result = auth.authenticate(username="new_user", password="new_pass")
        assert result["status"] == "authenticated"
        assert auth.username == "new_user"
        assert auth.password == "new_pass"

        # Authenticate with missing credentials
        auth = BasicAuth("test_service")
        result = auth.authenticate()
        assert "error" in result


class TestOAuth2Auth:

    def test_initialization(self):
        """Test OAuth2 auth initialization"""
        # Initialize with direct values
        auth = OAuth2Auth(
            "test_service",
            client_id="client_id",
            client_secret="client_secret",
            redirect_uri="https://example.com/callback",
            auth_url="https://auth.example.com/oauth2/authorize",
            token_url="https://auth.example.com/oauth2/token",
            scopes=["read", "write"]
        )
        assert auth.service_name == "test_service"
        assert auth.client_id == "client_id"
        assert auth.client_secret == "client_secret"
        assert auth.redirect_uri == "https://example.com/callback"
        assert auth.auth_url == "https://auth.example.com/oauth2/authorize"
        assert auth.token_url == "https://auth.example.com/oauth2/token"
        assert auth.scopes == ["read", "write"]

        # Initialize with environment variables
        with patch.dict(os.environ, {
            "TEST_CLIENT_ID": "env_client_id",
            "TEST_CLIENT_SECRET": "env_client_secret",
            "TEST_REDIRECT_URI": "https://env-example.com/callback"
        }):
            auth = OAuth2Auth(
                "test_service",
                client_id_env="TEST_CLIENT_ID",
                client_secret_env="TEST_CLIENT_SECRET",
                redirect_uri_env="TEST_REDIRECT_URI"
            )
            assert auth.client_id == "env_client_id"
            assert auth.client_secret == "env_client_secret"
            assert auth.redirect_uri == "https://env-example.com/callback"

    def test_is_authenticated(self):
        """Test is_authenticated functionality"""
        auth = OAuth2Auth("test_service")

        # Should not be authenticated initially
        assert auth.is_authenticated() == False

        # Set token data and expiration
        auth.token_data = {"access_token": "test_token"}
        auth.token_expires = time.time() + 3600  # 1 hour from now
        assert auth.is_authenticated() == True

        # Test with expired token
        auth.token_expires = time.time() - 3600  # 1 hour in the past
        assert auth.is_authenticated() == False

    def test_get_auth_headers(self):
        """Test get_auth_headers functionality"""
        auth = OAuth2Auth("test_service")
        auth.token_data = {"access_token": "test_token"}
        auth.token_expires = time.time() + 3600  # 1 hour from now

        headers = auth.get_auth_headers()
        assert headers["Authorization"] == "Bearer test_token"

        # Should raise error if not authenticated
        auth = OAuth2Auth("test_service")
        with pytest.raises(ValueError, match="OAuth2 token for test_service not available or expired"):
            auth.get_auth_headers()

    def test_get_auth_url(self):
        """Test get_auth_url functionality"""
        auth = OAuth2Auth(
            "test_service",
            client_id="client_id",
            redirect_uri="https://example.com/callback",
            auth_url="https://auth.example.com/oauth2/authorize",
            scopes=["read", "write"]
        )

        # Get auth URL with provided state
        url = auth.get_auth_url(state="test_state")

        # URL should contain all required parameters
        assert "https://auth.example.com/oauth2/authorize" in url
        assert "response_type=code" in url
        assert "client_id=client_id" in url
        assert "redirect_uri=https://example.com/callback" in url
        assert "scope=read%20write" in url
        assert "state=test_state" in url

        # Test with missing required parameters
        auth = OAuth2Auth("test_service")
        with pytest.raises(ValueError, match="Auth URL, client ID, and redirect URI are required"):
            auth.get_auth_url()

    def test_authenticate(self):
        """Test authenticate functionality"""
        auth = OAuth2Auth("test_service")

        # Authenticate with token data
        token_data = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_in": 3600
        }
        result = auth.authenticate(token_data=token_data)
        assert result["status"] == "authenticated"
        assert auth.token_data == token_data
        assert auth.token_expires > time.time()

        # Authenticate with authorization code
        result = auth.authenticate(code="test_code")
        assert result["status"] == "pending"
        assert result["action"] == "exchange_code"

        # Authenticate with missing data
        result = auth.authenticate()
        assert "error" in result


class TestAuthHandlerRegistry:

    def setup_method(self):
        """Clear the auth handler registry before each test"""
        from app.tools.utils.auth import _AUTH_HANDLERS
        _AUTH_HANDLERS.clear()

    def test_register_and_get_handler(self):
        """Test registering and retrieving auth handlers"""
        # Create and register an auth handler
        auth = ApiKeyAuth("test_service", api_key="test_key")
        register_auth_handler("test_service", auth)

        # Retrieve the handler
        retrieved_auth = get_auth_handler("test_service")
        assert retrieved_auth is auth

        # Case-insensitive lookup
        retrieved_auth = get_auth_handler("TEST_SERVICE")
        assert retrieved_auth is auth

        # Non-existent handler
        assert get_auth_handler("nonexistent") is None

    def test_create_auth_handler(self):
        """Test creating auth handlers of different types"""
        # Create API key auth
        auth = create_auth_handler(
            "api_service",
            "api_key",
            api_key="test_key"
        )
        assert isinstance(auth, ApiKeyAuth)
        assert auth.api_key == "test_key"

        # Create basic auth
        auth = create_auth_handler(
            "basic_service",
            "basic",
            username="user",
            password="pass"
        )
        assert isinstance(auth, BasicAuth)
        assert auth.username == "user"
        assert auth.password == "pass"

        # Create OAuth2 auth
        auth = create_auth_handler(
            "oauth_service",
            "oauth2",
            client_id="client_id",
            client_secret="client_secret"
        )
        assert isinstance(auth, OAuth2Auth)
        assert auth.client_id == "client_id"
        assert auth.client_secret == "client_secret"

        # Create with invalid type
        with pytest.raises(ValueError, match="Unsupported auth type"):
            create_auth_handler("invalid_service", "invalid_type")
