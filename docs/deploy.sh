#!/bin/bash

echo "MCP Tool Kit Documentation Deployment"
echo "===================================="
echo

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    echo "Please install Node.js 18.0 or above from https://nodejs.org"
    exit 1
fi

# Check node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js version must be 18.0 or above"
    echo "Current version: $(node -v)"
    exit 1
fi

echo "Choose deployment target:"
echo "1. Local development server"
echo "2. Build for production"
echo "3. Deploy to GitHub Pages"
echo "4. Deploy to Netlify"
echo "5. Deploy to Vercel"
echo "6. Build Docker image"
echo

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo "Starting local development server..."
        npm install
        npm start
        ;;
    2)
        echo "Building for production..."
        npm install
        npm run build
        echo
        echo "Build complete! Files are in the 'build' directory."
        echo "You can test the build with: npm run serve"
        ;;
    3)
        echo "Deploying to GitHub Pages..."
        echo "Make sure you've configured docusaurus.config.js with:"
        echo "  - url: your GitHub Pages URL"
        echo "  - baseUrl: your repository name"
        echo "  - organizationName: your GitHub username"
        echo "  - projectName: your repository name"
        echo
        read -p "Have you configured these settings? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            npm install
            npm run deploy
        else
            echo "Please configure docusaurus.config.js first"
        fi
        ;;
    4)
        echo "Deploying to Netlify..."
        echo
        echo "Option 1: Use Netlify CLI"
        echo "  npm install -g netlify-cli"
        echo "  netlify deploy"
        echo
        echo "Option 2: Connect GitHub repo at https://app.netlify.com"
        echo "  Build command: cd docs && npm install && npm run build"
        echo "  Publish directory: docs/build"
        ;;
    5)
        echo "Deploying to Vercel..."
        if ! command -v vercel &> /dev/null; then
            echo "Installing Vercel CLI..."
            npm install -g vercel
        fi
        npm install
        npm run build
        vercel --prod
        ;;
    6)
        echo "Building Docker image..."
        
        # Create Dockerfile if it doesn't exist
        if [ ! -f "Dockerfile" ]; then
            cat > Dockerfile << 'EOF'
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
            echo "Created Dockerfile"
        fi
        
        docker build -t mcp-tool-kit-docs .
        echo
        echo "Docker image built successfully!"
        echo "Run with: docker run -p 8080:80 mcp-tool-kit-docs"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac