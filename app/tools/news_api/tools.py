#!/usr/bin/env python3
"""
Tool functions for NewsAPI.
"""
import json
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.news_api.service import get_service


@register_tool(category="news")
async def news_top_headlines(
    country: Optional[str] = None,
    category: Optional[str] = None,
    sources: Optional[str] = None,
    q: Optional[str] = None,
    page_size: int = 5,
    page: int = 1,
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
    news_api = get_service()
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


@register_tool(category="news")
async def news_search(
    q: str,
    sources: Optional[str] = None,
    domains: Optional[str] = None,
    from_param: Optional[str] = None,
    to: Optional[str] = None,
    language: str = "en",
    sort_by: str = "publishedAt",
    page_size: int = 5,
    page: int = 1,
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
    news_api = get_service()
    if not news_api:
        return "NewsAPI key not configured. Please set the NEWS_API_KEY environment variable."

    # Build params dict, excluding None values
    params = {'q': q}
    if sources:
        params['sources'] = sources
    if domains:
        params['domains'] = domains
    if from_param:
        params['from'] = from_param
    if to:
        params['to'] = to
    if language:
        params['language'] = language
    if sort_by:
        params['sortBy'] = sort_by
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


@register_tool(category="news")
async def news_sources(
    category: Optional[str] = None,
    language: Optional[str] = None,
    country: Optional[str] = None,
) -> str:
    """Get available news sources from NewsAPI.

    Returns the subset of news publishers that are available through NewsAPI.

    Parameters:
    - category: Find sources that display news of this category (e.g., 'business', 'technology')
    - language: Find sources that display news in a specific language (e.g., 'en', 'fr')
    - country: Find sources that display news in a specific country (e.g., 'us', 'gb')
    """
    news_api = get_service()
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
