#!/usr/bin/env python3
"""
Service implementation for Brave Search API.
"""
import os
from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase

@dataclass
class BraveSearchService(ToolServiceBase):
    """Service to handle Brave Search API calls"""
    
    api_key: Optional[str] = None
    rate_limit_per_second: int = 1  # Updated to match subscription
    rate_limit_per_month: int = 15000
    
    # Initialize request_count as a field with a default factory
    request_count: dict = field(default_factory=lambda: {
        "second": 0,
        "month": 0,
        "last_reset": datetime.now().timestamp()
    })
    
    def __post_init__(self):
        """Post-initialization setup"""
        super().__init__()
        if not self.api_key:
            self.api_key = self.get_env_var("BRAVE_API_KEY")
    
    def initialize(self) -> bool:
        """
        Initialize the Brave Search service.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            import httpx  # Test if httpx is installed
            
            if not self.api_key:
                self.logger.error("Brave Search API key is not configured")
                return False
                
            self.initialized = True
            self.logger.info("Brave Search service initialized successfully")
            return True
        except ImportError:
            self.logger.error("httpx library not installed. Please install with 'pip install httpx'")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Brave Search service: {str(e)}")
            return False

    def check_rate_limit(self):
        """
        Check if we've hit the rate limit.
        
        Raises:
            ValueError: If rate limit has been exceeded
        """
        now = datetime.now().timestamp()
        # Reset counter after 1 second
        if now - self.request_count["last_reset"] > 1:  # 1 second window
            self.request_count["second"] = 0
            self.request_count["last_reset"] = now

        if (self.request_count["second"] >= self.rate_limit_per_second or
                self.request_count["month"] >= self.rate_limit_per_month):
            raise ValueError("Rate limit exceeded")

        self.request_count["second"] += 1
        self.request_count["month"] += 1

    async def perform_web_search(self, query: str, count: int = 10, offset: int = 0) -> str:
        """
        Execute a web search using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return
            offset: Offset for pagination
            
        Returns:
            Formatted search results
        """
        self._is_initialized()
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
        """
        Execute a local search using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            Formatted search results for local businesses
        """
        self._is_initialized()
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


# Singleton instance
_service_instance = None

def get_service() -> BraveSearchService:
    """
    Get or initialize the Brave Search service singleton.
    
    Returns:
        BraveSearchService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = BraveSearchService()
        _service_instance.initialize()
    return _service_instance