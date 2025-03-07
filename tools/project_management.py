#!/usr/bin/env python3
import os
import json
import logging
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Project Management tools MCP reference set")


class ProjectManagementTools(str, Enum):
    """Enum of Project Management tool names"""
    GET_PROJECTS = "pm_get_projects"
    GET_PROJECT = "pm_get_project"
    GET_TASKS = "pm_get_tasks"
    CREATE_TASK = "pm_create_task"
    UPDATE_TASK = "pm_update_task"
    GET_TEAM_MEMBERS = "pm_get_team_members"
    ASSIGN_TASK = "pm_assign_task"
    GET_TASK_COMMENTS = "pm_get_task_comments"
    ADD_TASK_COMMENT = "pm_add_task_comment"
    CREATE_PROJECT = "pm_create_project"
    GET_MILESTONES = "pm_get_milestones"
    CREATE_MILESTONE = "pm_create_milestone"
    GENERATE_REPORT = "pm_generate_report"


class ProjectManagementService:
    """Service to handle Project Management API operations"""

    def __init__(self, api_key=None, instance_url=None, provider="asana"):
        """Initialize the Project Management service"""
        # API credentials
        self.api_key = api_key or os.environ.get("PM_API_KEY")
        self.instance_url = instance_url or os.environ.get("PM_INSTANCE_URL")
        self.provider = provider or os.environ.get("PM_PROVIDER", "asana")

        # Validate credentials
        if not self.api_key:
            logging.warning(
                "Project Management API key not configured. Please set PM_API_KEY environment variable.")

        if self.provider == "asana" and not self.api_key:
            logging.warning("Asana API requires an API key.")
        elif self.provider == "jira" and (not self.api_key or not self.instance_url):
            logging.warning(
                "Jira API requires both an API key and instance URL.")

    async def get_projects(self, workspace_id=None, limit=20):
        """Get a list of projects"""
        try:
            # Simulate project data for demo purposes
            # In a real implementation, this would make an API call to the PM provider
            projects = []
            for i in range(1, limit + 1):
                projects.append({
                    "id": f"proj_{i}",
                    "name": f"Project {i}",
                    "description": f"Description for Project {i}",
                    "status": "active" if i % 3 != 0 else "completed",
                    "created_at": (datetime.now() - timedelta(days=i*5)).isoformat(),
                    "workspace_id": workspace_id or "default_workspace"
                })

            return {
                "projects": projects,
                "count": len(projects),
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_project(self, project_id):
        """Get a specific project by ID"""
        try:
            # Simulate project data
            project = {
                "id": project_id,
                "name": f"Project {project_id.split('_')[1]}",
                "description": f"Detailed description for {project_id}",
                "status": "active",
                "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "owner": "user_123",
                "team_members": ["user_123", "user_456", "user_789"],
                "tasks_completed": 15,
                "tasks_total": 32,
                "milestones": [
                    {
                        "id": "mile_1",
                        "name": "Planning Phase",
                        "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                        "status": "completed"
                    },
                    {
                        "id": "mile_2",
                        "name": "Development Phase",
                        "due_date": (datetime.now() + timedelta(days=20)).isoformat(),
                        "status": "in_progress"
                    },
                    {
                        "id": "mile_3",
                        "name": "Testing Phase",
                        "due_date": (datetime.now() + timedelta(days=25)).isoformat(),
                        "status": "not_started"
                    }
                ]
            }

            return project
        except Exception as e:
            return {"error": str(e)}

    async def get_tasks(self, project_id=None, assignee_id=None, status=None, limit=50):
        """Get tasks with optional filtering"""
        try:
            # Simulate task data
            tasks = []
            statuses = ["not_started", "in_progress", "completed", "blocked"]

            for i in range(1, limit + 1):
                task_status = status or statuses[i % len(statuses)]

                # Only include tasks matching filter criteria
                if status and task_status != status:
                    continue

                # Generate a task
                task = {
                    "id": f"task_{i}",
                    "name": f"Task {i}",
                    "description": f"Description for Task {i}",
                    "status": task_status,
                    "priority": "high" if i % 5 == 0 else "medium" if i % 3 == 0 else "low",
                    "due_date": (datetime.now() + timedelta(days=i % 14)).isoformat(),
                    "created_at": (datetime.now() - timedelta(days=i % 10)).isoformat(),
                    "assignee_id": assignee_id or f"user_{(i % 3) + 1}",
                    "project_id": project_id or f"proj_{(i % 5) + 1}"
                }

                tasks.append(task)

            return {
                "tasks": tasks,
                "count": len(tasks),
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def create_task(self, project_id, name, description=None, assignee_id=None,
                          due_date=None, priority="medium", status="not_started"):
        """Create a new task"""
        try:
            # Simulate task creation
            task = {
                "id": f"task_{int(datetime.now().timestamp())}",
                "name": name,
                "description": description or "",
                "status": status,
                "priority": priority,
                "due_date": due_date or (datetime.now() + timedelta(days=7)).isoformat(),
                "created_at": datetime.now().isoformat(),
                "assignee_id": assignee_id,
                "project_id": project_id
            }

            return {
                "status": "success",
                "task": task,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def update_task(self, task_id, updates):
        """Update a task with the provided changes"""
        try:
            # Simulate task update by returning the updated task
            # In a real implementation, we'd first fetch the task then apply updates

            # Create a mock existing task
            existing_task = {
                "id": task_id,
                "name": f"Task {task_id.split('_')[1]}",
                "description": "Original task description",
                "status": "in_progress",
                "priority": "medium",
                "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "assignee_id": "user_1",
                "project_id": "proj_1"
            }

            # Apply updates
            updated_task = {**existing_task, **updates}

            return {
                "status": "success",
                "task": updated_task,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_team_members(self, workspace_id=None, project_id=None):
        """Get team members for a workspace or project"""
        try:
            # Simulate team member data
            members = []

            for i in range(1, 11):
                member = {
                    "id": f"user_{i}",
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "role": "admin" if i == 1 else "manager" if i <= 3 else "member",
                    "department": ["Engineering", "Design", "Marketing", "Product", "Support"][i % 5]
                }

                members.append(member)

            return {
                "members": members,
                "count": len(members),
                "workspace_id": workspace_id,
                "project_id": project_id,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def assign_task(self, task_id, assignee_id):
        """Assign a task to a team member"""
        try:
            # Simulate task assignment
            return {
                "status": "success",
                "task_id": task_id,
                "assignee_id": assignee_id,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_task_comments(self, task_id, limit=20):
        """Get comments for a specific task"""
        try:
            # Simulate comment data
            comments = []

            for i in range(1, limit + 1):
                comment = {
                    "id": f"comment_{i}",
                    "task_id": task_id,
                    "text": f"This is comment {i} on task {task_id}",
                    "created_at": (datetime.now() - timedelta(hours=i*2)).isoformat(),
                    "author_id": f"user_{(i % 5) + 1}",
                    "author_name": f"User {(i % 5) + 1}"
                }

                comments.append(comment)

            return {
                "comments": comments,
                "count": len(comments),
                "task_id": task_id,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def add_task_comment(self, task_id, text, author_id=None):
        """Add a comment to a task"""
        try:
            # Simulate adding a comment
            comment = {
                "id": f"comment_{int(datetime.now().timestamp())}",
                "task_id": task_id,
                "text": text,
                "created_at": datetime.now().isoformat(),
                "author_id": author_id or "user_1",
                "author_name": f"User {author_id.split('_')[1] if author_id else '1'}"
            }

            return {
                "status": "success",
                "comment": comment,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def create_project(self, name, description=None, workspace_id=None, team_members=None):
        """Create a new project"""
        try:
            # Simulate project creation
            project = {
                "id": f"proj_{int(datetime.now().timestamp())}",
                "name": name,
                "description": description or "",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "workspace_id": workspace_id or "default_workspace",
                "team_members": team_members or []
            }

            return {
                "status": "success",
                "project": project,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_milestones(self, project_id):
        """Get milestones for a project"""
        try:
            # Simulate milestone data
            milestones = []

            for i in range(1, 6):
                milestone = {
                    "id": f"mile_{i}",
                    "project_id": project_id,
                    "name": f"Milestone {i}",
                    "description": f"Description for Milestone {i}",
                    "due_date": (datetime.now() + timedelta(days=i*10)).isoformat(),
                    "status": "completed" if i == 1 else "in_progress" if i == 2 else "not_started"
                }

                milestones.append(milestone)

            return {
                "milestones": milestones,
                "count": len(milestones),
                "project_id": project_id,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def create_milestone(self, project_id, name, description=None, due_date=None):
        """Create a new milestone"""
        try:
            # Simulate milestone creation
            milestone = {
                "id": f"mile_{int(datetime.now().timestamp())}",
                "project_id": project_id,
                "name": name,
                "description": description or "",
                "due_date": due_date or (datetime.now() + timedelta(days=30)).isoformat(),
                "status": "not_started",
                "created_at": datetime.now().isoformat()
            }

            return {
                "status": "success",
                "milestone": milestone,
                "provider": self.provider
            }
        except Exception as e:
            return {"error": str(e)}

    async def generate_report(self, project_id=None, report_type="progress", start_date=None, end_date=None):
        """Generate a project report"""
        try:
            # Get default date range if not provided
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()

            # Simulate report data
            report = {
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "project_id": project_id,
                "date_range": {
                    "start": start_date,
                    "end": end_date
                }
            }

            # Different report types
            if report_type == "progress":
                report["data"] = {
                    "tasks_total": 45,
                    "tasks_completed": 28,
                    "tasks_in_progress": 12,
                    "tasks_blocked": 5,
                    "completion_percentage": 62,
                    "on_track": True,
                    "days_ahead_schedule": 2,
                    "milestones": {
                        "total": 5,
                        "completed": 2,
                        "upcoming": [
                            {
                                "name": "Feature Freeze",
                                "due_in_days": 5
                            },
                            {
                                "name": "Beta Release",
                                "due_in_days": 12
                            }
                        ]
                    }
                }
            elif report_type == "team_performance":
                report["data"] = {
                    "team_members": [
                        {
                            "id": "user_1",
                            "name": "User 1",
                            "tasks_assigned": 12,
                            "tasks_completed": 8,
                            "on_time_completion_rate": 92
                        },
                        {
                            "id": "user_2",
                            "name": "User 2",
                            "tasks_assigned": 15,
                            "tasks_completed": 10,
                            "on_time_completion_rate": 87
                        },
                        {
                            "id": "user_3",
                            "name": "User 3",
                            "tasks_assigned": 18,
                            "tasks_completed": 14,
                            "on_time_completion_rate": 95
                        }
                    ],
                    "avg_completion_rate": 91,
                    "top_performer": "user_3"
                }
            elif report_type == "time_tracking":
                report["data"] = {
                    "total_hours": 320,
                    "hours_by_category": {
                        "Development": 180,
                        "Design": 45,
                        "Testing": 65,
                        "Meetings": 30
                    },
                    "hours_by_team_member": {
                        "user_1": 105,
                        "user_2": 98,
                        "user_3": 117
                    }
                }

            return report
        except Exception as e:
            return {"error": str(e)}

# Tool function definitions


async def pm_get_projects(workspace_id: str = None, limit: int = 20, ctx: Context = None) -> str:
    """Get a list of projects from the project management system

    Parameters:
    - workspace_id: Optional ID of the workspace to get projects from
    - limit: Maximum number of projects to return (default: 20)
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.get_projects(workspace_id, limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_get_project(project_id: str, ctx: Context = None) -> str:
    """Get detailed information about a specific project

    Parameters:
    - project_id: ID of the project to retrieve
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.get_project(project_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_get_tasks(project_id: str = None, assignee_id: str = None,
                       status: str = None, limit: int = 50, ctx: Context = None) -> str:
    """Get tasks with optional filtering

    Parameters:
    - project_id: Optional ID of the project to get tasks from
    - assignee_id: Optional ID of the user assigned to tasks
    - status: Optional status filter (not_started, in_progress, completed, blocked)
    - limit: Maximum number of tasks to return (default: 50)
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.get_tasks(project_id, assignee_id, status, limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_create_task(project_id: str, name: str, description: str = None,
                         assignee_id: str = None, due_date: str = None,
                         priority: str = "medium", status: str = "not_started",
                         ctx: Context = None) -> str:
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
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.create_task(
            project_id, name, description, assignee_id, due_date, priority, status
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_update_task(task_id: str, updates: Dict[str, Any], ctx: Context = None) -> str:
    """Update an existing task

    Parameters:
    - task_id: ID of the task to update
    - updates: Dictionary of fields to update (name, description, status, priority, due_date, assignee_id)
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.update_task(task_id, updates)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_get_team_members(workspace_id: str = None, project_id: str = None, ctx: Context = None) -> str:
    """Get team members for a workspace or project

    Parameters:
    - workspace_id: Optional ID of the workspace
    - project_id: Optional ID of the project
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.get_team_members(workspace_id, project_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_assign_task(task_id: str, assignee_id: str, ctx: Context = None) -> str:
    """Assign a task to a team member

    Parameters:
    - task_id: ID of the task to assign
    - assignee_id: ID of the user to assign the task to
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.assign_task(task_id, assignee_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_get_task_comments(task_id: str, limit: int = 20, ctx: Context = None) -> str:
    """Get comments for a specific task

    Parameters:
    - task_id: ID of the task to get comments for
    - limit: Maximum number of comments to return (default: 20)
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.get_task_comments(task_id, limit)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_add_task_comment(task_id: str, text: str, author_id: str = None, ctx: Context = None) -> str:
    """Add a comment to a task

    Parameters:
    - task_id: ID of the task to comment on
    - text: Comment text
    - author_id: Optional ID of the comment author
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.add_task_comment(task_id, text, author_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_create_project(name: str, description: str = None, workspace_id: str = None,
                            team_members: List[str] = None, ctx: Context = None) -> str:
    """Create a new project

    Parameters:
    - name: Name of the project
    - description: Optional detailed description of the project
    - workspace_id: Optional ID of the workspace to create the project in
    - team_members: Optional list of user IDs to add to the project
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.create_project(name, description, workspace_id, team_members)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_get_milestones(project_id: str, ctx: Context = None) -> str:
    """Get milestones for a project

    Parameters:
    - project_id: ID of the project to get milestones for
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.get_milestones(project_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_create_milestone(project_id: str, name: str, description: str = None,
                              due_date: str = None, ctx: Context = None) -> str:
    """Create a new milestone

    Parameters:
    - project_id: ID of the project to create the milestone in
    - name: Name of the milestone
    - description: Optional detailed description of the milestone
    - due_date: Optional due date in ISO format (YYYY-MM-DD)
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.create_milestone(project_id, name, description, due_date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


async def pm_generate_report(project_id: str = None, report_type: str = "progress",
                             start_date: str = None, end_date: str = None, ctx: Context = None) -> str:
    """Generate a project report

    Parameters:
    - project_id: Optional ID of the project to generate a report for
    - report_type: Type of report (progress, team_performance, time_tracking)
    - start_date: Optional start date for the report period in ISO format (YYYY-MM-DD)
    - end_date: Optional end date for the report period in ISO format (YYYY-MM-DD)
    """
    pm_service = _get_pm_service()
    if not pm_service:
        return "Project Management service not properly initialized. Please check environment variables."

    try:
        result = await pm_service.generate_report(project_id, report_type, start_date, end_date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# Tool registration and initialization
_pm_service = None


def initialize_pm_service(api_key=None, instance_url=None, provider=None):
    """Initialize the Project Management service"""
    global _pm_service

    # Use environment variables as fallback
    api_key = api_key or os.environ.get("PM_API_KEY")
    instance_url = instance_url or os.environ.get("PM_INSTANCE_URL")
    provider = provider or os.environ.get("PM_PROVIDER", "asana")

    _pm_service = ProjectManagementService(api_key, instance_url, provider)
    return _pm_service


def _get_pm_service():
    """Get or initialize the Project Management service"""
    global _pm_service
    if _pm_service is None:
        _pm_service = initialize_pm_service()
    return _pm_service


def get_pm_tools():
    """Get a dictionary of all Project Management tools for registration with MCP"""
    return {
        ProjectManagementTools.GET_PROJECTS: pm_get_projects,
        ProjectManagementTools.GET_PROJECT: pm_get_project,
        ProjectManagementTools.GET_TASKS: pm_get_tasks,
        ProjectManagementTools.CREATE_TASK: pm_create_task,
        ProjectManagementTools.UPDATE_TASK: pm_update_task,
        ProjectManagementTools.GET_TEAM_MEMBERS: pm_get_team_members,
        ProjectManagementTools.ASSIGN_TASK: pm_assign_task,
        ProjectManagementTools.GET_TASK_COMMENTS: pm_get_task_comments,
        ProjectManagementTools.ADD_TASK_COMMENT: pm_add_task_comment,
        ProjectManagementTools.CREATE_PROJECT: pm_create_project,
        ProjectManagementTools.GET_MILESTONES: pm_get_milestones,
        ProjectManagementTools.CREATE_MILESTONE: pm_create_milestone,
        ProjectManagementTools.GENERATE_REPORT: pm_generate_report
    }

# This function will be called by the unified server to initialize the module


def initialize(mcp=None):
    """Initialize the Project Management module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_pm_service()

    logging.info("Project Management tools initialized successfully")
    return True
