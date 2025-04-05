# FRED (Federal Reserve Economic Data) Tool

## Overview
The FRED Tool provides access to economic data from the Federal Reserve Economic Data (FRED) database, maintained by the Federal Reserve Bank of St. Louis. It allows you to search for, retrieve, and analyze economic indicators and time series data.

## Features
- Search for economic data series by keywords
- Retrieve time series data for specific economic indicators
- Get detailed metadata about economic data series
- Access category information to organize economic indicators
- Support for various frequencies and unit transformations

## Configuration
This tool requires a FRED API key:
- `FRED_API_KEY`: Your FRED API subscription key

You can obtain an API key by registering at the [FRED API website](https://fred.stlouisfed.org/docs/api/api_key.html).

## Usage Examples

### Getting Series Data

```python
# Get unemployment rate data
result = await fred_get_series(
    series_id="UNRATE",  # Unemployment Rate
    observation_start="2020-01-01",
    observation_end="2023-12-31"
)
print(result)

# Get monthly inflation data with percentage change transformation
result = await fred_get_series(
    series_id="CPIAUCSL",  # Consumer Price Index for All Urban Consumers
    frequency="m",         # Monthly
    units="pch",           # Percent Change
    observation_start="2018-01-01"
)
print(result)

# Get quarterly GDP data
result = await fred_get_series(
    series_id="GDP",       # Gross Domestic Product
    frequency="q",         # Quarterly
    units="lin"            # Levels (no transformation)
)
print(result)
```

### Searching for Series

```python
# Search for inflation-related series
search_results = await fred_search(
    search_text="inflation",
    limit=5,
    order_by="popularity",
    sort_order="desc"
)
print(search_results)

# Search for employment series
search_results = await fred_search(
    search_text="employment nonfarm payroll",
    limit=10
)
print(search_results)
```

### Getting Series Information

```python
# Get detailed information about GDP series
series_info = await fred_get_series_info(series_id="GDP")
print(series_info)

# Get detailed information about unemployment rate
series_info = await fred_get_series_info(series_id="UNRATE")
print(series_info)
```

### Getting Category Information

```python
# Get the root category
root_category = await fred_get_category(category_id=0)
print(root_category)

# Get information about the "Money, Banking, & Finance" category
finance_category = await fred_get_category(category_id=32991)
print(finance_category)
```

## API Reference

### fred_get_series
Get data for a FRED series.

**Parameters:**
- `series_id`: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
- `observation_start`: Start date in YYYY-MM-DD format (optional)
- `observation_end`: End date in YYYY-MM-DD format (optional)
- `frequency`: Data frequency (optional)
  - `d`: Daily
  - `w`: Weekly
  - `m`: Monthly
  - `q`: Quarterly
  - `sa`: Semiannual
  - `a`: Annual
- `units`: Units transformation (optional)
  - `lin`: Levels (no transformation)
  - `chg`: Change
  - `ch1`: Change from Year Ago
  - `pch`: Percent Change
  - `pc1`: Percent Change from Year Ago
  - `pca`: Compounded Annual Rate of Change
  - `cch`: Continuously Compounded Rate of Change
  - `cca`: Continuously Compounded Annual Rate of Change
  - `log`: Natural Log

**Returns:**
- JSON string with time series data

### fred_search
Search for FRED series.

**Parameters:**
- `search_text`: The words to match against economic data series
- `limit`: Maximum number of results to return (default: 10)
- `order_by`: Order results by values of the specified attribute (default: 'search_rank')
  - `search_rank`: Relevance to search term
  - `series_id`: Series ID
  - `title`: Series title
  - `units`: Units
  - `frequency`: Frequency
  - `seasonal_adjustment`: Seasonal adjustment
  - `realtime_start`: Real-time start date
  - `realtime_end`: Real-time end date
  - `last_updated`: Last updated date
  - `observation_start`: Observation start date
  - `observation_end`: Observation end date
  - `popularity`: Popularity
- `sort_order`: Sort results in ascending or descending order ('asc' or 'desc', default: 'desc')

**Returns:**
- Formatted string with search results

### fred_get_series_info
Get metadata about a FRED series.

**Parameters:**
- `series_id`: The FRED series ID (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')

**Returns:**
- JSON string with series metadata

### fred_get_category
Get information about a FRED category.

**Parameters:**
- `category_id`: The FRED category ID (default: 0, which is the root category)

**Returns:**
- JSON string with category information

## Common FRED Series IDs

Here are some commonly used FRED series IDs for reference:

| Series ID | Description |
|-----------|-------------|
| GDP | Gross Domestic Product |
| GDPC1 | Real Gross Domestic Product |
| UNRATE | Unemployment Rate |
| CPIAUCSL | Consumer Price Index for All Urban Consumers |
| CPILFESL | Consumer Price Index for All Urban Consumers: All Items Less Food & Energy |
| FEDFUNDS | Federal Funds Effective Rate |
| DFF | Federal Funds Effective Rate (Daily) |
| T10Y2Y | 10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity |
| PAYEMS | All Employees, Total Nonfarm |
| INDPRO | Industrial Production Index |
| HOUST | Housing Starts: Total New Privately Owned |
| M2 | M2 Money Stock |
| DJIA | Dow Jones Industrial Average |
| SP500 | S&P 500 |

## Error Handling
The tool will return error messages if the request fails. Common errors include:
- Invalid series ID
- Invalid API key
- Rate limit exceeded
- Invalid date format
- Invalid frequency or units parameter

Example error handling:
```python
result = await fred_get_series(series_id="INVALID_ID")
if result.startswith("Error:"):
    print(f"Request failed: {result}")
else:
    data = json.loads(result)
    # Process the data
```

## Limitations
- API rate limits apply based on your FRED API subscription
- Some series might have restrictions or be unavailable
- Historical data availability varies by series
- Real-time data might have a slight delay
