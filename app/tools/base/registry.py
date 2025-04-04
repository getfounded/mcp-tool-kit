#!/usr/bin/env python3
"""
Enhanced registry system for MCP tools.
"""
import inspect
import logging
import functools
from typing import Dict, Any, Callable, List, Type, Optional, Union, Set

logger = logging.getLogger(__name__)

# Global registry for tools
_TOOLS_REGISTRY = {}
# Registry of services by type
_SERVICES_REGISTRY = {}

def register_tool(name: Optional[str] = None, category: Optional[str] = None, 
                  service_class: Optional[Type] = None, description: Optional[str] = None):
    """
    Decorator to register a function as a tool.
    
    Args:
        name: Optional override for the tool name (defaults to function name)
        category: Optional category for grouping tools
        service_class: Optional service class this tool depends on
        description: Optional short description for the tool
        
    Returns:
        The decorated function
    """
    def decorator(func):
        func_name = name or func.__name__
        
        # Extract parameter info from signature
        sig = inspect.signature(func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            # Skip 'self' or internal parameters
            if param_name in ('self', 'cls', 'ctx'):
                continue
                
            param_info = {
                'name': param_name,
                'required': param.default is param.empty,
                'type': str(param.annotation) if param.annotation is not param.empty else None,
                'default': None if param.default is param.empty else param.default
            }
            parameters[param_name] = param_info
        
        # Register the tool with enhanced metadata
        _TOOLS_REGISTRY[func_name] = {
            'function': func,
            'category': category,
            'service_class': service_class,
            'name': func_name,
            'description': description or '',
            'doc': func.__doc__,
            'signature': sig,
            'parameters': parameters
        }
        
        # Apply service dependency handling
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize service if needed
            if service_class:
                service = get_or_create_service(service_class)
                # If first arg is not service and func expects self, inject service
                if args and not isinstance(args[0], service_class) and 'self' in sig.parameters:
                    return func(service, *args, **kwargs)
            return func(*args, **kwargs)
            
        logger.debug(f"Registered tool: {func_name} (category: {category})")
        return wrapper
    return decorator

def get_or_create_service(service_class: Type) -> Any:
    """
    Get an existing service instance or create a new one.
    
    Args:
        service_class: The service class to instantiate
        
    Returns:
        Instance of the service class
    """
    if service_class not in _SERVICES_REGISTRY:
        logger.debug(f"Creating new service instance for {service_class.__name__}")
        service = service_class()
        if hasattr(service, 'initialize'):
            service.initialize()
        _SERVICES_REGISTRY[service_class] = service
    
    return _SERVICES_REGISTRY[service_class]

def get_service(service_class: Type) -> Optional[Any]:
    """
    Get an existing service instance if it exists.
    
    Args:
        service_class: The service class to get
        
    Returns:
        Instance of the service class or None if not registered
    """
    return _SERVICES_REGISTRY.get(service_class)

def get_all_tools() -> Dict[str, Dict[str, Any]]:
    """Get all registered tools"""
    return _TOOLS_REGISTRY

def get_tools_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all tools in a specific category"""
    return {name: info for name, info in _TOOLS_REGISTRY.items() 
            if info.get('category') == category}

def get_tool_categories() -> List[str]:
    """Get all unique tool categories"""
    categories = set()
    for tool_info in _TOOLS_REGISTRY.values():
        if 'category' in tool_info and tool_info['category']:
            categories.add(tool_info['category'])
    return sorted(list(categories))

def get_tools_by_service(service_class: Type) -> Dict[str, Dict[str, Any]]:
    """Get all tools that depend on a specific service"""
    return {name: info for name, info in _TOOLS_REGISTRY.items() 
            if info.get('service_class') == service_class}

def clear_registry() -> None:
    """Clear the tool registry (mainly for testing)"""
    _TOOLS_REGISTRY.clear()
    _SERVICES_REGISTRY.clear()
