FROM python:3.12-slim

WORKDIR /app

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

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install chromium firefox webkit && \
    playwright install-deps chromium

# Verify critical packages are installed
RUN python -c "import mcp; print('MCP installed successfully')" && \
    python -c "import playwright; print('Playwright installed successfully')"

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x mcp_unified_server.py mcp_server_v2.py

# Create a healthcheck script
RUN echo '#!/bin/bash\npython -c "import mcp" || exit 1' > healthcheck.sh && \
    chmod +x healthcheck.sh

# Create entrypoint script for debugging
RUN echo '#!/bin/bash\n\
echo "Starting MCP Server..."\n\
echo "Python version: $(python --version)"\n\
echo "Working directory: $(pwd)"\n\
echo "Available scripts:"\n\
ls -la *.py\n\
echo "Running MCP server v2..."\n\
python -u mcp_server_v2.py "$@"' > entrypoint.sh && \
    chmod +x entrypoint.sh

# Default command runs the new dynamic server
CMD ["./entrypoint.sh"]