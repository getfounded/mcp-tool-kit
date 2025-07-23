"""Dynamic tool registration system for MCP tools."""
import os
import sys
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Type, Optional
import logging
from app.tools.base_tool import BaseTool
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for dynamically loading and managing MCP tools."""
    
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.tools: Dict[str, BaseTool] = {}
        self.failed_tools: Dict[str, str] = {}
        
    def discover_tools(self, tools_dir: Path) -> List[str]:
        """Discover all tool modules in the specified directory.
        
        Returns a list of module names that potentially contain tools.
        """
        tool_modules = []
        
        for file in tools_dir.glob("*.py"):
            if file.name.startswith("_") or file.name in ["base_tool.py", "tool_registry.py"]:
                continue
                
            module_name = file.stem
            tool_modules.append(module_name)
            
        return tool_modules
        
    def load_tool_module(self, module_name: str) -> Optional[Type[BaseTool]]:
        """Load a tool module and return its tool class if it exists.
        
        Returns None if the module doesn't contain a valid tool class.
        """
        try:
            # Import the module
            module = importlib.import_module(f"app.tools.{module_name}")
            
            # Find classes that inherit from BaseTool
            tool_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseTool) and 
                    obj is not BaseTool):
                    tool_classes.append(obj)
                    
            if len(tool_classes) == 1:
                return tool_classes[0]
            elif len(tool_classes) > 1:
                # If multiple tool classes, try to find one that matches the module name
                for cls in tool_classes:
                    if cls.__name__.lower() == module_name.replace("_", "").lower():
                        return cls
                # Otherwise return the first one
                return tool_classes[0]
            else:
                # Try legacy format - look for specific functions
                if hasattr(module, 'set_external_mcp') and hasattr(module, 'initialize'):
                    return self._create_legacy_wrapper(module_name, module)
                    
            return None
            
        except Exception as e:
            logger.error(f"Failed to load tool module {module_name}: {str(e)}")
            self.failed_tools[module_name] = str(e)
            return None
            
    def _create_legacy_wrapper(self, module_name: str, module) -> Type[BaseTool]:
        """Create a wrapper for legacy tool modules that don't inherit from BaseTool."""
        
        class LegacyToolWrapper(BaseTool):
            def __init__(self):
                super().__init__()
                self.module = module
                self.module_name = module_name
                
            def get_name(self) -> str:
                return self.module_name.replace("_", " ").title()
                
            def get_description(self) -> str:
                return f"Legacy tool: {self.module_name}"
                
            def get_tools(self) -> Dict[str, callable]:
                # Try different function name patterns
                for func_name in [f'get_{self.module_name}_tools', 
                                 f'get_{self.module_name.replace("_", "")}_tools',
                                 'get_tools']:
                    if hasattr(self.module, func_name):
                        return getattr(self.module, func_name)()
                return {}
                
            def get_dependencies(self) -> List[str]:
                # Try to extract dependencies from module
                if hasattr(self.module, 'DEPENDENCIES'):
                    return self.module.DEPENDENCIES
                return []
                
            def initialize(self, **kwargs) -> None:
                # Set the external MCP if the module supports it
                if hasattr(self.module, 'set_external_mcp'):
                    self.module.set_external_mcp(self.mcp)
                    
                # Call initialize if it exists
                if hasattr(self.module, 'initialize'):
                    # Handle different initialize signatures
                    init_func = self.module.initialize
                    sig = inspect.signature(init_func)
                    if len(sig.parameters) == 0:
                        init_func()
                    elif 'mcp' in sig.parameters:
                        init_func(self.mcp)
                    else:
                        # Try to pass relevant kwargs
                        init_func(**{k: v for k, v in kwargs.items() 
                                   if k in sig.parameters})
                                   
                super().initialize(**kwargs)
                
            def validate_environment(self) -> bool:
                # Check for common environment variables based on module name
                env_var_patterns = [
                    f"{self.module_name.upper()}_API_KEY",
                    f"{self.module_name.upper()}_KEY",
                    f"MCP_{self.module_name.upper()}_KEY"
                ]
                
                # Special cases
                if self.module_name == "news_api":
                    return bool(os.environ.get("NEWS_API_KEY"))
                elif self.module_name == "fred":
                    return bool(os.environ.get("FRED_API_KEY"))
                elif self.module_name == "worldbank":
                    return True  # World Bank API doesn't require key
                    
                # For other tools, assume they're valid unless they have obvious API key requirements
                return True
                
        return LegacyToolWrapper
        
    def register_tool(self, tool_class: Type[BaseTool], **init_kwargs) -> bool:
        """Register a tool with the MCP server.
        
        Returns True if successful, False otherwise.
        """
        try:
            # Instantiate the tool
            tool = tool_class()
            tool.set_mcp(self.mcp)
            
            # Validate environment
            if not tool.validate_environment():
                logger.warning(f"Tool {tool.get_name()} failed environment validation")
                self.failed_tools[tool.get_name()] = "Failed environment validation"
                return False
                
            # Initialize the tool
            tool.initialize(**init_kwargs)
            
            # Get and register tool functions
            tool_functions = tool.get_tools()
            for tool_name, tool_func in tool_functions.items():
                self.mcp.tool(name=tool_name)(tool_func)
                
            # Add dependencies
            dependencies = tool.get_dependencies()
            if dependencies:
                self.mcp.dependencies.extend(dependencies)
                
            # Store the tool instance
            self.tools[tool.get_name()] = tool
            
            logger.info(f"Successfully registered tool: {tool.get_name()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool_class.__name__}: {str(e)}")
            self.failed_tools[tool_class.__name__] = str(e)
            return False
            
    def register_all_tools(self, tools_dir: Path, config: Optional[Dict] = None, **init_kwargs) -> Dict[str, bool]:
        """Discover and register all tools in the specified directory.
        
        Returns a dictionary mapping tool names to registration success status.
        """
        results = {}
        
        # Import config functions if config is provided
        if config:
            from config_loader import is_tool_enabled, get_tool_config
        
        # Discover tool modules
        tool_modules = self.discover_tools(tools_dir)
        logger.info(f"Discovered {len(tool_modules)} potential tool modules")
        
        # Load and register each tool
        for module_name in tool_modules:
            # Check if tool is enabled in config
            if config and not is_tool_enabled(config, module_name):
                logger.info(f"Tool {module_name} is disabled in configuration")
                results[module_name] = False
                continue
                
            tool_class = self.load_tool_module(module_name)
            if tool_class:
                # Get tool-specific config
                tool_config = get_tool_config(config, module_name) if config else {}
                merged_kwargs = {**init_kwargs, **tool_config}
                
                success = self.register_tool(tool_class, **merged_kwargs)
                results[module_name] = success
            else:
                results[module_name] = False
                
        return results
        
    def get_status(self) -> Dict[str, any]:
        """Get the status of all registered and failed tools."""
        return {
            "registered": list(self.tools.keys()),
            "failed": self.failed_tools,
            "total_tools": sum(len(tool.get_tools()) for tool in self.tools.values()),
            "total_dependencies": len(set(self.mcp.dependencies))
        }
        
    def cleanup(self) -> None:
        """Cleanup all registered tools."""
        for tool in self.tools.values():
            try:
                tool.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up tool {tool.get_name()}: {str(e)}")