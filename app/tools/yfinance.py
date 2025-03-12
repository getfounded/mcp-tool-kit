#!/usr/bin/env python3
import os
import json
import logging
import pandas as pd
import numpy as np
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta

# Ensure compatibility with mcp server
from mcp.server.fastmcp import FastMCP, Context

# External MCP reference for tool registration
external_mcp = None


def set_external_mcp(mcp):
    """Set the external MCP reference for tool registration"""
    global external_mcp
    external_mcp = mcp
    logging.info("YFinance tools MCP reference set")


class YFinanceTools(str, Enum):
    """Enum of YFinance tool names"""
    GET_TICKER_INFO = "yfinance_get_ticker_info"
    GET_HISTORICAL_DATA = "yfinance_get_historical_data"
    GET_FINANCIALS = "yfinance_get_financials"
    GET_BALANCE_SHEET = "yfinance_get_balance_sheet"
    GET_CASHFLOW = "yfinance_get_cashflow"
    GET_EARNINGS = "yfinance_get_earnings"
    GET_MAJOR_HOLDERS = "yfinance_get_major_holders"
    GET_INSTITUTIONAL_HOLDERS = "yfinance_get_institutional_holders"
    GET_RECOMMENDATIONS = "yfinance_get_recommendations"
    GET_CALENDAR = "yfinance_get_calendar"
    GET_OPTIONS = "yfinance_get_options"
    GET_NEWS = "yfinance_get_news"
    SEARCH_TICKER = "yfinance_search_ticker"
    DOWNLOAD_DATA = "yfinance_download_data"


