#!/usr/bin/env python3
"""
Sequential Thinking tools implementation using the decorator pattern.
"""
import json
from typing import Dict, List, Any, Optional

from app.tools.base.registry import register_tool
from app.tools.sequential_thinking.service import SequentialThinkingService


@register_tool(
    category="problem_solving",
    service_class=SequentialThinkingService,
    description="A detailed tool for dynamic and reflective problem-solving through sequential thoughts"
)
async def sequentialthinking(
    self,
    thought: str,
    thoughtNumber: int,
    totalThoughts: int,
    nextThoughtNeeded: bool,
    isRevision: Optional[bool] = None,
    revisesThought: Optional[int] = None,
    branchFromThought: Optional[int] = None,
    branchId: Optional[str] = None,
    needsMoreThoughts: Optional[bool] = None
) -> str:
    """
    A detailed tool for dynamic and reflective problem-solving through thoughts.

    This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
    Each thought can build on, question, or revise previous insights as understanding deepens.

    Args:
        thought: The content of the thought
        thoughtNumber: The number of this thought in the sequence
        totalThoughts: The total expected number of thoughts
        nextThoughtNeeded: Whether another thought is needed after this one
        isRevision: Whether this thought revises an earlier thought
        revisesThought: The number of the thought being revised
        branchFromThought: If branching, the thought number to branch from
        branchId: Identifier for a branch of thoughts
        needsMoreThoughts: Whether more thoughts are needed than originally planned

    Returns:
        JSON string with thought processing results
    """
    result = await self.process_thought(
        thought,
        thoughtNumber,
        totalThoughts,
        nextThoughtNeeded,
        isRevision,
        revisesThought,
        branchFromThought,
        branchId,
        needsMoreThoughts
    )
    return json.dumps(result, indent=2)


@register_tool(
    category="problem_solving",
    service_class=SequentialThinkingService,
    description="Get the complete thought history"
)
def get_thought_history(self) -> str:
    """
    Get the complete thought history.

    Returns:
        JSON string with all thoughts in the history
    """
    result = self.get_thought_history()
    return json.dumps(result, indent=2)


@register_tool(
    category="problem_solving",
    service_class=SequentialThinkingService,
    description="Get all thoughts in a specific branch"
)
def get_branch(self, branch_id: str) -> str:
    """
    Get all thoughts in a specific branch.

    Args:
        branch_id: The identifier of the branch

    Returns:
        JSON string with all thoughts in the branch
    """
    result = self.get_branch(branch_id)
    return json.dumps(result, indent=2)


@register_tool(
    category="problem_solving",
    service_class=SequentialThinkingService,
    description="Clear all thought history and branches"
)
def clear_thought_history(self) -> str:
    """
    Clear all thought history and branches.

    Returns:
        JSON string with the result of the operation
    """
    self.clear_history()
    return json.dumps({"status": "success", "message": "Thought history cleared"}, indent=2)
