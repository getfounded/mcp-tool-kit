#!/usr/bin/env python3
import os
import logging
from newsapi import NewsApiClient

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("News API tools MCP reference set")


class NewsAPIService:
    """Service to handle NewsAPI operations"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = NewsApiClient(api_key=api_key)

    def get_top_headlines(self, **kwargs):
        """Get top headlines"""
        try:
            return self.client.get_top_headlines(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def get_everything(self, **kwargs):
        """Search for news articles"""
        try:
            return self.client.get_everything(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def get_sources(self, **kwargs):
        """Get news sources"""
        try:
            return self.client.get_sources(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def format_articles(self, articles):
        """Format articles into a readable string"""
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

# Tool function definitions that will be registered with MCP


def news_top_headlines(
    country: str = None,
    category: str = None,
    sources: str = None,
    q: str = None,
    page_size: int = 5,
    page: int = 1,
    ctx: Context = None
) -> str:
    """Get top headlines from NewsAPI.

    Returns the latest headlines from sources, countries, or categories.

    Parameters:
    - country: The 2-letter ISO 3166-1 code of the country (e.g., 'us', 'gb')
    - category: The category to get headlines for (e.g., 'business', 'technology')
    - sources: Comma-separated string of source IDs
    - q: Keywords or phrases to search for
    - page_size: Number of results per page (max 100)
    - page: Page number to fetch

    Note: 'sources' cannot be mixed with 'country' or 'category' parameters.
    """
    news_api = _get_news_api_service()
    if not news_api:
        return "NewsAPI key not configured. Please set the NEWS_API_KEY environment variable."

    # Build params dict, excluding None values
    params = {}
    if country:
        params['country'] = country
    if category:
        params['category'] = category
    if sources:
        params['sources'] = sources
    if q:
        params['q'] = q
    if page_size:
        params['page_size'] = min(page_size, 100)
    if page:
        params['page'] = page

    # Get headlines
    response = news_api.get_top_headlines(**params)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format articles
    articles = response.get("articles", [])
    total_results = response.get("totalResults", 0)

    formatted = news_api.format_articles(articles)
    return f"Found {total_results} articles. Showing {len(articles)} results.\n\n{formatted}"


def news_search(
    q: str,
    sources: str = None,
    domains: str = None,
    from_param: str = None,
    to: str = None,
    language: str = "en",
    sort_by: str = "publishedAt",
    page_size: int = 5,
    page: int = 1,
    ctx: Context = None
) -> str:
    """Search for news articles using NewsAPI.

    Search through millions of articles from over 80,000 large and small news sources and blogs.

    Parameters:
    - q: Keywords or phrases to search for in the article title and body
    - sources: Comma-separated string of source IDs
    - domains: Comma-separated string of domains to restrict the search to
    - from_param: A date in ISO 8601 format (e.g., '2023-12-01') to get articles from
    - to: A date in ISO 8601 format (e.g., '2023-12-31') to get articles until
    - language: The 2-letter ISO-639-1 code of the language (default: 'en')
    - sort_by: The order to sort articles ('relevancy', 'popularity', 'publishedAt')
    - page_size: Number of results per page (max 100)
    - page: Page number to fetch
    """
    news_api = _get_news_api_service()
    if not news_api:
        return "NewsAPI key not configured. Please set the NEWS_API_KEY environment variable."

    # Build params dict, excluding None values
    params = {'q': q}
    if sources:
        params['sources'] = sources
    if domains:
        params['domains'] = domains
    if from_param:
        params['from_param'] = from_param
    if to:
        params['to'] = to
    if language:
        params['language'] = language
    if sort_by:
        params['sort_by'] = sort_by
    if page_size:
        params['page_size'] = min(page_size, 100)
    if page:
        params['page'] = page

    # Get articles
    response = news_api.get_everything(**params)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format articles
    articles = response.get("articles", [])
    total_results = response.get("totalResults", 0)

    formatted = news_api.format_articles(articles)
    return f"Found {total_results} articles. Showing {len(articles)} results.\n\n{formatted}"


def news_sources(
    category: str = None,
    language: str = None,
    country: str = None,
    ctx: Context = None
) -> str:
    """Get available news sources from NewsAPI.

    Returns the subset of news publishers that are available through NewsAPI.

    Parameters:
    - category: Find sources that display news of this category (e.g., 'business', 'technology')
    - language: Find sources that display news in a specific language (e.g., 'en', 'fr')
    - country: Find sources that display news in a specific country (e.g., 'us', 'gb')
    """
    news_api = _get_news_api_service()
    if not news_api:
        return "NewsAPI key not configured. Please set the NEWS_API_KEY environment variable."

    # Build params dict, excluding None values
    params = {}
    if category:
        params['category'] = category
    if language:
        params['language'] = language
    if country:
        params['country'] = country

    # Get sources
    response = news_api.get_sources(**params)

    if "error" in response:
        return f"Error: {response['error']}"

    # Format sources
    sources = response.get("sources", [])

    if not sources:
        return "No sources found matching the criteria."

    formatted = []
    for source in sources:
        formatted.append(f"""ID: {source.get('id', 'No ID')}
Name: {source.get('name', 'No Name')}
Description: {source.get('description', 'No Description')}
Category: {source.get('category', 'None')}
Language: {source.get('language', 'None')}
Country: {source.get('country', 'None')}
URL: {source.get('url', 'No URL')}
""")

    return f"Found {len(sources)} sources:\n\n" + "\n---\n".join(formatted)


# Tool registration and initialization
_news_api_service = None


def initialize_news_api_service(api_key=None):
    """Initialize the NewsAPI service"""
    global _news_api_service

    if api_key is None:
        api_key = os.environ.get("NEWS_API_KEY")

    if not api_key:
        logging.warning(
            "NewsAPI key not configured. Please set the NEWS_API_KEY environment variable.")
        return None

    _news_api_service = NewsAPIService(api_key=api_key)
    return _news_api_service


def _get_news_api_service():
    """Get or initialize the NewsAPI service"""
    global _news_api_service
    if _news_api_service is None:
        _news_api_service = initialize_news_api_service()
    return _news_api_service


def get_news_api_tools():
    """Get a dictionary of all NewsAPI tools for registration with MCP"""
    return {
        "news_top_headlines": news_top_headlines,
        "news_search": news_search,
        "news_sources": news_sources
    }
