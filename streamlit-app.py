import streamlit as st
import yaml
import os
import sys
from pathlib import Path
import subprocess
import json

# Add the parent directory to the path to allow importing from the main project
sys.path.append(str(Path(__file__).parent.parent))

# Set page config
st.set_page_config(
    page_title="MCP Tools Configuration",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load configuration
def load_config(config_path):
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        # Create default config if it doesn't exist
        default_config = {
            "enabled_tools": {},
            "tool_config": {}
        }
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        return default_config
    
    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except Exception as e:
            st.error(f"Error loading configuration: {str(e)}")
            return {"enabled_tools": {}, "tool_config": {}}

# Function to save configuration
def save_config(config, config_path):
    """Save configuration to YAML file"""
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")
        return False

# Function to discover available tools
def discover_tools(tools_path):
    """Scan the tools directory to find available tool modules"""
    available_tools = []
    
    if not os.path.exists(tools_path):
        return available_tools
    
    for item in os.listdir(tools_path):
        if item.endswith('.py') and not item.startswith('__'):
            tool_name = item[:-3]  # Remove .py extension
            available_tools.append(tool_name)
    
    return sorted(available_tools)

# Function to get tool description
def get_tool_description(tool_name, tools_path):
    """Extract a description from the tool module if available"""
    try:
        # Try to read the first few lines of the module to look for docstring or comments
        tool_path = os.path.join(tools_path, f"{tool_name}.py")
        with open(tool_path, 'r') as f:
            content = f.read(2000)  # Read first 2000 characters
        
        # Look for docstring
        import re
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring_match:
            description = docstring_match.group(1).strip()
            # Return first sentence or first 100 chars
            first_sentence = re.match(r'^(.*?[.!?])\s', description)
            if first_sentence:
                return first_sentence.group(1)
            return description[:100] + "..." if len(description) > 100 else description
        
        # Look for file header comment
        comment_match = re.search(r'# (.*?)\n', content)
        if comment_match:
            return comment_match.group(1).strip()
        
        return "No description available"
    except Exception:
        return "No description available"

# Function to restart the MCP server
def restart_server(server_path):
    """Restart the MCP server process"""
    try:
        # Check if server is running
        # This is a simplified check - in production you might want to use a more robust method
        result = subprocess.run(
            ["pgrep", "-f", server_path], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            # Server is running, kill it
            pid = result.stdout.strip()
            subprocess.run(["kill", pid])
            st.success(f"Stopped MCP server (PID: {pid})")
        
        # Start server
        subprocess.Popen(["python", server_path])
        return True
    except Exception as e:
        st.error(f"Error restarting server: {str(e)}")
        return False

# Function to check if server is running
def is_server_running(server_path):
    """Check if the MCP server is currently running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", server_path], 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

# Main application
def main():
    st.title("MCP Tools Configuration")
    
    # Sidebar for server control and config location
    with st.sidebar:
        st.header("Server Control")
        
        # Get paths
        project_root = st.text_input(
            "Project Directory", 
            value=str(Path(__file__).parent.parent),
            help="The root directory of the MCP Unified Server project"
        )
        
        tools_path = os.path.join(project_root, "tools")
        server_path = os.path.join(project_root, "mcp_unified_server.py")
        config_path = os.path.join(project_root, "config.yaml")
        
        # Check if server is running
        server_status = is_server_running(server_path)
        st.subheader("Server Status")
        if server_status:
            st.success("MCP Server is running")
        else:
            st.warning("MCP Server is not running")
        
        if st.button("Start/Restart Server"):
            with st.spinner("Restarting MCP Server..."):
                success = restart_server(server_path)
                if success:
                    st.success("Server restarted successfully")
        
        # Show server path
        st.caption(f"Server path: {server_path}")
        
        # Divider
        st.divider()
        
        # Load and save config
        if st.button("Reload Configuration"):
            st.session_state.config = load_config(config_path)
            st.success("Configuration reloaded")
        
        save_button = st.button("Save Configuration")
    
    # Initialize or get session state for config
    if "config" not in st.session_state:
        st.session_state.config = load_config(config_path)
    
    # Discover available tools
    available_tools = discover_tools(tools_path)
    
    # If no tools are in the config yet, add all available ones with default state
    if "enabled_tools" not in st.session_state.config:
        st.session_state.config["enabled_tools"] = {}
    
    for tool in available_tools:
        if tool not in st.session_state.config["enabled_tools"]:
            st.session_state.config["enabled_tools"][tool] = False
    
    # Initialize tool_config if not present
    if "tool_config" not in st.session_state.config:
        st.session_state.config["tool_config"] = {}
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["Enable/Disable Tools", "Tool Configuration", "Advanced Settings"])
    
    with tab1:
        st.header("Tool Management")
        st.info("Toggle tools on or off. Changes will take effect after saving and restarting the server.")
        
        # Create a container for the tools list
        tools_container = st.container()
        
        # Add tool toggle controls
        with tools_container:
            # Create columns for better layout
            cols = st.columns(2)
            
            # Sort tools by name
            sorted_tools = sorted(available_tools)
            
            # Distribute tools into columns
            half_length = (len(sorted_tools) + 1) // 2
            
            for i, tool in enumerate(sorted_tools):
                col_idx = 0 if i < half_length else 1
                with cols[col_idx]:
                    tool_enabled = st.checkbox(
                        f"{tool}",
                        value=st.session_state.config["enabled_tools"].get(tool, False),
                        help=get_tool_description(tool, tools_path),
                        key=f"tool_{tool}"
                    )
                    st.session_state.config["enabled_tools"][tool] = tool_enabled
    
    with tab2:
        st.header("Tool Configuration")
        st.info("Configure specific settings for each tool.")
        
        # Get list of enabled tools
        enabled_tools = [tool for tool, enabled in st.session_state.config["enabled_tools"].items() if enabled]
        
        # Tool selection
        selected_tool = st.selectbox(
            "Select a tool to configure",
            options=[""] + enabled_tools,
            format_func=lambda x: x if x else "Select a tool..."
        )
        
        if selected_tool:
            st.subheader(f"Configuration for {selected_tool}")
            
            # Initialize config for this tool if it doesn't exist
            if selected_tool not in st.session_state.config["tool_config"]:
                st.session_state.config["tool_config"][selected_tool] = {}
            
            tool_config = st.session_state.config["tool_config"][selected_tool]
            
            # Special handling for common tools
            if selected_tool == "filesystem":
                # Filesystem-specific config
                allowed_dirs = tool_config.get("allowed_directories", [])
                allowed_dirs_str = "\n".join(allowed_dirs) if allowed_dirs else ""
                
                new_allowed_dirs = st.text_area(
                    "Allowed Directories (one per line)",
                    value=allowed_dirs_str,
                    help="List of directories that the file system tools can access"
                )
                
                # Update config
                tool_config["allowed_directories"] = [d.strip() for d in new_allowed_dirs.split("\n") if d.strip()]
                
                # Allow file deletion option
                allow_deletion = st.checkbox(
                    "Allow File Deletion",
                    value=tool_config.get("allow_file_deletion", False),
                    help="Whether file deletion operations are allowed"
                )
                tool_config["allow_file_deletion"] = allow_deletion
                
            elif selected_tool == "brave_search":
                # Brave Search specific config
                rate_limit = st.number_input(
                    "Rate Limit (requests per minute)",
                    min_value=1,
                    max_value=1000,
                    value=tool_config.get("rate_limit", 100),
                    help="Maximum number of API requests per minute"
                )
                tool_config["rate_limit"] = rate_limit
                
                max_results = st.number_input(
                    "Maximum Results per Request",
                    min_value=1,
                    max_value=100,
                    value=tool_config.get("max_results", 10),
                    help="Maximum number of results to return per API request"
                )
                tool_config["max_results"] = max_results
                
                api_key = st.text_input(
                    "Brave API Key",
                    value=tool_config.get("api_key", ""),
                    type="password",
                    help="Your Brave Search API key"
                )
                if api_key:
                    tool_config["api_key"] = api_key
            
            # Generic config editor for other tools
            else:
                st.write("Edit configuration as JSON:")
                config_json = json.dumps(tool_config, indent=2) if tool_config else "{}"
                
                edited_config = st.text_area(
                    "Tool Configuration (JSON)",
                    value=config_json,
                    height=300
                )
                
                try:
                    # Parse and update config if valid JSON
                    if edited_config:
                        new_config = json.loads(edited_config)
                        st.session_state.config["tool_config"][selected_tool] = new_config
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")
    
    with tab3:
        st.header("Advanced Settings")
        
        # Environment variables display and edit
        st.subheader("Environment Variables")
        st.info("These environment variables are used by the MCP server and tools.")
        
        # Get current environment variables (filtered to relevant ones)
        relevant_prefixes = ["MCP_", "SF_", "BRAVE_", "BROWSERBASE_", "NEWS_API_", "SHOPIFY_", "LINKEDIN_"]
        env_vars = {k: v for k, v in os.environ.items() 
                   if any(k.startswith(prefix) for prefix in relevant_prefixes)}
        
        # Add some common environment variables if not present
        expected_vars = [
            "MCP_HOST", "MCP_PORT", "MCP_LOG_LEVEL", 
            "BRAVE_API_KEY", 
            "BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID",
            "NEWS_API_KEY",
            "SF_USERNAME", "SF_PASSWORD", "SF_SECURITY_TOKEN",
            "LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"
        ]
        
        for var in expected_vars:
            if var not in env_vars:
                env_vars[var] = ""
        
        # Display editable environment variables
        st.write("Note: Changes to environment variables won't persist between app restarts.")
        
        edited_vars = {}
        for var_name, var_value in sorted(env_vars.items()):
            # Use password input for sensitive values
            is_sensitive = any(s in var_name.upper() for s in ["KEY", "TOKEN", "SECRET", "PASSWORD"])
            
            new_value = st.text_input(
                var_name,
                value=var_value,
                type="password" if is_sensitive else "default"
            )
            
            if new_value != var_value:
                edited_vars[var_name] = new_value
        
        # Apply environment variable changes button
        if edited_vars and st.button("Apply Environment Variable Changes"):
            for var_name, var_value in edited_vars.items():
                if var_value:
                    os.environ[var_name] = var_value
                    st.success(f"Updated {var_name}")
            
            st.warning("Note: These changes are only effective for this session.")
            
        # Raw config editor
        st.subheader("Raw Configuration")
        if st.checkbox("Edit Raw YAML Configuration"):
            raw_config = yaml.dump(st.session_state.config, default_flow_style=False)
            
            edited_raw_config = st.text_area(
                "Raw Configuration (YAML)",
                value=raw_config,
                height=400
            )
            
            if st.button("Parse and Apply Raw Configuration"):
                try:
                    new_config = yaml.safe_load(edited_raw_config)
                    st.session_state.config = new_config
                    st.success("Raw configuration applied successfully")
                except Exception as e:
                    st.error(f"Error parsing configuration: {str(e)}")
    
    # Save configuration if button was pressed
    if save_button:
        if save_config(st.session_state.config, config_path):
            st.sidebar.success("Configuration saved successfully!")
            st.sidebar.info("Restart the server to apply changes.")
        else:
            st.sidebar.error("Failed to save configuration.")

# Run the app
if __name__ == "__main__":
    main()
