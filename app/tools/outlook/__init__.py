#!/usr/bin/env python3
"""
Outlook API tools module for MCP toolkit.

This module provides tools for interacting with Microsoft Outlook via the Microsoft Graph API.
"""
import logging
from app.tools.base.registry import register_tool

# Import service and tools
from app.tools.outlook.service import OutlookService
from app.tools.outlook.tools import *

# Setup logging
logger = logging.getLogger(__name__)
logger.info("Outlook API tools module initialized")
