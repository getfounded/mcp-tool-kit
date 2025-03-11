# agent_generator.py
import os
import textwrap
import logging
import uuid
from datetime import datetime

logger = logging.getLogger("agent_generator")


def create_agent(name, description, func_code):
    """
    Create and deploy a new agent from a description and function code

    Args:
        name: Agent name (will be converted to snake_case)
        description: Description of what the agent does
        func_code: Python code for the agent's run function body

    Returns:
        Path to the created agent file
    """
    # Convert name to snake_case
    agent_name = name.lower().replace(' ', '_').replace('-', '_')

    # Sanitize and format the function code
    indent = '        '  # 8 spaces for proper indentation
    formatted_code = textwrap.indent(textwrap.dedent(func_code), indent)

    # Generate a unique ID for the agent
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Create agent file content
    agent_code = f'''
# Auto-generated agent: {name}
# Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# ID: {unique_id}

from agent_registry import MCPAgent, register_agent
import json

@register_agent
class {name.replace(' ', '')}Agent(MCPAgent):
    agent_name = "{agent_name}"
    agent_description = "{description}"
    agent_version = "1.0"
    agent_author = "Auto-Generator"
    
    def run(self, params):
{formatted_code}
'''

    # Ensure the agents directory exists
    os.makedirs("agents", exist_ok=True)

    # Write the agent file
    filename = f"{agent_name}_{timestamp}.py"
    file_path = os.path.join("agents", filename)

    with open(file_path, "w") as f:
        f.write(agent_code)

    logger.info(f"Created agent {agent_name} at {file_path}")
    return file_path
