# Quick Install Guide - No Git Required! 🚀

Install MCP Tool Kit with a single command - no Git installation needed!

## 🖥️ Windows

Open PowerShell as Administrator and run:

```powershell
irm https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1 | iex
```

Or download and run manually:
1. Download: https://github.com/getfounded/mcp-tool-kit/releases/latest/download/install.ps1
2. Right-click → "Run with PowerShell"

## 🍎 macOS

Open Terminal and run:

```bash
bash <(curl -s https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
```

## 🐧 Linux

Open Terminal and run:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
```

## 📦 Alternative: Pre-packaged Downloads

If the above commands don't work, download the pre-packaged version:

### Windows
- [Download MCP-Tool-Kit-Windows.zip](https://github.com/getfounded/mcp-tool-kit/releases/latest/download/MCP-Tool-Kit-Windows.zip)
- Extract and run `install.bat`

### macOS/Linux
- [Download MCP-Tool-Kit-Unix.tar.gz](https://github.com/getfounded/mcp-tool-kit/releases/latest/download/MCP-Tool-Kit-Unix.tar.gz)
- Extract and run `./install.sh`

## 🐳 Docker-Only Installation

If you only have Docker and want the minimal setup:

```bash
docker run -it --name mcp-toolkit ghcr.io/getfounded/mcp-tool-kit:latest
```

## ✨ What the Installer Does

1. **Downloads MCP Tool Kit** - No Git required!
2. **Checks for Docker** - Offers to help install if missing
3. **Creates shortcuts** - Desktop and Start Menu/Applications
4. **Sets up launcher** - Easy menu-driven interface
5. **Configures paths** - Adds to system PATH (optional)

## 🚦 Post-Installation

After installation:

1. **Start MCP Tool Kit**:
   - Use the desktop shortcut, or
   - Run the launcher script in the installation directory

2. **Configure Claude Desktop**:
   - The installer will show you the exact path to add to your Claude config

3. **Choose your mode**:
   - Option 1: Claude Desktop integration (stdio)
   - Option 2: Web API access (SSE on port 8080)

## 🔧 System Requirements

- **Docker Desktop** (installer will help you get it)
- **Windows**: PowerShell 5.0+ (comes with Windows 10/11)
- **macOS**: macOS 10.14+
- **Linux**: bash, curl or wget

## 📚 Need Help?

- [Full Documentation](https://docs.mcp-tool-kit.com)
- [Troubleshooting Guide](https://docs.mcp-tool-kit.com/troubleshooting)
- [GitHub Issues](https://github.com/getfounded/mcp-tool-kit/issues)

## 🔄 Updating

The installer includes an update option. Just run the launcher and select "Update MCP Tool Kit".