#!/usr/bin/env python3
"""
Tool functions for SharePoint API.
"""
import json
from typing import Dict, Any, Optional
from mcp.server.fastmcp import Context

from app.tools.base.registry import register_tool
from app.tools.sharepoint.service import SharePointService, get_service


@register_tool(category="sharepoint")
async def sharepoint_authenticate(
    auth_method: str = "device_code", 
    client_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Authenticate with Microsoft SharePoint.
    
    Establishes authentication with SharePoint using one of the supported methods.
    
    Parameters:
    - auth_method: Authentication method to use ("device_code" or "client_credentials")
    - client_id: Microsoft application client ID
    - tenant_id: Microsoft tenant ID
    - client_secret: Microsoft client secret (required for client_credentials method)
    
    Returns:
    - JSON string with authentication result
    """
    sharepoint = get_service()
    
    try:
        if auth_method == "device_code":
            result = await sharepoint.authenticate_device_code()
        elif auth_method == "client_credentials":
            result = await sharepoint.authenticate_client_credentials()
        else:
            result = {"error": "Invalid authentication method. Use 'device_code' or 'client_credentials'"}
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Authentication error: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_list_sites(
    search: Optional[str] = None, 
    ctx: Context = None
) -> str:
    """List available SharePoint sites.
    
    Parameters:
    - search: Optional search term to filter sites
    
    Returns:
    - JSON string with list of sites
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.list_sites(search)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing sites: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_list_drives(
    site_id: Optional[str] = None, 
    ctx: Context = None
) -> str:
    """List available drives in a SharePoint site.
    
    Parameters:
    - site_id: ID of the site to list drives from (optional)
    
    Returns:
    - JSON string with list of drives
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.list_drives(site_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing drives: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_list_items(
    drive_id: str, 
    folder_id: str = "root", 
    ctx: Context = None
) -> str:
    """List files and folders in a SharePoint drive or folder.
    
    Parameters:
    - drive_id: ID of the drive
    - folder_id: ID of the folder (default: "root")
    
    Returns:
    - JSON string with list of items
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.list_items(drive_id, folder_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing items: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_download_file(
    drive_id: str, 
    item_id: str, 
    output_path: Optional[str] = None, 
    ctx: Context = None
) -> str:
    """Download a file from SharePoint.
    
    Parameters:
    - drive_id: ID of the drive containing the file
    - item_id: ID of the file to download
    - output_path: Local path to save the file (optional)
    
    Returns:
    - JSON string with download result
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.download_file(drive_id, item_id, output_path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error downloading file: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_upload_file(
    drive_id: str, 
    folder_id: str, 
    file_path: str,
    conflict_behavior: str = "replace", 
    ctx: Context = None
) -> str:
    """Upload a file to SharePoint.
    
    Parameters:
    - drive_id: ID of the drive to upload to
    - folder_id: ID of the folder to upload to
    - file_path: Local path of the file to upload
    - conflict_behavior: How to handle name conflicts (replace, rename, fail)
    
    Returns:
    - JSON string with upload result
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.upload_file(drive_id, folder_id, file_path, conflict_behavior)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error uploading file: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_create_folder(
    drive_id: str, 
    parent_id: str, 
    folder_name: str, 
    ctx: Context = None
) -> str:
    """Create a new folder in SharePoint.
    
    Parameters:
    - drive_id: ID of the drive to create the folder in
    - parent_id: ID of the parent folder
    - folder_name: Name of the new folder
    
    Returns:
    - JSON string with folder creation result
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.create_folder(drive_id, parent_id, folder_name)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating folder: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_delete_item(
    drive_id: str, 
    item_id: str, 
    ctx: Context = None
) -> str:
    """Delete a file or folder from SharePoint.
    
    Parameters:
    - drive_id: ID of the drive containing the item
    - item_id: ID of the item to delete
    
    Returns:
    - JSON string with deletion result
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.delete_item(drive_id, item_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error deleting item: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_search_items(
    drive_id: str, 
    query: str, 
    folder_id: Optional[str] = None, 
    ctx: Context = None
) -> str:
    """Search for items in a SharePoint drive or folder.
    
    Parameters:
    - drive_id: ID of the drive to search in
    - query: Search query
    - folder_id: ID of the folder to limit search to (optional)
    
    Returns:
    - JSON string with search results
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.search_items(drive_id, query, folder_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error searching items: {str(e)}"})


@register_tool(category="sharepoint")
async def sharepoint_get_item_info(
    drive_id: str, 
    item_id: str, 
    ctx: Context = None
) -> str:
    """Get information about a file or folder in SharePoint.
    
    Parameters:
    - drive_id: ID of the drive containing the item
    - item_id: ID of the item to get information about
    
    Returns:
    - JSON string with item information
    """
    sharepoint = get_service()
    
    try:
        result = await sharepoint.get_item_info(drive_id, item_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error getting item info: {str(e)}"})
