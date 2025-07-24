# MCP Tool Kit Installer for Windows
# No Git required - downloads directly from GitHub

$ErrorActionPreference = "Stop"

Write-Host "MCP Tool Kit Installer for Windows" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Function to download and extract ZIP
function Install-MCPToolKit {
    $installDir = "$env:USERPROFILE\mcp-tool-kit"
    $zipUrl = "https://github.com/getfounded/mcp-tool-kit/archive/refs/heads/main.zip"
    $zipFile = "$env:TEMP\mcp-tool-kit.zip"
    
    Write-Host "Installing MCP Tool Kit to: $installDir" -ForegroundColor Yellow
    
    # Download ZIP file
    Write-Host "Downloading MCP Tool Kit..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
        Write-Host "[OK] Downloaded successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download: $_" -ForegroundColor Red
        exit 1
    }
    
    # Extract ZIP
    Write-Host "Extracting files..." -ForegroundColor Yellow
    try {
        # Remove existing directory if exists
        if (Test-Path $installDir) {
            Remove-Item $installDir -Recurse -Force
        }
        
        # Extract to temp location
        $tempExtract = "$env:TEMP\mcp-extract"
        Expand-Archive -Path $zipFile -DestinationPath $tempExtract -Force
        
        # Move to final location
        $extractedDir = Get-ChildItem -Path $tempExtract -Directory | Select-Object -First 1
        Move-Item -Path $extractedDir.FullName -Destination $installDir -Force
        
        # Cleanup
        Remove-Item $tempExtract -Recurse -Force
        Remove-Item $zipFile -Force
        
        Write-Host "[OK] Extracted successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to extract: $_" -ForegroundColor Red
        exit 1
    }
    
    return $installDir
}

# Function to check and install Docker
function Ensure-Docker {
    if (Test-CommandExists "docker") {
        Write-Host "[OK] Docker is installed" -ForegroundColor Green
        
        # Check if Docker is running
        try {
            docker ps 2>&1 | Out-Null
            Write-Host "[OK] Docker is running" -ForegroundColor Green
        } catch {
            Write-Host "[WARNING] Docker is installed but not running" -ForegroundColor Yellow
            Write-Host "Please start Docker Desktop and run this installer again" -ForegroundColor Yellow
            
            # Try to start Docker Desktop
            $dockerDesktop = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
            if (Test-Path $dockerDesktop) {
                Write-Host "Attempting to start Docker Desktop..." -ForegroundColor Yellow
                Start-Process $dockerDesktop
                Write-Host "Please wait for Docker to start and run this installer again" -ForegroundColor Yellow
                exit 0
            }
        }
    } else {
        Write-Host "[WARNING] Docker is not installed" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Docker is required to run MCP Tool Kit" -ForegroundColor Yellow
        Write-Host "Would you like to download Docker Desktop? (y/n)" -ForegroundColor Cyan
        
        $response = Read-Host
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host "Opening Docker download page..." -ForegroundColor Yellow
            Start-Process "https://www.docker.com/products/docker-desktop/"
            Write-Host ""
            Write-Host "Please:" -ForegroundColor Yellow
            Write-Host "1. Download and install Docker Desktop" -ForegroundColor White
            Write-Host "2. Start Docker Desktop" -ForegroundColor White
            Write-Host "3. Run this installer again" -ForegroundColor White
            exit 0
        } else {
            Write-Host "[ERROR] Docker is required. Please install Docker Desktop first." -ForegroundColor Red
            exit 1
        }
    }
}

