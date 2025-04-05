#!/usr/bin/env python3
"""
Salesforce API tools module for MCP toolkit.

This module provides tools for interacting with the Salesforce API.
"""
import logging
from app.tools.base.registry import register_tool

# Import service and tools
from app.tools.salesforce.service import SalesforceService
from app.tools.salesforce.tools import *

# Setup logging
logger = logging.getLogger(__name__)
logger.info("Salesforce API tools module initialized")
