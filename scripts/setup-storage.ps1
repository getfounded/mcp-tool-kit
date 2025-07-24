# PowerShell script to set up storage directory on Windows
$storageDir = "$env:USERPROFILE\mcp-tool-kit-storage"

# Create the storage directory if it doesn't exist
if (!(Test-Path -Path $storageDir)) {
    Write-Host "Creating storage directory at: $storageDir"
    New-Item -ItemType Directory -Force -Path $storageDir
    Write-Host "Storage directory created successfully!"
} else {
    Write-Host "Storage directory already exists at: $storageDir"
}

# Create subdirectories for better organization
$subdirs = @("documents", "downloads", "workspace")
foreach ($subdir in $subdirs) {
    $path = Join-Path $storageDir $subdir
    if (!(Test-Path -Path $path)) {
        New-Item -ItemType Directory -Force -Path $path
        Write-Host "Created subdirectory: $subdir"
    }
}

Write-Host "`nStorage setup complete!"
Write-Host "Your MCP Tool Kit storage is located at: $storageDir"