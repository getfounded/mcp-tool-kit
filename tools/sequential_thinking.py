#!/usr/bin/env python3
import json
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Sequential Thinking tools MCP reference set")


class ThoughtData(BaseModel):
    thought: str
    thoughtNumber: int
    totalThoughts: int
    nextThoughtNeeded: bool
    isRevision: Optional[bool] = None
    revisesThought: Optional[int] = None
    branchFromThought: Optional[int] = None
    branchId: Optional[str] = None
    needsMoreThoughts: Optional[bool] = None


class SequentialThinkingService:
    """Service to handle sequential thinking operations"""

    def __init__(self):
        self.thought_history = []
        self.branches = {}

    def format_thought(self, thought_data: ThoughtData) -> str:
        """Format a thought with nice visual indicators"""
        t = thought_data

        if t.isRevision:
            prefix = "🔄 Revision"
            context = f" (revising thought {t.revisesThought})"
        elif t.branchFromThought:
            prefix = "🌿 Branch"
            context = f" (from thought {t.branchFromThought}, ID: {t.branchId})"
        else:
            prefix = "💭 Thought"
            context = ""

        header = f"{prefix} {t.thoughtNumber}/{t.totalThoughts}{context}"
        border = "─" * max(len(header), len(t.thought) + 4)

        return f"""
┌{border}┐
│ {header} │
├{border}┤
│ {t.thought.ljust(len(border) - 2)} │
└{border}┘"""

    async def process_thought(self,
                              thought: str,
                              thoughtNumber: int,
                              totalThoughts: int,
                              nextThoughtNeeded: bool,
                              isRevision: Optional[bool] = None,
                              revisesThought: Optional[int] = None,
                              branchFromThought: Optional[int] = None,
                              branchId: Optional[str] = None,
                              needsMoreThoughts: Optional[bool] = None,
                              ctx: Context = None
                              ) -> str:
        """Process a thought"""
        try:
            # Create thought data
            thought_data = ThoughtData(
                thought=thought,
                thoughtNumber=thoughtNumber,
                totalThoughts=max(thoughtNumber, totalThoughts),
                nextThoughtNeeded=nextThoughtNeeded,
                isRevision=isRevision,
                revisesThought=revisesThought,
                branchFromThought=branchFromThought,
                branchId=branchId,
                needsMoreThoughts=needsMoreThoughts
            )

            # Add to history
            self.thought_history.append(thought_data)

            # Handle branches
            if thought_data.branchFromThought and thought_data.branchId:
                if thought_data.branchId not in self.branches:
                    self.branches[thought_data.branchId] = []
                self.branches[thought_data.branchId].append(thought_data)

            # Print pretty formatted thought to stderr (useful for debugging)
            if ctx:
                ctx.info(self.format_thought(thought_data))

            # Return result
            return json.dumps({
                "thoughtNumber": thought_data.thoughtNumber,
                "totalThoughts": thought_data.totalThoughts,
                "nextThoughtNeeded": thought_data.nextThoughtNeeded,
                "branches": list(self.branches.keys()),
                "thoughtHistoryLength": len(self.thought_history)
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "status": "failed"
            }, indent=2)

# Tool function definitions that will be registered with MCP


async def sequential_thinking(
    thought: str,
    thoughtNumber: int,
    totalThoughts: int,
    nextThoughtNeeded: bool,
    isRevision: Optional[bool] = None,
    revisesThought: Optional[int] = None,
    branchFromThought: Optional[int] = None,
    branchId: Optional[str] = None,
    needsMoreThoughts: Optional[bool] = None,
    ctx: Context = None
) -> str:
    """A detailed tool for dynamic and reflective problem-solving through thoughts.

    This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
    Each thought can build on, question, or revise previous insights as understanding deepens.

    When to use this tool:
    - Breaking down complex problems into steps
    - Planning and design with room for revision
    - Analysis that might need course correction
    - Problems where the full scope might not be clear initially
    """
    try:
        return await _get_thinking_service().process_thought(
            thought,
            thoughtNumber,
            totalThoughts,
            nextThoughtNeeded,
            isRevision,
            revisesThought,
            branchFromThought,
            branchId,
            needsMoreThoughts,
            ctx
        )
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "failed"
        }, indent=2)

# Tool registration and initialization
_thinking_service_instance = None


def initialize_thinking_service():
    """Initialize the sequential thinking service"""
    global _thinking_service_instance
    _thinking_service_instance = SequentialThinkingService()
    return _thinking_service_instance


def _get_thinking_service():
    """Get or initialize the sequential thinking service"""
    global _thinking_service_instance
    if _thinking_service_instance is None:
        _thinking_service_instance = initialize_thinking_service()
    return _thinking_service_instance


def get_sequential_thinking_tools():
    """Get a dictionary of all sequential thinking tools for registration with MCP"""
    return {
        "sequentialthinking": sequential_thinking
    }
