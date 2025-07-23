---
sidebar_position: 1
---

# Installation

There are several ways to install and run MCP Tool Kit.

## Prerequisites

Before installing, ensure you have:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/downloads) (optional, for cloning the repository)

## Quick Install (Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/getfounded/mcp-tool-kit.git
cd mcp-tool-kit
```

Or download the ZIP file from GitHub and extract it.

### 2. Run the Launcher

#### Windows
Double-click `launch.bat` or run:
```cmd
launch.bat
```

#### Mac/Linux
```bash
chmod +x launch.sh
./launch.sh
```

### 3. Choose Your Mode

The launcher will present options:
1. **stdio mode** - For Claude Desktop integration
2. **SSE mode** - For web access at http://localhost:8080

## Manual Installation

### Using Docker Compose

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### Using Docker Directly

```bash
# Build the image
docker build -t mcp-tool-kit .

# Run the container
docker run -it --rm \
  -v ~/.env:/app/.env \
  -v ~/Documents:/app/documents \
  mcp-tool-kit
```

## Environment Configuration

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` to add your API keys:
```env
BRAVE_SEARCH_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
FRED_API_KEY=your_key_here
# Add other API keys as needed
```

## Verifying Installation

After starting the server, you can verify it's working:

### For stdio mode
Check the Docker logs:
```bash
docker logs mcp-server
```

### For SSE mode
Visit http://localhost:8080 in your browser.

## Troubleshooting

### Docker not found
- Ensure Docker Desktop is installed and running
- On Windows, make sure Docker is in your PATH

### Permission denied on Linux/Mac
```bash
chmod +x launch.sh
sudo ./launch.sh
```

### Port already in use
Change the port in `docker-compose.yml` or stop the conflicting service.

## Next Steps

- [Quick Start Guide](quick-start) - Connect to Claude Desktop
- [Configuration](configuration) - Configure tools and settings