#!/usr/bin/env python3
"""
Project Management service for MCP toolkit.
"""
import os
import json
import logging
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta

from app.tools.base.service import ToolServiceBase
from app.tools.utils.auth import create_auth_handler, AuthBase


class ProjectManagementService(ToolServiceBase):
    """Service to handle Project Management API operations"""

    def __init__(self):
        """Initialize the Project Management service"""
        super().__init__()
        # API credentials
        self.api_key = self.get_env_var("PM_API_KEY", required=False)
        self.instance_url = self.get_env_var("PM_INSTANCE_URL", required=False)
        self.provider = self.get_env_var("PM_PROVIDER", default="asana")

        # Create rate limiter for API requests
        self.create_rate_limiter("default", 100, 60)  # 100 requests per minute

        # Initialize authentication
        self._init_auth()

    def _init_auth(self):
        """Initialize authentication for the service"""
        self.auth_handler = None

        # Different auth methods based on provider
        if self.provider == "asana":
            if self.api_key:
                self.auth_handler = create_auth_handler(
                    "project_management",
                    "api_key",
                    api_key=self.api_key,
                    header_name="Authorization",
                    env_var="PM_API_KEY"
                )
        elif self.provider == "jira":
            self.auth_handler = create_auth_handler(
                "project_management",
                "basic",
                username=self.get_env_var("PM_USERNAME", required=False),
                password=self.api_key,
                username_env="PM_USERNAME",
                password_env="PM_API_KEY"
            )

    def initialize(self) -> bool:
        """Initialize the service"""
        if not self.api_key:
            self.logger.warning(
                "Project Management API key not configured. Please set PM_API_KEY environment variable.")

        if self.provider == "asana" and not self.api_key:
            self.logger.warning("Asana API requires an API key.")
        elif self.provider == "jira" and (not self.api_key or not self.instance_url):
            self.logger.warning(
                "Jira API requires both an API key and instance URL.")

        self.initialized = True
        return True

    async def get_projects(self, workspace_id=None, limit=20):
        """Get a list of projects"""
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
        self._is_initialized()
        self.apply_rate_limit("default", 100, 60, wait=True)

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
