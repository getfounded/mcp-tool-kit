---
sidebar_position: 1
---

# Introduction

Welcome to the **MCP Tool Kit** documentation! This toolkit provides a comprehensive set of tools for the Model Context Protocol (MCP), enabling AI assistants to interact with various services and perform complex tasks.

## What is MCP Tool Kit?

MCP Tool Kit is a collection of tools designed to extend the capabilities of AI assistants using the Model Context Protocol. It includes:

- **File System Operations** - Read, write, and manage files
- **Time & Timezone Tools** - Handle time conversions and timezone operations
- **Browser Automation** - Control web browsers programmatically
- **Document Management** - Work with PDFs, Excel, and PowerPoint files
- **Data Analysis** - Access financial data, economic indicators, and more
- **API Integrations** - Connect to various services like News API, Shopify, and more

## Key Features

### 🚀 Dynamic Tool Registration
Tools are automatically discovered and registered at runtime, making it easy to add new capabilities.

### 🔧 Flexible Configuration
Control which tools are enabled and configure their behavior through a simple YAML file.

### 🌐 Multiple Transport Options
Support for both stdio (for Claude Desktop) and SSE (Server-Sent Events) transports.

### 🐳 Docker Support
Easy deployment with Docker, including one-click launch scripts.

### 📚 Extensible Architecture
Built on a standardized base class system that makes creating new tools straightforward.

## Getting Started

To get started with MCP Tool Kit:

1. **[Install](getting-started/installation)** the toolkit using Docker or manual setup
2. **[Configure](getting-started/configuration)** the tools you want to use
3. **[Connect](getting-started/quick-start)** to Claude Desktop or use the SSE transport
4. **[Create](development/creating-tools)** your own custom tools

## Architecture Overview

```
mcp-tool-kit/
├── app/
│   └── tools/           # Tool modules
│       ├── base_tool.py # Base class for all tools
│       └── *.py         # Individual tool implementations
├── mcp_server_v2.py     # Dynamic server with auto-registration
├── config.yaml          # Configuration file
├── docker-compose.yml   # Docker configuration
└── launch.sh/bat        # Easy launch scripts
```

## Next Steps

- Learn how to [install](getting-started/installation) MCP Tool Kit
- Explore the [available tools](tools/overview)
- Start [developing your own tools](development/creating-tools)