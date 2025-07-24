# Deploy Documentation Now

The documentation site at docs.mcp-tool-kit.com appears to be showing only the README instead of the full Docusaurus documentation. Here's how to fix it:

## Quick Deploy Steps

### Option 1: Trigger GitHub Actions (Recommended)

1. Go to the [Actions tab](https://github.com/getfounded/mcp-tool-kit/actions) on GitHub
2. Find "Deploy Documentation to GitHub Pages" workflow
3. Click "Run workflow" > "Run workflow" to manually trigger deployment

### Option 2: Local Deployment

```bash
# Navigate to docs directory
cd docs

# Install dependencies
npm install

# Build the documentation
npm run build

# Deploy to GitHub Pages
npm run deploy
```

### Option 3: Force Deployment via Empty Commit

```bash
# Make an empty commit to trigger the workflow
git commit --allow-empty -m "Trigger docs deployment"
git push origin main
```

## Verify Deployment

After deployment (takes 2-5 minutes):
1. Visit https://docs.mcp-tool-kit.com
2. You should see the Docusaurus site, not just the README
3. Check for the proper navigation sidebar

## Troubleshooting

If the site still shows only README:

1. **Check GitHub Pages Settings**:
   - Go to Settings > Pages in your repository
   - Source should be "Deploy from a branch"
   - Branch should be "gh-pages" / "(root)"

2. **Clear GitHub Pages Cache**:
   - Go to Settings > Pages
   - Change custom domain to something else
   - Save, wait 1 minute
   - Change back to docs.mcp-tool-kit.com
   - Save again

3. **Check DNS**:
   - Ensure CNAME record points to getfounded.github.io
   - DNS propagation can take up to 24 hours

## Current Setup Status

✅ Docusaurus is properly configured
✅ GitHub Actions workflows are set up
✅ CNAME file is in place
✅ Documentation content exists

The issue is likely that:
- The workflow hasn't been triggered recently
- GitHub Pages is serving cached content
- The gh-pages branch needs to be updated