# agent_tools.py
import json
from typing import Dict, Any
import logging

from mcp.server.fastmcp import FastMCP, Context
from app.toolkit import MCPToolKit
from agent_registry import get_agent_instance, get_registered_agents

logger = logging.getLogger("agent_tools")

# Tool function for running agents


async def run_agent(agent_name: str, parameters: Dict[str, Any] = None, ctx: Context = None) -> str:
    """
    Run a registered agent with the provided parameters

    Parameters:
    - agent_name: Name of the registered agent to run
    - parameters: Dictionary of parameters to pass to the agent
    """
    try:
        # Create toolkit instance
        toolkit = MCPToolKit()

        # Get agent instance
        agent = get_agent_instance(agent_name, toolkit)

        # Run the agent
        result = agent.run(parameters or {})

        # Return JSON result
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error running agent {agent_name}: {str(e)}")
        return json.dumps({"error": f"Error running agent: {str(e)}"}, indent=2)

# Tool function to list available agents


async def list_agents(ctx: Context = None) -> str:
    """
    List all registered agents and their metadata
    """
    try:
        agents = get_registered_agents()

        # Get metadata for each agent
        agent_info = {}
        for name, agent_class in agents.items():
            agent_info[name] = agent_class.get_metadata()

        return json.dumps({"agents": agent_info}, indent=2)
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return json.dumps({"error": f"Error listing agents: {str(e)}"}, indent=2)

# Function to register agent tools with MCP


def register_agent_tools(mcp: FastMCP):
    """Register agent tools with the MCP server"""
    mcp.tool(name="run_agent")(run_agent)
    mcp.tool(name="list_agents")(list_agents)
    logger.info("Registered agent tools with MCP server")
