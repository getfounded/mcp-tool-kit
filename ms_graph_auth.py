#!/usr/bin/env python3
import os
import json
import time
from typing import Dict, Any, Optional, List
import requests
import msal

class MSGraphAuth:
    """Authentication handler for Microsoft Graph API"""
    
    def __init__(self, 
                 client_id: str, 
                 client_secret: str, 
                 tenant_id: str,
                 scopes: Optional[List[str]] = None):
        """
        Initialize Microsoft Graph authentication.
        
        Args:
            client_id: Application (client) ID from Azure portal
            client_secret: Client secret from Azure portal
            tenant_id: Directory (tenant) ID from Azure portal
            scopes: List of permission scopes required
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.scopes = scopes or ["https://graph.microsoft.com/.default"]
        
        # Token cache
        self.token_cache = {
            "access_token": None,
            "expires_at": 0
        }
        
        # MSAL app for authentication
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )
    
    def get_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            str: Access token for Microsoft Graph API
        """
        current_time = time.time()
        
        # Check if token is still valid (with 5-minute buffer)
        if (self.token_cache["access_token"] and 
            self.token_cache["expires_at"] > current_time + 300):
            return self.token_cache["access_token"]
        
        # Acquire token
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        
        if "access_token" in result:
            # Cache the token
            self.token_cache["access_token"] = result["access_token"]
            self.token_cache["expires_at"] = current_time + result.get("expires_in", 3600)
            return result["access_token"]
        else:
            error_description = result.get("error_description", "Unknown error")
            error = result.get("error", "Authentication failed")
            raise Exception(f"Failed to obtain access token: {error}: {error_description}")
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get headers for Microsoft Graph API requests.
        
        Returns:
            Dict[str, str]: Headers including authorization token
        """
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def make_request(self, method: str, endpoint: str, data: Any = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the Microsoft Graph API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/me/drive/root")
            data: Request payload for POST/PUT requests
            params: URL parameters
            
        Returns:
            Dict[str, Any]: API response
        """
        headers = self.get_headers()
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return self.make_request(method, endpoint, data, params)
        
        # Raise exception for other errors
        response.raise_for_status()
        
        # Return JSON response if available
        if response.content:
            try:
                return response.json()
            except ValueError:
                return {"content": response.content}
        return {}


