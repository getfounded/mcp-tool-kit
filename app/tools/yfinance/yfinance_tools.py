#!/usr/bin/env python3
"""
YFinance tools implementation using the decorator pattern.
"""
from typing import Dict, List, Any, Optional, Union

from app.tools.base.registry import register_tool
from app.tools.yfinance.yfinance_service import YFinanceService

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get basic information about a stock ticker symbol"
)
def yfinance_get_ticker_info(self, ticker_symbol: str) -> Dict[str, Any]:
    """
    Get basic information about a ticker symbol.

    Retrieves basic information such as company name, sector, industry, and financial data.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
        Dictionary containing the ticker's basic information
    """
    return self.get_ticker_info(ticker_symbol)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get historical price data for a stock ticker symbol"
)
def yfinance_get_historical_data(
    self,
    ticker_symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get historical market data for a ticker symbol.

    Retrieves historical price data including open, high, low, close, volume, etc.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
        period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date string (YYYY-MM-DD) - if provided with end, overrides period
        end: End date string (YYYY-MM-DD) - if provided with start, overrides period

    Returns:
        Dictionary containing historical price data
    """
    return self.get_historical_data(ticker_symbol, period, interval, start, end)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get income statement data for a stock ticker symbol"
)
def yfinance_get_financials(
    self,
    ticker_symbol: str,
    quarterly: bool = False
) -> Dict[str, Any]:
    """
    Get income statement data for a ticker symbol.

    Retrieves financial statement data for the specified ticker.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
        quarterly: If True, get quarterly data instead of annual

    Returns:
        Dictionary containing financial data
    """
    return self.get_financials(ticker_symbol, quarterly)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get balance sheet data for a stock ticker symbol"
)
def yfinance_get_balance_sheet(
    self,
    ticker_symbol: str,
    quarterly: bool = False
) -> Dict[str, Any]:
    """
    Get balance sheet data for a ticker symbol.

    Retrieves balance sheet data including assets, liabilities, and equity.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
        quarterly: If True, get quarterly data instead of annual

    Returns:
        Dictionary containing balance sheet data
    """
    return self.get_balance_sheet(ticker_symbol, quarterly)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get cash flow data for a stock ticker symbol"
)
def yfinance_get_cashflow(
    self,
    ticker_symbol: str,
    quarterly: bool = False
) -> Dict[str, Any]:
    """
    Get cash flow data for a ticker symbol.

    Retrieves cash flow statement data including operating, investing, and financing activities.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
        quarterly: If True, get quarterly data instead of annual

    Returns:
        Dictionary containing cash flow data
    """
    return self.get_cashflow(ticker_symbol, quarterly)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get earnings data for a stock ticker symbol"
)
def yfinance_get_earnings(
    self,
    ticker_symbol: str,
    quarterly: bool = False
) -> Dict[str, Any]:
    """
    Get earnings data for a ticker symbol.

    Retrieves earnings data including revenue, earnings per share, etc.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
        quarterly: If True, get quarterly data instead of annual

    Returns:
        Dictionary containing earnings data
    """
    return self.get_earnings(ticker_symbol, quarterly)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get major shareholders for a stock ticker symbol"
)
def yfinance_get_major_holders(
    self,
    ticker_symbol: str
) -> Dict[str, Any]:
    """
    Get major shareholders for a ticker symbol.

    Retrieves information about major shareholders including percentage ownership.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
        Dictionary containing major shareholders data
    """
    return self.get_major_holders(ticker_symbol)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get institutional shareholders for a stock ticker symbol"
)
def yfinance_get_institutional_holders(
    self,
    ticker_symbol: str
) -> Dict[str, Any]:
    """
    Get institutional shareholders for a ticker symbol.

    Retrieves information about institutional shareholders including funds and their holdings.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
        Dictionary containing institutional shareholders data
    """
    return self.get_institutional_holders(ticker_symbol)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get analyst recommendations for a stock ticker symbol"
)
def yfinance_get_recommendations(
    self,
    ticker_symbol: str
) -> Dict[str, Any]:
    """
    Get analyst recommendations for a ticker symbol.

    Retrieves analyst ratings and recommendations for the specified ticker.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
        Dictionary containing analyst recommendations
    """
    return self.get_recommendations(ticker_symbol)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get earnings calendar for a stock ticker symbol"
)
def yfinance_get_calendar(
    self,
    ticker_symbol: str
) -> Dict[str, Any]:
    """
    Get earnings calendar for a ticker symbol.

    Retrieves upcoming earnings dates and related information.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
        Dictionary containing earnings calendar data
    """
    return self.get_calendar(ticker_symbol)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get options chain data for a stock ticker symbol"
)
def yfinance_get_options(
    self,
    ticker_symbol: str,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get options chain data for a ticker symbol.

    Retrieves options data including calls and puts for specified expiration date.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
        date: Options expiration date (format: YYYY-MM-DD). If none, uses first available date.

    Returns:
        Dictionary containing options chain data
    """
    return self.get_options(ticker_symbol, date)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Get recent news about a stock ticker symbol"
)
def yfinance_get_news(
    self,
    ticker_symbol: str
) -> Dict[str, Any]:
    """
    Get recent news about a ticker symbol.

    Retrieves recent news articles related to the specified ticker.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
        Dictionary containing news articles
    """
    return self.get_news(ticker_symbol)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Search for ticker symbols matching a query"
)
def yfinance_search_ticker(
    self,
    query: str
) -> Dict[str, Any]:
    """
    Search for ticker symbols matching a query.

    Attempts to find ticker symbols that match the provided search query.

    Args:
        query: Search query string

    Returns:
        Dictionary containing search results
    """
    return self.search_ticker(query)

@register_tool(
    category="market_data",
    service_class=YFinanceService,
    description="Download historical market data for multiple tickers"
)
def yfinance_download_data(
    self,
    tickers: Union[str, List[str]],
    period: str = "1mo",
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
    group_by: str = "ticker",
    threads: bool = True
) -> Dict[str, Any]:
    """
    Download historical market data for multiple tickers.

    Retrieves historical price data for one or more ticker symbols.

    Args:
        tickers: Single ticker string or list of ticker symbols
        period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        start: Start date string (YYYY-MM-DD) - if provided with end, overrides period
        end: End date string (YYYY-MM-DD) - if provided with start, overrides period
        group_by: How to group the data ('ticker' or 'column')
        threads: Whether to use multi-threading for faster downloads

    Returns:
        Dictionary containing downloaded data
    """
    return self.download_data(tickers, period, interval, start, end, group_by, threads)
