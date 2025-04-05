# Brave Search Tool

## Overview
The Brave Search tool provides integration with the Brave Search API, allowing you to perform web searches and local business searches directly from your applications.

## Features
- Web search for general online content
- Local business search for location-based queries
- Pagination support for managing large result sets
- Configurable result count
- Automatic fallback from local to web search when needed

## Configuration
This tool requires a Brave Search API key:
- `BRAVE_API_KEY`: Your Brave Search API subscription key

You can obtain an API key by subscribing to the Brave Search API service.

## Usage Examples

### Web Search
```python
# Perform a basic web search
result = await brave_web_search(query="climate change solutions")

# Get more results
result = await brave_web_search(
    query="climate change solutions",
    count=20  # Maximum 20 results per request
)

# Paginate through results
result = await brave_web_search(
    query="climate change solutions",
    count=10,
    offset=10  # Skip the first 10 results
)
```

### Local Business Search
```python
# Search for local businesses
result = await brave_local_search(query="coffee shops near me")

# Control the number of results
result = await brave_local_search(
    query="restaurants downtown",
    count=10
)
```

## API Reference

### brave_web_search
Performs a web search using the Brave Search API.

**Parameters:**
- `query`: Search query string
- `count`: Number of results to return (default: 10, max: 20)
- `offset`: Number of results to skip for pagination (default: 0)

**Returns:**
- Formatted search results with titles, descriptions, and URLs

### brave_local_search
Searches for local businesses and places using the Brave Search API.

**Parameters:**
- `query`: Search query string
- `count`: Number of results to return (default: 5)

**Returns:**
- Formatted search results with business names, addresses, ratings, phone numbers, hours, and descriptions

## Error Handling
Both search functions will return an error message if the search fails, which includes:
- API key validation issues
- Rate limiting errors
- Network connectivity problems
- Invalid query parameters

Example error handling:
```python
result = await brave_web_search("my search query")
if result.startswith("Error:"):
    print(f"Search failed: {result}")
else:
    print("Search succeeded!")
    print(result)
```

## Limitations
- Maximum 20 results per web search request
- Rate limits apply based on your Brave Search API subscription
- Local search is optimized for location-based queries and may not work well for general informational queries
