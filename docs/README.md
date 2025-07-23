# MCP Tool Kit Documentation

This directory contains the Docusaurus-based documentation for MCP Tool Kit.

## 🚀 Quick Start

### Prerequisites
- Node.js 18.0 or above
- npm or yarn

### Installation

```bash
# Navigate to docs directory
cd docs

# Install dependencies
npm install
```

### Local Development

```bash
# Start the development server
npm start
```

This command starts a local development server and opens up a browser window at http://localhost:3000. Most changes are reflected live without having to restart the server.

### Build

```bash
# Build static files
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Serve Built Files

```bash
# Test the production build locally
npm run serve
```

## 📁 Project Structure

```
docs/
├── docs/                    # Markdown documentation files
│   ├── intro.md            # Homepage
│   ├── getting-started/    # Installation and setup guides
│   ├── development/        # Tool development guides
│   ├── tools/              # Tool documentation
│   ├── deployment/         # Deployment guides
│   └── api/                # API reference
├── src/                    # React components and custom pages
│   ├── components/         # React components
│   ├── css/               # Global styles
│   └── pages/             # Custom pages
├── static/                 # Static assets
├── docusaurus.config.js    # Docusaurus configuration
├── sidebars.js            # Sidebar configuration
└── package.json           # Dependencies and scripts
```

## 🚀 Deployment Options

### 1. GitHub Pages

Add to `docusaurus.config.js`:
```js
const config = {
  url: 'https://your-username.github.io',
  baseUrl: '/mcp-tool-kit/',
  organizationName: 'your-username',
  projectName: 'mcp-tool-kit',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
};
```

Deploy:
```bash
npm run deploy
```

### 2. Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/getfounded/mcp-tool-kit)

1. Connect your GitHub repo to Netlify
2. Set build command: `cd docs && npm install && npm run build`
3. Set publish directory: `docs/build`
4. Deploy!

### 3. Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd docs
vercel
```

Configuration:
- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm install`

### 4. Docker

Create `docs/Dockerfile`:
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
```

Build and run:
```bash
docker build -t mcp-docs .
docker run -p 8080:80 mcp-docs
```

### 5. Static Hosting

After building, upload the `build` directory to any static host:
- AWS S3 + CloudFront
- Google Cloud Storage
- Azure Static Web Apps
- Surge.sh
- Render

## 🔧 Configuration

### Changing Site Metadata

Edit `docusaurus.config.js`:
```js
const config = {
  title: 'Your Site Title',
  tagline: 'Your tagline',
  favicon: 'img/favicon.ico',
  url: 'https://your-site.com',
  baseUrl: '/',
};
```

### Adding New Documentation

1. Create a new `.md` file in the appropriate directory
2. Add front matter:
```md
---
sidebar_position: 1
title: My New Page
---

# My New Page
Content here...
```

3. Update `sidebars.js` if needed

### Custom Pages

Create React components in `src/pages/`:
```jsx
// src/pages/custom.js
import React from 'react';
import Layout from '@theme/Layout';

export default function Custom() {
  return (
    <Layout title="Custom Page">
      <h1>Custom Page</h1>
    </Layout>
  );
}
```

## 📝 Writing Documentation

### Markdown Features

- **Code blocks** with syntax highlighting
- **Admonitions** for notes, warnings, tips
- **Tabs** for multiple code examples
- **Live code editor** (optional plugin)

Example:
```md
:::tip Pro Tip
Use admonitions to highlight important information!
:::

```python
def hello_world():
    print("Hello from MCP Tool Kit!")
```
```

### Adding Images

Place images in `static/img/` and reference them:
```md
![Description](/img/my-image.png)
```

## 🛠️ Maintenance

### Updating Dependencies

```bash
# Check for updates
npm outdated

# Update Docusaurus
npm update @docusaurus/core @docusaurus/preset-classic
```

### Common Issues

**Build fails with memory error:**
```bash
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

**Port already in use:**
```bash
npm start -- --port 3001
```

## 📚 Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Markdown Guide](https://www.markdownguide.org/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes in the `docs/` directory
4. Test locally with `npm start`
5. Submit a pull request

## 📄 License

The documentation is licensed under the same license as the MCP Tool Kit project.