@echo off
REM MCP Tool Kit Installer for Windows (Batch version)
REM No Git required - downloads directly from GitHub

echo MCP Tool Kit Installer for Windows
echo ===================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell is required but not found!
    echo Please install PowerShell or use Windows 10/11
    pause
    exit /b 1
)

REM Run PowerShell installer
echo Starting PowerShell installer...
echo.

powershell -ExecutionPolicy Bypass -Command "& {irm https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1 | iex}"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Trying alternative method...
    echo Downloading installer script...
    
    REM Try to download using PowerShell
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1' -OutFile '%TEMP%\mcp-install.ps1'"
    
    if exist "%TEMP%\mcp-install.ps1" (
        echo Running installer...
        powershell -ExecutionPolicy Bypass -File "%TEMP%\mcp-install.ps1"
        del "%TEMP%\mcp-install.ps1"
    ) else (
        echo.
        echo [ERROR] Could not download installer!
        echo.
        echo Please try:
        echo 1. Check your internet connection
        echo 2. Temporarily disable antivirus/firewall
        echo 3. Download manually from: https://github.com/getfounded/mcp-tool-kit
    )
)

echo.
pause