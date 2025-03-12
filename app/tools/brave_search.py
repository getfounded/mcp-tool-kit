#!/usr/bin/env python3
import os
from dataclasses import dataclass
from datetime import datetime
import logging

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("Brave Search tools MCP reference set")


@dataclass
class BraveSearchService:
    """Service to handle Brave Search API calls"""
    api_key: str
    rate_limit_per_second: int = 25
    rate_limit_per_month: int = 15000

    def __post_init__(self):
        self.request_count = {
            "second": 0,
            "month": 0,
            "last_reset": datetime.now().timestamp()
        }

# Fix 1: Update the rate limit to match your subscription


@dataclass
class BraveSearchService:
    """Service to handle Brave Search API calls"""
    api_key: str
    rate_limit_per_second: int = 1  # Update to match your subscription
    rate_limit_per_month: int = 15000

    def check_rate_limit(self):
        """Check if we've hit the rate limit"""
        now = datetime.now().timestamp()
        # Fix 2: Reset counter after 1 second, not 1000
        if now - self.request_count["last_reset"] > 1:  # 1 second window
            self.request_count["second"] = 0
            self.request_count["last_reset"] = now

        if (self.request_count["second"] >= self.rate_limit_per_second or
                self.request_count["month"] >= self.rate_limit_per_month):
            raise ValueError("Rate limit exceeded")

        self.request_count["second"] += 1
        self.request_count["month"] += 1

    async def perform_web_search(self, query: str, count: int = 10, offset: int = 0) -> str:
        """Execute a web search using Brave Search API"""
        import httpx

        self.check_rate_limit()
        url = "https://api.search.brave.com/res/v1/web/search"

        params = {
            "q": query,
            "count": min(count, 20),
            "offset": offset
        }

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)

            if not response.is_success:
                return f"Brave API error: {response.status_code} {response.reason_phrase}\n{response.text}"

            data = response.json()

            # Extract web results
            results = []
            for result in data.get("web", {}).get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "description": result.get("description", ""),
                    "url": result.get("url", "")
                })

            # Format results
            formatted_results = []
            for r in results:
                formatted_results.append(
                    f"Title: {r['title']}\nDescription: {r['description']}\nURL: {r['url']}"
                )

            return "\n\n".join(formatted_results)

    async def perform_local_search(self, query: str, count: int = 5) -> str:
        """Execute a local search using Brave Search API"""
        import httpx

        self.check_rate_limit()
        url = "https://api.search.brave.com/res/v1/web/search"

        params = {
            "q": query,
            "search_lang": "en",
            "result_filter": "locations",
            "count": min(count, 20)
        }

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        async with httpx.AsyncClient() as client:
            web_response = await client.get(url, params=params, headers=headers)

            if not web_response.is_success:
                return f"Brave API error: {web_response.status_code} {web_response.reason_phrase}\n{web_response.text}"

            web_data = web_response.json()
            location_ids = []

            for location in web_data.get("locations", {}).get("results", []):
                if "id" in location:
                    location_ids.append(location["id"])

            if not location_ids:
                return await self.perform_web_search(query, count)

            # Get POI details and descriptions
            pois_data = await self._get_pois_data(location_ids, client, headers)
            descriptions_data = await self._get_descriptions_data(location_ids, client, headers)

            return self._format_local_results(pois_data, descriptions_data)

    async def _get_pois_data(self, ids, client, headers):
        """Get details for local places/businesses"""
        self.check_rate_limit()
        url = "https://api.search.brave.com/res/v1/local/pois"

        params = {}
        for id in ids:
            if id:  # Skip empty IDs
                params.setdefault("ids", []).append(id)

        response = await client.get(url, params=params, headers=headers)

        if not response.is_success:
            raise ValueError(
                f"Brave API error: {response.status_code} {response.reason_phrase}")

        return response.json()

    async def _get_descriptions_data(self, ids, client, headers):
        """Get descriptions for local places/businesses"""
        self.check_rate_limit()
        url = "https://api.search.brave.com/res/v1/local/descriptions"

        params = {}
        for id in ids:
            if id:  # Skip empty IDs
                params.setdefault("ids", []).append(id)

        response = await client.get(url, params=params, headers=headers)

        if not response.is_success:
            raise ValueError(
                f"Brave API error: {response.status_code} {response.reason_phrase}")

        return response.json()

    def _format_local_results(self, pois_data, desc_data):
        """Format local search results into a readable string"""
        results = []

        for poi in pois_data.get("results", []):
            # Extract address components
            address_parts = [
                poi.get("address", {}).get("streetAddress", ""),
                poi.get("address", {}).get("addressLocality", ""),
                poi.get("address", {}).get("addressRegion", ""),
                poi.get("address", {}).get("postalCode", "")
            ]
            address = ", ".join(
                [part for part in address_parts if part]) or "N/A"

            # Extract rating
            rating_value = poi.get("rating", {}).get("ratingValue", "N/A")
            rating_count = poi.get("rating", {}).get("ratingCount", 0)

            # Format result
            formatted_result = f"""Name: {poi.get('name', 'Unknown')}
Address: {address}
Phone: {poi.get('phone', 'N/A')}
Rating: {rating_value} ({rating_count} reviews)
Price Range: {poi.get('priceRange', 'N/A')}
Hours: {', '.join(poi.get('openingHours', [])) or 'N/A'}
Description: {desc_data.get('descriptions', {}).get(poi.get('id', ''), 'No description available')}
"""
            results.append(formatted_result)

        if not results:
            return "No local results found"

        return "\n---\n".join(results)