class YFinanceService:
    """Service to handle YFinance operations"""

    def __init__(self):
        """Initialize the YFinance service"""
        try:
            import yfinance as yf
            self.yf = yf
            self.initialized = True
        except ImportError:
            logging.error(
                "yfinance library not installed. Please install with 'pip install yfinance'")
            self.initialized = False
            self.yf = None

    def _is_initialized(self):
        """Check if the service is properly initialized"""
        if not self.initialized:
            raise ValueError(
                "YFinance service not properly initialized. Check if yfinance library is installed.")
        return True

    def _sanitize_data(self, data):
        """Convert data to JSON-serializable format"""
        if isinstance(data, pd.DataFrame):
            # Reset index if it's a date or complex object
            if not isinstance(data.index, pd.RangeIndex):
                data = data.reset_index()

            # Handle NaN values
            return json.loads(data.replace({np.nan: None}).to_json(orient='records', date_format='iso'))

        elif isinstance(data, pd.Series):
            return json.loads(data.replace({np.nan: None}).to_json())

        elif isinstance(data, dict):
            # Recursively convert each value
            return {k: self._sanitize_data(v) for k, v in data.items()}

        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]

        elif isinstance(data, (np.integer, np.floating)):
            return int(data) if isinstance(data, np.integer) else float(data)

        elif isinstance(data, (datetime, np.datetime64)):
            return data.isoformat()

        elif pd.isna(data):
            return None

        return data

    async def get_ticker_info(self, ticker_symbol):
        """Get basic information about a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)
            info = ticker.info

            # Clean up data for JSON serialization
            cleaned_info = self._sanitize_data(info)

            return {
                "symbol": ticker_symbol,
                "info": cleaned_info
            }
        except Exception as e:
            return {"error": f"Error retrieving ticker info: {str(e)}"}

    async def get_historical_data(self, ticker_symbol, period="1mo", interval="1d", start=None, end=None):
        """Get historical market data for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            # If start and end dates are provided, use them instead of period
            if start and end:
                history = ticker.history(
                    start=start, end=end, interval=interval)
            else:
                history = ticker.history(period=period, interval=interval)

            # Clean up data for JSON serialization
            cleaned_history = self._sanitize_data(history)

            return {
                "symbol": ticker_symbol,
                "period": period if not (start and end) else f"{start} to {end}",
                "interval": interval,
                "data": cleaned_history
            }
        except Exception as e:
            return {"error": f"Error retrieving historical data: {str(e)}"}

    async def get_financials(self, ticker_symbol, quarterly=False):
        """Get income statement data for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                financials = ticker.quarterly_financials
            else:
                financials = ticker.financials

            # Clean up data for JSON serialization
            cleaned_financials = self._sanitize_data(financials)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "financials": cleaned_financials
            }
        except Exception as e:
            return {"error": f"Error retrieving financials: {str(e)}"}

    async def get_balance_sheet(self, ticker_symbol, quarterly=False):
        """Get balance sheet data for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                balance_sheet = ticker.quarterly_balance_sheet
            else:
                balance_sheet = ticker.balance_sheet

            # Clean up data for JSON serialization
            cleaned_balance_sheet = self._sanitize_data(balance_sheet)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "balance_sheet": cleaned_balance_sheet
            }
        except Exception as e:
            return {"error": f"Error retrieving balance sheet: {str(e)}"}

    async def get_cashflow(self, ticker_symbol, quarterly=False):
        """Get cash flow data for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                cashflow = ticker.quarterly_cashflow
            else:
                cashflow = ticker.cashflow

            # Clean up data for JSON serialization
            cleaned_cashflow = self._sanitize_data(cashflow)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "cashflow": cleaned_cashflow
            }
        except Exception as e:
            return {"error": f"Error retrieving cashflow: {str(e)}"}

    async def get_earnings(self, ticker_symbol, quarterly=False):
        """Get earnings data for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            if quarterly:
                earnings = ticker.quarterly_earnings
            else:
                earnings = ticker.earnings

            # Clean up data for JSON serialization
            cleaned_earnings = self._sanitize_data(earnings)

            return {
                "symbol": ticker_symbol,
                "period": "quarterly" if quarterly else "annual",
                "earnings": cleaned_earnings
            }
        except Exception as e:
            return {"error": f"Error retrieving earnings: {str(e)}"}

    async def get_major_holders(self, ticker_symbol):
        """Get major shareholders for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)
            major_holders = ticker.major_holders

            # Clean up data for JSON serialization
            cleaned_holders = self._sanitize_data(major_holders)

            return {
                "symbol": ticker_symbol,
                "major_holders": cleaned_holders
            }
        except Exception as e:
            return {"error": f"Error retrieving major holders: {str(e)}"}

    async def get_institutional_holders(self, ticker_symbol):
        """Get institutional shareholders for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)
            institutional_holders = ticker.institutional_holders

            # Clean up data for JSON serialization
            cleaned_holders = self._sanitize_data(institutional_holders)

            return {
                "symbol": ticker_symbol,
                "institutional_holders": cleaned_holders
            }
        except Exception as e:
            return {"error": f"Error retrieving institutional holders: {str(e)}"}

    async def get_recommendations(self, ticker_symbol):
        """Get analyst recommendations for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)
            recommendations = ticker.recommendations

            # Clean up data for JSON serialization
            cleaned_recommendations = self._sanitize_data(recommendations)

            return {
                "symbol": ticker_symbol,
                "recommendations": cleaned_recommendations
            }
        except Exception as e:
            return {"error": f"Error retrieving recommendations: {str(e)}"}

    async def get_calendar(self, ticker_symbol):
        """Get earnings calendar for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)
            calendar = ticker.calendar

            # Clean up data for JSON serialization
            cleaned_calendar = self._sanitize_data(calendar)

            return {
                "symbol": ticker_symbol,
                "calendar": cleaned_calendar
            }
        except Exception as e:
            return {"error": f"Error retrieving calendar: {str(e)}"}

    async def get_options(self, ticker_symbol, date=None):
        """Get options chain data for a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            # Get available expiration dates if no date specified
            expiration_dates = ticker.options

            if not expiration_dates:
                return {
                    "symbol": ticker_symbol,
                    "error": "No options data available for this ticker"
                }

            # Use the first available date if none specified
            selected_date = date if date and date in expiration_dates else expiration_dates[
                0]

            # Get options chain for the selected date
            calls = ticker.option_chain(selected_date).calls
            puts = ticker.option_chain(selected_date).puts

            # Clean up data for JSON serialization
            cleaned_calls = self._sanitize_data(calls)
            cleaned_puts = self._sanitize_data(puts)

            return {
                "symbol": ticker_symbol,
                "expiration_date": selected_date,
                "available_dates": expiration_dates,
                "calls": cleaned_calls,
                "puts": cleaned_puts
            }
        except Exception as e:
            return {"error": f"Error retrieving options data: {str(e)}"}

    async def get_news(self, ticker_symbol):
        """Get recent news about a ticker"""
        try:
            self._is_initialized()

            ticker = self.yf.Ticker(ticker_symbol)

            # Some versions of yfinance have news, others don't
            if hasattr(ticker, 'news'):
                news = ticker.news

                # Clean up data for JSON serialization
                cleaned_news = self._sanitize_data(news)

                return {
                    "symbol": ticker_symbol,
                    "news": cleaned_news
                }
            else:
                return {
                    "symbol": ticker_symbol,
                    "error": "News not available in this version of yfinance"
                }
        except Exception as e:
            return {"error": f"Error retrieving news: {str(e)}"}

    async def search_ticker(self, query):
        """Search for ticker symbols matching a query"""
        try:
            self._is_initialized()

            # yfinance doesn't have a built-in search function, but we can use Ticker to get summary
            # This is a simple placeholder implementation
            try:
                ticker = self.yf.Ticker(query)
                if 'symbol' in ticker.info:
                    # This is a valid ticker
                    return {
                        "query": query,
                        "results": [
                            {
                                "symbol": ticker.info['symbol'],
                                "name": ticker.info.get('longName', ''),
                                "exchange": ticker.info.get('exchange', '')
                            }
                        ]
                    }
                else:
                    return {"query": query, "results": []}
            except:
                return {"query": query, "results": []}
        except Exception as e:
            return {"error": f"Error searching ticker: {str(e)}"}

    async def download_data(self, tickers, period="1mo", interval="1d", start=None, end=None, group_by="ticker", threads=True):
        """Download historical market data for multiple tickers"""
        try:
            self._is_initialized()

            # Convert single ticker to list if needed
            if isinstance(tickers, str):
                tickers = [tickers]

            # If start and end dates are provided, use them instead of period
            if start and end:
                data = self.yf.download(
                    tickers=tickers,
                    start=start,
                    end=end,
                    interval=interval,
                    group_by=group_by,
                    threads=threads
                )
            else:
                data = self.yf.download(
                    tickers=tickers,
                    period=period,
                    interval=interval,
                    group_by=group_by,
                    threads=threads
                )

            # Clean up data for JSON serialization
            cleaned_data = self._sanitize_data(data)

            return {
                "tickers": tickers,
                "period": period if not (start and end) else f"{start} to {end}",
                "interval": interval,
                "data": cleaned_data
            }
        except Exception as e:
            return {"error": f"Error downloading data: {str(e)}"}


# Tool function definitions that will be registered with MCP

async def yfinance_get_ticker_info(ticker_symbol: str, ctx: Context = None) -> str:
    """Get basic information about a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
    - JSON string containing the ticker's basic information
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_ticker_info(ticker_symbol)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving ticker info: {str(e)}"


