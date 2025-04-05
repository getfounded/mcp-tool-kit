#!/usr/bin/env python3
"""
Microsoft Teams API tools module for MCP toolkit.

This module provides tools for interacting with Microsoft Teams via the Microsoft Graph API.
"""
import logging
from app.tools.base.registry import register_tool

# Import service and tools
from app.tools.teams.service import TeamsService
from app.tools.teams.tools import *

# Setup logging
logger = logging.getLogger(__name__)
logger.info("Microsoft Teams API tools module initialized")
