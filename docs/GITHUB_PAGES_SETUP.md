# GitHub Pages Setup Guide

This guide will help you deploy the MCP Tool Kit documentation to GitHub Pages.

## Prerequisites

1. You must have write access to the repository
2. GitHub Pages must be enabled for the repository
3. Node.js 18+ must be installed locally

## Setup Steps

### 1. Enable GitHub Pages in Repository Settings

1. Go to your repository on GitHub: https://github.com/getfounded/mcp-tool-kit
2. Click on **Settings** (in the repository, not your profile)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select **Deploy from a branch**
5. Under **Branch**, select **gh-pages** and **/ (root)**
6. Click **Save**

### 2. Initial Manual Deployment (One-time)

Before the automatic deployment works, you need to create the `gh-pages` branch:

```bash
# Navigate to docs directory
cd docs

# Install dependencies
npm install

# Deploy to GitHub Pages
npm run deploy
```

This command will:
- Build the documentation
- Create a `gh-pages` branch if it doesn't exist
- Push the built files to that branch
- The site will be available at: https://getfounded.github.io/mcp-tool-kit/

### 3. Automatic Deployment (GitHub Actions)

After the initial deployment, the GitHub Actions will automatically deploy when you:
- Push changes to the `main` branch
- Modify any files in the `docs/` directory

Two workflows are available:
1. `deploy-docs.yml` - Uses GitHub's official pages deployment
2. `deploy-docs-docusaurus.yml` - Uses Docusaurus's built-in deployment

**Note**: Use only one workflow at a time. You can disable one by renaming it to `.yml.disabled`

### 4. Verify Deployment

After deployment (manual or automatic):
1. Go to https://getfounded.github.io/mcp-tool-kit/
2. You should see the documentation site
3. Check the Actions tab in GitHub to see deployment status

## Troubleshooting

### "npm run deploy" fails with permission error

Make sure you're authenticated with GitHub:
```bash
# Set up git credentials
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# Or use GitHub CLI
gh auth login
```

### GitHub Action fails

1. Check that GitHub Pages is enabled in repository settings
2. Ensure the `gh-pages` branch exists (create with initial manual deployment)
3. Check the Actions tab for specific error messages

### Site not updating

1. It can take 5-10 minutes for changes to appear
2. Clear your browser cache
3. Check the deployment status in Settings > Pages

### Custom Domain

To use a custom domain:
1. Create a `CNAME` file in `docs/static/` with your domain
2. Configure your domain's DNS to point to GitHub Pages
3. Enable HTTPS in repository settings

## Local Development

To test changes locally before deploying:

```bash
cd docs
npm install
npm start
```

This starts a development server at http://localhost:3000

## Manual Deployment Options

If you prefer not to use GitHub Actions:

```bash
# Option 1: Direct deployment
cd docs
npm run deploy

# Option 2: Build and deploy separately
npm run build
# Then commit the build folder to gh-pages branch manually
```

## Additional Configuration

### Change Documentation URL

Edit `docs/docusaurus.config.js`:
```js
url: 'https://yourdomain.com',
baseUrl: '/', // Change to '/' for custom domain
```

### Deploy to Different Branch

Edit the `deploymentBranch` in `docusaurus.config.js`:
```js
deploymentBranch: 'docs-deployment', // Instead of 'gh-pages'
```

## Security Notes

- The GitHub Actions use `GITHUB_TOKEN` which is automatically provided
- No additional secrets need to be configured
- The token has limited permissions (only pages deployment)

## Need Help?

- Check Docusaurus deployment docs: https://docusaurus.io/docs/deployment
- Open an issue: https://github.com/getfounded/mcp-tool-kit/issues