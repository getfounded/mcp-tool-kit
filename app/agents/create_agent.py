# create_agent.py
#!/usr/bin/env python3
import os
import sys
import textwrap
import argparse
from datetime import datetime


def create_agent(name, description, code_content):
    """Generate and deploy an agent file from basic parameters"""
    # Convert name to snake_case for the agent_name
    agent_name = name.lower().replace(' ', '_').replace('-', '_')

    # Convert to CamelCase for the class name
    class_name = ''.join(word.capitalize() for word in name.split())
    if not class_name.endswith('Agent'):
        class_name += 'Agent'

    # Format the code with proper indentation
    indent = '        '  # 8 spaces for method body
    formatted_code = textwrap.indent(textwrap.dedent(code_content), indent)

    # Create the agent code
    agent_code = f'''
# Agent: {name}
# Description: {description}
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

from agent_registry import MCPAgent, register_agent
import json

@register_agent
class {class_name}(MCPAgent):
    agent_name = "{agent_name}"
    agent_description = "{description}"
    agent_version = "1.0"
    agent_author = "Auto-Generator"
    
    def run(self, params):
{formatted_code}
'''

    # Create the agents directory if it doesn't exist
    os.makedirs("agents", exist_ok=True)

    # Write the agent file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{agent_name}_{timestamp}.py"
    file_path = os.path.join("agents", filename)

    with open(file_path, "w") as f:
        f.write(agent_code)

    print(f"✅ Agent created successfully: {file_path}")
    print(f"   Agent '{agent_name}' is now available automatically!")
    return file_path


def main():
    parser = argparse.ArgumentParser(description="Create a new agent")
    parser.add_argument("name", help="Name of the agent")
    parser.add_argument(
        "description", help="Description of what the agent does")
    parser.add_argument("--code", help="Code for the agent's run method body")
    parser.add_argument(
        "--code-file", help="File containing code for the run method")
    parser.add_argument("--template", choices=["basic", "lookup", "calculator"],
                        help="Use a predefined template")

    args = parser.parse_args()

    # Determine the code content
    code_content = ""

    if args.code:
        code_content = args.code
    elif args.code_file:
        with open(args.code_file, "r") as f:
            code_content = f.read()
    elif args.template:
        if args.template == "basic":
            code_content = '''
            # Simple agent template
            if "query" not in params:
                return {"error": "No query provided"}
                
            query = params["query"]
            
            # Process the query
            result = f"Processed: {query}"
            
            return {
                "success": True,
                "result": result
            }
            '''
        elif args.template == "lookup":
            code_content = '''
            # Web lookup agent template
            if "query" not in params:
                return {"error": "No query provided"}
                
            query = params["query"]
            
            # Search for information
            search_results = self.toolkit.web_search(query, count=3)
            
            return {
                "success": True,
                "results": search_results
            }
            '''
        elif args.template == "calculator":
            code_content = '''
            # Calculator agent template
            if "expression" not in params:
                return {"error": "No expression provided"}
                
            expression = params["expression"]
            
            try:
                # Safely evaluate the expression
                result = eval(expression)
                return {
                    "success": True,
                    "result": result
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
            '''
    else:
        # If no code provided, open an editor
        import tempfile
        import subprocess

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
            tmp.write(b"""# Write your agent code here
# This is the body of the 'run' method
# 'params' contains input parameters
# 'self.toolkit' gives access to all MCPToolKit methods
# Return a dictionary with your results

# Example:
result = {}
if "query" in params:
    # Your agent logic here
    result["answer"] = "Response to " + params["query"]
else:
    result["error"] = "No query provided"
    
return result
""")
            tmp_path = tmp.name

        # Open editor
        editor = os.environ.get("EDITOR", "nano")
        subprocess.call([editor, tmp_path])

        # Read the edited code
        with open(tmp_path, "r") as f:
            code_content = f.read()

        # Clean up
        os.unlink(tmp_path)

    # Create the agent
    create_agent(args.name, args.description, code_content)


if __name__ == "__main__":
    main()