async def yfinance_get_historical_data(
    ticker_symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    start: str = None,
    end: str = None,
    ctx: Context = None
) -> str:
    """Get historical market data for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
    - period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    - start: Start date string (YYYY-MM-DD) - if provided with end, overrides period
    - end: End date string (YYYY-MM-DD) - if provided with start, overrides period

    Returns:
    - JSON string containing historical price data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_historical_data(ticker_symbol, period, interval, start, end)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving historical data: {str(e)}"


async def yfinance_get_financials(
    ticker_symbol: str,
    quarterly: bool = False,
    ctx: Context = None
) -> str:
    """Get income statement data for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
    - quarterly: If True, get quarterly data instead of annual

    Returns:
    - JSON string containing financial data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_financials(ticker_symbol, quarterly)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving financials: {str(e)}"


async def yfinance_get_balance_sheet(
    ticker_symbol: str,
    quarterly: bool = False,
    ctx: Context = None
) -> str:
    """Get balance sheet data for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
    - quarterly: If True, get quarterly data instead of annual

    Returns:
    - JSON string containing balance sheet data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_balance_sheet(ticker_symbol, quarterly)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving balance sheet: {str(e)}"


async def yfinance_get_cashflow(
    ticker_symbol: str,
    quarterly: bool = False,
    ctx: Context = None
) -> str:
    """Get cash flow data for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
    - quarterly: If True, get quarterly data instead of annual

    Returns:
    - JSON string containing cash flow data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_cashflow(ticker_symbol, quarterly)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving cashflow: {str(e)}"


async def yfinance_get_earnings(
    ticker_symbol: str,
    quarterly: bool = False,
    ctx: Context = None
) -> str:
    """Get earnings data for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
    - quarterly: If True, get quarterly data instead of annual

    Returns:
    - JSON string containing earnings data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_earnings(ticker_symbol, quarterly)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving earnings: {str(e)}"


async def yfinance_get_major_holders(
    ticker_symbol: str,
    ctx: Context = None
) -> str:
    """Get major shareholders for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
    - JSON string containing major shareholders data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_major_holders(ticker_symbol)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving major holders: {str(e)}"


async def yfinance_get_institutional_holders(
    ticker_symbol: str,
    ctx: Context = None
) -> str:
    """Get institutional shareholders for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
    - JSON string containing institutional shareholders data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_institutional_holders(ticker_symbol)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving institutional holders: {str(e)}"


async def yfinance_get_recommendations(
    ticker_symbol: str,
    ctx: Context = None
) -> str:
    """Get analyst recommendations for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
    - JSON string containing analyst recommendations
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_recommendations(ticker_symbol)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving recommendations: {str(e)}"


