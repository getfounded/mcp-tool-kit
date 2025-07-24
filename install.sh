#!/bin/bash
# MCP Tool Kit Installer for Mac/Linux
# No Git required - downloads directly from GitHub

set -e

echo -e "\033[36mMCP Tool Kit Installer for Mac/Linux\033[0m"
echo -e "\033[36m====================================\033[0m"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Function to download and extract
install_mcp_toolkit() {
    local install_dir="$HOME/mcp-tool-kit"
    local zip_url="https://github.com/getfounded/mcp-tool-kit/archive/refs/heads/main.zip"
    local temp_zip="/tmp/mcp-tool-kit.zip"
    
    echo -e "\033[33mInstalling MCP Tool Kit to: $install_dir\033[0m"
    
    # Download ZIP file
    echo -e "\033[33mDownloading MCP Tool Kit...\033[0m"
    if command_exists curl; then
        curl -L -o "$temp_zip" "$zip_url" || { echo -e "\033[31m[ERROR] Failed to download\033[0m"; exit 1; }
    elif command_exists wget; then
        wget -O "$temp_zip" "$zip_url" || { echo -e "\033[31m[ERROR] Failed to download\033[0m"; exit 1; }
    else
        echo -e "\033[31m[ERROR] Neither curl nor wget found. Please install one of them.\033[0m"
        exit 1
    fi
    echo -e "\033[32m[OK] Downloaded successfully\033[0m"
    
    # Extract ZIP
    echo -e "\033[33mExtracting files...\033[0m"
    
    # Remove existing directory if exists
    [ -d "$install_dir" ] && rm -rf "$install_dir"
    
    # Extract
    if command_exists unzip; then
        unzip -q "$temp_zip" -d "/tmp/mcp-extract" || { echo -e "\033[31m[ERROR] Failed to extract\033[0m"; exit 1; }
    else
        echo -e "\033[31m[ERROR] unzip not found. Please install it.\033[0m"
        exit 1
    fi
    
    # Move to final location
    mv /tmp/mcp-extract/mcp-tool-kit-main "$install_dir"
    
    # Cleanup
    rm -rf /tmp/mcp-extract "$temp_zip"
    
    echo -e "\033[32m[OK] Extracted successfully\033[0m"
    
    echo "$install_dir"
}

# Function to check and install Docker
ensure_docker() {
    if command_exists docker; then
        echo -e "\033[32m[OK] Docker is installed\033[0m"
        
        # Check if Docker is running
        if docker ps >/dev/null 2>&1; then
            echo -e "\033[32m[OK] Docker is running\033[0m"
        else
            echo -e "\033[33m[WARNING] Docker is installed but not running\033[0m"
            
            local os_type=$(detect_os)
            if [ "$os_type" = "macos" ]; then
                echo -e "\033[33mAttempting to start Docker Desktop...\033[0m"
                open -a Docker || echo -e "\033[33mPlease start Docker Desktop manually\033[0m"
            else
                echo -e "\033[33mPlease start Docker daemon:\033[0m"
                echo "  sudo systemctl start docker"
            fi
            
            echo -e "\033[33mWaiting for Docker to start...\033[0m"
            local max_wait=60
            local waited=0
            while [ $waited -lt $max_wait ]; do
                if docker ps >/dev/null 2>&1; then
                    echo -e "\033[32m[OK] Docker is now running!\033[0m"
                    return 0
                fi
                sleep 2
                waited=$((waited + 2))
                echo -n "."
            done
            echo ""
            echo -e "\033[31m[ERROR] Docker failed to start. Please start it manually.\033[0m"
            exit 1
        fi
    else
        echo -e "\033[33m[WARNING] Docker is not installed\033[0m"
        echo ""
        echo -e "\033[33mDocker is required to run MCP Tool Kit\033[0m"
        echo -e "\033[36mWould you like to open the Docker installation page? (y/n)\033[0m"
        
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            local os_type=$(detect_os)
            if [ "$os_type" = "macos" ]; then
                open "https://www.docker.com/products/docker-desktop/"
            else
                xdg-open "https://www.docker.com/products/docker-desktop/" 2>/dev/null || \
                echo "Please visit: https://www.docker.com/products/docker-desktop/"
            fi
            
            echo ""
            echo -e "\033[33mPlease:\033[0m"
            echo "1. Download and install Docker Desktop"
            echo "2. Start Docker Desktop"
            echo "3. Run this installer again"
            exit 0
        else
            echo -e "\033[31m[ERROR] Docker is required. Please install Docker first.\033[0m"
            exit 1
        fi
    fi
}

# Function to create desktop entry (Linux)
create_desktop_entry() {
    local install_path="$1"
    local desktop_file="$HOME/.local/share/applications/mcp-tool-kit.desktop"
    
    mkdir -p "$HOME/.local/share/applications"
    
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MCP Tool Kit
Comment=Model Context Protocol Tool Kit
Exec=$install_path/launch.sh
Icon=utilities-terminal
Terminal=true
Categories=Development;
EOF
    
    chmod +x "$desktop_file"
    echo -e "\033[32m[OK] Created desktop entry\033[0m"
}

# Function to create macOS app
create_macos_app() {
    local install_path="$1"
    local app_path="$HOME/Applications/MCP Tool Kit.app"
    
    mkdir -p "$HOME/Applications"
    mkdir -p "$app_path/Contents/MacOS"
    
    # Create launcher script
    cat > "$app_path/Contents/MacOS/MCP Tool Kit" << EOF
#!/bin/bash
osascript -e 'tell app "Terminal" to do script "cd \"$install_path\" && ./launch.sh"'
EOF
    
    chmod +x "$app_path/Contents/MacOS/MCP Tool Kit"
    
    # Create Info.plist
    cat > "$app_path/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>MCP Tool Kit</string>
    <key>CFBundleName</key>
    <string>MCP Tool Kit</string>
    <key>CFBundleIdentifier</key>
    <string>com.mcp.toolkit</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF
    
    echo -e "\033[32m[OK] Created macOS app in ~/Applications\033[0m"
}

