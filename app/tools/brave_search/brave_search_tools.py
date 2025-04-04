#!/usr/bin/env python3
"""
Brave Search tools implementation using the decorator pattern.
"""
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.brave_search.brave_search_service import BraveSearchService

@register_tool(
    category="search",
    service_class=BraveSearchService,
    description="Search the web for general information, news, articles, and online content"
)
async def brave_web_search(
    self,
    query: str,
    count: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Performs a web search using the Brave Search API.

    Ideal for general queries, news, articles, and online content.
    Use this for broad information gathering, recent events, or when you need diverse web sources.
    Supports pagination, content filtering, and freshness controls.
    Maximum 20 results per request, with offset for pagination.

    Args:
        query: Search query string
        count: Number of results to return (max 20)
        offset: Offset for pagination

    Returns:
        Dictionary with search results
    """
    return await self.perform_web_search(query, count, offset)

@register_tool(
    category="search",
    service_class=BraveSearchService,
    description="Search for local businesses and places by location"
)
async def brave_local_search(
    self,
    query: str,
    count: int = 5
) -> Dict[str, Any]:
    """
    Searches for local businesses and places using Brave's Local Search API.

    Best for queries related to physical locations, businesses, restaurants, services, etc.
    Returns detailed information including business names, addresses, ratings, phone numbers and opening hours.
    Use this when the query implies 'near me' or mentions specific locations.
    Automatically falls back to web search if no local results are found.

    Args:
        query: Search query string
        count: Number of results to return (max 20)

    Returns:
        Dictionary with local search results
    """
    return await self.perform_local_search(query, count)
