#!/usr/bin/env python3
import os
import json
import logging
import asyncio
import tempfile
import time
from enum import Enum
from typing import List, Dict, Optional, Any, Union, BinaryIO
from pathlib import Path

# Microsoft Authentication Library for handling OAuth
import msal
# For HTTP requests
import requests

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None

def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("SharePoint API tools MCP reference set")


class SharePointTools(str, Enum):
    """Enum of SharePoint tool names"""
    AUTHENTICATE = "sharepoint_authenticate"
    LIST_SITES = "sharepoint_list_sites"
    LIST_DRIVES = "sharepoint_list_drives"
    LIST_ITEMS = "sharepoint_list_items"
    DOWNLOAD_FILE = "sharepoint_download_file"
    UPLOAD_FILE = "sharepoint_upload_file"
    CREATE_FOLDER = "sharepoint_create_folder"
    DELETE_ITEM = "sharepoint_delete_item"
    SEARCH_ITEMS = "sharepoint_search_items"
    GET_ITEM_INFO = "sharepoint_get_item_info"


class SharePointService:
    """Service to handle SharePoint operations via Microsoft Graph API"""
    
    def __init__(self, client_id=None, tenant_id=None, client_secret=None):
        """Initialize SharePoint service with authentication parameters"""
        # Try to get credentials from environment if not provided
        self.client_id = client_id or os.environ.get("MS_GRAPH_CLIENT_ID")
        self.tenant_id = tenant_id or os.environ.get("MS_GRAPH_TENANT_ID")
        self.client_secret = client_secret or os.environ.get("MS_GRAPH_CLIENT_SECRET")
        
        # Set default attributes
        self.app = None
        self.access_token = None
        self.token_expires_at = 0
        self.authenticated = False
        self.temp_dir = tempfile.mkdtemp(prefix="sharepoint_")
        
        # Microsoft Graph API endpoints
        self.authority_url = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_url = "https://graph.microsoft.com/v1.0"
        
        # Required scopes for SharePoint operations
        self.scopes = [
            "https://graph.microsoft.com/Files.ReadWrite.All",
            "https://graph.microsoft.com/Sites.ReadWrite.All"
        ]
        
        # Initialize MSAL app if credentials are available
        if self.client_id and self.tenant_id:
            self._initialize_app()
            logging.info("SharePoint service initialized")
        else:
            logging.warning("SharePoint credentials not provided. Authentication will fail.")
    
    def _initialize_app(self):
        """Initialize the MSAL application"""
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
    
    def _is_token_valid(self):
        """Check if the current access token is valid"""
        return self.access_token and time.time() < self.token_expires_at - 300  # 5 minute buffer
    
    async def authenticate_device_code(self):
        """Authenticate using device code flow (interactive)"""
        if not self.app:
            return {"error": "MSAL app not initialized. Check credentials."}
        
        try:
            # Start device code flow
            flow = self.app.initiate_device_flow(scopes=self.scopes)
            if "user_code" not in flow:
                return {"error": f"Failed to initiate device code flow: {flow.get('error_description', 'Unknown error')}"}
            
            # Return information for user to complete authentication
            print(f"To sign in, use a web browser to open {flow['verification_uri']} and enter the code {flow['user_code']} to authenticate.")
            
            # Poll for token
            result = self.app.acquire_token_by_device_flow(flow)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expires_at = time.time() + result.get("expires_in", 3600)
                self.authenticated = True
                return {"status": "authenticated", "expires_at": self.token_expires_at}
            else:
                return {"error": f"Authentication failed: {result.get('error_description', 'Unknown error')}"}
        
        except Exception as e:
            return {"error": f"Device code authentication error: {str(e)}"}
    
    async def authenticate_client_credentials(self):
        """Authenticate using client credentials flow (non-interactive)"""
        if not self.app or not self.client_secret:
            return {"error": "Confidential client app not initialized. Check credentials."}
        
        try:
            # Acquire token using client credentials
            result = self.app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expires_at = time.time() + result.get("expires_in", 3600)
                self.authenticated = True
                return {"status": "authenticated", "expires_at": self.token_expires_at}
            else:
                return {"error": f"Authentication failed: {result.get('error_description', 'Unknown error')}"}
        
        except Exception as e:
            return {"error": f"Client credentials authentication error: {str(e)}"}
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self._is_token_valid():
            if self.client_secret:
                return await self.authenticate_client_credentials()
            else:
                return {"error": "Not authenticated. Please call authenticate_device_code first."}
        return {"status": "authenticated", "expires_at": self.token_expires_at}
    
    async def _make_request(self, method, endpoint, params=None, data=None, json_data=None, headers=None, stream=False):
        """Make authenticated request to Microsoft Graph API"""
        # Ensure authentication
        auth_result = await self._ensure_authenticated()
        if "error" in auth_result:
            return auth_result
        
        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        if headers:
            request_headers.update(headers)
        
        # Prepare URL
        url = f"{self.graph_url}/{endpoint}"
        
        # Make request
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                stream=stream
            )
            
            # Handle response
            if response.status_code >= 400:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = f"{error_msg} - {error_data['error'].get('message', 'Unknown error')}"
                except:
                    error_msg = f"{error_msg} - {response.text}"
                
                return {"error": error_msg}
            
            # Return streamed response if requested
            if stream:
                return response
            
            # Return JSON if available, otherwise text
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            else:
                return {"content": response.text}
            
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    async def list_sites(self, search=None):
        """List available SharePoint sites"""
        endpoint = "sites"
        params = {}
        
        if search:
            params["search"] = search
        
        return await self._make_request("GET", endpoint, params=params)
    
    async def list_drives(self, site_id=None):
        """List available drives in a SharePoint site"""
        if site_id:
            endpoint = f"sites/{site_id}/drives"
        else:
            endpoint = "me/drives"
        
        return await self._make_request("GET", endpoint)
    
    async def list_items(self, drive_id, folder_id="root"):
        """List items (files and folders) in a drive folder"""
        endpoint = f"drives/{drive_id}/items/{folder_id}/children"
        return await self._make_request("GET", endpoint)
    
    async def download_file(self, drive_id, item_id, output_path=None):
        """Download a file from SharePoint"""
        endpoint = f"drives/{drive_id}/items/{item_id}/content"
        
        # Get file info to determine name if output_path is not specified
        if not output_path:
            file_info = await self.get_item_info(drive_id, item_id)
            if "error" in file_info:
                return file_info
            
            file_name = file_info.get("name", f"download_{item_id}")
            output_path = os.path.join(self.temp_dir, file_name)
        
        # Stream the file download
        response = await self._make_request("GET", endpoint, stream=True)
        if isinstance(response, dict) and "error" in response:
            return response
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                    f.write(chunk)
            
            return {
                "status": "success",
                "file_path": output_path,
                "size": os.path.getsize(output_path)
            }
        
        except Exception as e:
            return {"error": f"Error saving file: {str(e)}"}
    
    async def upload_file(self, drive_id, folder_id, file_path, conflict_behavior="replace"):
        """Upload a file to SharePoint"""
        # Get file name and size
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Different upload methods based on file size
        if file_size <= 4 * 1024 * 1024:  # 4MB - Simple upload
            return await self._simple_upload(drive_id, folder_id, file_path, file_name, conflict_behavior)
        else:
            return await self._chunked_upload(drive_id, folder_id, file_path, file_name, file_size, conflict_behavior)
    
    async def _simple_upload(self, drive_id, folder_id, file_path, file_name, conflict_behavior):
        """Simple upload for files under 4MB"""
        endpoint = f"drives/{drive_id}/items/{folder_id}:/{file_name}:/content"
        
        # Add conflict behavior query parameter
        params = {"@microsoft.graph.conflictBehavior": conflict_behavior}
        
        # Read file and prepare for upload
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Set content type header based on file extension
            content_type = self._get_content_type(file_path)
            headers = {"Content-Type": content_type}
            
            # Upload file
            return await self._make_request("PUT", endpoint, params=params, data=file_content, headers=headers)
        
        except Exception as e:
            return {"error": f"Error uploading file: {str(e)}"}
    
    async def _chunked_upload(self, drive_id, folder_id, file_path, file_name, file_size, conflict_behavior):
        """Chunked upload for files over 4MB"""
        # Create upload session
        endpoint = f"drives/{drive_id}/items/{folder_id}:/{file_name}:/createUploadSession"
        
        # Set conflict behavior in request body
        session_data = {
            "item": {
                "@microsoft.graph.conflictBehavior": conflict_behavior
            }
        }
        
        # Start upload session
        session_result = await self._make_request("POST", endpoint, json_data=session_data)
        if "error" in session_result:
            return session_result
        
        upload_url = session_result.get("uploadUrl")
        if not upload_url:
            return {"error": "Failed to create upload session"}
        
        try:
            # Upload in chunks
            chunk_size = 4 * 1024 * 1024  # 4MB chunks
            with open(file_path, 'rb') as f:
                uploaded = 0
                while uploaded < file_size:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    chunk_start = uploaded
                    chunk_end = min(uploaded + len(chunk) - 1, file_size - 1)
                    content_range = f"bytes {chunk_start}-{chunk_end}/{file_size}"
                    
                    # Upload chunk
                    headers = {
                        "Content-Length": str(len(chunk)),
                        "Content-Range": content_range
                    }
                    
                    # Use direct requests here since the upload URL is outside Graph API
                    chunk_response = requests.put(
                        url=upload_url,
                        data=chunk,
                        headers=headers
                    )
                    
                    if chunk_response.status_code not in (202, 201, 200):
                        return {"error": f"Chunk upload failed: {chunk_response.status_code} - {chunk_response.text}"}
                    
                    # Update progress
                    uploaded += len(chunk)
                    
                    # If 201 or 200, upload is complete
                    if chunk_response.status_code in (200, 201):
                        return chunk_response.json()
            
            return {"error": "Unexpected end of file during upload"}
        
        except Exception as e:
            return {"error": f"Error in chunked upload: {str(e)}"}
    
    async def create_folder(self, drive_id, parent_id, folder_name):
        """Create a new folder in SharePoint"""
        endpoint = f"drives/{drive_id}/items/{parent_id}/children"
        
        folder_data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        
        return await self._make_request("POST", endpoint, json_data=folder_data)
    
    async def delete_item(self, drive_id, item_id):
        """Delete a file or folder from SharePoint"""
        endpoint = f"drives/{drive_id}/items/{item_id}"
        return await self._make_request("DELETE", endpoint)
    
    async def search_items(self, drive_id, query, folder_id=None):
        """Search for items in a drive or folder"""
        if folder_id:
            endpoint = f"drives/{drive_id}/items/{folder_id}/search(q='{query}')"
        else:
            endpoint = f"drives/{drive_id}/root/search(q='{query}')"
        
        return await self._make_request("GET", endpoint)
    
    async def get_item_info(self, drive_id, item_id):
        """Get information about a file or folder"""
        endpoint = f"drives/{drive_id}/items/{item_id}"
        return await self._make_request("GET", endpoint)
    
    def _get_content_type(self, file_path):
        """Determine content type based on file extension"""
        # Map of common file extensions to MIME types
        extension_map = {
            ".txt": "text/plain",
            ".html": "text/html",
            ".htm": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".zip": "application/zip",
            ".csv": "text/csv"
        }
        
        # Get file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Return mapped content type or default
        return extension_map.get(ext, "application/octet-stream")