# Function to create desktop shortcut
function Create-DesktopShortcut {
    param($targetPath)
    
    $shortcutPath = "$env:USERPROFILE\Desktop\MCP Tool Kit.lnk"
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$targetPath\launch.ps1`""
    $Shortcut.WorkingDirectory = $targetPath
    $Shortcut.IconLocation = "powershell.exe"
    $Shortcut.Description = "Launch MCP Tool Kit"
    $Shortcut.Save()
    
    Write-Host "[OK] Created desktop shortcut" -ForegroundColor Green
}

# Main installation process
Write-Host "Checking requirements..." -ForegroundColor Yellow
Write-Host ""

# Check Docker
Ensure-Docker

# Install MCP Tool Kit
Write-Host ""
$installPath = Install-MCPToolKit

# Create enhanced launch script
$launchScript = @'
# MCP Tool Kit Launcher
Write-Host "MCP Tool Kit Launcher" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker ps 2>&1 | Out-Null
} catch {
    Write-Host "[ERROR] Docker is not running!" -ForegroundColor Red
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    
    $dockerDesktop = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerDesktop) {
        Start-Process $dockerDesktop
        Write-Host "Waiting for Docker to start (this may take a minute)..." -ForegroundColor Yellow
        
        $maxWait = 60
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 2
            $waited += 2
            try {
                docker ps 2>&1 | Out-Null
                Write-Host "[OK] Docker is now running!" -ForegroundColor Green
                break
            } catch {
                Write-Host "." -NoNewline
            }
        }
        Write-Host ""
    }
}

# Change to install directory
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "Select an option:" -ForegroundColor Cyan
Write-Host "1. Start for Claude Desktop (stdio mode)" -ForegroundColor White
Write-Host "2. Start for Web Access (SSE mode on port 8080)" -ForegroundColor White
Write-Host "3. Stop MCP Tool Kit" -ForegroundColor White
Write-Host "4. Update MCP Tool Kit" -ForegroundColor White
Write-Host "5. View Logs" -ForegroundColor White
Write-Host "6. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host "Starting MCP Tool Kit for Claude Desktop..." -ForegroundColor Yellow
        docker-compose down 2>$null
        docker-compose up -d
        docker exec -it mcp-server python mcp_server_v2.py
    }
    "2" {
        Write-Host "Starting MCP Tool Kit for Web Access..." -ForegroundColor Yellow
        docker-compose down 2>$null
        docker-compose up -d
        docker exec -d mcp-server python mcp_server_v2.py --transport sse
        Write-Host "[OK] Server started on http://localhost:8080" -ForegroundColor Green
        Write-Host "Press any key to stop the server..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    "3" {
        Write-Host "Stopping MCP Tool Kit..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "[OK] Stopped" -ForegroundColor Green
    }
    "4" {
        Write-Host "Updating MCP Tool Kit..." -ForegroundColor Yellow
        & "$PSScriptRoot\..\install.ps1"
    }
    "5" {
        Write-Host "Showing logs (press Ctrl+C to exit)..." -ForegroundColor Yellow
        docker logs -f mcp-server
    }
    "6" {
        exit 0
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'@

$launchScript | Out-File -FilePath "$installPath\launch.ps1" -Encoding UTF8

# Create desktop shortcut
Write-Host ""
Write-Host "Would you like to create a desktop shortcut? (y/n)" -ForegroundColor Cyan
$response = Read-Host
if ($response -eq 'y' -or $response -eq 'Y') {
    Create-DesktopShortcut -targetPath $installPath
}

# Create Start Menu entry
$startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\MCP Tool Kit"
if (!(Test-Path $startMenuPath)) {
    New-Item -ItemType Directory -Path $startMenuPath -Force | Out-Null
}
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$startMenuPath\MCP Tool Kit.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$installPath\launch.ps1`""
$Shortcut.WorkingDirectory = $installPath
$Shortcut.IconLocation = "powershell.exe"
$Shortcut.Description = "Launch MCP Tool Kit"
$Shortcut.Save()
Write-Host "[OK] Created Start Menu entry" -ForegroundColor Green

# Show completion message
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "MCP Tool Kit has been installed to:" -ForegroundColor White
Write-Host "  $installPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start MCP Tool Kit:" -ForegroundColor White
Write-Host "  - Use the desktop shortcut (if created)" -ForegroundColor Yellow
Write-Host "  - Or run: $installPath\launch.ps1" -ForegroundColor Yellow
Write-Host "  - Or find it in the Start Menu" -ForegroundColor Yellow
Write-Host ""
Write-Host "For Claude Desktop configuration:" -ForegroundColor White
Write-Host "  Add to: $env:APPDATA\Claude\claude_desktop_config.json" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")