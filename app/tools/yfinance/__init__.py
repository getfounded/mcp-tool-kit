"""
YFinance tools for accessing stock market data.
"""
from app.tools.yfinance.tools import *


def get_yfinance_tools():
    """Return a dictionary of YFinance tools for registration."""
    return {
        "yfinance_get_ticker_info": yfinance_get_ticker_info,
        "yfinance_get_historical_data": yfinance_get_historical_data,
        "yfinance_get_financials": yfinance_get_financials,
        "yfinance_get_balance_sheet": yfinance_get_balance_sheet,
        "yfinance_get_cashflow": yfinance_get_cashflow,
        "yfinance_get_earnings": yfinance_get_earnings,
        "yfinance_get_major_holders": yfinance_get_major_holders,
        "yfinance_get_institutional_holders": yfinance_get_institutional_holders,
        "yfinance_get_recommendations": yfinance_get_recommendations,
        "yfinance_get_calendar": yfinance_get_calendar,
        "yfinance_get_options": yfinance_get_options,
        "yfinance_get_news": yfinance_get_news,
        "yfinance_search_ticker": yfinance_search_ticker,
        "yfinance_download_data": yfinance_download_data
    }


def set_external_mcp(mcp_instance):
    """Set external MCP reference for this module."""
    global mcp
    mcp = mcp_instance


def initialize(mcp_instance):
    """Initialize the YFinance module with MCP instance."""
    set_external_mcp(mcp_instance)
    return True