# Tool function definitions that will be registered with MCP

async def sharepoint_authenticate(auth_method: str = "device_code", 
                                 client_id: Optional[str] = None,
                                 tenant_id: Optional[str] = None,
                                 client_secret: Optional[str] = None,
                                 ctx: Context = None) -> str:
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
    sharepoint = _get_sharepoint_service(client_id, tenant_id, client_secret)
    if not sharepoint:
        return json.dumps({"error": "Failed to initialize SharePoint service"})
    
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


async def sharepoint_list_sites(search: Optional[str] = None, ctx: Context = None) -> str:
    """List available SharePoint sites.
    
    Parameters:
    - search: Optional search term to filter sites
    
    Returns:
    - JSON string with list of sites
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.list_sites(search)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing sites: {str(e)}"})


async def sharepoint_list_drives(site_id: Optional[str] = None, ctx: Context = None) -> str:
    """List available drives in a SharePoint site.
    
    Parameters:
    - site_id: ID of the site to list drives from (optional)
    
    Returns:
    - JSON string with list of drives
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.list_drives(site_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing drives: {str(e)}"})


async def sharepoint_list_items(drive_id: str, folder_id: str = "root", ctx: Context = None) -> str:
    """List files and folders in a SharePoint drive or folder.
    
    Parameters:
    - drive_id: ID of the drive
    - folder_id: ID of the folder (default: "root")
    
    Returns:
    - JSON string with list of items
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.list_items(drive_id, folder_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error listing items: {str(e)}"})


async def sharepoint_download_file(drive_id: str, item_id: str, 
                                  output_path: Optional[str] = None, 
                                  ctx: Context = None) -> str:
    """Download a file from SharePoint.
    
    Parameters:
    - drive_id: ID of the drive containing the file
    - item_id: ID of the file to download
    - output_path: Local path to save the file (optional)
    
    Returns:
    - JSON string with download result
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.download_file(drive_id, item_id, output_path)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error downloading file: {str(e)}"})


async def sharepoint_upload_file(drive_id: str, folder_id: str, file_path: str,
                                conflict_behavior: str = "replace", ctx: Context = None) -> str:
    """Upload a file to SharePoint.
    
    Parameters:
    - drive_id: ID of the drive to upload to
    - folder_id: ID of the folder to upload to
    - file_path: Local path of the file to upload
    - conflict_behavior: How to handle name conflicts (replace, rename, fail)
    
    Returns:
    - JSON string with upload result
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.upload_file(drive_id, folder_id, file_path, conflict_behavior)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error uploading file: {str(e)}"})


async def sharepoint_create_folder(drive_id: str, parent_id: str, folder_name: str, ctx: Context = None) -> str:
    """Create a new folder in SharePoint.
    
    Parameters:
    - drive_id: ID of the drive to create the folder in
    - parent_id: ID of the parent folder
    - folder_name: Name of the new folder
    
    Returns:
    - JSON string with folder creation result
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.create_folder(drive_id, parent_id, folder_name)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error creating folder: {str(e)}"})


async def sharepoint_delete_item(drive_id: str, item_id: str, ctx: Context = None) -> str:
    """Delete a file or folder from SharePoint.
    
    Parameters:
    - drive_id: ID of the drive containing the item
    - item_id: ID of the item to delete
    
    Returns:
    - JSON string with deletion result
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.delete_item(drive_id, item_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error deleting item: {str(e)}"})


async def sharepoint_search_items(drive_id: str, query: str, folder_id: Optional[str] = None, ctx: Context = None) -> str:
    """Search for items in a SharePoint drive or folder.
    
    Parameters:
    - drive_id: ID of the drive to search in
    - query: Search query
    - folder_id: ID of the folder to limit search to (optional)
    
    Returns:
    - JSON string with search results
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.search_items(drive_id, query, folder_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error searching items: {str(e)}"})


async def sharepoint_get_item_info(drive_id: str, item_id: str, ctx: Context = None) -> str:
    """Get information about a file or folder in SharePoint.
    
    Parameters:
    - drive_id: ID of the drive containing the item
    - item_id: ID of the item to get information about
    
    Returns:
    - JSON string with item information
    """
    sharepoint = _get_sharepoint_service()
    if not sharepoint:
        return json.dumps({"error": "SharePoint service not initialized"})
    
    try:
        result = await sharepoint.get_item_info(drive_id, item_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error getting item info: {str(e)}"})


# Tool registration and initialization
_sharepoint_service = None


def initialize_sharepoint_service(client_id=None, tenant_id=None, client_secret=None):
    """Initialize the SharePoint service with credentials"""
    global _sharepoint_service
    
    # Use environment variables as fallback
    client_id = client_id or os.environ.get("MS_GRAPH_CLIENT_ID")
    tenant_id = tenant_id or os.environ.get("MS_GRAPH_TENANT_ID")
    client_secret = client_secret or os.environ.get("MS_GRAPH_CLIENT_SECRET")
    
    if not (client_id and tenant_id):
        logging.warning("SharePoint credentials not configured properly. "\
                        "Set MS_GRAPH_CLIENT_ID and MS_GRAPH_TENANT_ID environment variables.")
        return None
    
    try:
        _sharepoint_service = SharePointService(client_id, tenant_id, client_secret)
        return _sharepoint_service
    except Exception as e:
        logging.error(f"Failed to initialize SharePoint service: {str(e)}")
        return None


def _get_sharepoint_service(client_id=None, tenant_id=None, client_secret=None):
    """Get or initialize the SharePoint service"""
    global _sharepoint_service
    if _sharepoint_service is None:
        _sharepoint_service = initialize_sharepoint_service(client_id, tenant_id, client_secret)
    return _sharepoint_service


def get_sharepoint_tools():
    """Get a dictionary of all SharePoint tools for registration with MCP"""
    return {
        SharePointTools.AUTHENTICATE: sharepoint_authenticate,
        SharePointTools.LIST_SITES: sharepoint_list_sites,
        SharePointTools.LIST_DRIVES: sharepoint_list_drives,
        SharePointTools.LIST_ITEMS: sharepoint_list_items,
        SharePointTools.DOWNLOAD_FILE: sharepoint_download_file,
        SharePointTools.UPLOAD_FILE: sharepoint_upload_file,
        SharePointTools.CREATE_FOLDER: sharepoint_create_folder,
        SharePointTools.DELETE_ITEM: sharepoint_delete_item,
        SharePointTools.SEARCH_ITEMS: sharepoint_search_items,
        SharePointTools.GET_ITEM_INFO: sharepoint_get_item_info
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the SharePoint module with MCP reference and credentials"""
    if mcp:
        set_external_mcp(mcp)
    
    # Initialize the service
    service = initialize_sharepoint_service()
    if service:
        logging.info("SharePoint service initialized successfully")
    else:
        logging.warning("Failed to initialize SharePoint service")
    
    return service is not None


if __name__ == "__main__":
    print("SharePoint service module - use with MCP Unified Server")
