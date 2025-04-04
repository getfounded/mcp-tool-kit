#!/usr/bin/env python3
"""
Tool functions for Brave Search API.
"""
from typing import Dict, Any, Optional
from mcp.server.fastmcp import Context

from app.tools.base.registry import register_tool
from app.tools.brave_search.service import get_service

@register_tool(category="search")
async def brave_web_search(
    query: str, 
    count: int = 10, 
    offset: int = 0, 
    ctx: Context = None
) -> str:
    """Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content.

    Use this for broad information gathering, recent events, or when you need diverse web sources.
    Supports pagination, content filtering, and freshness controls.
    Maximum 20 results per request, with offset for pagination.
    """
    brave_search = get_service()

    try:
        return await brave_search.perform_web_search(query, count, offset)
    except Exception as e:
        return f"Error: {str(e)}"


@register_tool(category="search")
async def brave_local_search(
    query: str, 
    count: int = 5, 
    ctx: Context = None
) -> str:
    """Searches for local businesses and places using Brave's Local Search API.

    Best for queries related to physical locations, businesses, restaurants, services, etc.
    Returns detailed information including business names, addresses, ratings, phone numbers and opening hours.
    Use this when the query implies 'near me' or mentions specific locations.
    Automatically falls back to web search if no local results are found.
    """
    brave_search = get_service()

    try:
        return await brave_search.perform_local_search(query, count)
    except Exception as e:
        return f"Error: {str(e)}"