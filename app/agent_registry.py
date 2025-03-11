# agent_registry.py
import os
import importlib
import inspect
import logging
from typing import Dict, Any, Callable, List, Type

logger = logging.getLogger("agent_registry")

# Dictionary to store registered agents
registered_agents = {}


class MCPAgent:
    """Base class for all MCP agents"""

    # Class variables for agent metadata
    agent_name = None
    agent_description = None
    agent_version = "1.0"
    agent_author = None

    def __init__(self, toolkit):
        self.toolkit = toolkit

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Return agent metadata"""
        return {
            "name": cls.agent_name,
            "description": cls.agent_description,
            "version": cls.agent_version,
            "author": cls.agent_author
        }

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with the provided parameters
        Must be implemented by subclasses
        """
        raise NotImplementedError("Agents must implement the run method")


def register_agent(agent_class: Type[MCPAgent]):
    """Decorator to register an agent class"""
    if not issubclass(agent_class, MCPAgent):
        raise TypeError(
            f"{agent_class.__name__} must be a subclass of MCPAgent")

    if not agent_class.agent_name:
        agent_class.agent_name = agent_class.__name__

    registered_agents[agent_class.agent_name] = agent_class
    logger.info(f"Registered agent: {agent_class.agent_name}")
    return agent_class


def load_agents_from_directory(directory: str) -> List[str]:
    """
    Load all agent modules from a directory
    Returns list of loaded agent names
    """
    loaded_agents = []

    # Ensure the directory exists
    if not os.path.exists(directory):
        logger.warning(f"Agent directory not found: {directory}")
        return loaded_agents

    # Find all Python files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]  # Remove .py extension

            try:
                # Import the module
                module_path = f"{os.path.basename(directory)}.{module_name}"
                module = importlib.import_module(module_path)

                # Find agent classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, MCPAgent) and
                            obj != MCPAgent):

                        # Register the agent if it has a name
                        if obj.agent_name:
                            registered_agents[obj.agent_name] = obj
                            loaded_agents.append(obj.agent_name)
                            logger.info(
                                f"Loaded agent '{obj.agent_name}' from {filename}")

            except Exception as e:
                logger.error(
                    f"Error loading agent module {module_name}: {str(e)}")

    return loaded_agents


def get_registered_agents() -> Dict[str, Type[MCPAgent]]:
    """Get dictionary of all registered agents"""
    return registered_agents


def get_agent_instance(agent_name: str, toolkit) -> MCPAgent:
    """Get an instance of a registered agent"""
    if agent_name not in registered_agents:
        raise ValueError(f"Agent '{agent_name}' not found in registry")

    agent_class = registered_agents[agent_name]
    return agent_class(toolkit)
