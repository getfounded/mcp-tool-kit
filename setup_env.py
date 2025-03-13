#!/usr/bin/env python3
"""
Environment Setup Script for MCP Tool Kit

This script helps you set up environment variables for the MCP Tool Kit
by creating or updating a .env file in the repository.

Usage:
    python setup_env.py
"""
import os
import sys
from pathlib import Path


def main():
    print("MCP Tool Kit Environment Setup")
    print("==============================")
    print("This script will help you set up environment variables for the MCP Tool Kit.")
    print("It will create or update a .env file in the repository root.")
    print()

    # Check if .env file exists
    env_file = Path(".env")
    existing_vars = {}

    if env_file.exists():
        print(f"Found existing .env file at {env_file.absolute()}")
        # Parse existing variables
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key.strip()] = value.strip()
        print(f"Found {len(existing_vars)} existing variables.")
        print()

        update = input(
            "Do you want to update the existing .env file? (y/n): ").lower()
        if update != 'y':
            print("Setup canceled. Existing .env file was not modified.")
            return

    # Define required environment variables with descriptions
    env_vars = {
        "BRAVE_API_KEY": {
            "description": "API key for Brave Search functionality",
            "required": True,
            "default": existing_vars.get("BRAVE_API_KEY", ""),
            "example": "YOUR_BRAVE_API_KEY",
            "url": "https://brave.com/search/api/"
        },
        "BROWSERBASE_API_KEY": {
            "description": "API key for browser automation functionality",
            "required": True,
            "default": existing_vars.get("BROWSERBASE_API_KEY", ""),
            "example": "YOUR_BROWSERBASE_API_KEY",
            "url": "https://browserbase.io/"
        },
        "BROWSERBASE_PROJECT_ID": {
            "description": "Project ID for browser automation functionality",
            "required": True,
            "default": existing_vars.get("BROWSERBASE_PROJECT_ID", ""),
            "example": "YOUR_BROWSERBASE_PROJECT_ID",
            "url": "https://browserbase.io/"
        },
        "NEWS_API_KEY": {
            "description": "API key for NewsAPI functionality",
            "required": True,
            "default": existing_vars.get("NEWS_API_KEY", ""),
            "example": "YOUR_NEWS_API_KEY",
            "url": "https://newsapi.org/"
        },
        "FRED_API_KEY": {
            "description": "API key for FRED economic data API",
            "required": True,
            "default": existing_vars.get("FRED_API_KEY", ""),
            "example": "YOUR_FRED_API_KEY",
            "url": "https://fred.stlouisfed.org/docs/api/api_key.html"
        },
        "STREAMLIT_APPS_DIR": {
            "description": "Directory for Streamlit applications",
            "required": False,
            "default": existing_vars.get("STREAMLIT_APPS_DIR", os.path.expanduser("~/streamlit_apps")),
            "example": "/path/to/streamlit/apps"
        },
        "MCP_FILESYSTEM_DIRS": {
            "description": "Comma-separated list of directories that can be accessed by filesystem tools",
            "required": False,
            "default": existing_vars.get("MCP_FILESYSTEM_DIRS", os.path.expanduser("~")),
            "example": "/path/to/dir1,/path/to/dir2"
        },
        "MCP_LOG_LEVEL": {
            "description": "Logging level (debug, info, warning, error)",
            "required": False,
            "default": existing_vars.get("MCP_LOG_LEVEL", "info"),
            "example": "info"
        }
    }

    # Collect values from user
    new_values = {}
    print("\nPlease enter values for the following environment variables:")
    print("(Press Enter to use default or existing value shown in brackets)")
    print()

    for key, info in env_vars.items():
        default = info["default"]
        default_display = f"[{default}]" if default else ""

        # Show URL for API keys that need to be obtained
        url_info = f" (Get it from: {info['url']})" if "url" in info else ""

        while True:
            prompt = f"{key}: {info['description']}{url_info} {default_display}: "
            value = input(prompt).strip()

            # Use default if empty
            if not value and default:
                value = default

            # Validate required fields
            if info["required"] and not value:
                print(f"Error: {key} is required.")
                continue

            new_values[key] = value
            break

    # Write to .env file
    print("\nWriting environment variables to .env file...")

    with open(env_file, 'w') as f:
        f.write("# Environment variables for MCP Tool Kit\n")
        f.write("# Generated by setup_env.py\n\n")

        for key, info in env_vars.items():
            if key in new_values and new_values[key]:
                f.write(f"# {info['description']}\n")
                f.write(f"{key}={new_values[key]}\n\n")

    print(
        f"Environment setup complete. Configuration saved to {env_file.absolute()}")
    print("\nYou can manually edit this file at any time to update your configuration.")
    print("Remember to restart the MCP server after changing environment variables.")


if __name__ == "__main__":
    main()