class PowerPointGraphAPI:
    """Microsoft Graph API wrapper for PowerPoint operations"""
    
    def __init__(self, auth: MSGraphAuth):
        """
        Initialize PowerPoint Graph API wrapper.
        
        Args:
            auth: Authenticated MSGraphAuth instance
        """
        self.auth = auth
    
    def list_presentations(self, folder_path: str = "/") -> List[Dict[str, Any]]:
        """
        List all PowerPoint presentations in a OneDrive folder.
        
        Args:
            folder_path: Path to the folder in OneDrive
            
        Returns:
            List[Dict[str, Any]]: List of presentations
        """
        # Get folder ID if not root
        folder_id = "root"
        if folder_path and folder_path != "/":
            folder_id = self._get_item_id_by_path(folder_path)
        
        # List items in the folder
        endpoint = f"/me/drive/items/{folder_id}/children"
        params = {
            "$filter": "file/mimeType eq 'application/vnd.openxmlformats-officedocument.presentationml.presentation'"
        }
        
        response = self.auth.make_request("GET", endpoint, params=params)
        return response.get("value", [])
    
    def get_presentation(self, file_path: str) -> Dict[str, Any]:
        """
        Get details of a PowerPoint presentation.
        
        Args:
            file_path: Path to the presentation in OneDrive
            
        Returns:
            Dict[str, Any]: Presentation details
        """
        item_id = self._get_item_id_by_path(file_path)
        endpoint = f"/me/drive/items/{item_id}"
        return self.auth.make_request("GET", endpoint)
    
    def create_presentation(self, name: str, folder_path: str = "/") -> Dict[str, Any]:
        """
        Create a new PowerPoint presentation.
        
        Args:
            name: Name of the presentation
            folder_path: Path to the folder in OneDrive
            
        Returns:
            Dict[str, Any]: Created presentation details
        """
        # Get folder ID if not root
        folder_id = "root"
        if folder_path and folder_path != "/":
            folder_id = self._get_item_id_by_path(folder_path)
        
        endpoint = f"/me/drive/items/{folder_id}/children"
        data = {
            "name": name if name.endswith(".pptx") else f"{name}.pptx",
            "@microsoft.graph.conflictBehavior": "rename",
            "file": {}
        }
        
        return self.auth.make_request("POST", endpoint, data=data)
    
    def upload_presentation(self, file_path: str, content: bytes, folder_path: str = "/") -> Dict[str, Any]:
        """
        Upload a PowerPoint presentation to OneDrive.
        
        Args:
            file_path: Local file path
            content: File content as bytes
            folder_path: Path to the folder in OneDrive
            
        Returns:
            Dict[str, Any]: Uploaded presentation details
        """
        # Get folder ID if not root
        folder_id = "root"
        if folder_path and folder_path != "/":
            folder_id = self._get_item_id_by_path(folder_path)
        
        file_name = os.path.basename(file_path)
        
        # Small files (< 4MB): direct upload
        if len(content) < 4 * 1024 * 1024:
            endpoint = f"/me/drive/items/{folder_id}:/{file_name}:/content"
            headers = self.auth.get_headers()
            headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            
            url = f"https://graph.microsoft.com/v1.0{endpoint}"
            response = requests.put(url, headers=headers, data=content)
            response.raise_for_status()
            
            return response.json()
        else:
            # Large files: create upload session
            endpoint = f"/me/drive/items/{folder_id}:/{file_name}:/createUploadSession"
            upload_session = self.auth.make_request("POST", endpoint)
            
            upload_url = upload_session.get("uploadUrl")
            if not upload_url:
                raise Exception("Failed to create upload session")
            
            # Upload in chunks
            chunk_size = 3 * 1024 * 1024  # 3 MB chunks
            total_size = len(content)
            
            for i in range(0, total_size, chunk_size):
                chunk = content[i:i+chunk_size]
                chunk_end = min(i + chunk_size - 1, total_size - 1)
                
                headers = {
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {i}-{chunk_end}/{total_size}"
                }
                
                response = requests.put(upload_url, data=chunk, headers=headers)
                if response.status_code in (200, 201, 202):
                    if response.status_code in (200, 201):
                        return response.json()
                else:
                    response.raise_for_status()
            
            raise Exception("Upload failed to complete")
    
    def download_presentation(self, file_path: str) -> bytes:
        """
        Download a PowerPoint presentation from OneDrive.
        
        Args:
            file_path: Path to the presentation in OneDrive
            
        Returns:
            bytes: Presentation content
        """
        item_id = self._get_item_id_by_path(file_path)
        endpoint = f"/me/drive/items/{item_id}/content"
        
        # Special handling for download
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        headers = self.auth.get_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content
    
    def delete_presentation(self, file_path: str) -> None:
        """
        Delete a PowerPoint presentation from OneDrive.
        
        Args:
            file_path: Path to the presentation in OneDrive
        """
        item_id = self._get_item_id_by_path(file_path)
        endpoint = f"/me/drive/items/{item_id}"
        
        self.auth.make_request("DELETE", endpoint)
    
    def _get_item_id_by_path(self, path: str) -> str:
        """
        Get OneDrive item ID by path.
        
        Args:
            path: Path to the item in OneDrive
            
        Returns:
            str: Item ID
        """
        # Clean up path
        path = path.strip("/")
        
        endpoint = f"/me/drive/root:/{path}"
        response = self.auth.make_request("GET", endpoint)
        
        item_id = response.get("id")
        if not item_id:
            raise Exception(f"Item not found: {path}")
        
        return item_id


# Example usage
if __name__ == "__main__":
    # Configure with your Azure app registration details
    client_id = os.environ.get("MS_CLIENT_ID")
    client_secret = os.environ.get("MS_CLIENT_SECRET")
    tenant_id = os.environ.get("MS_TENANT_ID")
    
    if not all([client_id, client_secret, tenant_id]):
        print("Please set MS_CLIENT_ID, MS_CLIENT_SECRET, and MS_TENANT_ID environment variables")
        exit(1)
    
    # Initialize auth
    auth = MSGraphAuth(client_id, client_secret, tenant_id)
    
    # Initialize PowerPoint API
    ppt_api = PowerPointGraphAPI(auth)
    
    # List presentations
    presentations = ppt_api.list_presentations()
    print(f"Found {len(presentations)} presentations")
    
    for pres in presentations:
        print(f"- {pres.get('name')}")