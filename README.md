# MCP Tool Kit

A comprehensive toolkit for the Model Context Protocol (MCP) with automatic tool discovery and multiple transport options.

[![PyPI version](https://img.shields.io/pypi/v/mcptoolkit.svg)](https://pypi.org/project/mcptoolkit/)
[![Python versions](https://img.shields.io/pypi/pyversions/mcptoolkit.svg)](https://pypi.org/project/mcptoolkit/)
[![License](https://img.shields.io/github/license/getfounded/mcp-tool-kit.svg)](https://github.com/getfounded/mcp-tool-kit/blob/main/LICENSE)

📚 **[Official Documentation](https://docs.mcp-tool-kit.com)** | 🌐 **[Website](https://mcp-tool-kit.com)** | 💬 **[Community](https://github.com/getfounded/mcp-tool-kit/discussions)**

---

🚀 **Built by [UsefulAI](https://usefulai.ai)** | 📖 **[From GitHub to Commercial Success](https://usefulai.ai/blog/articles/from-github-to-commercial-success)**

## 🚀 Quick Install - No Git Required!

Choose your platform and run ONE command:

### 🖥️ Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.ps1 | iex
```

### 🍎 macOS (Terminal)
```bash
bash <(curl -s https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
```

### 🐧 Linux (Terminal)
```bash
bash <(wget -qO- https://raw.githubusercontent.com/getfounded/mcp-tool-kit/main/install.sh)
```

**That's it!** The installer will:
- ✅ Download MCP Tool Kit (no Git needed!)
- ✅ Check for Docker (helps install if missing)
- ✅ Create desktop shortcuts
- ✅ Set up everything automatically

## 📦 Alternative Installation Methods

<details>
<summary>Manual Download</summary>

1. Download the latest release:
   - [Windows: MCP-Tool-Kit-Windows.zip](https://github.com/getfounded/mcp-tool-kit/releases/latest)
   - [Mac/Linux: MCP-Tool-Kit-Unix.tar.gz](https://github.com/getfounded/mcp-tool-kit/releases/latest)

2. Extract and run:
   - **Windows**: Run `install.bat`
   - **Mac/Linux**: Run `./install.sh`
</details>

<details>
<summary>Git Installation (for developers)</summary>

1. **Clone the repository**
   ```bash
   git clone https://github.com/getfounded/mcp-tool-kit.git
   cd mcp-tool-kit
   ```

2. **Run the launcher**
   - **Windows**: Double-click `launch.bat`
   - **Mac/Linux**: Run `./launch.sh`
</details>

<details>
<summary>Docker-Only Installation</summary>

```bash
docker run -it --name mcp-toolkit ghcr.io/getfounded/mcp-tool-kit:latest
```
</details>

## 🔧 Features

### Dynamic Tool Registration
Tools are automatically discovered and registered at runtime - no manual configuration needed!

### Multiple Transport Options
- **stdio**: For Claude Desktop integration
- **SSE (Server-Sent Events)**: For web-based access

### 120+ Available Tools
- 📁 **File System**: Read, write, and manage files
- 🕐 **Time Tools**: Timezone conversions and time operations
- 🌐 **Web Search**: Brave Search integration
- 🤖 **Browser Automation**: Playwright-based browser control
- 📊 **Data Analysis**: Yahoo Finance, FRED, World Bank data
- 📄 **Document Tools**: PDF, Excel, PowerPoint manipulation
- 🎯 **And many more!**

### Easy Configuration
Control everything through a simple `config.yaml` file:

```yaml
enabled_tools:
  filesystem: true
  time_tools: true
  brave_search: true
  # ... more tools

tool_config:
  filesystem:
    allowed_directories: ["~/Documents", "~/Downloads"]
  brave_search:
    max_results: 10
```

## 📋 Environment Setup

1. Copy `.env.template` to `.env`
2. Add your API keys:
   ```env
   BRAVE_SEARCH_API_KEY=your_key_here
   NEWS_API_KEY=your_key_here
   FRED_API_KEY=your_key_here
   # ... other keys
   ```

## 💾 Storage Setup

MCP Tool Kit uses a dedicated storage directory for file operations:

- **Windows**: `C:\Users\{Username}\mcp-tool-kit-storage`
- **Mac/Linux**: `~/mcp-tool-kit-storage`

### Automatic Setup
The storage directory is automatically created when you first run the Docker container. You can also manually set it up:

**Windows (PowerShell)**:
```powershell
.\scripts\setup-storage.ps1
```

**Mac/Linux**:
```bash
./scripts/setup-storage.sh
```

### Storage Structure
```
mcp-tool-kit-storage/
├── documents/     # For document files
├── downloads/     # For downloaded files
└── workspace/     # For temporary work files
```

All file operations through the filesystem tool will be restricted to this directory for security.

## 🔌 Connecting to Claude Desktop

1. Start the server in stdio mode using the launcher
2. Add to Claude Desktop configuration:
   ```json
   {
     "mcpServers": {
       "mcp-tool-kit": {
         "command": "docker",
         "args": ["exec", "-i", "mcp-server", "python", "mcp_server_v2.py"]
       }
     }
   }
   ```

## 🌐 Using SSE Mode

1. Start the server in SSE mode using the launcher
2. Access the server at `http://localhost:8080`
3. Use the SSE endpoints:
   - `/sse` - Server-Sent Events stream
   - `/messages` - Send messages to the server

## 🛠️ Creating Custom Tools

Tools now use a standardized base class system:

```python
from app.tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    def get_name(self) -> str:
        return "My Custom Tool"
        
    def get_tools(self) -> Dict[str, Callable]:
        return {
            "my_function": self.my_function
        }
        
    async def my_function(self, param: str, ctx: Context = None) -> str:
        return f"Processed: {param}"
```

See the [developer documentation](https://docs.mcp-tool-kit.com) for detailed guides.

## 📚 Documentation

Full documentation is available at [https://docs.mcp-tool-kit.com](https://docs.mcp-tool-kit.com).

To run documentation locally:
1. `cd docs`
2. `npm install`
3. `npm start`

## 🐳 Docker Commands

### Using the Launcher (Recommended)
The launcher scripts handle all Docker operations automatically.

### Manual Commands
```bash
# Start server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop server
docker-compose down

# Rebuild after changes
docker-compose build --no-cache
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add your tool to `app/tools/`
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- [GitHub Issues](https://github.com/getfounded/mcp-tool-kit/issues)
- [Documentation](https://docs.mcp-tool-kit.com)
- [Discord Community](#) (coming soon)