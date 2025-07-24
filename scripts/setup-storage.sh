#!/bin/bash
# Bash script to set up storage directory on Unix-like systems

STORAGE_DIR="$HOME/mcp-tool-kit-storage"

# Create the storage directory if it doesn't exist
if [ ! -d "$STORAGE_DIR" ]; then
    echo "Creating storage directory at: $STORAGE_DIR"
    mkdir -p "$STORAGE_DIR"
    echo "Storage directory created successfully!"
else
    echo "Storage directory already exists at: $STORAGE_DIR"
fi

# Create subdirectories for better organization
subdirs=("documents" "downloads" "workspace")
for subdir in "${subdirs[@]}"; do
    path="$STORAGE_DIR/$subdir"
    if [ ! -d "$path" ]; then
        mkdir -p "$path"
        echo "Created subdirectory: $subdir"
    fi
done

echo ""
echo "Storage setup complete!"
echo "Your MCP Tool Kit storage is located at: $STORAGE_DIR"