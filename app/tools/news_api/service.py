#!/usr/bin/env python3
"""
Service implementation for NewsAPI.
"""
import logging
from typing import Dict, List, Any, Optional, Union

from app.tools.base.service import ToolServiceBase


class NewsAPIService(ToolServiceBase):
    """Service to handle NewsAPI operations"""

    def __init__(self, api_key=None):
        """
        Initialize the NewsAPI service.

        Args:
            api_key: Optional API key (will use environment variable if not provided)
        """
        super().__init__()
        self.api_key = api_key or self.get_env_var("NEWS_API_KEY")
        self.client = None

    def initialize(self) -> bool:
        """
        Initialize the NewsAPI client.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            from newsapi import NewsApiClient
            self.client = NewsApiClient(api_key=self.api_key)
            self.initialized = True
            self.logger.info("NewsAPI client initialized successfully")
            return True
        except ImportError:
            self.logger.error(
                "newsapi-python module not installed. Please install it with 'pip install newsapi-python'")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize NewsAPI client: {str(e)}")
            return False

    def get_top_headlines(self, **kwargs):
        """
        Get top headlines.

        Args:
            **kwargs: Parameters for the NewsAPI get_top_headlines method

        Returns:
            Dictionary with headline data
        """
        try:
            self._is_initialized()
            # Apply rate limiting if configured
            # Default: 100 requests per day
            self.apply_rate_limit("newsapi", 100, 86400, wait=True)
            return self.client.get_top_headlines(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def get_everything(self, **kwargs):
        """
        Search for news articles.

        Args:
            **kwargs: Parameters for the NewsAPI get_everything method

        Returns:
            Dictionary with article data
        """
        try:
            self._is_initialized()
            # Apply rate limiting if configured
            # Default: 100 requests per day
            self.apply_rate_limit("newsapi", 100, 86400, wait=True)
            return self.client.get_everything(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def get_sources(self, **kwargs):
        """
        Get news sources.

        Args:
            **kwargs: Parameters for the NewsAPI get_sources method

        Returns:
            Dictionary with source data
        """
        try:
            self._is_initialized()
            # Apply rate limiting if configured
            # Default: 100 requests per day
            self.apply_rate_limit("newsapi", 100, 86400, wait=True)
            return self.client.get_sources(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def format_articles(self, articles):
        """
        Format articles into a readable string.

        Args:
            articles: List of article dictionaries

        Returns:
            Formatted string representation of articles
        """
        if not articles or len(articles) == 0:
            return "No articles found."

        formatted = []
        for article in articles:
            source = article.get("source", {}).get("name", "Unknown Source")
            title = article.get("title", "No Title")
            description = article.get("description", "No Description")
            url = article.get("url", "")
            published_at = article.get("publishedAt", "")

            formatted.append(f"""Source: {source}
Title: {title}
Published: {published_at}
Description: {description}
URL: {url}
""")

        return "\n---\n".join(formatted)


# Singleton instance
_service_instance = None


def get_service() -> NewsAPIService:
    """
    Get or initialize the NewsAPI service singleton.

    Returns:
        NewsAPIService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = NewsAPIService()
        _service_instance.initialize()
    return _service_instance
