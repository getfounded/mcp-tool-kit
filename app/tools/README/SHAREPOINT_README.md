# SharePoint API Tool for MCP

A comprehensive tool for integrating with Microsoft SharePoint via the Microsoft Graph API, enabling Claude to upload, download, and manage files in SharePoint.

## Overview

The SharePoint API Tool provides seamless access to SharePoint sites, document libraries, and files through Microsoft's Graph API. This enables:

- Authentication via device code flow (interactive) or client credentials (automated)
- Browsing SharePoint sites and document libraries (drives)
- Uploading and downloading files (including large file support)
- Creating and managing folders
- Searching for content
- Managing file metadata

## Installation

1. Add the `sharepoint.py` file to your `tools` directory in the MCP Unified Server
2. Install required dependencies:
   ```bash
   pip install msal requests