# Create enhanced launch script
create_launch_script() {
    local install_path="$1"
    
    cat > "$install_path/launch.sh" << 'EOF'
#!/bin/bash
# MCP Tool Kit Launcher

echo -e "\033[36mMCP Tool Kit Launcher\033[0m"
echo -e "\033[36m=====================\033[0m"
echo ""

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo -e "\033[31m[ERROR] Docker is not running!\033[0m"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "\033[33mAttempting to start Docker Desktop...\033[0m"
        open -a Docker
        
        echo -e "\033[33mWaiting for Docker to start (this may take a minute)...\033[0m"
        max_wait=60
        waited=0
        while [ $waited -lt $max_wait ]; do
            if docker ps >/dev/null 2>&1; then
                echo -e "\033[32m[OK] Docker is now running!\033[0m"
                break
            fi
            sleep 2
            waited=$((waited + 2))
            echo -n "."
        done
        echo ""
    else
        echo "Please start Docker daemon:"
        echo "  sudo systemctl start docker"
        exit 1
    fi
fi

# Change to script directory
cd "$(dirname "$0")"

echo ""
echo -e "\033[36mSelect an option:\033[0m"
echo "1. Start for Claude Desktop (stdio mode)"
echo "2. Start for Web Access (SSE mode on port 8080)"
echo "3. Stop MCP Tool Kit"
echo "4. Update MCP Tool Kit"
echo "5. View Logs"
echo "6. Check Docker Images Status"
echo "7. Exit"
echo ""

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        echo -e "\033[33mStarting MCP Tool Kit for Claude Desktop...\033[0m"
        docker-compose down 2>/dev/null
        docker-compose up -d
        docker exec -it mcp-server python mcp_server_v2.py
        ;;
    2)
        echo -e "\033[33mStarting MCP Tool Kit for Web Access...\033[0m"
        docker-compose down 2>/dev/null
        docker-compose up -d
        docker exec -d mcp-server python mcp_server_v2.py --transport sse
        echo -e "\033[32m[OK] Server started on http://localhost:8080\033[0m"
        echo "Press Enter to stop the server..."
        read
        docker-compose down
        ;;
    3)
        echo -e "\033[33mStopping MCP Tool Kit...\033[0m"
        docker-compose down
        echo -e "\033[32m[OK] Stopped\033[0m"
        ;;
    4)
        echo -e "\033[33mUpdating MCP Tool Kit...\033[0m"
        bash <(curl -s https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
        ;;
    5)
        echo -e "\033[33mShowing logs (press Ctrl+C to exit)...\033[0m"
        docker logs -f mcp-server
        ;;
    6)
        echo -e "\033[33mChecking Docker images...\033[0m"
        docker images | grep mcp-server || echo "No MCP images found"
        echo ""
        docker ps -a | grep mcp-server || echo "No MCP containers found"
        ;;
    7)
        exit 0
        ;;
    *)
        echo -e "\033[31mInvalid choice!\033[0m"
        ;;
esac

echo ""
echo "Press Enter to exit..."
read
EOF
    
    chmod +x "$install_path/launch.sh"
}

# Main installation process
echo -e "\033[33mChecking requirements...\033[0m"
echo ""

# Check Docker
ensure_docker

# Install MCP Tool Kit
echo ""
install_path=$(install_mcp_toolkit)

# Create launch script
create_launch_script "$install_path"

# Create desktop/app entries
echo ""
echo -e "\033[36mWould you like to create a desktop shortcut? (y/n)\033[0m"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    os_type=$(detect_os)
    if [ "$os_type" = "macos" ]; then
        create_macos_app "$install_path"
    elif [ "$os_type" = "linux" ]; then
        create_desktop_entry "$install_path"
    fi
fi

# Add to PATH
echo ""
echo -e "\033[36mWould you like to add MCP Tool Kit to your PATH? (y/n)\033[0m"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    shell_rc=""
    if [ -f "$HOME/.bashrc" ]; then
        shell_rc="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        shell_rc="$HOME/.zshrc"
    fi
    
    if [ -n "$shell_rc" ]; then
        echo "export PATH=\"\$PATH:$install_path\"" >> "$shell_rc"
        echo -e "\033[32m[OK] Added to PATH in $shell_rc\033[0m"
        echo "Run 'source $shell_rc' to update current session"
    fi
fi

# Show completion message
echo ""
echo -e "\033[32m================================\033[0m"
echo -e "\033[32mInstallation Complete!\033[0m"
echo -e "\033[32m================================\033[0m"
echo ""
echo "MCP Tool Kit has been installed to:"
echo -e "  \033[33m$install_path\033[0m"
echo ""
echo "To start MCP Tool Kit:"
if [ "$(detect_os)" = "macos" ]; then
    echo -e "  - Open from ~/Applications/MCP Tool Kit.app"
    echo -e "  - Or run: \033[33m$install_path/launch.sh\033[0m"
else
    echo -e "  - Use the desktop shortcut (if created)"
    echo -e "  - Or run: \033[33m$install_path/launch.sh\033[0m"
fi
echo ""
echo "For Claude Desktop configuration:"
if [ "$(detect_os)" = "macos" ]; then
    echo -e "  Add to: \033[33m~/Library/Application Support/Claude/claude_desktop_config.json\033[0m"
else
    echo -e "  Add to: \033[33m~/.config/Claude/claude_desktop_config.json\033[0m"
fi
echo ""
echo "Press Enter to exit..."
read