# create_agent_cli.py
#!/usr/bin/env python3
import sys
import os
import argparse
import textwrap
from agent_generator import create_agent


def main():
    parser = argparse.ArgumentParser(
        description="Create and deploy a new agent instantly")
    parser.add_argument("name", help="Name of the agent")
    parser.add_argument(
        "description", help="Description of what the agent does")
    parser.add_argument(
        "--code", help="Python code for the agent's run function body")
    parser.add_argument(
        "--code-file", help="File containing the Python code for the agent's run function body")

    args = parser.parse_args()

    # Get the code
    if args.code:
        code = args.code
    elif args.code_file:
        with open(args.code_file, "r") as f:
            code = f.read()
    else:
        # If no code provided, open an editor
        import tempfile
        import subprocess

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
            tmp.write(b"""# Write your agent code here
# This is the body of the 'run' method
# 'params' contains input parameters
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
            code = f.read()

        # Clean up
        os.unlink(tmp_path)

    # Create the agent
    file_path = create_agent(args.name, args.description, code)
    print(f"✅ Agent created successfully at: {file_path}")
    print(f"   Agent '{args.name}' is now ready to use!")


if __name__ == "__main__":
    main()
