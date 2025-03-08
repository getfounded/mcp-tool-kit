#!/usr/bin/env python3
"""
QuickBooks Configuration Utility

This script helps set up and test the QuickBooks integration by:
1. Walking through the OAuth2 setup process for QuickBooks
2. Testing the connection
3. Creating a configuration file or .env file

Usage:
    python qb_config.py setup  # Run the initial setup
    python qb_config.py test   # Test the configuration
"""

import os
import sys
import json
import time
import webbrowser
import base64
from urllib.parse import urlencode, parse_qs
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Default configuration
DEFAULT_CONFIG = {
    "QB_CLIENT_ID": "",
    "QB_CLIENT_SECRET": "",
    "QB_REDIRECT_URI": "http://localhost:8080/callback",
    "QB_REFRESH_TOKEN": "",
    "QB_REALM_ID": ""
}

# QuickBooks API URLs
AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
API_BASE_URL = "https://quickbooks.api.intuit.com/v3/company"

# Try to load existing environment variables
load_dotenv()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle the OAuth callback"""

    def do_GET(self):
        """Handle GET requests to the server"""
        # Parse query parameters
        query_components = parse_qs(self.path.split(
            '?')[1]) if '?' in self.path else {}

        if self.path.startswith('/callback'):
            # Extract the authorization code
            auth_code = query_components.get('code', [''])[0]
            realm_id = query_components.get('realmId', [''])[0]

            # Store in the class for retrieval
            self.__class__.auth_code = auth_code
            self.__class__.realm_id = realm_id

            # Respond to the client
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Send a success message
            response = """
            <html>
            <head><title>Authentication Successful</title></head>
            <body>
                <h1>Authentication Successful!</h1>
                <p>You have successfully authenticated with QuickBooks. You can close this window now.</p>
            </body>
            </html>
            """
            self.wfile.write(response.encode('utf-8'))

            # Signal the server to shut down
            self.__class__.should_shutdown = True

    def log_message(self, format, *args):
        """Suppress logging"""
        return


def get_config_path():
    """Get the path for the configuration file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qb_config.json')


def load_config():
    """Load configuration from file or environment variables"""
    config_path = get_config_path()
    config = DEFAULT_CONFIG.copy()

    # Try to load from file
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Warning: Error loading configuration file: {str(e)}")

    # Override with environment variables
    for key in config:
        if os.environ.get(key):
            config[key] = os.environ.get(key)

    return config


def save_config(config):
    """Save configuration to file"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
    except Exception as e:
        print(f"Error saving configuration: {str(e)}")


def create_env_file(config):
    """Create .env file from configuration"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    try:
        with open(env_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        print(f"Environment variables saved to {env_path}")
    except Exception as e:
        print(f"Error creating .env file: {str(e)}")


def start_oauth_flow(config):
    """Start the OAuth flow for QuickBooks"""
    # Start a local server to handle the callback
    OAuthCallbackHandler.should_shutdown = False
    OAuthCallbackHandler.auth_code = None
    OAuthCallbackHandler.realm_id = None

    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)

    # Build the authorization URL
    auth_params = {
        'client_id': config['QB_CLIENT_ID'],
        'redirect_uri': config['QB_REDIRECT_URI'],
        'response_type': 'code',
        'scope': 'com.intuit.quickbooks.accounting',
        'state': str(int(time.time()))
    }

    auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"

    print(f"Opening browser to authorize QuickBooks integration...")
    webbrowser.open(auth_url)

    print("Waiting for authorization callback...")

    # Run the server until we get the callback
    while not OAuthCallbackHandler.should_shutdown:
        server.handle_request()

    # Get the authorization code and realm ID
    auth_code = OAuthCallbackHandler.auth_code
    realm_id = OAuthCallbackHandler.realm_id

    if not auth_code:
        print("Error: No authorization code received")
        return config

    print(f"Authorization code received")
    print(f"Realm ID (Company ID): {realm_id}")

    # Exchange the authorization code for tokens
    client_id = config['QB_CLIENT_ID']
    client_secret = config['QB_CLIENT_SECRET']
    redirect_uri = config['QB_REDIRECT_URI']

    token_params = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }

    # Create basic auth header
    auth_string = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(TOKEN_URL, headers=headers, data=token_params)
        response.raise_for_status()
        token_data = response.json()

        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            print("Error: No refresh token received")
            return config

        # Update the configuration
        config['QB_REFRESH_TOKEN'] = refresh_token
        config['QB_REALM_ID'] = realm_id

        print("Successfully obtained refresh token and company ID")

    except Exception as e:
        print(f"Error exchanging authorization code for tokens: {str(e)}")

    return config