# Tool function definitions that will be registered with MCP


async def brave_web_search(query: str, count: int = 10, offset: int = 0, ctx: Context = None) -> str:
    """Performs a web search using the Brave Search API, ideal for general queries, news, articles, and online content.

    Use this for broad information gathering, recent events, or when you need diverse web sources.
    Supports pagination, content filtering, and freshness controls.
    Maximum 20 results per request, with offset for pagination.
    """
    brave_search = _get_brave_search_service()
    if not brave_search:
        return "Brave Search API key not configured. Please set the BRAVE_API_KEY environment variable."

    try:
        return await brave_search.perform_web_search(query, count, offset)
    except Exception as e:
        return f"Error: {str(e)}"


async def brave_local_search(query: str, count: int = 5, ctx: Context = None) -> str:
    """Searches for local businesses and places using Brave's Local Search API.

    Best for queries related to physical locations, businesses, restaurants, services, etc.
    Returns detailed information including business names, addresses, ratings, phone numbers and opening hours.
    Use this when the query implies 'near me' or mentions specific locations.
    Automatically falls back to web search if no local results are found.
    """
    brave_search = _get_brave_search_service()
    if not brave_search:
        return "Brave Search API key not configured. Please set the BRAVE_API_KEY environment variable."

    try:
        return await brave_search.perform_local_search(query, count)
    except Exception as e:
        return f"Error: {str(e)}"

# Tool registration and initialization
_brave_search_service = None


def initialize_brave_search(api_key=None):
    """Initialize the Brave Search service"""
    global _brave_search_service

    if api_key is None:
        api_key = os.environ.get("BRAVE_API_KEY")

    if not api_key:
        logging.warning(
            "Brave Search API key not configured. Please set the BRAVE_API_KEY environment variable.")
        return None

    _brave_search_service = BraveSearchService(api_key=api_key)
    return _brave_search_service


def _get_brave_search_service():
    """Get or initialize the Brave Search service"""
    global _brave_search_service
    if _brave_search_service is None:
        _brave_search_service = initialize_brave_search()
    return _brave_search_service


def get_brave_search_tools():
    """Get a dictionary of all Brave Search tools for registration with MCP"""
    return {
        "brave_web_search": brave_web_search,
        "brave_local_search": brave_local_search
    }