async def yfinance_get_calendar(
    ticker_symbol: str,
    ctx: Context = None
) -> str:
    """Get earnings calendar for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
    - JSON string containing earnings calendar data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_calendar(ticker_symbol)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving calendar: {str(e)}"


async def yfinance_get_options(
    ticker_symbol: str,
    date: str = None,
    ctx: Context = None
) -> str:
    """Get options chain data for a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)
    - date: Options expiration date (format: YYYY-MM-DD). If none, uses first available date.

    Returns:
    - JSON string containing options chain data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_options(ticker_symbol, date)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving options data: {str(e)}"


async def yfinance_get_news(
    ticker_symbol: str,
    ctx: Context = None
) -> str:
    """Get recent news about a ticker symbol

    Parameters:
    - ticker_symbol: The stock ticker symbol (e.g., 'AAPL' for Apple)

    Returns:
    - JSON string containing news articles
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.get_news(ticker_symbol)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error retrieving news: {str(e)}"


async def yfinance_search_ticker(
    query: str,
    ctx: Context = None
) -> str:
    """Search for ticker symbols matching a query

    Parameters:
    - query: Search query string

    Returns:
    - JSON string containing search results
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.search_ticker(query)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error searching ticker: {str(e)}"


async def yfinance_download_data(
    tickers: Union[str, List[str]],
    period: str = "1mo",
    interval: str = "1d",
    start: str = None,
    end: str = None,
    group_by: str = "ticker",
    threads: bool = True,
    ctx: Context = None
) -> str:
    """Download historical market data for multiple tickers

    Parameters:
    - tickers: Single ticker string or list of ticker symbols
    - period: Data period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    - interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    - start: Start date string (YYYY-MM-DD) - if provided with end, overrides period
    - end: End date string (YYYY-MM-DD) - if provided with start, overrides period
    - group_by: How to group the data ('ticker' or 'column')
    - threads: Whether to use multi-threading for faster downloads

    Returns:
    - JSON string containing downloaded data
    """
    yfinance = _get_yfinance_service()
    if not yfinance:
        return "YFinance service not properly initialized. Check if yfinance library is installed."

    try:
        result = await yfinance.download_data(tickers, period, interval, start, end, group_by, threads)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error downloading data: {str(e)}"

# Tool registration and initialization
_yfinance_service = None


def initialize_yfinance_service():
    """Initialize the YFinance service"""
    global _yfinance_service
    _yfinance_service = YFinanceService()
    return _yfinance_service


def _get_yfinance_service():
    """Get or initialize the YFinance service"""
    global _yfinance_service
    if _yfinance_service is None:
        _yfinance_service = initialize_yfinance_service()
    return _yfinance_service


def get_yfinance_tools():
    """Get a dictionary of all YFinance tools for registration with MCP"""
    return {
        YFinanceTools.GET_TICKER_INFO: yfinance_get_ticker_info,
        YFinanceTools.GET_HISTORICAL_DATA: yfinance_get_historical_data,
        YFinanceTools.GET_FINANCIALS: yfinance_get_financials,
        YFinanceTools.GET_BALANCE_SHEET: yfinance_get_balance_sheet,
        YFinanceTools.GET_CASHFLOW: yfinance_get_cashflow,
        YFinanceTools.GET_EARNINGS: yfinance_get_earnings,
        YFinanceTools.GET_MAJOR_HOLDERS: yfinance_get_major_holders,
        YFinanceTools.GET_INSTITUTIONAL_HOLDERS: yfinance_get_institutional_holders,
        YFinanceTools.GET_RECOMMENDATIONS: yfinance_get_recommendations,
        YFinanceTools.GET_CALENDAR: yfinance_get_calendar,
        YFinanceTools.GET_OPTIONS: yfinance_get_options,
        YFinanceTools.GET_NEWS: yfinance_get_news,
        YFinanceTools.SEARCH_TICKER: yfinance_search_ticker,
        YFinanceTools.DOWNLOAD_DATA: yfinance_download_data
    }


# This function will be called by the unified server to initialize the module
def initialize(mcp=None):
    """Initialize the YFinance module with MCP reference"""
    if mcp:
        set_external_mcp(mcp)

    # Initialize the service
    service = initialize_yfinance_service()

    # Check if the initialization was successful
    if service and service.initialized:
        logging.info("YFinance service initialized successfully")
        return True
    else:
        logging.warning(
            "Failed to initialize YFinance service. Please ensure yfinance is installed.")
        return False


if __name__ == "__main__":
    print("YFinance service module - use with MCP Unified Server")
