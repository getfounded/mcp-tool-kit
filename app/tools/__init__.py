#!/usr/bin/env python3
"""
Enhanced tool discovery and initialization for the MCP Toolkit.
"""
import importlib
import importlib.util
import os
import sys
import inspect
import logging
import pkgutil
from typing import Dict, Any, List, Optional, Set, Type, Union

from app.tools.base.registry import get_all_tools, get_or_create_service

logger = logging.getLogger(__name__)


def discover_tool_modules() -> List[str]:
    """
    Discover all potential tool modules with improved recursive discovery.

    Returns:
        List of module names that could contain tools
    """
    tools_dir = os.path.dirname(__file__)

    # Find all potential module directories or files
    modules = []

    def _scan_directory(directory: str, package_prefix: str = "") -> None:
        """Recursively scan directory for tool modules."""
        for entry in os.listdir(directory):
            # Skip hidden files, __pycache__, and base directory if top-level
            if entry.startswith('_') or entry.startswith('.'):
                continue

            if package_prefix == "" and entry == 'base':
                continue

            entry_path = os.path.join(directory, entry)

            # Include Python files
            if entry.endswith('.py'):
                module_name = f"{package_prefix}{entry[:-3]}"
                modules.append(module_name)

            # Include directories with __init__.py (subpackages)
            elif os.path.isdir(entry_path) and os.path.exists(os.path.join(entry_path, '__init__.py')):
                subpackage = f"{package_prefix}{entry}"
                modules.append(subpackage)

                # Recursively scan subpackage
                _scan_directory(entry_path, f"{subpackage}.")

    # Start scanning from the tools directory
    _scan_directory(tools_dir)

    logger.debug(f"Discovered potential tool modules: {modules}")
    return modules


def import_tool_module(module_name: str) -> Optional[Any]:
    """
    Import a module by name with enhanced error handling.

    Args:
        module_name: Name of the module to import

    Returns:
        The imported module or None if import failed
    """
    full_module_name = f'app.tools.{module_name}'

    try:
        module = importlib.import_module(full_module_name)
        logger.info(f"Imported tool module: {module_name}")
        return module
    except ImportError as e:
        logger.error(f"Failed to import tool module {module_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in tool module {module_name}: {e}", exc_info=True)
        return None


def discover_tools() -> Dict[str, Dict[str, Any]]:
    """
    Discover and import all tool modules.

    Returns:
        Dictionary of all registered tools
    """
    modules = discover_tool_modules()

    # Import each module to trigger registration
    imported_modules = []
    for module_name in modules:
        module = import_tool_module(module_name)
        if module:
            imported_modules.append(module)

    tools = get_all_tools()
    logger.info(
        f"Discovered {len(tools)} tools across {len(imported_modules)} modules")
    return tools


def find_subclass_in_module(module: Any, parent_class: Type) -> List[Type]:
    """
    Find all subclasses of a parent class in a module.

    Args:
        module: The module to search
        parent_class: The parent class to look for subclasses of

    Returns:
        List of subclass types found in the module
    """
    subclasses = []

    for name, obj in inspect.getmembers(module):
        # Skip if not a class or is the parent class itself
        if not inspect.isclass(obj) or obj is parent_class:
            continue

        # Check if it's a subclass of the parent
        if inspect.isclass(obj) and issubclass(obj, parent_class):
            subclasses.append(obj)

    return subclasses


def initialize_services(service_class: Type) -> None:
    """
    Initialize all services of a given type.

    Args:
        service_class: Base service class to find and initialize subclasses of
    """
    services_initialized = 0

    # Discover all modules
    modules = discover_tool_modules()

    # Import modules and look for service classes
    for module_name in modules:
        module = import_tool_module(module_name)
        if not module:
            continue

        # Find service classes in this module
        service_classes = find_subclass_in_module(module, service_class)

        # Initialize each service
        for cls in service_classes:
            # Skip abstract classes
            if inspect.isabstract(cls):
                continue

            # Initialize service
            try:
                get_or_create_service(cls)
                services_initialized += 1
            except Exception as e:
                logger.error(
                    f"Failed to initialize service {cls.__name__}: {e}")

    logger.info(
        f"Initialized {services_initialized} services of type {service_class.__name__}")


# Auto-discover on import
tools = discover_tools()
