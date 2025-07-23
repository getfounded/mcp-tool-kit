#!/bin/bash

echo "========================================"
echo "MCP Tool Kit Launcher"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed."
    echo
    echo "Please install Docker Desktop from:"
    echo "https://www.docker.com/products/docker-desktop"
    echo
    exit 1
fi

echo "[INFO] Docker is installed."
echo

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "[WARNING] Git is not installed."
    echo "You may need Git for future updates."
    echo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Install Git on macOS: brew install git"
    else
        echo "Install Git on Linux: sudo apt-get install git"
    fi
    echo
fi

# Check docker-compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "[INFO] Using 'docker-compose' (legacy syntax)"
else
    COMPOSE_CMD="docker compose"
    echo "[INFO] Using 'docker compose' (new syntax)"
fi

echo
echo "Choose an option:"
echo "1. Start MCP Server (stdio mode - for Claude Desktop)"
echo "2. Start MCP Server (SSE mode - for web access)"
echo "3. Stop MCP Server"
echo "4. View server logs"
echo "5. Rebuild server (after updates)"
echo "6. Setup environment file"
echo "7. Exit"
echo

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        echo
        echo "Starting MCP Server in stdio mode..."
        $COMPOSE_CMD up -d
        echo
        echo "Server started! To connect with Claude Desktop:"
        echo "1. Open Claude Desktop settings"
        echo "2. Add server with command: docker exec -it mcp-server python mcp_server_v2.py"
        echo
        ;;
    2)
        echo
        echo "Starting MCP Server in SSE mode..."
        $COMPOSE_CMD up -d
        sleep 3
        docker exec -d mcp-server python mcp_server_v2.py --transport sse --port 8080
        echo
        echo "Server started in SSE mode!"
        echo "Access at: http://localhost:8080"
        echo
        ;;
    3)
        echo
        echo "Stopping MCP Server..."
        $COMPOSE_CMD down
        echo "Server stopped."
        ;;
    4)
        echo
        echo "Showing server logs (press Ctrl+C to exit)..."
        $COMPOSE_CMD logs -f
        ;;
    5)
        echo
        echo "Rebuilding server..."
        $COMPOSE_CMD build --no-cache
        echo "Rebuild complete."
        ;;
    6)
        echo
        echo "Setting up environment file..."
        if [ ! -f .env ]; then
            cp .env.template .env
            echo "Created .env file from template."
            echo "Please edit .env to add your API keys."
        else
            echo ".env file already exists."
        fi
        ;;
    7)
        exit 0
        ;;
    *)
        echo "Invalid choice. Please try again."
        ;;
esac

echo
read -p "Press Enter to continue..."