def test_connection(config):
    """Test the connection to QuickBooks API"""
    # Check for required configuration
    required_keys = ['QB_CLIENT_ID', 'QB_CLIENT_SECRET',
                     'QB_REDIRECT_URI', 'QB_REFRESH_TOKEN', 'QB_REALM_ID']
    missing_keys = [key for key in required_keys if not config.get(key)]

    if missing_keys:
        print(
            f"Error: Missing required configuration: {', '.join(missing_keys)}")
        return False

    # Get access token using refresh token
    client_id = config['QB_CLIENT_ID']
    client_secret = config['QB_CLIENT_SECRET']
    refresh_token = config['QB_REFRESH_TOKEN']
    realm_id = config['QB_REALM_ID']

    # Create basic auth header
    auth_string = f"{client_id}:{client_secret}"
    auth_header = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    token_params = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    try:
        print("Testing connection to QuickBooks API...")

        # Get access token
        response = requests.post(TOKEN_URL, headers=headers, data=token_params)
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get('access_token')
        if not access_token:
            print("Error: Failed to obtain access token")
            return False

        # Test API access by getting company info
        api_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        api_url = f"{API_BASE_URL}/{realm_id}/companyinfo/{realm_id}"
        response = requests.get(api_url, headers=api_headers)
        response.raise_for_status()

        company_data = response.json()
        company_name = company_data.get(
            'CompanyInfo', {}).get('CompanyName', 'Unknown')

        print(
            f"Successfully connected to QuickBooks for company: {company_name}")

        # Update refresh token if a new one was provided
        if token_data.get('refresh_token'):
            config['QB_REFRESH_TOKEN'] = token_data.get('refresh_token')
            print("Updated refresh token with new value")
            save_config(config)

        return True

    except Exception as e:
        print(f"Error testing connection: {str(e)}")
        return False


def setup_config():
    """Guide the user through setting up QuickBooks integration"""
    print("=== QuickBooks Integration Setup ===")
    print("\nThis utility will help you set up the QuickBooks integration.")
    print("You'll need to have a QuickBooks Online Developer account and an app set up.")
    print("Visit https://developer.intuit.com/ to get started.\n")

    config = load_config()

    # Get client ID and secret
    config['QB_CLIENT_ID'] = input(
        f"Enter your QuickBooks Client ID [{config['QB_CLIENT_ID']}]: ") or config['QB_CLIENT_ID']
    config['QB_CLIENT_SECRET'] = input(
        f"Enter your QuickBooks Client Secret [{config['QB_CLIENT_SECRET']}]: ") or config['QB_CLIENT_SECRET']

    # Set default redirect URI
    if not config['QB_REDIRECT_URI']:
        config['QB_REDIRECT_URI'] = "http://localhost:8080/callback"

    print(f"\nRedirect URI set to: {config['QB_REDIRECT_URI']}")
    print("Make sure this exact redirect URI is configured in your QuickBooks app settings!")

    # Ask to proceed with OAuth flow
    proceed = input(
        "\nProceed with OAuth authorization? (y/n): ").lower() == 'y'

    if proceed:
        config = start_oauth_flow(config)

    # Save the configuration
    save_config(config)

    # Create .env file
    create_env = input(
        "\nCreate .env file with these settings? (y/n): ").lower() == 'y'
    if create_env:
        create_env_file(config)

    # Test the connection
    test = input("\nTest the connection to QuickBooks? (y/n): ").lower() == 'y'
    if test:
        test_connection(config)

    print("\nSetup complete!")


def main():
    """Main entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'

    if command == 'setup':
        setup_config()
    elif command == 'test':
        config = load_config()
        test_connection(config)
    else:
        print("Usage:")
        print("  python qb_config.py setup  # Run the initial setup")
        print("  python qb_config.py test   # Test the configuration")


if __name__ == "__main__":
    main()
