---
sidebar_position: 1
---

# Installation

There are several ways to install and run MCP Tool Kit.

## 🚀 Quick Install - No Git Required!

The easiest way to install MCP Tool Kit is using our one-line installers:

### 🖥️ Windows

Open PowerShell as Administrator and run:

```powershell
irm https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1 | iex
```

### 🍎 macOS

Open Terminal and run:

```bash
bash <(curl -s https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
```

### 🐧 Linux

Open Terminal and run:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
```

## ✨ What the Quick Installer Does

The installer will automatically:

1. **Download MCP Tool Kit** - No Git required!
2. **Check for Docker** - Helps install if missing
3. **Create shortcuts** - Desktop and Start Menu/Applications
4. **Set up launcher** - Easy menu-driven interface
5. **Configure paths** - Optionally adds to system PATH

## 📋 Prerequisites

The only requirement is:
- **Docker Desktop** - The installer will help you install it if needed

Supported Operating Systems:
- Windows 10/11 (with PowerShell 5.0+)
- macOS 10.14+
- Linux with bash shell

## 📦 Alternative Installation Methods

### Method 1: Download Pre-packaged Release

1. Download the latest release:
   - [Windows: MCP-Tool-Kit-Windows.zip](https://github.com/getfounded/mcp-tool-kit/releases/latest)
   - [Mac/Linux: MCP-Tool-Kit-Unix.tar.gz](https://github.com/getfounded/mcp-tool-kit/releases/latest)

2. Extract and run:
   - **Windows**: Run `install.bat`
   - **Mac/Linux**: Run `./install.sh`

### Method 2: Git Clone (for developers)

```bash
git clone https://github.com/getfounded/mcp-tool-kit.git
cd mcp-tool-kit
```

### Method 3: Docker-Only Installation

If you already have Docker and want the minimal setup:

```bash
docker run -it --name mcp-toolkit ghcr.io/getfounded/mcp-tool-kit:latest
```

## 🚦 Running MCP Tool Kit

After installation, use the launcher:

### Windows
Double-click the desktop shortcut or run:
```cmd
C:\Users\%USERNAME%\mcp-tool-kit\launch.ps1
```

### Mac/Linux
Open from Applications (macOS) or run:
```bash
~/mcp-tool-kit/launch.sh
```

### Choose Your Mode

The launcher will present options:
1. **stdio mode** - For Claude Desktop integration
2. **SSE mode** - For web access at http://localhost:8080
3. **Update** - Update to the latest version
4. **View logs** - Check server logs

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