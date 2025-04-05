#!/usr/bin/env python3
"""
Enhanced Streamlit service implementation for creating and managing Streamlit applications.
"""
import os
import sys
import logging
import subprocess
import signal
import time
import re
import threading
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from app.tools.base.service import ToolServiceBase


class StreamlitService(ToolServiceBase):
    """Service to manage Streamlit applications"""

    def __init__(self):
        """Initialize the Streamlit service"""
        super().__init__()
        self.apps_dir = None
        self.port_range = (8501, 8599)
        self.running_apps = {}  # app_id -> {process, port, url, log_path, log_file}

        # Add lock for thread safety
        self.lock = threading.Lock()

        # Keep track of used ports
        self.used_ports = set()

    def initialize(self) -> Tuple[bool, str]:
        """
        Initialize the Streamlit service with required libraries.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Get apps directory from environment or use default
            self.apps_dir = self.get_env_var(
                "STREAMLIT_APPS_DIR",
                default=os.path.expanduser("~/streamlit_apps")
            )

            # Create apps directory if it doesn't exist
            os.makedirs(self.apps_dir, exist_ok=True)

            # Check if streamlit is installed
            try:
                # Run streamlit version command
                process = subprocess.run(
                    [sys.executable, "-m", "streamlit", "--version"],
                    capture_output=True,
                    text=True,
                    check=False
                )

                if process.returncode != 0:
                    error_msg = "Streamlit is not installed correctly. Please install with 'pip install streamlit'"
                    self.logger.error(error_msg)
                    return False, error_msg

                streamlit_version = process.stdout.strip()
                self.logger.info(
                    f"Found Streamlit version {streamlit_version}")

                # Check if psutil is available
                if not PSUTIL_AVAILABLE:
                    self.logger.warning(
                        "psutil module not installed. Process management may be limited. Install with 'pip install psutil'")

                self.logger.info(
                    f"Initialized Streamlit service at {self.apps_dir}")
                self.initialized = True
                return True, f"Streamlit service initialized successfully at {self.apps_dir}"

            except Exception as e:
                error_msg = f"Error checking Streamlit installation: {e}"
                self.logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            self.logger.error(f"Failed to initialize Streamlit service: {e}")
            return False, f"Failed to initialize Streamlit service: {str(e)}"

    def _find_available_port(self) -> int:
        """
        Find an available port for a Streamlit app.

        Returns:
            int: Available port number

        Raises:
            ValueError: If no ports are available
        """
        with self.lock:
            for port in range(self.port_range[0], self.port_range[1] + 1):
                if port not in self.used_ports:
                    # Check if port is really free (in case an external process is using it)
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', port))
                    sock.close()
                    if result != 0:  # Port is available
                        self.used_ports.add(port)
                        return port

            raise ValueError(f"No available ports in range {self.port_range}")

    def _release_port(self, port: int) -> None:
        """
        Release a port when an app is stopped.

        Args:
            port: Port number to release
        """
        with self.lock:
            if port in self.used_ports:
                self.used_ports.remove(port)

    def validate_app_id(self, app_id: str) -> str:
        """
        Validate that an app ID is safe and suitable for a filename.

        Args:
            app_id: App ID to validate

        Returns:
            Validated app ID

        Raises:
            ValueError: If app ID contains invalid characters
        """
        if not re.match(r'^[a-zA-Z0-9_-]+$', app_id):
            raise ValueError(
                "App ID must contain only letters, numbers, underscores, and hyphens")
        return app_id

    def get_app_path(self, app_id: str) -> str:
        """
        Get the file path for a Streamlit app.

        Args:
            app_id: App ID

        Returns:
            Path to the app file
        """
        safe_app_id = self.validate_app_id(app_id)
        return os.path.join(self.apps_dir, f"{safe_app_id}.py")

    async def create_app(self, app_id: str, code: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a new Streamlit app with the given code.

        Args:
            app_id: Unique identifier for the app
            code: Python code for the Streamlit app
            overwrite: Whether to overwrite an existing app with the same ID

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If app already exists and overwrite is False
        """
        self._is_initialized()

        safe_app_id = self.validate_app_id(app_id)
        app_path = self.get_app_path(safe_app_id)

        # Check if app already exists
        if os.path.exists(app_path) and not overwrite:
            raise ValueError(
                f"App {app_id} already exists. Use overwrite=True to replace it.")

        # Write the app code to the file
        with open(app_path, 'w') as f:
            f.write(code)

        self.logger.info(f"Created Streamlit app '{app_id}' at {app_path}")

        return {
            "app_id": safe_app_id,
            "path": app_path,
            "status": "created"
        }

    async def run_app(self, app_id: str, port: Optional[int] = None, browser: bool = False) -> Dict[str, Any]:
        """
        Run a Streamlit app as a background process.

        Args:
            app_id: Identifier of the app to run
            port: Optional port number (if not specified, an available port will be used)
            browser: Whether to open the app in a browser window

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If app does not exist
        """
        self._is_initialized()

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

            self.logger.info(
                f"Started Streamlit app '{app_id}' on port {port}")

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

    async def stop_app(self, app_id: str) -> Dict[str, Any]:
        """
        Stop a running Streamlit app.

        Args:
            app_id: Identifier of the app to stop

        Returns:
            Dictionary with operation result
        """
        self._is_initialized()

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
            if PSUTIL_AVAILABLE:
                # Use psutil for better process management
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            else:
                # Fallback to basic process termination
                process.terminate()

            # Wait for termination (with timeout)
            process.wait(timeout=10)

            # Close the log file
            if not log_file.closed:
                log_file.close()

            # Release the port
            self._release_port(port)

            # Remove from running apps
            del self.running_apps[safe_app_id]

            self.logger.info(f"Stopped Streamlit app '{app_id}'")

            return {
                "app_id": safe_app_id,
                "status": "stopped"
            }

        except Exception as e:
            self.logger.error(
                f"Error stopping Streamlit app '{app_id}': {str(e)}")

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

    async def list_apps(self) -> Dict[str, Any]:
        """
        List all available Streamlit apps.

        Returns:
            Dictionary with app information
        """
        self._is_initialized()

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

    async def get_app_url(self, app_id: str) -> Dict[str, Any]:
        """
        Get the URL for a running Streamlit app.

        Args:
            app_id: Identifier of the app

        Returns:
            Dictionary with URL information
        """
        self._is_initialized()

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

    async def modify_app(self, app_id: str, code_updates: Optional[List[Tuple[str, str]]] = None,
                         append_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Modify an existing Streamlit app.

        Args:
            app_id: Identifier of the app to modify
            code_updates: List of tuples (old_text, new_text) for text replacements
            append_code: Code to append to the end of the app

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If app does not exist
        """
        self._is_initialized()

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

        self.logger.info(f"Modified Streamlit app '{app_id}'")

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

    async def check_dependencies(self) -> Dict[str, Any]:
        """
        Check if Streamlit and required dependencies are installed.

        Returns:
            Dictionary with dependency information
        """
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
