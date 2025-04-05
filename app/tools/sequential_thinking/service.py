#!/usr/bin/env python3
"""
Enhanced Sequential Thinking service for reflective problem-solving.
"""
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pydantic import BaseModel

from app.tools.base.service import ToolServiceBase


class ThoughtData(BaseModel):
    """Data model for a single thought"""
    thought: str
    thoughtNumber: int
    totalThoughts: int
    nextThoughtNeeded: bool
    isRevision: Optional[bool] = None
    revisesThought: Optional[int] = None
    branchFromThought: Optional[int] = None
    branchId: Optional[str] = None
    needsMoreThoughts: Optional[bool] = None


class SequentialThinkingService(ToolServiceBase):
    """Service for managing sequential thinking operations"""

    def __init__(self):
        """Initialize the Sequential Thinking service"""
        super().__init__()
        self.thought_history = []
        self.branches = {}

    def initialize(self) -> Tuple[bool, str]:
        """
        Initialize the Sequential Thinking service.

        Returns:
            Tuple of (success, message)
        """
        self.initialized = True
        return True, "Sequential Thinking service initialized successfully"

    def format_thought(self, thought_data: ThoughtData) -> str:
        """
        Format a thought with visual indicators.

        Args:
            thought_data: The thought data to format

        Returns:
            A formatted string representation of the thought
        """
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
                              needsMoreThoughts: Optional[bool] = None
                              ) -> Dict[str, Any]:
        """
        Process a thought in a sequential thinking process.

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
            Dictionary with thought processing results
        """
        self._is_initialized()

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

            # Log formatted thought
            self.logger.info(self.format_thought(thought_data))

            # Return result
            return {
                "thoughtNumber": thought_data.thoughtNumber,
                "totalThoughts": thought_data.totalThoughts,
                "nextThoughtNeeded": thought_data.nextThoughtNeeded,
                "branches": list(self.branches.keys()),
                "thoughtHistoryLength": len(self.thought_history)
            }

        except Exception as e:
            self.logger.error(f"Error processing thought: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }

    def get_thought_history(self) -> List[Dict]:
        """
        Get the complete thought history.

        Returns:
            List of thought data dictionaries
        """
        self._is_initialized()
        return [t.dict() for t in self.thought_history]

    def get_branch(self, branch_id: str) -> List[Dict]:
        """
        Get all thoughts in a specific branch.

        Args:
            branch_id: The identifier of the branch

        Returns:
            List of thought data dictionaries in the branch
        """
        self._is_initialized()
        if branch_id not in self.branches:
            return []
        return [t.dict() for t in self.branches[branch_id]]

    def clear_history(self) -> None:
        """Clear all thought history and branches"""
        self._is_initialized()
        self.thought_history = []
        self.branches = {}
