# deploy_template_agent.py
#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from datetime import datetime
import re


def deploy_template(template_name, agent_name=None, agent_description=None):
    """Deploy an agent from a template with customizations"""
    # Find the template
    template_dir = "agent_templates"
    template_path = None

    if template_name.endswith(".py"):
        template_path = os.path.join(template_dir, template_name)
    else:
        template_path = os.path.join(template_dir, f"{template_name}.py")
        if not os.path.exists(template_path):
            template_path = os.path.join(
                template_dir, f"{template_name}_agent_template.py")

    if not os.path.exists(template_path):
        print(f"Error: Template '{template_name}' not found in {template_dir}")
        return False

    # Read the template
    with open(template_path, "r") as f:
        template_content = f.read()

    # Make customizations if specified
    if agent_name or agent_description:
        # Update agent_name if specified
        if agent_name:
            snake_case_name = agent_name.lower().replace(' ', '_').replace('-', '_')
            template_content = re.sub(
                r'agent_name\s*=\s*"[^"]*"',
                f'agent_name = "{snake_case_name}"',
                template_content
            )

            # Try to update class name too (more complex, might not always work)
            camel_case_name = ''.join(word.capitalize()
                                      for word in agent_name.split())
            if not camel_case_name.endswith('Agent'):
                camel_case_name += 'Agent'

            template_content = re.sub(
                r'class\s+\w+\(\s*MCPAgent\s*\)',
                f'class {camel_case_name}(MCPAgent)',
                template_content
            )

        # Update description if specified
        if agent_description:
            template_content = re.sub(
                r'agent_description\s*=\s*"[^"]*"',
                f'agent_description = "{agent_description}"',
                template_content
            )

    # Create agents directory if it doesn't exist
    os.makedirs("agents", exist_ok=True)

    # Generate a filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    template_basename = os.path.basename(template_path)
    filename = template_basename.replace("_template", f"_{timestamp}")

    # Write to agents directory
    destination = os.path.join("agents", filename)
    with open(destination, "w") as f:
        f.write(template_content)

    print(f"✅ Agent deployed from template: {destination}")
    print("   Agent is now available automatically!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Deploy an agent from a template")
    parser.add_argument("template", help="Name of the template")
    parser.add_argument("--name", help="Custom name for the agent")
    parser.add_argument(
        "--description", help="Custom description for the agent")

    args = parser.parse_args()
    deploy_template(args.template, args.name, args.description)


if __name__ == "__main__":
    main()
