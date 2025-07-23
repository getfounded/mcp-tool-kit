@echo off
echo ========================================
echo MCP Tool Kit Launcher
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH.
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [INFO] Docker is installed.
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Git is not installed or not in PATH.
    echo You may need Git for future updates.
    echo.
    echo Download Git from: https://git-scm.com/download/win
    echo.
)

REM Check if docker-compose exists
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Using 'docker compose' (new syntax)
    set COMPOSE_CMD=docker compose
) else (
    echo [INFO] Using 'docker-compose' (legacy syntax)
    set COMPOSE_CMD=docker-compose
)

echo.
echo Choose an option:
echo 1. Start MCP Server (stdio mode - for Claude Desktop)
echo 2. Start MCP Server (SSE mode - for web access)
echo 3. Stop MCP Server
echo 4. View server logs
echo 5. Rebuild server (after updates)
echo 6. Exit
echo.

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto start_stdio
if "%choice%"=="2" goto start_sse
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto rebuild
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
pause
goto :eof

:start_stdio
echo.
echo Starting MCP Server in stdio mode...
%COMPOSE_CMD% up -d
echo.
echo Server started! To connect with Claude Desktop:
echo 1. Open Claude Desktop settings
echo 2. Add server with command: docker exec -it mcp-server python mcp_server_v2.py
echo.
pause
goto :eof

:start_sse
echo.
echo Starting MCP Server in SSE mode...
%COMPOSE_CMD% up -d
timeout /t 3 >nul
docker exec -d mcp-server python mcp_server_v2.py --transport sse --port 8080
echo.
echo Server started in SSE mode!
echo Access at: http://localhost:8080
echo.
pause
goto :eof

:stop
echo.
echo Stopping MCP Server...
%COMPOSE_CMD% down
echo Server stopped.
pause
goto :eof

:logs
echo.
echo Showing server logs (press Ctrl+C to exit)...
%COMPOSE_CMD% logs -f
pause
goto :eof

:rebuild
echo.
echo Rebuilding server...
%COMPOSE_CMD% build --no-cache
echo Rebuild complete.
pause
goto :eof

:end