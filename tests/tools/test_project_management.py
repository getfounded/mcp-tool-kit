#!/usr/bin/env python3
"""
Unit tests for Project Management tools.
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock

from app.tools.project_management.service import ProjectManagementService
from app.tools.base.registry import get_tools_by_service, get_tool_categories


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up environment variables for testing"""
    monkeypatch.setenv("PM_API_KEY", "test_api_key")
    monkeypatch.setenv("PM_INSTANCE_URL", "https://test.example.com")
    monkeypatch.setenv("PM_PROVIDER", "asana")


@pytest.fixture
def pm_service(mock_env_vars):
    """Create a test PM service"""
    service = ProjectManagementService()
    service.initialize()
    return service


def test_service_initialization(pm_service):
    """Test service initialization"""
    assert pm_service.initialized
    assert pm_service.api_key == "test_api_key"
    assert pm_service.instance_url == "https://test.example.com"
    assert pm_service.provider == "asana"


def test_tools_registration():
    """Test that all PM tools are registered"""
    tools = get_tools_by_service(ProjectManagementService)
    assert len(tools) >= 13  # At least 13 PM tools
    assert "pm_get_projects" in tools
    assert "pm_create_task" in tools
    assert "pm_generate_report" in tools

    # Check category registration
    categories = get_tool_categories()
    assert "Project Management" in categories


async def test_get_projects(pm_service):
    """Test get_projects functionality"""
    result = await pm_service.get_projects(limit=5)
    assert "projects" in result
    assert len(result["projects"]) == 5
    assert "count" in result
    assert result["count"] == 5
    assert "provider" in result
    assert result["provider"] == "asana"


async def test_get_project(pm_service):
    """Test get_project functionality"""
    result = await pm_service.get_project("proj_123")
    assert result["id"] == "proj_123"
    assert "name" in result
    assert "description" in result
    assert "status" in result
    assert "team_members" in result
    assert "milestones" in result
    assert len(result["milestones"]) == 3


async def test_create_task(pm_service):
    """Test create_task functionality"""
    result = await pm_service.create_task(
        project_id="proj_123",
        name="Test Task",
        description="Test Description",
        priority="high"
    )
    assert result["status"] == "success"
    assert "task" in result
    assert result["task"]["name"] == "Test Task"
    assert result["task"]["description"] == "Test Description"
    assert result["task"]["priority"] == "high"
    assert result["task"]["project_id"] == "proj_123"


async def test_get_tasks(pm_service):
    """Test get_tasks functionality"""
    # Test with no filters
    result = await pm_service.get_tasks(limit=10)
    assert "tasks" in result
    assert len(result["tasks"]) <= 10

    # Test with status filter
    result = await pm_service.get_tasks(status="in_progress", limit=10)
    assert "tasks" in result
    for task in result["tasks"]:
        assert task["status"] == "in_progress"

    # Test with project filter
    project_id = "proj_1"
    result = await pm_service.get_tasks(project_id=project_id, limit=10)
    assert "tasks" in result
    for task in result["tasks"]:
        assert task["project_id"] == project_id


async def test_generate_report(pm_service):
    """Test generate_report functionality"""
    # Test progress report
    result = await pm_service.generate_report(
        project_id="proj_123",
        report_type="progress"
    )
    assert result["report_type"] == "progress"
    assert "data" in result
    assert "tasks_total" in result["data"]
    assert "completion_percentage" in result["data"]

    # Test team performance report
    result = await pm_service.generate_report(
        project_id="proj_123",
        report_type="team_performance"
    )
    assert result["report_type"] == "team_performance"
    assert "data" in result
    assert "team_members" in result["data"]
    assert "avg_completion_rate" in result["data"]
