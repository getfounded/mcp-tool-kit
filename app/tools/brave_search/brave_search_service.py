#!/usr/bin/env python3
"""
Brave Search API service for web and local search functionality.
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase

class BraveSearchService(ToolServiceBase):
    """Service to handle Brave Search API calls with rate limiting"""
    
    def __init__(self):
        """Initialize the Brave Search service"""
        super().__init__()
        self.api_key = None
        self.rate_limit_per_second = 1  # Default rate limits
        self.rate_limit_per_month = 15000
        self.request_count = {
            "second": 0,
            "month": 0,
            "last_reset": datetime.now().timestamp()
        }
    
    def initialize(self) -> bool:
        """
        Initialize the Brave Search service with API key.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        # Get API key from environment
        self.api_key = self.get_env_var("BRAVE_API_KEY", required=True)
        
        # Get optional rate limit configuration from environment
        self.rate_limit_per_second = int(self.get_env_var("BRAVE_RATE_LIMIT_SECOND", default="1"))
        self.rate_limit_per_month = int(self.get_env_var("BRAVE_RATE_LIMIT_MONTH", default="15000"))
        
        # Create rate limiter for requests
        self.create_rate_limiter("brave_search_api", calls=self.rate_limit_per_second, period=1.0)
        
        self.logger.info(f"Brave Search service initialized with rate limit: {self.rate_limit_per_second} calls per second, {self.rate_limit_per_month} calls per month")
        self.initialized = True
        return True
    
    def check_rate_limit(self) -> None:
        """
        Check if we've hit the rate limit.
        
        Raises:
            ValueError: If rate limit is exceeded
        """
        self._is_initialized()
        
        # Apply rate limiting
        self.apply_rate_limit("brave_search_api", self.rate_limit_per_second, 1.0)
        
        # Check monthly limit
        now = datetime.now().timestamp()
        # Reset counter after 1 second
        if now - self.request_count["last_reset"] > 1:  # 1 second window
            self.request_count["second"] = 0
            self.request_count["last_reset"] = now
        
        if self.request_count["month"] >= self.rate_limit_per_month:
            raise ValueError("Monthly rate limit exceeded")
        
        self.request_count["second"] += 1
        self.request_count["month"] += 1
    
    async def perform_web_search(self, query: str, count: int = 10, offset: int = 0) -> Union[List[Dict[str, str]], str]:
        """
        Execute a web search using Brave Search API.
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            offset: Offset for pagination
            
        Returns:
            List of search results or error message
        """
        self._is_initialized()
        
        try:
            # Check rate limit
            self.check_rate_limit()
            
            # Import httpx for async requests
            import httpx
            
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
                    error_message = f"Brave API error: {response.status_code} {response.reason_phrase}\n{response.text}"
                    self.logger.error(error_message)
                    return error_message
                
                data = response.json()
                
                # Extract web results
                results = []
                for result in data.get("web", {}).get("results", []):
                    results.append({
                        "title": result.get("title", ""),
                        "description": result.get("description", ""),
                        "url": result.get("url", ""),
                        "age": result.get("age", ""),
                        "source": result.get("source", ""),
                        "index": len(results)  # Add index for citation reference
                    })
                
                return {
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "has_more": data.get("web", {}).get("more", False)
                }
                
        except Exception as e:
            self.logger.error(f"Error in web search: {e}")
            return f"Error in web search: {str(e)}"
    
    async def perform_local_search(self, query: str, count: int = 5) -> Union[Dict[str, Any], str]:
        """
        Execute a local search using Brave Search API.
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            
        Returns:
            Dictionary with local search results or error message
        """
        self._is_initialized()
        
        try:
            # Check rate limit
            self.check_rate_limit()
            
            # Import httpx for async requests
            import httpx
            
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
                    error_message = f"Brave API error: {web_response.status_code} {web_response.reason_phrase}\n{web_response.text}"
                    self.logger.error(error_message)
                    return error_message
                
                web_data = web_response.json()
                location_ids = []
                
                for location in web_data.get("locations", {}).get("results", []):
                    if "id" in location:
                        location_ids.append(location["id"])
                
                if not location_ids:
                    # Fall back to web search if no local results
                    self.logger.info("No local results found, falling back to web search")
                    return await self.perform_web_search(query, count)
                
                # Get POI details and descriptions
                try:
                    pois_data = await self._get_pois_data(location_ids, client, headers)
                    descriptions_data = await self._get_descriptions_data(location_ids, client, headers)
                    
                    # Format the results
                    formatted_results = self._format_local_results(pois_data, descriptions_data)
                    
                    return {
                        "query": query,
                        "results": formatted_results,
                        "count": len(formatted_results)
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error processing local search results: {e}")
                    # Fall back to web search if processing fails
                    return await self.perform_web_search(query, count)
                
        except Exception as e:
            self.logger.error(f"Error in local search: {e}")
            return f"Error in local search: {str(e)}"
    
    async def _get_pois_data(self, ids: List[str], client: Any, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Get details for local places/businesses.
        
        Args:
            ids: List of location IDs
            client: HTTPX client instance
            headers: API request headers
            
        Returns:
            Dictionary with POI data
            
        Raises:
            ValueError: If API request fails
        """
        # Check rate limit
        self.check_rate_limit()
        
        url = "https://api.search.brave.com/res/v1/local/pois"
        
        params = {}
        for id in ids:
            if id:  # Skip empty IDs
                params.setdefault("ids", []).append(id)
        
        response = await client.get(url, params=params, headers=headers)
        
        if not response.is_success:
            error = f"Brave API error: {response.status_code} {response.reason_phrase}"
            self.logger.error(error)
            raise ValueError(error)
        
        return response.json()
    
    async def _get_descriptions_data(self, ids: List[str], client: Any, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Get descriptions for local places/businesses.
        
        Args:
            ids: List of location IDs
            client: HTTPX client instance
            headers: API request headers
            
        Returns:
            Dictionary with description data
            
        Raises:
            ValueError: If API request fails
        """
        # Check rate limit
        self.check_rate_limit()
        
        url = "https://api.search.brave.com/res/v1/local/descriptions"
        
        params = {}
        for id in ids:
            if id:  # Skip empty IDs
                params.setdefault("ids", []).append(id)
        
        response = await client.get(url, params=params, headers=headers)
        
        if not response.is_success:
            error = f"Brave API error: {response.status_code} {response.reason_phrase}"
            self.logger.error(error)
            raise ValueError(error)
        
        return response.json()
    
    def _format_local_results(self, pois_data: Dict[str, Any], desc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format local search results.
        
        Args:
            pois_data: Points of interest data
            desc_data: Description data
            
        Returns:
            List of formatted business listings
        """
        results = []
        
        for i, poi in enumerate(pois_data.get("results", [])):
            # Extract address components
            address_parts = [
                poi.get("address", {}).get("streetAddress", ""),
                poi.get("address", {}).get("addressLocality", ""),
                poi.get("address", {}).get("addressRegion", ""),
                poi.get("address", {}).get("postalCode", "")
            ]
            address = ", ".join([part for part in address_parts if part]) or "N/A"
            
            # Extract rating
            rating_value = poi.get("rating", {}).get("ratingValue", "N/A")
            rating_count = poi.get("rating", {}).get("ratingCount", 0)
            
            # Get description
            description = desc_data.get("descriptions", {}).get(poi.get("id", ""), "No description available")
            
            # Format result as structured data
            formatted_result = {
                "name": poi.get("name", "Unknown"),
                "address": address,
                "phone": poi.get("phone", "N/A"),
                "rating": f"{rating_value} ({rating_count} reviews)" if rating_value != "N/A" else "N/A",
                "price_range": poi.get("priceRange", "N/A"),
                "hours": ", ".join(poi.get("openingHours", [])) or "N/A",
                "description": description,
                "index": i  # Add index for reference
            }
            
            results.append(formatted_result)
        
        return results
