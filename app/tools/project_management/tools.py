#!/usr/bin/env python3
"""
Project Management tool functions.
"""
import json
from typing import List, Dict, Optional, Any, Union

from app.tools.base.registry import register_tool
from app.tools.project_management.service import ProjectManagementService


@register_tool(
    name="pm_get_projects",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Get a list of projects from the project management system"
)
async def get_projects(self, workspace_id: str = None, limit: int = 20):
    """Get a list of projects from the project management system

    Parameters:
    - workspace_id: Optional ID of the workspace to get projects from
    - limit: Maximum number of projects to return (default: 20)
    """
    try:
        result = await self.get_projects(workspace_id, limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_get_project",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Get detailed information about a specific project"
)
async def get_project(self, project_id: str):
    """Get detailed information about a specific project

    Parameters:
    - project_id: ID of the project to retrieve
    """
    try:
        result = await self.get_project(project_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_get_tasks",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Get tasks with optional filtering"
)
async def get_tasks(self, project_id: str = None, assignee_id: str = None,
                    status: str = None, limit: int = 50):
    """Get tasks with optional filtering

    Parameters:
    - project_id: Optional ID of the project to get tasks from
    - assignee_id: Optional ID of the user assigned to tasks
    - status: Optional status filter (not_started, in_progress, completed, blocked)
    - limit: Maximum number of tasks to return (default: 50)
    """
    try:
        result = await self.get_tasks(project_id, assignee_id, status, limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_create_task",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Create a new task in the project management system"
)
async def create_task(self, project_id: str, name: str, description: str = None,
                      assignee_id: str = None, due_date: str = None,
                      priority: str = "medium", status: str = "not_started"):
    """Create a new task in the project management system

    Parameters:
    - project_id: ID of the project to create the task in
    - name: Name of the task
    - description: Optional detailed description of the task
    - assignee_id: Optional ID of the user to assign the task to
    - due_date: Optional due date in ISO format (YYYY-MM-DD)
    - priority: Task priority (low, medium, high)
    - status: Initial task status (not_started, in_progress, completed, blocked)
    """
    try:
        result = await self.create_task(
            project_id, name, description, assignee_id, due_date, priority, status
        )
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_update_task",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Update an existing task"
)
async def update_task(self, task_id: str, updates: Dict[str, Any]):
    """Update an existing task

    Parameters:
    - task_id: ID of the task to update
    - updates: Dictionary of fields to update (name, description, status, priority, due_date, assignee_id)
    """
    try:
        result = await self.update_task(task_id, updates)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_get_team_members",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Get team members for a workspace or project"
)
async def get_team_members(self, workspace_id: str = None, project_id: str = None):
    """Get team members for a workspace or project

    Parameters:
    - workspace_id: Optional ID of the workspace
    - project_id: Optional ID of the project
    """
    try:
        result = await self.get_team_members(workspace_id, project_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_assign_task",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Assign a task to a team member"
)
async def assign_task(self, task_id: str, assignee_id: str):
    """Assign a task to a team member

    Parameters:
    - task_id: ID of the task to assign
    - assignee_id: ID of the user to assign the task to
    """
    try:
        result = await self.assign_task(task_id, assignee_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_get_task_comments",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Get comments for a specific task"
)
async def get_task_comments(self, task_id: str, limit: int = 20):
    """Get comments for a specific task

    Parameters:
    - task_id: ID of the task to get comments for
    - limit: Maximum number of comments to return (default: 20)
    """
    try:
        result = await self.get_task_comments(task_id, limit)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_add_task_comment",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Add a comment to a task"
)
async def add_task_comment(self, task_id: str, text: str, author_id: str = None):
    """Add a comment to a task

    Parameters:
    - task_id: ID of the task to comment on
    - text: Comment text
    - author_id: Optional ID of the comment author
    """
    try:
        result = await self.add_task_comment(task_id, text, author_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_create_project",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Create a new project"
)
async def create_project(self, name: str, description: str = None, workspace_id: str = None,
                         team_members: List[str] = None):
    """Create a new project

    Parameters:
    - name: Name of the project
    - description: Optional detailed description of the project
    - workspace_id: Optional ID of the workspace to create the project in
    - team_members: Optional list of user IDs to add to the project
    """
    try:
        result = await self.create_project(name, description, workspace_id, team_members)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_get_milestones",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Get milestones for a project"
)
async def get_milestones(self, project_id: str):
    """Get milestones for a project

    Parameters:
    - project_id: ID of the project to get milestones for
    """
    try:
        result = await self.get_milestones(project_id)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_create_milestone",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Create a new milestone"
)
async def create_milestone(self, project_id: str, name: str, description: str = None,
                           due_date: str = None):
    """Create a new milestone

    Parameters:
    - project_id: ID of the project to create the milestone in
    - name: Name of the milestone
    - description: Optional detailed description of the milestone
    - due_date: Optional due date in ISO format (YYYY-MM-DD)
    """
    try:
        result = await self.create_milestone(project_id, name, description, due_date)
        return result
    except Exception as e:
        return {"error": str(e)}


@register_tool(
    name="pm_generate_report",
    category="Project Management",
    service_class=ProjectManagementService,
    description="Generate a project report"
)
async def generate_report(self, project_id: str = None, report_type: str = "progress",
                          start_date: str = None, end_date: str = None):
    """Generate a project report

    Parameters:
    - project_id: Optional ID of the project to generate a report for
    - report_type: Type of report (progress, team_performance, time_tracking)
    - start_date: Optional start date for the report period in ISO format (YYYY-MM-DD)
    - end_date: Optional end date for the report period in ISO format (YYYY-MM-DD)
    """
    try:
        result = await self.generate_report(project_id, report_type, start_date, end_date)
        return result
    except Exception as e:
        return {"error": str(e)}
