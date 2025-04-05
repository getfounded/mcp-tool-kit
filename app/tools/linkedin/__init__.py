#!/usr/bin/env python3
"""
LinkedIn API tools module for MCP toolkit.

This module provides tools for interacting with the LinkedIn API.
"""
import logging
from app.tools.base.registry import register_tool

# Import service and tools
from app.tools.linkedin.service import LinkedInService
from app.tools.linkedin.tools import *

# Setup logging
logger = logging.getLogger(__name__)
logger.info("LinkedIn API tools module initialized")
