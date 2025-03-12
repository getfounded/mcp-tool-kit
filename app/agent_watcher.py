# agent_watcher.py
import os
import time
import logging
import importlib.util
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.agent_registry import MCPAgent, registered_agents

logger = logging.getLogger("agent_watcher")


class AgentFileHandler(FileSystemEventHandler):
    """Handler that automatically loads agent files when they're added or modified"""

    def on_created(self, event):
        """Called when a file is created in the watched directory"""
        if event.is_directory or not event.src_path.endswith('.py'):
            return
        self._process_agent_file(event.src_path)

    def on_modified(self, event):
        """Called when a file is modified in the watched directory"""
        if event.is_directory or not event.src_path.endswith('.py'):
            return
        self._process_agent_file(event.src_path)

    def _process_agent_file(self, file_path):
        """Process an agent file and load any agent classes"""
        try:
            filename = os.path.basename(file_path)
            module_name = filename[:-3]  # Remove .py extension

            logger.info(f"Processing agent file: {filename}")

            # Check if the module is already loaded
            if module_name in sys.modules:
                # Reload the module
                module = importlib.reload(sys.modules[module_name])
                logger.info(f"Reloaded agent module: {module_name}")
            else:
                # Import the module
                spec = importlib.util.spec_from_file_location(
                    module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                logger.info(f"Loaded new agent module: {module_name}")

            # Find agent classes in the module
            agent_count = 0
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and
                    issubclass(obj, MCPAgent) and
                    obj != MCPAgent and
                        obj.agent_name):

                    registered_agents[obj.agent_name] = obj
                    agent_count += 1
                    logger.info(
                        f"Registered agent '{obj.agent_name}' from {filename}")

            if agent_count == 0:
                logger.warning(f"No valid agent classes found in {filename}")
            else:
                logger.info(
                    f"Successfully loaded {agent_count} agents from {filename}")

        except Exception as e:
            logger.error(f"Error processing agent file {file_path}: {str(e)}")


def start_agent_watcher(agents_dir="agents"):
    """Start watching the agents directory for changes"""
    # Create the directory if it doesn't exist
    os.makedirs(agents_dir, exist_ok=True)

    # Set up the file watcher
    event_handler = AgentFileHandler()
    observer = Observer()
    observer.schedule(event_handler, agents_dir, recursive=False)
    observer.start()

    logger.info(
        f"Started agent directory watcher for {os.path.abspath(agents_dir)}")

    # Load existing agent files
    for filename in os.listdir(agents_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            event_handler._process_agent_file(
                os.path.join(agents_dir, filename))

    return observer
