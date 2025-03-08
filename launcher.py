#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import time
import webbrowser
from pathlib import Path

def start_server(server_path, background=True):
    """Start the MCP server"""
    print(f"Starting MCP server from {server_path}...")
    
    if background:
        # Start server in the background
        if os.name == 'nt':  # Windows
            server_process = subprocess.Popen(
                ["python", server_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix/Linux/Mac
            server_process = subprocess.Popen(
                ["python", server_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        print(f"MCP server started with PID: {server_process.pid}")
        return server_process
    else:
        # Start server in the foreground (blocking)
        subprocess.run(["python", server_path])
        return None

def start_config_ui(ui_path, port=8501):
    """Start the Streamlit configuration UI"""
    print(f"Starting configuration UI from {ui_path} on port {port}...")
    
    # Start Streamlit app
    if os.name == 'nt':  # Windows
        ui_process = subprocess.Popen(
            ["streamlit", "run", ui_path, "--server.port", str(port)],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:  # Unix/Linux/Mac
        ui_process = subprocess.Popen(
            ["streamlit", "run", ui_path, "--server.port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    print(f"Configuration UI started with PID: {ui_process.pid}")
    
    # Give it a moment to start
    time.sleep(2)
    
    # Open browser
    webbrowser.open(f"http://localhost:{port}")
    
    return ui_process

def main():
    parser = argparse.ArgumentParser(description="MCP Unified Server Launcher")
    parser.add_argument("--server-only", action="store_true", help="Start only the MCP server")
    parser.add_argument("--ui-only", action="store_true", help="Start only the configuration UI")
    parser.add_argument("--server-port", type=int, default=8000, help="Port for the MCP server")
    parser.add_argument("--ui-port", type=int, default=8501, help="Port for the Streamlit UI")
    args = parser.parse_args()
    
    # Get paths
    base_dir = Path(__file__).parent
    server_path = base_dir / "mcp_unified_server.py"
    ui_path = base_dir / "config_ui.py"
    
    # Check if files exist
    if not server_path.exists():
        print(f"Error: MCP server file not found at {server_path}")
        return 1
        
    if not ui_path.exists() and not args.server_only:
        print(f"Error: Configuration UI file not found at {ui_path}")
        print("Make sure to place the config_ui.py file in the same directory as this launcher.")
        return 1
    
    processes = []
    
    try:
        # Start the server if requested
        if not args.ui_only:
            server_process = start_server(server_path, background=not args.server_only)
            if server_process:
                processes.append(server_process)
                print(f"MCP server running on http://localhost:{args.server_port}")
        
        # Start the UI if requested
        if not args.server_only:
            ui_process = start_config_ui(ui_path, port=args.ui_port)
            processes.append(ui_process)
            print(f"Configuration UI running on http://localhost:{args.ui_port}")
        
        # If not running in background, we'll exit when the process exits
        if args.server_only and not args.ui_only:
            return 0
            
        # Keep the main process alive so we can handle keyboard interrupt
        print("\nPress Ctrl+C to stop all services...\n")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down services...")
        
        # Terminate all child processes
        for process in processes:
            if process.poll() is None:  # If process is still running
                process.terminate()
                print(f"Terminated process with PID: {process.pid}")
        
        print("All services stopped.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
