#!/usr/bin/env python3
import os
import sys
import json
import logging
import tempfile
import subprocess
import signal
import time
import re
import psutil
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from enum import Enum
import threading

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Streamlit tools MCP reference set")


class StreamlitTools(str, Enum):
    """Enum of Streamlit tool names"""
    CREATE_APP = "streamlit_create_app"
    RUN_APP = "streamlit_run_app"
    STOP_APP = "streamlit_stop_app"
    LIST_APPS = "streamlit_list_apps"
    GET_APP_URL = "streamlit_get_app_url"
    MODIFY_APP = "streamlit_modify_app"
    CHECK_DEPS = "streamlit_check_deps"


class StreamlitService:
    """Service to manage Streamlit applications via MCP"""

    def __init__(self, apps_dir=None, port_range=(8501, 8599)):
        """Initialize the Streamlit service"""
        self.apps_dir = apps_dir or os.path.expanduser("~/streamlit_apps")
        self.port_range = port_range
        self.running_apps = {}  # app_id -> {process, port, url}
        self.app_logs = {}  # app_id -> log_content

        # Create apps directory if it doesn't exist
        os.makedirs(self.apps_dir, exist_ok=True)

        # Track used ports
        self.used_ports = set()

        # Add lock for thread safety
        self.lock = threading.Lock()

        logging.info(f"Initialized Streamlit service at {self.apps_dir}")

    def _find_available_port(self):
        """Find an available port for a Streamlit app"""
        with self.lock:
            for port in range(self.port_range[0], self.port_range[1] + 1):
                if port not in self.used_ports:
                    # Also check if port is really free (in case an external process is using it)
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    if result != 0:  # Port is available
                        self.used_ports.add(port)
                        return port

            raise ValueError(f"No available ports in range {self.port_range}")

    def _release_port(self, port):
        """Release a port when an app is stopped"""
        with self.lock:
            if port in self.used_ports:
                self.used_ports.remove(port)

    def validate_app_id(self, app_id):
        """Validate that an app ID is safe and suitable for a filename"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', app_id):
            raise ValueError(
                "App ID must contain only letters, numbers, underscores, and hyphens")
        return app_id

    def get_app_path(self, app_id):
        """Get the file path for a Streamlit app"""
        safe_app_id = self.validate_app_id(app_id)
        return os.path.join(self.apps_dir, f"{safe_app_id}.py")

    async def create_app(self, app_id, code, overwrite=False):
        """Create a new Streamlit app with the given code"""
        safe_app_id = self.validate_app_id(app_id)
        app_path = self.get_app_path(safe_app_id)

        # Check if app already exists
        if os.path.exists(app_path) and not overwrite:
            raise ValueError(
                f"App {app_id} already exists. Use overwrite=True to replace it.")

        # Write the app code to the file
        with open(app_path, 'w') as f:
            f.write(code)

        logging.info(f"Created Streamlit app '{app_id}' at {app_path}")

        return {
            "app_id": safe_app_id,
            "path": app_path,
            "status": "created"
        }

    async def run_app(self, app_id, port=None, browser=False):
        """Run a Streamlit app as a background process"""
        safe_app_id = self.validate_app_id(app_id)
        app_path = self.get_app_path(safe_app_id)

        # Check if app exists
        if not os.path.exists(app_path):
            raise ValueError(f"App {app_id} does not exist.")

        # Check if app is already running
        if safe_app_id in self.running_apps:
            return {
                "app_id": safe_app_id,
                "status": "already_running",
                "port": self.running_apps[safe_app_id]["port"],
                "url": self.running_apps[safe_app_id]["url"]
            }

        # Find an available port if not specified
        if port is None:
            port = self._find_available_port()

        # Create a log file
        log_path = os.path.join(self.apps_dir, f"{safe_app_id}.log")
        log_file = open(log_path, 'w')

        # Build the command
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            app_path,
            "--server.port", str(port),
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]

        if browser:
            cmd.extend(["--server.headless", "false"])

        # Launch the process
        try:
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Wait a bit to ensure process starts correctly
            time.sleep(2)

            # Check if process is running
            if process.poll() is not None:
                # Process failed to start
                log_file.close()
                with open(log_path, 'r') as f:
                    error_log = f.read()

                self._release_port(port)
                raise RuntimeError(
                    f"Failed to start Streamlit app. Error: {error_log}")

            # Store process info
            url = f"http://localhost:{port}"
            self.running_apps[safe_app_id] = {
                "process": process,
                "port": port,
                "url": url,
                "log_path": log_path,
                "log_file": log_file
            }

            logging.info(f"Started Streamlit app '{app_id}' on port {port}")

            return {
                "app_id": safe_app_id,
                "status": "running",
                "port": port,
                "url": url
            }

        except Exception as e:
            # Clean up if process failed to start
            log_file.close()
            self._release_port(port)
            raise Exception(f"Error starting Streamlit app: {str(e)}")

    async def stop_app(self, app_id):
        """Stop a running Streamlit app"""
        safe_app_id = self.validate_app_id(app_id)

        # Check if app is running
        if safe_app_id not in self.running_apps:
            return {
                "app_id": safe_app_id,
                "status": "not_running"
            }

        # Get process info
        app_info = self.running_apps[safe_app_id]
        process = app_info["process"]
        log_file = app_info["log_file"]
        port = app_info["port"]

        # Terminate the process (and all child processes)
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()

            # Wait for termination (with timeout)
            process.wait(timeout=10)

            # Close the log file
            if not log_file.closed:
                log_file.close()

            # Release the port
            self._release_port(port)

            # Remove from running apps
            del self.running_apps[safe_app_id]

            logging.info(f"Stopped Streamlit app '{app_id}'")

            return {
                "app_id": safe_app_id,
                "status": "stopped"
            }

        except Exception as e:
            logging.error(f"Error stopping Streamlit app '{app_id}': {str(e)}")

            # If process didn't terminate gracefully, kill it
            try:
                process.kill()
                self._release_port(port)

                # Close the log file
                if not log_file.closed:
                    log_file.close()

                # Remove from running apps
                del self.running_apps[safe_app_id]

                return {
                    "app_id": safe_app_id,
                    "status": "killed"
                }
            except Exception as kill_error:
                return {
                    "app_id": safe_app_id,
                    "status": "error",
                    "error": f"Failed to kill app: {str(kill_error)}"
                }

    async def list_apps(self):
        """List all available Streamlit apps"""
        # Get all .py files in the apps directory
        app_files = [f for f in os.listdir(self.apps_dir) if f.endswith('.py')]

        # Sort apps by timestamp (newest first)
        app_files.sort(key=lambda f: os.path.getmtime(
            os.path.join(self.apps_dir, f)), reverse=True)

        # Format results
        apps = []
        for app_file in app_files:
            app_id = app_file[:-3]  # Remove .py extension
            app_path = os.path.join(self.apps_dir, app_file)

            # Get file stats
            stats = os.stat(app_path)

            # Check if app is running
            is_running = app_id in self.running_apps

            app_info = {
                "app_id": app_id,
                "path": app_path,
                "size_bytes": stats.st_size,
                "modified": time.ctime(stats.st_mtime),
                "running": is_running
            }

            if is_running:
                app_info["port"] = self.running_apps[app_id]["port"]
                app_info["url"] = self.running_apps[app_id]["url"]

            apps.append(app_info)

        return {
            "apps": apps,
            "count": len(apps),
            "apps_dir": self.apps_dir
        }

    async def get_app_url(self, app_id):
        """Get the URL for a running Streamlit app"""
        safe_app_id = self.validate_app_id(app_id)

        # Check if app is running
        if safe_app_id not in self.running_apps:
            return {
                "app_id": safe_app_id,
                "status": "not_running"
            }

        # Get app URL
        app_info = self.running_apps[safe_app_id]

        return {
            "app_id": safe_app_id,
            "status": "running",
            "port": app_info["port"],
            "url": app_info["url"]
        }

    async def modify_app(self, app_id, code_updates=None, append_code=None):
        """Modify an existing Streamlit app"""
        safe_app_id = self.validate_app_id(app_id)
        app_path = self.get_app_path(safe_app_id)

        # Check if app exists
        if not os.path.exists(app_path):
            raise ValueError(f"App {app_id} does not exist.")

        # Read current code
        with open(app_path, 'r') as f:
            current_code = f.read()

        # Apply code updates if provided
        if code_updates:
            for old_text, new_text in code_updates:
                current_code = current_code.replace(old_text, new_text)

        # Append code if provided
        if append_code:
            current_code += "\n\n" + append_code

        # Write the updated code back to the file
        with open(app_path, 'w') as f:
            f.write(current_code)

        logging.info(f"Modified Streamlit app '{app_id}'")

        # Restart the app if it's running
        was_running = safe_app_id in self.running_apps
        result = {"app_id": safe_app_id,
                  "status": "modified", "was_running": was_running}

        if was_running:
            port = self.running_apps[safe_app_id]["port"]
            await self.stop_app(safe_app_id)
            restart_result = await self.run_app(safe_app_id, port=port)
            result["restart"] = restart_result

        return result

    async def check_dependencies(self):
        """Check if Streamlit and required dependencies are installed"""
        # Check for Streamlit
        try:
            # Run streamlit version command
            process = subprocess.run(
                [sys.executable, "-m", "streamlit", "--version"],
                capture_output=True,
                text=True,
                check=False
            )

            if process.returncode != 0:
                return {
                    "status": "error",
                    "streamlit_installed": False,
                    "error": process.stderr.strip() or "Streamlit is not installed correctly",
                    "install_command": "pip install streamlit"
                }

            streamlit_version = process.stdout.strip()

            # Check for other dependencies
            dependencies = ["pandas", "numpy",
                            "matplotlib", "altair", "plotly"]
            installed_deps = {}

            for dep in dependencies:
                try:
                    # Try to import the module
                    __import__(dep)
                    installed_deps[dep] = True
                except ImportError:
                    installed_deps[dep] = False

            return {
                "status": "success",
                "streamlit_installed": True,
                "streamlit_version": streamlit_version,
                "dependencies": installed_deps,
                "missing_dependencies": [dep for dep, installed in installed_deps.items() if not installed]
            }

        except Exception as e:
            return {
                "status": "error",
                "streamlit_installed": False,
                "error": str(e),
                "install_command": "pip install streamlit"
            }

# Tool function definitions that will be registered with MCP


async def streamlit_create_app(app_id: str, code: str, overwrite: bool = False, ctx: Context = None) -> str:
    """Create a new Streamlit app with the provided code

    Parameters:
    - app_id: Unique identifier for the app (letters, numbers, underscores, and hyphens only)
    - code: Python code for the Streamlit app
    - overwrite: Whether to overwrite an existing app with the same ID
    """
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.create_app(app_id, code, overwrite)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


async def streamlit_run_app(app_id: str, port: int = None, browser: bool = False, ctx: Context = None) -> str:
    """Run a Streamlit app as a background process

    Parameters:
    - app_id: Identifier of the app to run
    - port: Optional port number (if not specified, an available port will be used)
    - browser: Whether to open the app in a browser window
    """
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.run_app(app_id, port, browser)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


async def streamlit_stop_app(app_id: str, ctx: Context = None) -> str:
    """Stop a running Streamlit app

    Parameters:
    - app_id: Identifier of the app to stop
    """
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.stop_app(app_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


async def streamlit_list_apps(ctx: Context = None) -> str:
    """List all available Streamlit apps"""
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.list_apps()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


async def streamlit_get_app_url(app_id: str, ctx: Context = None) -> str:
    """Get the URL for a running Streamlit app

    Parameters:
    - app_id: Identifier of the app
    """
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.get_app_url(app_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


async def streamlit_modify_app(app_id: str, code_updates: List[tuple] = None, append_code: str = None, ctx: Context = None) -> str:
    """Modify an existing Streamlit app

    Parameters:
    - app_id: Identifier of the app to modify
    - code_updates: List of tuples (old_text, new_text) for text replacements
    - append_code: Code to append to the end of the app
    """
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.modify_app(app_id, code_updates, append_code)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)


async def streamlit_check_deps(ctx: Context = None) -> str:
    """Check if Streamlit and required dependencies are installed"""
    streamlit = _get_streamlit_service()

    try:
        result = await streamlit.check_dependencies()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)

# Tool registration and initialization
_streamlit_service = None


def initialize_streamlit_service(apps_dir=None, port_range=(8501, 8599)):
    """Initialize the Streamlit service"""
    global _streamlit_service

    # Check if streamlit is installed
    try:
        import streamlit
        streamlit_version = streamlit.__version__
        logging.info(f"Found Streamlit version {streamlit_version}")
    except ImportError:
        logging.error(
            "Streamlit is not installed. Please install it with 'pip install streamlit'")
        return None

    # Rest of initialization code...

    # Use environment variables as fallback
    if apps_dir is None:
        apps_dir = os.environ.get("STREAMLIT_APPS_DIR")

    if apps_dir is None:
        apps_dir = os.path.expanduser("~/streamlit_apps")

    _streamlit_service = StreamlitService(apps_dir, port_range)
    return _streamlit_service


def _get_streamlit_service():
    """Get or initialize the Streamlit service"""
    global _streamlit_service
    if _streamlit_service is None:
        _streamlit_service = initialize_streamlit_service()
    return _streamlit_service


def get_streamlit_tools():
    """Get a dictionary of all Streamlit tools for registration with MCP"""
    return {
        StreamlitTools.CREATE_APP: streamlit_create_app,
        StreamlitTools.RUN_APP: streamlit_run_app,
        StreamlitTools.STOP_APP: streamlit_stop_app,
        StreamlitTools.LIST_APPS: streamlit_list_apps,
        StreamlitTools.GET_APP_URL: streamlit_get_app_url,
        StreamlitTools.MODIFY_APP: streamlit_modify_app,
        StreamlitTools.CHECK_DEPS: streamlit_check_deps
    }

# This function will be called by the unified server to initialize the module


def initialize(mcp=None):
    """Initialize the Streamlit module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_streamlit_service()
    if service:
        logging.info("Streamlit service initialized successfully")
    else:
        logging.warning("Failed to initialize Streamlit service")

    return service is not None


if __name__ == "__main__":
    print("Streamlit service module - use with MCP Unified Server")
