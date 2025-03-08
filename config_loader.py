#!/usr/bin/env python3
import os
import yaml
from pathlib import Path
import logging

def load_config(config_path=None):
    """Load configuration from YAML file"""
    if not config_path:
        # Default config path is config.yaml in the same directory as this file
        config_path = Path(__file__).parent / "config.yaml"
    
    if not os.path.exists(config_path):
        logging.warning(f"Configuration file not found at {config_path}, using default settings")
        return {"enabled_tools": {}, "tool_config": {}}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logging.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        return {"enabled_tools": {}, "tool_config": {}}

def is_tool_enabled(config, tool_name):
    """Check if a tool is enabled in configuration"""
    if not config:
        return False
    
    # If no tools are specifically enabled or disabled, assume all are enabled
    if "enabled_tools" not in config or not config["enabled_tools"]:
        return True
        
    return config.get("enabled_tools", {}).get(tool_name, False)

def get_tool_config(config, tool_name):
    """Get configuration for a specific tool"""
    if not config:
        return {}
        
    return config.get("tool_config", {}).get(tool_name, {})

# Get all enabled tool names
def get_enabled_tools(config):
    """Get a list of all enabled tool names"""
    if not config or "enabled_tools" not in config:
        return []
        
    return [tool for tool, enabled in config.get("enabled_tools", {}).items() if enabled]

# Example config.yaml file structure
DEFAULT_CONFIG = {
    "enabled_tools": {
        "filesystem": True,
        "time_tools": True,
        "sequential_thinking": True,
        "brave_search": True,
        "browserbase": True,
        "worldbank": True,
        "news_api": True,
        "ppt": True,
        "data_analysis": True,
        "document_management": True,
        "yfinance": True,
        "shopify": False,
        "linkedin": False,
        "salesforce": False,
        "outlook": False
    },
    "tool_config": {
        "brave_search": {
            "rate_limit": 100,
            "max_results": 10,
            "api_key": "" # Override with env var if present
        },
        "filesystem": {
            "allowed_directories": ["~/documents", "~/downloads"],
            "allow_file_deletion": False
        }
    }
}

# Create default config file if it doesn't exist
def create_default_config(config_path=None):
    """Create a default configuration file if it doesn't exist"""
    if not config_path:
        config_path = Path(__file__).parent / "config.yaml"
    
    if not os.path.exists(config_path):
        try:
            with open(config_path, 'w') as f:
                yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
            logging.info(f"Created default configuration at {config_path}")
            return True
        except Exception as e:
            logging.error(f"Error creating default configuration: {str(e)}")
            return False
    
    return False
