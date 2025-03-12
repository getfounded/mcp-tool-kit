FROM python:3.12-slim

WORKDIR /app
COPY app/ /app/app/

# Install system dependencies for Playwright/Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    ca-certificates \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies - with proper dependency handling
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Install Playwright and browsers
RUN playwright install chromium firefox webkit
RUN playwright install-deps chromium

# Verify MCP and Playwright are installed
RUN python -c "import mcp; print(f'MCP')"
RUN python -c "import playwright; print(f'Playwright')"

# Copy application code
COPY . .

# Make the script executable
RUN chmod +x mcp_unified_server.py

# Create a healthcheck script
RUN echo '#!/bin/bash\npython -c "import mcp" || exit 1\ncurl -f http://localhost:8000/health || exit 1' > healthcheck.sh
RUN chmod +x healthcheck.sh

# Create entrypoint script with better debugging
RUN echo '#!/bin/bash\necho "DEBUG: Starting server"\necho "Python version: $(python --version)"\necho "Installed packages:"\npip list\necho "Environment variables:"\nenv | grep -v "API_KEY"\necho "Running MCP server..."\npython -u mcp_unified_server.py\necho "DEBUG: Server exited with code $?"' > entrypoint.sh
RUN chmod +x entrypoint.sh

# Command to run the server with unbuffered output
CMD ["./entrypoint.sh"]
