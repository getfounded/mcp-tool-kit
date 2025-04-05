# SharePoint Tool

## Overview
The SharePoint tool provides integration with Microsoft SharePoint via the Microsoft Graph API, allowing you to work with files, folders, and other SharePoint resources.

## Features
- Authentication with Microsoft Graph API
- List SharePoint sites and drives
- Browse, upload, and download files
- Create and manage folders
- Search for files and content

## Configuration
This tool requires Microsoft Graph API credentials:
- `MS_GRAPH_CLIENT_ID`: Your Microsoft application client ID
- `MS_GRAPH_TENANT_ID`: Your Microsoft tenant ID
- `MS_GRAPH_CLIENT_SECRET`: (Optional) Your Microsoft client secret

These can be set as environment variables or provided directly when calling the authentication functions.

## Authentication Methods

### Device Code Authentication
This interactive authentication method is suitable for user-based access:
1. The tool provides a URL and code
2. The user opens the URL in a browser and enters the code
3. The user authenticates with their Microsoft account
4. The tool receives an access token for API operations

### Client Credentials Authentication
This non-interactive authentication method is suitable for service-to-service scenarios and requires a client secret:
1. The service authenticates directly using the client ID, tenant ID, and client secret
2. No user interaction is needed

## Usage Examples

### Authentication
```python
# Device code authentication (interactive)
result = await sharepoint_authenticate(auth_method="device_code")
print(result)

# Client credentials authentication (non-interactive)
result = await sharepoint_authenticate(
    auth_method="client_credentials",
    client_id="your_client_id",
    tenant_id="your_tenant_id",
    client_secret="your_client_secret"
)
print(result)
```

### Working with Sites and Drives
```python
# List all sites
sites = await sharepoint_list_sites()

# List drives in a site
drives = await sharepoint_list_drives(site_id="site_id")
```

### File and Folder Operations
```python
# List files and folders
items = await sharepoint_list_items(drive_id="drive_id", folder_id="folder_id")

# Download a file
download_result = await sharepoint_download_file(
    drive_id="drive_id",
    item_id="file_id",
    output_path="/path/to/save/file.txt"
)

# Upload a file
upload_result = await sharepoint_upload_file(
    drive_id="drive_id",
    folder_id="folder_id",
    file_path="/path/to/local/file.txt",
    conflict_behavior="replace"  # Options: replace, rename, fail
)

# Create a folder
folder_result = await sharepoint_create_folder(
    drive_id="drive_id",
    parent_id="parent_folder_id",
    folder_name="New Folder"
)

# Delete a file or folder
delete_result = await sharepoint_delete_item(
    drive_id="drive_id",
    item_id="item_id"
)
```

### Search and Information
```python
# Search for items
search_results = await sharepoint_search_items(
    drive_id="drive_id",
    query="search term",
    folder_id="optional_folder_id"  # Optional: limit search to a folder
)

# Get item information
item_info = await sharepoint_get_item_info(
    drive_id="drive_id",
    item_id="item_id"
)
```

## API Reference

### sharepoint_authenticate
Authenticate with Microsoft SharePoint.

**Parameters:**
- `auth_method`: Authentication method to use ("device_code" or "client_credentials")
- `client_id`: Microsoft application client ID (optional)
- `tenant_id`: Microsoft tenant ID (optional)
- `client_secret`: Microsoft client secret (required for client_credentials method)

**Returns:**
- JSON string with authentication result

### sharepoint_list_sites
List available SharePoint sites.

**Parameters:**
- `search`: Optional search term to filter sites

**Returns:**
- JSON string with list of sites

### sharepoint_list_drives
List available drives in a SharePoint site.

**Parameters:**
- `site_id`: ID of the site to list drives from (optional)

**Returns:**
- JSON string with list of drives

### sharepoint_list_items
List files and folders in a SharePoint drive or folder.

**Parameters:**
- `drive_id`: ID of the drive
- `folder_id`: ID of the folder (default: "root")

**Returns:**
- JSON string with list of items

### sharepoint_download_file
Download a file from SharePoint.

**Parameters:**
- `drive_id`: ID of the drive containing the file
- `item_id`: ID of the file to download
- `output_path`: Local path to save the file (optional)

**Returns:**
- JSON string with download result

### sharepoint_upload_file
Upload a file to SharePoint.

**Parameters:**
- `drive_id`: ID of the drive to upload to
- `folder_id`: ID of the folder to upload to
- `file_path`: Local path of the file to upload
- `conflict_behavior`: How to handle name conflicts (replace, rename, fail)

**Returns:**
- JSON string with upload result

### sharepoint_create_folder
Create a new folder in SharePoint.

**Parameters:**
- `drive_id`: ID of the drive to create the folder in
- `parent_id`: ID of the parent folder
- `folder_name`: Name of the new folder

**Returns:**
- JSON string with folder creation result

### sharepoint_delete_item
Delete a file or folder from SharePoint.

**Parameters:**
- `drive_id`: ID of the drive containing the item
- `item_id`: ID of the item to delete

**Returns:**
- JSON string with deletion result

### sharepoint_search_items
Search for items in a SharePoint drive or folder.

**Parameters:**
- `drive_id`: ID of the drive to search in
- `query`: Search query
- `folder_id`: ID of the folder to limit search to (optional)

**Returns:**
- JSON string with search results

### sharepoint_get_item_info
Get information about a file or folder in SharePoint.

**Parameters:**
- `drive_id`: ID of the drive containing the item
- `item_id`: ID of the item to get information about

**Returns:**
- JSON string with item information

## Error Handling
All SharePoint tools return JSON responses that include an "error" property when an error occurs. Always check for this property in the response to handle errors appropriately.

Example error handling:
```python
result = await sharepoint_authenticate(auth_method="device_code")
result_json = json.loads(result)

if "error" in result_json:
    print(f"Error: {result_json['error']}")
else:
    print("Authentication successful!")
```

## Limitations
- Large file uploads (>4MB) use a chunked upload process which might be slower
- The token expires after 1 hour and is automatically refreshed when possible
- Some operations require specific SharePoint permissions in your Microsoft application
