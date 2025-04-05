#!/usr/bin/env python3
"""
Service implementation for SharePoint API.
"""
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

from app.tools.base.service import ToolServiceBase


class SharePointService(ToolServiceBase):
    """Service to handle SharePoint operations via Microsoft Graph API"""
    
    def __init__(self, client_id=None, tenant_id=None, client_secret=None):
        """Initialize SharePoint service with authentication parameters"""
        super().__init__()
        
        # Try to get credentials from environment if not provided
        self.client_id = client_id or self.get_env_var("MS_GRAPH_CLIENT_ID")
        self.tenant_id = tenant_id or self.get_env_var("MS_GRAPH_TENANT_ID")
        self.client_secret = client_secret or self.get_env_var("MS_GRAPH_CLIENT_SECRET")
        
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
    
    def initialize(self) -> bool:
        """Initialize the SharePoint service"""
        try:
            if self.client_id and self.tenant_id:
                self._initialize_app()
                self.logger.info("SharePoint service initialized")
                self.initialized = True
                return True
            else:
                self.logger.warning("SharePoint credentials not provided. Authentication will fail.")
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize SharePoint service: {str(e)}")
            return False
    
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
        self._is_initialized()
        
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
        self._is_initialized()
        
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
        self._is_initialized()
        
        endpoint = "sites"
        params = {}
        
        if search:
            params["search"] = search
        
        return await self._make_request("GET", endpoint, params=params)
    
    async def list_drives(self, site_id=None):
        """List available drives in a SharePoint site"""
        self._is_initialized()
        
        if site_id:
            endpoint = f"sites/{site_id}/drives"
        else:
            endpoint = "me/drives"
        
        return await self._make_request("GET", endpoint)
    
    async def list_items(self, drive_id, folder_id="root"):
        """List items (files and folders) in a drive folder"""
        self._is_initialized()
        
        endpoint = f"drives/{drive_id}/items/{folder_id}/children"
        return await self._make_request("GET", endpoint)
    
    async def download_file(self, drive_id, item_id, output_path=None):
        """Download a file from SharePoint"""
        self._is_initialized()
        
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
        self._is_initialized()
        
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
        self._is_initialized()
        
        endpoint = f"drives/{drive_id}/items/{parent_id}/children"
        
        folder_data = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        
        return await self._make_request("POST", endpoint, json_data=folder_data)
    
    async def delete_item(self, drive_id, item_id):
        """Delete a file or folder from SharePoint"""
        self._is_initialized()
        
        endpoint = f"drives/{drive_id}/items/{item_id}"
        return await self._make_request("DELETE", endpoint)
    
    async def search_items(self, drive_id, query, folder_id=None):
        """Search for items in a drive or folder"""
        self._is_initialized()
        
        if folder_id:
            endpoint = f"drives/{drive_id}/items/{folder_id}/search(q='{query}')"
        else:
            endpoint = f"drives/{drive_id}/root/search(q='{query}')"
        
        return await self._make_request("GET", endpoint)
    
    async def get_item_info(self, drive_id, item_id):
        """Get information about a file or folder"""
        self._is_initialized()
        
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


# Singleton instance
_service_instance = None


def get_service() -> SharePointService:
    """
    Get or initialize the SharePoint service singleton.

    Returns:
        SharePointService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = SharePointService()
        _service_instance.initialize()
    return _service_instance