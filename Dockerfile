FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify MCP is installed
RUN python -c "import mcp; print(f'MCP')"

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
