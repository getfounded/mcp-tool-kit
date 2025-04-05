#!/usr/bin/env python3
"""
SharePoint tools for MCP toolkit.
"""

# Import the tools to ensure they are registered
from app.tools.sharepoint.tools import (
    sharepoint_authenticate,
    sharepoint_list_sites,
    sharepoint_list_drives,
    sharepoint_list_items,
    sharepoint_download_file,
    sharepoint_upload_file,
    sharepoint_create_folder,
    sharepoint_delete_item,
    sharepoint_search_items,
    sharepoint_get_item_info
)
